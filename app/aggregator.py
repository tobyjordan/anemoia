"""
  anemoia.ai - aggregator.py
  Copyright (C) 2018 Toby Jordan
"""

import feedparser
from dateutil import parser
import pytz


class NewsAggregator:

  def __init__(self):
    """News Aggregator Object
      Scrape from RSS feeds and return recent news.
    """
    self._default_feeds = [
      "http://feeds.reuters.com/reuters/UKTopNews",
      "http://feeds.bbci.co.uk/news/rss.xml",
      "https://www.nasa.gov/rss/dyn/breaking_news.rss"
    ]

  def get_latest(self, feeds=None):
    """Return latest stories from a list of RSS feeds.
      Args:
        feeds (optional, array): An array of rss feed url's as strings.
    """
    entries = []
    for feed in (feeds if feeds else self._default_feeds):
      _feed = NewsAggregator.feed_to_object(NewsAggregator.parse(feed))
      for entry in _feed["entries"]:
        _entry = entry
        _entry["source"] = _feed["name"]
        entries.append(_entry)

    entries.sort(key=lambda e: e["date"], reverse=True)
    return entries

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
    if len(entry.summary) > 86:
      return ((entry.summary[:75] if entry.summary[:75][-1] != " " else entry.summary[:74]) + '...')
    else:
      return entry.summary

  @staticmethod
  def datetime_from_string(date):
    """Given a string, return a python datetime object.
      Args:
        date (string): Formatted date string.
    """
    _date = date.replace("EDT", "UTC-5").replace("EST", "UTC-5")
    _date = parser.parse(_date).astimezone(pytz.utc)
    return _date

  @staticmethod
  def feed_to_object(parsed_feed):
    """Given a feed, returned from feedparser, return a uniform object.
      Args:
        parsed_feed (feedparser.FeedParserDict): Parsed feed, returned from feedparser.
    """
    return {
      "name": parsed_feed.feed.title,
      "subtitle": parsed_feed.feed.subtitle,
      "entries": [
        {
          "title": entry.title,
          "thumbnail": entry.media_thumbnail[0]["url"] if media_thumbnail in entry.keys() else "#"
          "link": entry.link,
          "summary": NewsAggregator.format_summary(entry.summary),
          "date": NewsAggregator.datetime_from_string(
            entry.published if "published" in entry.keys() else entry.date if "date" in entry.keys() else "recent")
        } for entry in (parsed_feed.entries[0:10] if len(parsed_feed.entries) >= 10 else parsed_feed.entries)
      ]
    }


# Print Entries
if __name__ == '__main__':
  aggregator = NewsAggregator()
  entries = aggregator.get_latest()
  print(entries)
