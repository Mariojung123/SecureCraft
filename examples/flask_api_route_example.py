# ── Flask API Route Pattern ───────────────────────────────────────────────────
# Reference: backend/app.py
# Pattern: All routes follow this structure — validate input, load meta, process, return jsonify

from flask import jsonify, request

# ── GET route with path param ─────────────────────────────────────────────────
@app.get("/api/challenges/<challenge_id>")
def get_challenge(challenge_id):
    meta = load_challenge_meta(challenge_id)
    if not meta:
        return jsonify({"error": "Challenge not found"}), 404

    language = request.args.get("language", "python").lower()
    # ... processing ...
    return jsonify({
        "id": challenge_id,
        "title": meta.get("title", challenge_id),
    })


# ── POST route with JSON body + async background task ─────────────────────────
@app.post("/api/submit")
def submit():
    data = request.get_json(force=True)
    challenge_id = data.get("challenge_id", "").strip()
    code = data.get("code", "").strip()

    # Always validate required fields
    if not challenge_id:
        return jsonify({"error": "challenge_id is required"}), 400
    if not code:
        return jsonify({"error": "code is required"}), 400

    meta = load_challenge_meta(challenge_id)
    if not meta:
        return jsonify({"error": "Challenge not found"}), 404

    session_id = str(uuid.uuid4())

    # Store in-memory session state
    with sessions_lock:
        sessions[session_id] = {
            "status": "processing",
            "challenge_id": challenge_id,
            "report": None,
            "error": None,
        }

    # Background thread pattern for long-running work
    def coordinator():
        try:
            result = do_work(challenge_id, code)
            _update_session(session_id, status="done", report=result)
        except Exception as exc:
            _update_session(session_id, status="error", error=str(exc))

    threading.Thread(target=coordinator, daemon=True).start()
    return jsonify({"session_id": session_id, "status": "processing"})


# ── Session state helper ───────────────────────────────────────────────────────
def _update_session(session_id: str, **kwargs) -> None:
    with sessions_lock:
        if session_id in sessions:
            sessions[session_id].update(kwargs)
