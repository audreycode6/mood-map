from flask import (
    flash,
    Flask,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

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
    pass  # TODO


@app.route("/login")
def display_login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    pass  # TODO


if __name__ == "__main__":
    app.run(debug=True, port=5003)
