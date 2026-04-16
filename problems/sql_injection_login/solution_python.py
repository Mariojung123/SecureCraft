import sqlite3
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder="templates")
DB_PATH = "/tmp/users.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
    )
    conn.execute(
        "INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'admin', 'supersecret123')"
    )
    conn.commit()
    conn.close()


# FIXED: parameterized query — user input is passed as bound values,
# never interpolated into the SQL string.
def login(username, password):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password),
    )
    return cursor.fetchone()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login_route():
    data = request.get_json(force=True)
    user = login(data.get("username", ""), data.get("password", ""))
    if user:
        return jsonify({"success": True, "user": user[1]})
    return jsonify({"success": False}), 401


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080)
