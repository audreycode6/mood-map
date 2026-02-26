from flask import (
    flash,
    Flask,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

from bcrypt import hashpw, gensalt

from database_persistence import DatabasePersistence

app = Flask(__name__)
app.secret_key = "dev_secret_key"


@app.before_request
def load_db():
    g.storage = DatabasePersistence()


@app.route("/register")
def display_register():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username").strip().lower()
    password = request.form.get("password").strip().lower()

    # TODO check both fields filled out\ (helper func)
    # TODO check if username is unique
    print(f"TEST username and pw: {username} {password}")

    if username is not None and password is not None:
        is_valid = g.storage.is_unique_user(username)
        if is_valid:
            print(f"flash success: {is_valid}")
            # TODO add user to db
            hashed_pw = hashpw(password.encode("utf-8"), gensalt())
            print(f"pw: {password} -> hash : {hashed_pw}")
            return render_template("login.html")

            # success redirect to login with flash message and create new user in db

    # error redirect to same page with user filled out with flash message

    print("flash error: Invalid credentials, please try again")
    return render_template("register.html", username=username), 422


@app.route("/login")
def display_login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username").strip()
    password = request.form.get("password").strip()

    # check valid input
    # TODO check username and pw to db
    # success redirect to index with login view
    # error redirect to same page with flash message
    print(f"TEST username and pw: {username} {password}")
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
