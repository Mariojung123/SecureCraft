import sqlite3
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder="templates")
DB_PATH = "/tmp/shop.db"


def get_db():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price REAL)"
    )
    conn.execute("CREATE TABLE IF NOT EXISTS secrets (id INTEGER PRIMARY KEY, token TEXT)")
    conn.execute("INSERT OR IGNORE INTO products VALUES (1, 'Widget', 9.99)")
    conn.execute("INSERT OR IGNORE INTO products VALUES (2, 'Gadget', 19.99)")
    conn.execute("INSERT OR IGNORE INTO secrets VALUES (1, 'API_KEY_12345')")
    conn.commit()
    conn.close()


# FIXED: parameterized LIKE query — the wildcard characters are concatenated
# in Python, not injected into SQL, so UNION attacks are impossible.
def search_products(term):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM products WHERE name LIKE ?",
        ('%' + term + '%',),
    )
    return cursor.fetchall()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search_route():
    term = request.args.get("q", "")
    results = search_products(term)
    return jsonify(results)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080)
