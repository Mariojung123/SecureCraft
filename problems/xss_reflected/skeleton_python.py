from flask import Flask, request, render_template

app = Flask(__name__, template_folder="templates")


# VULNERABLE: the query parameter is inserted raw into the HTML response.
# Fix this to escape the query before rendering.
def search_page(query):
    return f"<html><body><h1>Results for: {query}</h1></body></html>"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search_route():
    query = request.args.get("q", "")
    return search_page(query)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
