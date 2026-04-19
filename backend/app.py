import json
import os
import threading
import uuid

from dotenv import load_dotenv
load_dotenv(override=True)  # override=True ensures .env values win over blank shell vars

import requests as http_requests

from flask import Flask, jsonify, request
from flask_cors import CORS

import sandbox.orchestrator as orchestrator
from ai_analyzer import build_chat_system_prompt, chat_with_ai
from services.submit_service import EXT_MAP, read_skeleton, run_submit_pipeline

app = Flask(__name__)
CORS(app, origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5001",
    "http://127.0.0.1:5001",
])

PROBLEMS_DIR = os.getenv(
    "PROBLEMS_DIR",
    os.path.join(os.path.dirname(__file__), "..", "problems"),
)

# ── In-memory stores ──────────────────────────────────────────────────────────

# Keyed by session_id (async submit flow)
# {
#   "status":       "processing" | "done" | "error",
#   "challenge_id": str,
#   "report":       dict | None,
#   "port":         int | None,
#   "container_id": str | None,
#   "error":        str | None,
# }
sessions: dict = {}
sessions_lock = threading.Lock()


# ── Helpers ───────────────────────────────────────────────────────────────────


def load_challenge_meta(challenge_id: str) -> dict | None:
    meta_path = os.path.join(PROBLEMS_DIR, challenge_id, "meta.json")
    if not os.path.exists(meta_path):
        return None
    with open(meta_path) as fh:
        return json.load(fh)


_challenges_cache: list | None = None

def list_challenges() -> list:
    global _challenges_cache
    if _challenges_cache is not None:
        return _challenges_cache
    challenges = []
    if not os.path.isdir(PROBLEMS_DIR):
        return challenges
    for name in sorted(os.listdir(PROBLEMS_DIR)):
        path = os.path.join(PROBLEMS_DIR, name)
        if os.path.isdir(path):
            meta = load_challenge_meta(name)
            if meta:
                challenges.append({
                    "id": name,
                    "title": meta.get("title", name),
                    "category": meta.get("category", "Uncategorized"),
                    "difficulty": meta.get("difficulty", "Medium"),
                    "description": meta.get("description", ""),
                })
    _challenges_cache = challenges
    return challenges


# ── Challenge routes ──────────────────────────────────────────────────────────

@app.get("/api/challenges")
def get_challenges():
    return jsonify(list_challenges())


@app.get("/api/challenges/<challenge_id>")
def get_challenge(challenge_id):
    meta = load_challenge_meta(challenge_id)
    if not meta:
        return jsonify({"error": "Challenge not found"}), 404

    language = request.args.get("language", "python").lower()
    skeleton = read_skeleton(PROBLEMS_DIR, challenge_id, language)

    return jsonify({
        "id": challenge_id,
        "title": meta.get("title", challenge_id),
        "category": meta.get("category", "Uncategorized"),
        "difficulty": meta.get("difficulty", "Medium"),
        "description": meta.get("description", ""),
        "hint": meta.get("hint", ""),
        "language": language,
        "languages": meta.get("languages", ["python"]),
        "skeleton": skeleton,
    })


# ── Async submit ──────────────────────────────────────────────────────────────

@app.post("/api/submit")
def submit():
    """
    Accepts { "challenge_id": str, "code": str }.
    Returns { "session_id": str, "status": "processing" } immediately.
    Background pipeline: build image → validate + sandbox concurrently.
    """
    data = request.get_json(force=True)
    challenge_id = data.get("challenge_id", "").strip()
    code = data.get("code", "").strip()
    language = data.get("language", "python").lower()

    if not challenge_id:
        return jsonify({"error": "challenge_id is required"}), 400
    if not code:
        return jsonify({"error": "code is required"}), 400

    meta = load_challenge_meta(challenge_id)
    if not meta:
        return jsonify({"error": "Challenge not found"}), 404

    session_id = str(uuid.uuid4())

    with sessions_lock:
        sessions[session_id] = {
            "status": "processing",
            "challenge_id": challenge_id,
            "language": language,
            "code": code,
            "report": None,
            "port": None,
            "container_id": None,
            "error": None,
        }

    threading.Thread(
        target=run_submit_pipeline,
        args=(session_id, challenge_id, code, language, meta, sessions, sessions_lock, PROBLEMS_DIR),
        daemon=True,
        name=f"coord-{session_id[:8]}",
    ).start()

    return jsonify({"session_id": session_id, "status": "processing"})


@app.post("/api/attack")
def attack():
    data = request.get_json(force=True)
    session_id = data.get("session_id", "").strip()
    payload = data.get("payload", {})

    with sessions_lock:
        session = sessions.get(session_id)

    if not session or not session.get("port"):
        return jsonify({"error": "Sandbox not ready"}), 404

    port = session["port"]
    try:
        resp = http_requests.post(
            f"http://127.0.0.1:{port}/login",
            json=payload,
            timeout=5,
        )
        try:
            body = resp.json()
        except Exception:
            body = {"raw": resp.text}
        return jsonify({"status_code": resp.status_code, "body": body})
    except http_requests.exceptions.RequestException as exc:
        return jsonify({"error": f"Failed to reach sandbox: {exc}"}), 502


@app.post("/api/chat")
def chat():
    data = request.get_json(force=True)
    session_id = data.get("session_id", "").strip()
    user_message = data.get("message", "").strip()
    history = data.get("history", [])

    if not user_message:
        return jsonify({"reply": None, "error": "message is required"}), 400

    with sessions_lock:
        session = sessions.get(session_id)

    report = session.get("report") if session else None
    language = session.get("language", "python") if session else "python"
    system_prompt = build_chat_system_prompt(report, language)

    try:
        reply = chat_with_ai(system_prompt, history, user_message)
        return jsonify({"reply": reply, "error": None})
    except Exception as exc:
        app.logger.warning("Chat AI error: %s", exc)
        return jsonify({"reply": None, "error": "AI unavailable"})


@app.get("/api/report/<session_id>")
def get_session_report(session_id):
    with sessions_lock:
        session = sessions.get(session_id)

    if not session:
        return jsonify({"error": "Session not found"}), 404

    if session["status"] != "done":
        return jsonify({"status": "processing"})

    return jsonify(session["report"])


@app.get("/api/sessions/<session_id>")
def get_session(session_id):
    """Poll endpoint. Returns current status + report once validation is done."""
    with sessions_lock:
        session = sessions.get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    response = {
        "session_id": session_id,
        "status": session["status"],
        "challenge_id": session["challenge_id"],
        "language": session.get("language", "python"),
        "code": session.get("code", ""),
        "port": session["port"],
    }
    if session["status"] == "done" and session["report"]:
        response["report"] = session["report"]
    if session["error"]:
        response["error"] = session["error"]

    return jsonify(response)


if __name__ == "__main__":
    list_challenges()  # warm cache on startup
    # threaded=True so Flask can handle concurrent poll requests while
    # background threads are building/running containers
    app.run(host="0.0.0.0", debug=False, port=5001, threaded=True)
