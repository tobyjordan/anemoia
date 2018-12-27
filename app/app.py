import flask
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
  return flask.render_template("index.html", latest_feed=latest_feed, curated_feed=curated_feed, more_feed=top_feed)

@app.route("/about")
def about():
  return flask.render_template("about.html")
