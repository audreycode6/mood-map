from functools import wraps

from flask import (
    flash,
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from bcrypt import hashpw, gensalt, checkpw

from database_persistence import DatabasePersistence

app = Flask(__name__)
app.secret_key = "dev_secret_key"


def is_logged_in():
    return session.get("username")


def require_login(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        if not is_logged_in():
            # print(f"TESTing: func: {request.path}")
            session["protected_page_path"] = request.path
            flash("You must be logged in to do that.")
            return redirect(
                url_for("display_login")
            )  # TODO how to remember and redirect to appropriate path if successful login

        return func(*args, **kwargs)

    return decorated_func


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
                # store username in session to track logged in user
                session["username"] = username
                print("==> FLash: Success user authenticated")

                # if proceeding from login redirect go back to original path
                if session["protected_page_path"]:
                    print(f"TEST: {session['protected_page_path']}")
                    return redirect(session["protected_page_path"])

                # default
                return render_template("view_entries.html")

    # error redirect to same page with flash message
    print(f"==> flash ERror: Invalid credentials, please try again")
    return render_template("login.html"), 404


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    print("You have been signed out.")
    # TODO flash
    return redirect(url_for("login"))


@app.route("/view_entries")
@require_login
def view_entries():
    # TODO
    return render_template("view_entries.html")


@app.route("/create_entry")
@require_login
def display_create_entry():
    # TODO
    return render_template("create_entry.html")


@app.route("/create_entry", methods=["POSTS"])
@require_login
def create_entry():
    # TODO
    return render_template("create_entry.html")


@app.route("/view_entry/<int:entry_id>")
@require_login
def display_entry():  # TODO
    return render_template("view_entry.html")


@app.route("/edit_entry/<int:entry_id>")
@require_login
def display_edit_entry():
    # TODO
    return render_template("edit_entry.html")


@app.route("/edit_entry/<int:entry_id>", methods=["POSTS"])
@require_login
def edit_entry():
    # TODO
    return render_template("view_entry.html")


@app.route("/delete_entry/<int:entry_id>", methods=["POSTS"])
@require_login
def delete_entry():
    # TODO
    return render_template("view_entry.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
