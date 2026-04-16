import time
from collections import defaultdict
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder="templates")

USERS = {"admin": "correct_password"}

# FIXED: sliding-window rate limiter keyed by client IP.
# Each IP is allowed at most MAX_ATTEMPTS requests within a WINDOW-second window.
ATTEMPTS = defaultdict(list)
MAX_ATTEMPTS = 5
WINDOW = 60


def is_rate_limited(ip):
    now = time.time()
    # Drop timestamps that have fallen outside the current window
    ATTEMPTS[ip] = [t for t in ATTEMPTS[ip] if now - t < WINDOW]
    if len(ATTEMPTS[ip]) >= MAX_ATTEMPTS:
        return True
    ATTEMPTS[ip].append(now)
    return False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    ip = request.remote_addr
    if is_rate_limited(ip):
        return jsonify({"error": "Too many requests"}), 429

    data = request.get_json(force=True)
    username = data.get("username", "")
    password = data.get("password", "")

    if USERS.get(username) == password:
        return jsonify({"success": True})
    return jsonify({"success": False}), 401


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
