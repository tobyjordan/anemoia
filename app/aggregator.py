"""
  anemoia - aggregator.py
  Copyright (C) 2018 Toby Jordan
"""

import feedparser
from dateutil import parser
import pytz
import requests


class NewsAggregator:

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

  def get_latest(self, feeds=None, count=None):
    """Return latest stories from a list of RSS feeds.
      Args:
        feeds (optional, array): An array of rss feed url's as strings.
    """
    entries = []
    for feed in (feeds if feeds else self._default_feeds):
      _feed = self.feed_to_object(NewsAggregator.parse(feed))
      for entry in _feed["entries"]:
        _entry = entry
        _entry["source"] = _feed["name"]
        _entry["logo"] = _feed["logo"]
        entries.append(_entry)

    entries.sort(key=lambda e: e["date"], reverse=True)
    return entries if count is None else entries[:count]

  def feed_to_object(self, parsed_feed):
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
          "summary": NewsAggregator.format_summary(entry.summary),
          "date": NewsAggregator.datetime_from_string(
            entry.published if "published" in entry.keys() else entry.date if "date" in entry.keys() else "recent")
        } for entry in (parsed_feed.entries[0:10] if len(parsed_feed.entries) >= 10 else parsed_feed.entries)
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

  @staticmethod
  def parse(feed):
    """Wrapper for feedparser, parse function.
      Args:
        feed (string): URL of feed to parse.
    """
    return feedparser.parse(feed)

  @staticmethod
  def format_summary(summary):
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
    if len(summary) > 250:
      return ((summary[:250] if summary[:249][-1] != " " else summary[:250]) + '...')
    else:
      return summary

  @staticmethod
  def datetime_from_string(date):
    """Given a string, return a python datetime object.
      Args:
        date (string): Formatted date string.
    """
    _date = date.replace("EDT", "UTC-5").replace("EST", "UTC-5")
    _date = parser.parse(_date).astimezone(pytz.utc)
    return _date


# Print Entries
if __name__ == '__main__':
  aggregator = NewsAggregator()
  entries = aggregator.get_latest()
  print(entries)
