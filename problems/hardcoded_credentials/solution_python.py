import hmac
import os
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder="templates")


# FIXED: secret is read from the environment at runtime — never stored in
# source code. hmac.compare_digest() provides constant-time comparison to
# prevent timing oracle attacks.
def check_api_key(provided_key):
    expected = os.environ.get("ADMIN_API_KEY", "")
    if not expected:
        return False
    return hmac.compare_digest(provided_key, expected)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin")
def admin_route():
    key = request.headers.get("X-Api-Key", "")
    if not check_api_key(key):
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"data": "Sensitive admin data"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
