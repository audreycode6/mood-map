from database_persistence import DatabasePersistence
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

from services.auth.auth_service import login_user, register_user, require_login
from services.entries_and_emotions.entries_and_emotions_service import (
    emotion_deletion,
    entry_creation,
    entry_deletion,
    get_edit_entry_view,
    get_entries,
    get_entry,
    update_entry_and_emotions,
)

app = Flask(__name__)
app.secret_key = "dev_secret_key"


@app.before_request
def load_db():
    g.storage = DatabasePersistence()


"""
____________
ROUTES
____________
"""


@app.route("/<path:invalid_path>")
def catch_all(invalid_path):
    flash(f"Page '{invalid_path}' doesn't exist.", "error")
    return render_template("error_page.html"), 404


@app.route("/")
def index():
    return redirect(url_for("view_entries"))


@app.route("/register")
def display_register():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username").strip().lower()
    password = request.form.get("password").strip()

    return register_user(username, password)


@app.route("/login")
def display_login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username").strip().lower()
    password = request.form.get("password").strip()

    return login_user(username, password)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been signed out.")
    return redirect(url_for("display_login"))


@app.route("/view_entries/", defaults={"page_num": 0})
@app.route("/view_entries/<int:page_num>")
@require_login
def view_entries(page_num):
    return get_entries(page_num)


@app.route("/create_entry")
@require_login
def display_create_entry():
    return render_template("create_entry.html")


@app.route("/create_entry", methods=["POST"])
@require_login
def create_entry():
    # Get users input
    entry_date = request.form.get("entry_date")
    energy_level = request.form.get("energy_level")
    mood_range = request.form.get("mood_range")
    emotions_string = request.form.get("emotions")
    reflection = request.form.get("reflection")

    return entry_creation(
        entry_date, energy_level, mood_range, reflection, emotions_string
    )


@app.route("/view_entry/<int:entry_id>")
@require_login
def display_entry(entry_id):
    return get_entry(entry_id)


@app.route("/edit_entry/<int:entry_id>")
@require_login
def display_edit_entry(entry_id):
    return get_edit_entry_view(entry_id)


@app.route("/edit_entry/<int:entry_id>", methods=["POST"])
@require_login
def edit_entry_and_emotions(entry_id):
    # Get users input
    entry_date = request.form.get("entry_date")
    energy_level = request.form.get("energy_level")
    mood_range = request.form.get("mood_range")
    reflection = request.form.get("reflection")
    emotions_string = request.form.get("emotions")

    return update_entry_and_emotions(
        entry_date, energy_level, mood_range, entry_id, reflection, emotions_string
    )


@app.route("/delete_entry/<int:entry_id>", methods=["POST"])
@require_login
def delete_entry(entry_id):
    return entry_deletion(entry_id)


@app.route("/delete_emotion/<int:entry_id>/<emotion>")
@require_login
def delete_emotion(entry_id, emotion):
    return emotion_deletion(entry_id, emotion)


if __name__ == "__main__":
    app.run(debug=True, port=5003)
