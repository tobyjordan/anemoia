import flask
import os
from itsdangerous import URLSafeTimedSerializer
from flask_moment import Moment

from data import DatabaseHandler


app = flask.Flask("__name__")
moment = Moment(app)


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
    return flask.redirect(flask.url_for("index"))
