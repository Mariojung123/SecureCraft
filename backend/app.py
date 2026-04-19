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
from ai_analyzer import chat_with_ai
from services.submit_service import EXT_MAP, assemble_report

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

# Keyed by report_id (legacy synchronous submit flow)
reports: dict = {}

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


def _update_session(session_id: str, **kwargs) -> None:
    with sessions_lock:
        if session_id in sessions:
            sessions[session_id].update(kwargs)


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
    ext = EXT_MAP.get(language, "py")
    skeleton_path = os.path.join(PROBLEMS_DIR, challenge_id, f"skeleton_{language}.{ext}")
    skeleton = ""
    if os.path.exists(skeleton_path):
        with open(skeleton_path) as fh:
            skeleton = fh.read()

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

    Two threads run concurrently in the background after the image is built:
      Thread 1 — Validation: run attack.sh + check.py, store report.
      Thread 2 — Sandbox: keep a container running, expose it on a host port.
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
            "code": code,           # stored so the sandbox page can display it
            "report": None,
            "port": None,
            "container_id": None,
            "error": None,
        }

    def coordinator():
        # ── Phase 1: build the image (shared by both threads) ────────────────
        try:
            image_tag = orchestrator.build_image(challenge_id, code, language)
        except Exception as exc:
            _update_session(session_id, status="error", error=f"Image build failed: {exc}")
            return

        # ── Phase 2: validation + sandbox run concurrently ───────────────────
        validation_done = threading.Event()

        def validation_thread():
            validation_result = orchestrator.run_validation(challenge_id, image_tag, language)
            with sessions_lock:
                sess = sessions.get(session_id, {})
                submitted_code = sess.get("code", "")
                lang = sess.get("language", "python")

            report = assemble_report(
                session_id=session_id,
                challenge_id=challenge_id,
                code=submitted_code,
                language=lang,
                meta=meta,
                validation_result=validation_result,
                problems_dir=PROBLEMS_DIR,
            )
            _update_session(session_id, report=report, status="done")
            validation_done.set()

        def sandbox_thread():
            try:
                container_id, port = orchestrator.run_sandbox(image_tag, session_id, language)
                _update_session(session_id, container_id=container_id, port=port)
            except Exception as exc:
                # Sandbox failure is non-fatal; validation result still matters
                _update_session(session_id, error=f"Sandbox error: {exc}")

        t1 = threading.Thread(target=validation_thread, daemon=True, name=f"validate-{session_id[:8]}")
        t2 = threading.Thread(target=sandbox_thread, daemon=True, name=f"sandbox-{session_id[:8]}")

        t1.start()
        t2.start()
        t1.join()
        t2.join()

    threading.Thread(target=coordinator, daemon=True, name=f"coord-{session_id[:8]}").start()

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
    if report:
        problem_id = report.get("challenge_id", "unknown")
        language = session.get("language", "python")
        vulnerability_explanation = report.get("vulnerability_explanation") or report.get("explanation", "")
        attack_payload = report.get("attack_payload", "")
        problem_title = report.get("title", problem_id)
    else:
        problem_id = "unknown"
        language = "python"
        vulnerability_explanation = ""
        attack_payload = ""
        problem_title = "unknown"

    system_prompt = (
        f"You are a security education assistant for SecureCraft, a secure coding education platform.\n"
        f"The student just completed the {problem_id} challenge in {language}.\n"
        f"Their submitted code had this vulnerability: {vulnerability_explanation}\n"
        f"The attack payload used was: {attack_payload}\n"
        f"Your role is to help them deeply understand the security concepts behind this challenge.\n"
        f"Keep responses concise, educational, and encouraging.\n"
        f"Use code examples when helpful. Respond in the same language the student uses."
    )

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
        "port": session["port"],            # None until sandbox container is ready
    }
    if session["status"] == "done" and session["report"]:
        response["report"] = session["report"]
    if session["error"]:
        response["error"] = session["error"]

    return jsonify(response)


# ── Legacy synchronous submit (kept for backwards compat) ────────────────────

@app.post("/api/challenges/<challenge_id>/submit")
def submit_challenge(challenge_id):
    meta = load_challenge_meta(challenge_id)
    if not meta:
        return jsonify({"error": "Challenge not found"}), 404

    data = request.get_json(force=True)
    code = data.get("code", "")
    if not code.strip():
        return jsonify({"error": "No code submitted"}), 400

    try:
        image_tag = orchestrator.build_image(challenge_id, code)
        result = orchestrator.run_validation(challenge_id, image_tag)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    report_id = str(uuid.uuid4())
    reports[report_id] = {
        "report_id": report_id,
        "challenge_id": challenge_id,
        "title": meta.get("title", challenge_id),
        "passed": result["passed"],
        "attack_output": result["attack_output"],
        "check_output": result["check_output"],
        "canonical_fix": meta.get("canonical_fix", ""),
        "explanation": meta.get("explanation", ""),
    }

    return jsonify({
        "passed": result["passed"],
        "output": result["attack_output"],
        "report_id": report_id,
    })


@app.get("/api/reports/<report_id>")
def get_report(report_id):
    report = reports.get(report_id)
    if not report:
        return jsonify({"error": "Report not found"}), 404
    return jsonify(report)


if __name__ == "__main__":
    list_challenges()  # warm cache on startup
    # threaded=True so Flask can handle concurrent poll requests while
    # background threads are building/running containers
    app.run(host="0.0.0.0", debug=False, port=5001, threaded=True)
