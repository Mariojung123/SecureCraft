import os
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder="templates")
BASE_DIR = "/app/files"


# VULNERABLE: the filename is joined to BASE_DIR without checking
# whether the result escapes the base directory.
def get_file(filename):
    path = os.path.join(BASE_DIR, filename)
    if not os.path.isfile(path):
        return None, "Not found"
    with open(path) as f:
        return f.read(), None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/download")
def download_route():
    filename = request.args.get("file", "")
    content, err = get_file(filename)
    if err:
        return jsonify({"error": err}), 404
    return jsonify({"content": content})


if __name__ == "__main__":
    os.makedirs(BASE_DIR, exist_ok=True)
    with open(os.path.join(BASE_DIR, "public.txt"), "w") as f:
        f.write("This file is public.")
    app.run(host="0.0.0.0", port=8080)
