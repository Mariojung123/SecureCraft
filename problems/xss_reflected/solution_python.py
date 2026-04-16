import html
from flask import Flask, request, render_template

app = Flask(__name__, template_folder="templates")


# FIXED: query is HTML-escaped before being inserted into the response.
# <, >, ", & are converted to safe entities so the browser renders them
# as text rather than interpreting them as HTML.
def search_page(query):
    safe_query = html.escape(query)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>QuickSearch – Results</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}
    body{{background:#f1f5f9;min-height:100vh}}
    nav{{background:#4f46e5;padding:13px 24px;display:flex;align-items:center;gap:10px}}
    .logo{{color:#fff;font-weight:700;font-size:15px}}
    .tag{{background:rgba(255,255,255,.2);color:#fff;font-size:10px;padding:2px 9px;border-radius:99px;font-weight:600;letter-spacing:.06em}}
    .wrap{{max-width:640px;margin:40px auto;padding:0 16px}}
    .card{{background:#fff;border-radius:12px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,.08)}}
    h1{{font-size:18px;font-weight:700;color:#1e293b;margin-bottom:8px}}
    .query{{background:#f1f5f9;border-radius:6px;padding:8px 12px;font-family:monospace;font-size:14px;color:#4f46e5;margin-bottom:16px;word-break:break-all}}
    a{{color:#4f46e5;font-size:13px;text-decoration:none}}
    a:hover{{text-decoration:underline}}
  </style>
</head>
<body>
  <nav><span class="logo">&#128269; QuickSearch</span><span class="tag">WEB SEARCH</span></nav>
  <div class="wrap">
    <div class="card">
      <h1>Results for:</h1>
      <div class="query">{safe_query}</div>
      <a href="/">&larr; New search</a>
    </div>
  </div>
</body>
</html>"""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search_route():
    query = request.args.get("q", "")
    return search_page(query)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
