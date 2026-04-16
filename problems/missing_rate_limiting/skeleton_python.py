from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder="templates")

USERS = {"admin": "correct_password"}


# VULNERABLE: no rate limiting — infinite brute-force attempts allowed.
# Fix this to limit each IP to 5 attempts per 60 seconds.
def is_rate_limited(ip):
    return False  # TODO: implement rate limiting


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
