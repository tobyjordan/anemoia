import flask
import os
from itsdangerous import URLSafeTimedSerializer
from flask_moment import Moment

from data import DatabaseHandler


app = flask.Flask("__name__")
moment = Moment(app)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or "default"
app.config["SECURITY_PASSWORD_SALT"] = os.environ.get(
    "SECURITY_PASSWORD_SALT") or "default"


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email


@app.route("/")
def index():
    handle = DatabaseHandler()
    latest_feed = handle.get_from_table("latest")
    curated_feed = handle.get_from_table("curated")
    top_feed = handle.get_from_table("top")
    handle.close()
    return flask.render_template(
        "index.html", latest_feed=latest_feed, curated_feed=curated_feed, more_feed=top_feed)


@app.route("/about")
def about():
    return flask.render_template("about.html")


@app.route("/mailinglist", methods=["POST", "GET"])
def register_email():
    if flask.request.method == "POST":
        handle = DatabaseHandler()
        print("Added email.")
        handle.new_subscriber(flask.request.form["email"])
        handle.close()
        token = generate_confirmation_token(flask.request.form["email"])
    return flask.redirect(flask.url_for("index"))
