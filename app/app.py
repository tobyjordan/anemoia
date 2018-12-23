import flask
from flask_moment import Moment
import json

from aggregator import NewsAggregator


app = flask.Flask("__name__")
moment = Moment(app)

with open("feeds.json", "r") as f:
  _feeds = json.loads(f.read())
  _latest_feeds = _feeds["latest"]
  _top_feeds = _feeds["top"]
  _curated_feeds = _feeds["curated"]

agg = NewsAggregator()
latest_feed = agg.ranked_latest(_latest_feeds, count=5)
curated_feed = agg.ranked_random(_curated_feeds, count=4)
top_feed = agg.get_latest(_top_feeds, count=5)

@app.route("/")
def index():
  return flask.render_template("index.html", latest_feed=latest_feed, curated_feed=curated_feed, more_feed=top_feed)

@app.route("/about")
def about():
  return flask.render_template("about.html")
