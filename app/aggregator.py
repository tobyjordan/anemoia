"""
  anemoia - aggregator.py
  Copyright (C) 2018 Toby Jordan
"""

import feedparser
from dateutil import parser
import pytz
import datetime
import requests
import random
import json

from data import DatabaseHandler

class Aggregator:

  def __init__(self):
    pass

  def generate_score(self, entry):
    _diff = (datetime.datetime.timestamp(datetime.datetime.utcnow()) - \
      datetime.datetime.timestamp(entry["date"])) / 25
    _rank = {
      "BBC News - World": 0,
      "World News - Breaking international news and headlines | Sky News": 15,
      "Reuters: Top News": 80,
      "Reuters: World News": 80,
      "Al Jazeera English": 15
    }
    return _diff + _rank[entry["source"]]

  def feed_to_object(self, parsed_feed, count=10):
    """Given a feed, returned from feedparser, return a uniform object.
      Args:
        parsed_feed (feedparser.FeedParserDict): Parsed feed, returned from feedparser.
    """
    return {
      "name": parsed_feed.feed.title,
      "logo": self.get_feed_logo(parsed_feed.feed),
      "subtitle": parsed_feed.feed.subtitle,
      "entries": [
        {
          "title": entry.title.replace("&apos;", "'").replace("&#8217;", "'"),
          "thumbnail": self.get_thumbnail(entry),
          "link": entry.link,
          "summary": self.format_summary(entry.summary),
          "date": self.datetime_from_string(
            entry.published if "published" in entry.keys() else entry.date if "date" in entry.keys() else "recent")
        } for entry in (parsed_feed.entries[0:count] if len(parsed_feed.entries) >= count else parsed_feed.entries)
      ]
    }

  def get_thumbnail(self, entry):
    """Given an RSS entry, return a thumbnail if one exists.
      Args:
        entry (feedparser.FeedParserDict): Entry from which to extract a thumbnail URL.
    """
    try:
      if "media_thumbnail" in entry.keys():
        return entry["media_thumbnail"][0]["url"]
      else:
        return entry["media_content"][0]["url"]
    except Exception:
      return None

  def get_feed_logo(self, feed):
    """Given a string, return a python datetime object.
      Args:
        feed (feedparser.FeedParserDict): Feed from which to extract a logo URL.
    """
    try:
      if "href" in feed["image"].keys():
        _logo = feed["image"]["href"]
      else:
        _logo = feed["image"]["link"]
    except Exception:
      return None

    if _logo not in self.cached_urls.keys():
      try:
        self.cached_urls[_logo] = requests.get(_logo).status_code in [200, 301, 302]
      except Exception:
        self.cached_urls[_logo] = None

    return _logo if self.cached_urls[_logo] else None

  def parse(self, feed):
    """Wrapper for feedparser, parse function.
      Args:
        feed (string): URL of feed to parse.
    """
    return feedparser.parse(feed)

  def format_summary(self, summary):
    """Helper function to truncate an feed.entry summary.
      Args:
        summary (string): untruncated summary from feedparser object.
    """
    
    # Remove new lines
    summary = summary.replace('\n', ' ').replace('\r', '')

    # Remove HTML
    if "<" in summary:
      summary = summary[:summary.index("<")]

    # Truncate
    if len(summary) > 180:
      return ((summary[:180] if summary[:179][-1] != " " else summary[:180]) + '...')
    else:
      return summary

  def datetime_from_string(self, date):
    """Given a string, return a python datetime object.
      Args:
        date (string): Formatted date string.
    """
    _date = date.replace("EDT", "UTC-5").replace("EST", "UTC-5")
    _date = parser.parse(_date).astimezone(pytz.utc)
    return _date


class NewsAggregator(Aggregator):

  def __init__(self):
    """News Aggregator Object
      Scrape from RSS feeds and return recent news.
    """
    self._default_feeds = [
      "http://feeds.reuters.com/reuters/UKTopNews",
      "http://feeds.bbci.co.uk/news/rss.xml",
      "https://www.nasa.gov/rss/dyn/breaking_news.rss",
      "http://www.wsj.com/xml/rss/3_7085.xml",
      "https://www.aljazeera.com/xml/rss/all.xml"
    ]
    self.cached_urls = {}

    super().__init__()

  def get_latest(self, feeds=None, count=None):
    """Return latest stories from a list of RSS feeds.
      Args:
        feeds (optional, array): An array of rss feed url's as strings.
    """
    entries = []
    for feed in (feeds if feeds else self._default_feeds):
      _feed = self.feed_to_object(self.parse(feed))
      for entry in _feed["entries"]:
        _entry = entry
        _entry["source"] = _feed["name"]
        _entry["logo"] = _feed["logo"]
        entries.append(_entry)

    entries.sort(key=lambda e: e["date"], reverse=True)
    return entries if count is None else entries[:count]

  def ranked_random(self, feeds=None, count=None):
    """Return latest stories from a list of RSS feeds.
      Args:
        feeds (optional, array): An array of rss feed url's as strings.
    """
    entries = []
    for feed in (feeds if feeds else self._default_feeds):
      _feed = self.feed_to_object(self.parse(feed))
      for entry in _feed["entries"]:
        _entry = entry
        _entry["source"] = _feed["name"]
        _entry["logo"] = _feed["logo"]
        entries.append(_entry)

    for entry in entries:
      if entry["source"] == "Fortune" and random.randint(0, 10) > 6:
        entries.remove(entry)

    random.shuffle(entries)
    return entries if count is None else entries[:count]

  def ranked_latest(self, feeds=None, count=None):
    """Return latest stories from a list of RSS feeds.
      Args:
        feeds (optional, array): An array of rss feed url's as strings.
    """
    entries = []
    for feed in (feeds if feeds else self._default_feeds):
      _feed = self.feed_to_object(self.parse(feed))
      for entry in _feed["entries"]:
        _entry = entry
        _entry["source"] = _feed["name"]
        _entry["logo"] = _feed["logo"]
        _entry["score"] = self.generate_score(_entry)
        entries.append(_entry)

    entries.sort(key=lambda e: e["score"], reverse=False)
    entries.sort(key=lambda e: e["score"], reverse=False)
    return entries if count is None else entries[:count]


class DatabaseAggregator(NewsAggregator):

  def __init__(self):
    self.handle = DatabaseHandler()

    with open("feeds.json", "r") as f:
      _feeds = json.loads(f.read())
      self._latest_feeds = _feeds["latest"]
      self._top_feeds = _feeds["top"]
      self._curated_feeds = _feeds["curated"]

    super().__init__()

  def aggregate_latest(self):
    self.handle.delete_from_table("latest_articles")
    for article in self.ranked_latest(self._latest_feeds, count=5):
      self.handle.write_article("latest_articles", article)

  def aggregate_top(self):
    self.handle.delete_from_table("top_articles")
    for article in self.get_latest(self._top_feeds, count=5):
      self.handle.write_article("top_articles", article)

  def aggregate_curated(self):
    self.handle.delete_from_table("curated_articles")
    for article in self.ranked_random(self._curated_feeds, count=4):
      self.handle.write_article("curated_articles", article)
    
  
# Print Entries
if __name__ == '__main__':
  aggregator = DatabaseAggregator()

  aggregator.aggregate_latest()
  aggregator.aggregate_top()
  aggregator.aggregate_curated()

  aggregator.handle.close()
