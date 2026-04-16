import os
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder="templates")
BASE_DIR = "/app/files"


# FIXED: os.path.realpath() resolves all ../ segments to a canonical
# absolute path. We then verify the result starts with the real base
# directory — if not, the request is rejected with 403.
def get_file(filename):
    real_base = os.path.realpath(BASE_DIR)
    requested = os.path.realpath(os.path.join(BASE_DIR, filename))
    if not requested.startswith(real_base + os.sep):
        return None, "Access denied"
    if not os.path.isfile(requested):
        return None, "Not found"
    with open(requested) as f:
        return f.read(), None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/download")
def download_route():
    filename = request.args.get("file", "")
    content, err = get_file(filename)
    if err:
        status = 403 if err == "Access denied" else 404
        return jsonify({"error": err}), status
    return jsonify({"content": content})


if __name__ == "__main__":
    os.makedirs(BASE_DIR, exist_ok=True)
    with open(os.path.join(BASE_DIR, "public.txt"), "w") as f:
        f.write("This file is public.")
    app.run(host="0.0.0.0", port=8080)
