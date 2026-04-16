from flask import Flask, request, redirect, render_template

app = Flask(__name__, template_folder="templates")
comments = []  # In-memory store


# VULNERABLE: comments are inserted raw into HTML.
# Fix this to escape each comment before rendering.
def render_comments(comment_list):
    items = "".join(
        f"""<div class="comment">
          <div class="avatar">{c[0].upper() if c else "?"}</div>
          <div class="body"><p class="text">{c}</p></div>
        </div>"""
        for c in comment_list
    ) or '<p class="empty">No comments yet. Be the first!</p>'
    return render_template("index.html", items=items)


@app.route("/")
def index():
    return render_comments(comments)


@app.route("/comment", methods=["POST"])
def add_comment():
    text = request.form.get("text", "")
    comments.append(text)
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
