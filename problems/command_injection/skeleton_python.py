import subprocess
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder="templates")


# VULNERABLE: hostname is passed directly to a shell command.
# Fix this to avoid shell injection.
def ping_host(hostname):
    result = subprocess.run(
        f"ping -c 1 {hostname}",
        shell=True,
        capture_output=True,
        text=True,
        timeout=10,
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
