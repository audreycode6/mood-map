from functools import wraps

from flask import (
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from services.auth.utils import get_hashed_pw_str, validate_login, validate_registration


def require_login(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        if not session.get("username"):
            session["protected_page_path"] = request.path
            flash("Please log in to continue.")
            return redirect(url_for("display_login"))

        return func(*args, **kwargs)

    return decorated_func


def register_user(username, password):
    # Validate username and pw
    error_list = validate_registration(username, password)
    if error_list:
        for error in error_list:
            flash(error, "error")
        return render_template("register.html", username=username), 422

    # Format pw to be db ready
    hashed_pw_str = get_hashed_pw_str(password)

    # Register user in db
    g.storage.register_new_user(username, hashed_pw_str)
    flash(f"'{username}' has been registered!", "success")
    return redirect(url_for("display_login"))


def login_user(username, password):
    # Validate input
    user_id = validate_login(username, password)
    if not user_id:
        flash("Invalid credentials, please try again", "error")
        return render_template("login.html"), 401

    # Store username in session to track logged in user
    session["username"] = username
    session["user_id"] = user_id

    # If proceeding from a login redirect, go back to original path
    protected_page = session.pop("protected_page_path", None)
    if protected_page:
        return redirect(protected_page)

    return redirect(url_for("view_entries"))
