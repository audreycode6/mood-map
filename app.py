from flask import (
    flash,
    Flask,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

from bcrypt import hashpw, gensalt, checkpw

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
    password = request.form.get("password").strip()

    if username and password:
        if not g.storage.user_exists(username):
            hashed_pw = hashpw(password.encode("utf-8"), gensalt())
            # convert to str before storing in db
            hashed_pw_str = hashed_pw.decode("utf-8")

            # create user
            g.storage.register_new_user(username, hashed_pw_str)
            # TODO add flash
            print("==> flash Success: user is registered ")
            return render_template("login.html")

        else:
            error = f"user {username} already exists"

    else:
        error = "missing input"

    print(f"==> flash error: {error}, please try again")
    return render_template("register.html", username=username), 422


@app.route("/login")
def display_login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username").strip().lower()
    password = request.form.get("password").strip()

    # validate input
    if username and password:
        result = g.storage.user_exists(username)
        if result:
            hashed_pw = result[2].encode("utf-8")
            b_pw = password.encode("utf-8")
            if checkpw(b_pw, hashed_pw):
                print("==> FLash: Success user authenticated")

                # success redirect to index with login view
                return render_template("view_entries.html")

    # error redirect to same page with flash message
    print(f"==> flash ERror: Invalid credentials, please try again")
    return render_template("login.html"), 404


@app.route("/view_entries")
def view_entries():
    return render_template("view_entries.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
