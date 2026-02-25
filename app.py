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


if __name__ == "__main__":
    app.run(debug=True, port=5003)
