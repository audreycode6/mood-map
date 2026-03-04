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
                session["user_id"] = result[0]
                print("==> FLash: Success user authenticated")

                # if proceeding from login redirect go back to original path
                protected_page = session.pop("protected_page_path", None)
                if protected_page:
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
    return render_template(
        "create_entry.html",
        pending_emotions=session.get("pending_emotions", []),
        entry_date=request.args.get("entry_date", ""),
        energy_level=request.args.get("energy_level", ""),
        mood_range=request.args.get("mood_range", ""),
        reflection=request.args.get("reflection", ""),
    )


def validate_entry(entry_date, energy_level, mood_range):
    if not entry_date:
        raise ValueError("Missing a date")
    # check that entry date for that user doesnt already exists
    if g.storage.check_unique_date(
        session["user_id"], entry_date
    ):  # TODO when in edit mode do not care if it is same date
        raise ValueError(f"You already have an entry for this date: {entry_date}.")
    if not energy_level:
        raise ValueError("Missing a value for energy level")
    if not mood_range:
        raise ValueError("Missing a value for mood range")


@app.route("/add_pending_emotion", methods=["POST"])
@require_login
def add_emotion_to_list():  # TODO
    emotion = request.form.get("emotion", "").strip()
    print(f"result of emotion from form: {emotion}")
    if emotion:
        session.setdefault("pending_emotions", [])
        session["pending_emotions"].append(emotion)
        session.modified = True
        print(f"TEST: emotion added to session: {session['pending_emotions']}")
    return redirect(
        url_for(
            "display_create_entry",
            entry_date=request.form.get("entry_date", ""),
            energy_level=request.form.get("energy_level", ""),
            mood_range=request.form.get("mood_range", ""),
            reflection=request.form.get("reflection", ""),
        )
    )


@app.route("/create_entry", methods=["POST"])
@require_login
def create_entry():  # TODO add emotions
    # TODO maybe add a valid_request_body_keys_exist like budget.py
    entry_date = request.form.get("entry_date")
    energy_level = request.form.get("energy_level")
    mood_range = request.form.get("mood_range")
    emotions = request.form.get("emotions")
    reflection = request.form.get("reflection")

    user_id = session["user_id"]
    try:
        validate_entry(entry_date, energy_level, mood_range)
        entry_id = g.storage.create_new_entry(
            user_id, entry_date, energy_level, mood_range, reflection
        )
        print(f"SUCCESS: entry_id = {entry_id[0]}")
        if emotions:
            print(f"TEST: emotions {emotions}")
            g.storage.add_emotions(entry_id[0], emotions)
        return redirect(f"/view_entry/{entry_id[0]}")
    except ValueError as e:
        print(f"flash ERROR: {e}")
        return (
            render_template(
                "create_entry.html",
                entry_date=entry_date,
                energy_level=energy_level,
                mood_range=mood_range,
                reflection=reflection,
                emotions=emotions,
            ),
            404,
        )
    except Exception as e:
        print(f"flash ERROR: {e}")

    # redirect to display view

    # TODO if invalid input redirect to same page with flash message for each error
    # TODO intepolate valid entries so they dont have to rewrite
    return render_template("create_entry.html")


@app.route("/view_entry/<int:entry_id>")
@require_login
def display_entry(entry_id):  # TODO
    id, user_id, date, energy_level, mood_range, reflection = g.storage.get_entry(
        entry_id
    )

    print(f"TEST entry data: {id, user_id, date, energy_level, mood_range, reflection}")

    emotions_list = g.storage.get_entry_emotions(entry_id)
    # TODO retrieve emotions
    return render_template(
        "view_entry.html",
        entry_id=id,
        date=date,
        energy_level=energy_level,
        mood_range=mood_range,
        reflection=reflection,
        emotions=emotions_list,
    )


# @app.route("/view_entry/<int:entry_id>", methods=["POST"])
# @require_login
# def add_emotion(entry_id):  # TODO
#     emotion = request.form.get("emotion")
#     g.storage.add_emotion()

#     # TODO retrieve emotions
#     return render_template(
#         "view_entry.html",
#         entry_id=id,
#         date=date,
#         energy_level=energy_level,
#         mood_range=mood_range,
#         reflection=reflection,
#     )


@app.route("/edit_entry/<int:entry_id>")
@require_login
def display_edit_entry(entry_id):
    id, user_id, date, energy_level, mood_range, reflection = g.storage.get_entry(
        entry_id
    )
    emotions_list = g.storage.get_entry_emotions(entry_id)
    return render_template(
        "edit_entry.html",
        entry_id=entry_id,
        entry_date=date,
        energy_level=energy_level,
        mood_range=mood_range,
        reflection=reflection,
        emotions=emotions_list,
    )


def validate_edited_entry(entry_id, entry_date, energy_level, mood_range):
    if not entry_date:
        raise ValueError("Missing a date")
    entry_date_is_same = g.storage.get_entry_date(entry_id)[0]
    if str(entry_date_is_same) != entry_date:  # if not current entry_date value
        # check that entry date for that user doesnt already exists
        if g.storage.check_unique_date(session["user_id"], entry_date):
            raise ValueError(f"You already have an entry for this date: {entry_date}.")
    if not energy_level:
        raise ValueError("Missing a value for energy level")
    if not mood_range:
        raise ValueError("Missing a value for mood range")


@app.route("/edit_entry/<int:entry_id>", methods=["POST"])
@require_login
def edit_entry(entry_id):
    # TODO prob can make the validation more generalized and reusable
    # currently takes all info and updates it all, rather than individual value that is diff
    entry_date = request.form.get("entry_date")
    energy_level = request.form.get("energy_level")
    mood_range = request.form.get("mood_range")
    reflection = request.form.get("reflection")

    try:
        validate_edited_entry(entry_id, entry_date, energy_level, mood_range)
        g.storage.update_entry(
            entry_id, entry_date, energy_level, mood_range, reflection
        )
        print("SUCCESS ..?")
        return redirect(f"/view_entry/{entry_id}")
    except ValueError as e:
        print(f"flash ERROR: {e}")
        return (
            render_template(
                "edit_entry.html",
                entry_id=entry_id,
                entry_date=entry_date,
                energy_level=energy_level,
                mood_range=mood_range,
                reflection=reflection,
            ),
            404,
        )
    except Exception as e:
        print(f"flash ERROR: {e}")

    return render_template("view_entry.html", entry_id=entry_id)


@app.route("/delete_entry/<int:entry_id>", methods=["POST"])
@require_login
def delete_entry(entry_id):
    g.storage.delete_entry(entry_id)
    print("Successfully deleted entry...")
    return render_template("view_entries.html")


@app.route("/delete_emotion/<emotion>")
@require_login
def delete_emotion(emotion):
    # TODO change emotions shcema to have unique emotion value: UNIQUE(emotion, entry_id)
    emotion_id, entry_id = g.storage.get_emotions_id_and_entry_id(emotion)
    print(f"TEst return: {entry_id}")
    g.storage.delete_emotion(emotion_id)
    id, user_id, date, energy_level, mood_range, reflection = g.storage.get_entry(
        entry_id
    )
    emotions_list = g.storage.get_entry_emotions(entry_id)
    return render_template(
        "view_entry.html",
        entry_id=entry_id,
        entry_date=date,
        energy_level=energy_level,
        mood_range=mood_range,
        reflection=reflection,
        emotions=emotions_list,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5003)
