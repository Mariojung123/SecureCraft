from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder="templates")

users = {
    1: {"id": 1, "username": "alice", "email": "alice@example.com", "ssn": "123-45-6789"},
    2: {"id": 2, "username": "bob", "email": "bob@example.com", "ssn": "987-65-4321"},
}


# VULNERABLE: any authenticated user can access any profile by changing user_id.
# Fix this to check that the requester can only access their own profile.
def get_profile(requesting_user_id, target_user_id):
    user = users.get(target_user_id)
    if not user:
        return None, "Not found"
    return user, None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/profile/<int:user_id>")
def profile_route(user_id):
    # Simulate: requester is always user 1 (logged-in user)
    requester_id = int(request.headers.get("X-User-Id", "1"))
    profile, err = get_profile(requester_id, user_id)
    if err:
        return jsonify({"error": err}), 403
    return jsonify(profile)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
