import flask
import datetime
import pytz
import aggregator

app = flask.Flask("__name__")

entries = aggregator.NewsAggregator().get_latest()

latest_feed = entries[:5]
curated_feed = entries[5:9]
more_feed = entries[10:15]

@app.route("/")
def index():
  return flask.render_template("index.html", latest_feed=latest_feed, curated_feed=curated_feed, more_feed=more_feed)
