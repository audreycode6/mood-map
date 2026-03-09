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
ENTRY_VIEW_LIMIT = 5


"""
______________
HELPER FUNCS
____________
"""


def is_logged_in():
    return session.get("username")


def get_valid_page_nums():
    # get total of entries
    total_entries = g.storage.get_user_entry_count(session["user_id"])
    entry_range = list(range(1, total_entries[0] + 1, ENTRY_VIEW_LIMIT))
    valid_page_nums = []
    page_num = 0
    for num in entry_range:
        valid_page_nums.append(page_num)
        page_num += 1
    return valid_page_nums


def validate_entry(entry_date, energy_level, mood_range):
    error_list = []
    if not entry_date:
        error_list.append("Missing a date")
    if entry_date:  # check that entry date for that user doesnt already exists
        if g.storage.check_unique_date(session["user_id"], entry_date):
            error_list.append(f"You already have an entry for this date: {entry_date}.")
    if not energy_level:
        error_list.append("Missing a value for energy level")
    if not mood_range:
        error_list.append("Missing a value for mood range")

    return error_list


def validate_edited_entry(entry_id, entry_date, energy_level, mood_range):
    error_list = []
    if not entry_date:
        error_list.append("Missing a date")
    if entry_date:
        entry_date_is_same = g.storage.get_entry_date(entry_id)[0]
        if str(entry_date_is_same) != entry_date:  # if not current entry_date value
            # check that entry date for that user doesnt already exists
            if g.storage.check_unique_date(session["user_id"], entry_date):
                error_list.append(
                    f"You already have an entry for this date: {entry_date}."
                )
    if not energy_level:
        error_list.append("Missing a value for energy level")
    if not mood_range:
        error_list.append("Missing a value for mood range")

    return error_list


def validate_unique_emotions(emotions_string, error_list):
    count_emotions = {}
    for emotion in emotions_string.split():
        if emotion in count_emotions:
            count_emotions[emotion] += 1
            error_list.append(f'This emotion, "{emotion}", is already listed ')
        else:
            count_emotions[emotion] = 1
    return error_list


def require_login(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        if not is_logged_in():
            session["protected_page_path"] = request.path
            flash("You must be logged in to do that.")
            return redirect(url_for("display_login")), 404

        return func(*args, **kwargs)

    return decorated_func


@app.before_request
def load_db():
    g.storage = DatabasePersistence()


"""
____________
ROUTES
____________
"""


@app.route("/register")
def display_register():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username").strip().lower()
    password = request.form.get("password").strip()

    error_list = []
    user_exists = g.storage.user_exists(username)

    if user_exists:
        error_list.append(f"User '{username}' already exists")

    if not username or not password:
        error_list.append("Missing input")

    if username and password and not user_exists:
        hashed_pw = hashpw(password.encode("utf-8"), gensalt())
        # convert to str before storing in db
        hashed_pw_str = hashed_pw.decode("utf-8")

        # create user
        g.storage.register_new_user(username, hashed_pw_str)
        flash(f"'{username}' has been registered!", "success")
        return redirect(url_for("display_login"))

    for error in error_list:
        flash(error, "error")
    return render_template("register.html", username=username), 422


@app.route("/")
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

                # if proceeding from login redirect go back to original path
                protected_page = session.pop("protected_page_path", None)
                if protected_page:
                    return redirect(protected_page)

                # default
                return redirect(url_for("view_entries"))

    # error redirect to same page with flash message
    flash("Invalid credentials, please try again", "error")
    return render_template("login.html"), 404


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been signed out.")
    return redirect(url_for("display_login"))


@app.route("/view_entries/", defaults={"page_num": 0})
@app.route("/view_entries/<int:page_num>")
@require_login
def view_entries(page_num):
    try:
        user_id = session["user_id"]
        entries_info = g.storage.get_users_entries_ids_and_date(
            user_id, page_num, ENTRY_VIEW_LIMIT
        )
        valid_page_nums_list = get_valid_page_nums()
        # validate page view of entries
        if page_num != 0 and page_num not in valid_page_nums_list:
            raise ValueError(f"Page {page_num} out of entry views range")

        session["page_num"] = page_num
        return render_template(
            "view_entries.html",
            entries_info=entries_info,
            page_num=page_num,
            valid_page_nums_list=valid_page_nums_list,
        )
    except ValueError as e:
        flash(f"{e}", "error")
        return redirect(url_for("view_entries")), 404


@app.route("/create_entry")
@require_login
def display_create_entry():
    return render_template("create_entry.html")


@app.route("/create_entry", methods=["POST"])
@require_login
def create_entry():
    entry_date = request.form.get("entry_date")
    energy_level = request.form.get("energy_level")
    mood_range = request.form.get("mood_range")
    emotions_string = request.form.get("emotions")
    reflection = request.form.get("reflection")

    user_id = session["user_id"]
    try:
        error_list = validate_entry(entry_date, energy_level, mood_range)
        if error_list:
            for error in error_list:
                flash(error, "error")
            return (
                render_template(
                    "create_entry.html",
                    entry_date=entry_date,
                    energy_level=energy_level,
                    mood_range=mood_range,
                    reflection=reflection,
                    emotions=emotions_string,
                ),
                404,
            )

        entry_id = g.storage.create_new_entry(
            user_id, entry_date, energy_level, mood_range, reflection
        )
        if emotions_string:
            g.storage.add_emotions(entry_id[0], emotions_string)
        return redirect(f"/view_entry/{entry_id[0]}")

    except Exception as e:
        flash(e, "error")

    return render_template("create_entry.html"), 504


@app.route("/view_entry/<int:entry_id>")
@require_login
def display_entry(entry_id):
    try:
        id, user_id, date, energy_level, mood_range, reflection = g.storage.get_entry(
            entry_id
        )
        emotions_list = g.storage.get_entry_emotions(entry_id)
        return render_template(
            "view_entry.html",
            entry_id=id,
            date=date,
            energy_level=energy_level,
            mood_range=mood_range,
            reflection=reflection,
            emotions=emotions_list,
        )
    except TypeError:
        flash("Unauthorized entry id", "error")
        return redirect(url_for("view_entries")), 404


@app.route("/edit_entry/<int:entry_id>")
@require_login
def display_edit_entry(entry_id):
    try:
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
            emotions=" ".join(emotions_list),
        )
    except TypeError:
        flash("Unauthorized entry id", "error")
        return (
            redirect(url_for("view_entries")),
            404,
        )


