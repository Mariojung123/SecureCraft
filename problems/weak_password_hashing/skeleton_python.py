import hashlib
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder="templates")

# Simulated user store: {username: hashed_password}
users = {}


# VULNERABLE: MD5 is used to hash passwords.
# Fix this to use bcrypt instead.
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()


def verify_password(password, stored_hash):
    return hashlib.md5(password.encode()).hexdigest() == stored_hash


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True)
    username = data.get("username", "")
    password = data.get("password", "")
    users[username] = hash_password(password)
    return jsonify({"ok": True})


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    username = data.get("username", "")
    password = data.get("password", "")
    stored = users.get(username)
    if stored and verify_password(password, stored):
        return jsonify({"success": True})
    return jsonify({"success": False}), 401


@app.route("/hash")
def get_hash():
    """Expose the stored hash (simulates a database leak)."""
    username = request.args.get("user", "")
    return jsonify({"hash": users.get(username, "")})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
