import re
import subprocess
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder="templates")


# FIXED: hostname is validated against a strict allowlist pattern and passed
# as a list with shell=False — no shell interpreter is involved.
def ping_host(hostname):
    if not re.match(r'^[a-zA-Z0-9._-]+$', hostname):
        return 'Invalid hostname'
    result = subprocess.run(
        ['ping', '-c', '1', hostname],
        capture_output=True,
        text=True,
        timeout=5,
        shell=False,
    )
    return result.stdout + result.stderr


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ping")
def ping_route():
    hostname = request.args.get("host", "")
    output = ping_host(hostname)
    return jsonify({"output": output})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