@app.route("/edit_entry/<int:entry_id>", methods=["POST"])
@require_login
def edit_entry_and_emotions(entry_id):
    entry_date = request.form.get("entry_date")
    energy_level = request.form.get("energy_level")
    mood_range = request.form.get("mood_range")
    reflection = request.form.get("reflection")
    emotions_string = request.form.get("emotions")

    try:
        error_list = validate_edited_entry(
            entry_id, entry_date, energy_level, mood_range
        )
        if emotions_string:
            error_list = validate_unique_emotions(emotions_string, error_list)
        if error_list:
            for error in error_list:
                flash(error, "error")
            return (
                render_template(
                    "edit_entry.html",
                    entry_id=entry_id,
                    entry_date=entry_date,
                    energy_level=energy_level,
                    mood_range=mood_range,
                    reflection=reflection,
                    emotions=emotions_string,
                ),
                404,
            )

        g.storage.update_entry(
            entry_id, entry_date, energy_level, mood_range, reflection
        )
        """
            in order to edit emotions list need to
            delete all current emotions to ensure deletions
            in edit mode are applied accurately
        """
        g.storage.delete_entries_emotions(entry_id)
        g.storage.add_emotions(entry_id, emotions_string)
        return redirect(f"/view_entry/{entry_id}")

    except Exception as e:
        flash(e, "error")
        return redirect(url_for("view_entries")), 504


@app.route("/delete_entry/<int:entry_id>", methods=["POST"])
@require_login
def delete_entry(entry_id):
    g.storage.delete_entry(entry_id)
    flash("Successfully deleted entry...", "success")
    return redirect(f"/view_entries/{session['page_num']}")


@app.route("/delete_emotion/<int:entry_id>/<emotion>")
@require_login
def delete_emotion(entry_id, emotion):
    try:
        emotion_id = g.storage.get_emotions_id(emotion, entry_id)
        if emotion_id is None:
            raise TypeError()
        g.storage.delete_emotion(emotion_id, entry_id)
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
    except TypeError:
        flash(f"Invalid emotion: {emotion}", "error")
        return redirect(f"/edit_entry/{entry_id}"), 404


if __name__ == "__main__":
    app.run(debug=True, port=5003)
