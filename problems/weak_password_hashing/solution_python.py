import bcrypt
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder="templates")

# Simulated user store: {username: hashed_password}
users = {}


# FIXED: bcrypt is intentionally slow and salts each password automatically.
# Even identical passwords produce different hashes, and a single verification
# takes ~100ms — making brute-force billions of times harder than MD5.
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password, stored_hash):
    return bcrypt.checkpw(password.encode(), stored_hash.encode())


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
