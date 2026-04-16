from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder="templates")

# VULNERABLE: secret is hardcoded in source code.
# Fix this to read the key from an environment variable.
ADMIN_API_KEY = "super_secret_admin_key_1234"


def check_api_key(provided_key):
    return provided_key == ADMIN_API_KEY


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
