import json
import os
import sys
import tempfile
import threading
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# App factory with isolated tmp problems dir
# ---------------------------------------------------------------------------

def _make_app(problems_dir: str):
    import importlib
    import app as app_module
    importlib.reload(app_module)
    app_module.app.config["TESTING"] = True
    app_module.PROBLEMS_DIR = problems_dir
    app_module.sessions.clear()
    app_module._challenges_cache = None
    return app_module.app, app_module.sessions, app_module.sessions_lock


def _write_meta(problems_dir: str, challenge_id: str, extra: dict = None):
    challenge_dir = os.path.join(problems_dir, challenge_id)
    os.makedirs(challenge_dir, exist_ok=True)
    meta = {
        "id": challenge_id,
        "title": "Test Challenge",
        "languages": ["python"],
        "vuln_patterns": {"python": [r"eval\("]},
    }
    if extra:
        meta.update(extra)
    with open(os.path.join(challenge_dir, "meta.json"), "w") as f:
        json.dump(meta, f)
    skeleton_path = os.path.join(challenge_dir, "skeleton_python.py")
    with open(skeleton_path, "w") as f:
        f.write("# skeleton\n")


# ---------------------------------------------------------------------------
# GET /api/challenges
# ---------------------------------------------------------------------------

class TestGetChallenges:
    def test_empty_problems_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            flask_app, _, _ = _make_app(tmpdir)
            with flask_app.test_client() as client:
                resp = client.get("/api/challenges")
            assert resp.status_code == 200
            assert resp.get_json() == []

    def test_returns_challenge_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_meta(tmpdir, "sql_injection")
            flask_app, _, _ = _make_app(tmpdir)
            with flask_app.test_client() as client:
                resp = client.get("/api/challenges")
            data = resp.get_json()
            assert resp.status_code == 200
            assert len(data) == 1
            assert data[0]["id"] == "sql_injection"
            assert data[0]["title"] == "Test Challenge"

    def test_multiple_challenges_sorted(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_meta(tmpdir, "xss_reflected")
            _write_meta(tmpdir, "sql_injection")
            flask_app, _, _ = _make_app(tmpdir)
            with flask_app.test_client() as client:
                resp = client.get("/api/challenges")
            ids = [c["id"] for c in resp.get_json()]
            assert ids == sorted(ids)


# ---------------------------------------------------------------------------
# POST /api/submit
# ---------------------------------------------------------------------------

class TestSubmit:
    def test_missing_challenge_id(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            flask_app, _, _ = _make_app(tmpdir)
            with flask_app.test_client() as client:
                resp = client.post("/api/submit", json={"code": "x = 1"})
            assert resp.status_code == 400
            assert "challenge_id" in resp.get_json()["error"]

    def test_missing_code(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_meta(tmpdir, "sql_injection")
            flask_app, _, _ = _make_app(tmpdir)
            with flask_app.test_client() as client:
                resp = client.post("/api/submit", json={"challenge_id": "sql_injection"})
            assert resp.status_code == 400
            assert "code" in resp.get_json()["error"]

    def test_unknown_challenge(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            flask_app, _, _ = _make_app(tmpdir)
            with flask_app.test_client() as client:
                resp = client.post("/api/submit", json={"challenge_id": "no_such", "code": "x=1"})
            assert resp.status_code == 404

    def test_valid_submit_returns_session_id(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_meta(tmpdir, "sql_injection")
            flask_app, _, _ = _make_app(tmpdir)
            with patch("app.run_submit_pipeline"):
                with flask_app.test_client() as client:
                    resp = client.post("/api/submit", json={
                        "challenge_id": "sql_injection",
                        "code": "x = 1",
                    })
            assert resp.status_code == 200
            data = resp.get_json()
            assert "session_id" in data
            assert data["status"] == "processing"


# ---------------------------------------------------------------------------
# GET /api/report/<session_id>
# ---------------------------------------------------------------------------

class TestGetReport:
    def test_unknown_session(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            flask_app, _, _ = _make_app(tmpdir)
            with flask_app.test_client() as client:
                resp = client.get("/api/report/nonexistent-id")
            assert resp.status_code == 404

    def test_processing_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            flask_app, sessions, sessions_lock = _make_app(tmpdir)
            sid = "test-session-processing"
            with sessions_lock:
                sessions[sid] = {"status": "processing", "report": None}
            with flask_app.test_client() as client:
                resp = client.get(f"/api/report/{sid}")
            assert resp.status_code == 200
            assert resp.get_json()["status"] == "processing"

    def test_done_status_returns_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            flask_app, sessions, sessions_lock = _make_app(tmpdir)
            sid = "test-session-done"
            report = {"challenge_id": "sql_injection", "vulnerable_lines": [3], "severity": "HIGH"}
            with sessions_lock:
                sessions[sid] = {"status": "done", "report": report}
            with flask_app.test_client() as client:
                resp = client.get(f"/api/report/{sid}")
            assert resp.status_code == 200
            data = resp.get_json()
            assert data["challenge_id"] == "sql_injection"
            assert data["severity"] == "HIGH"
