"""
  anemoia - aggregator.py
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
      "https://www.nasa.gov/rss/dyn/breaking_news.rss",
      "http://www.wsj.com/xml/rss/3_7085.xml",
      "https://www.aljazeera.com/xml/rss/all.xml"
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
        _entry["logo"] = _feed["logo"]
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
    if len(summary) > 86:
      return ((summary[:75] if summary[:74][-1] != " " else summary[:75]) + '...')
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

  @staticmethod
  def get_thumbnail(entry):
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

  @staticmethod
  def get_feed_logo(feed):
    """Given a string, return a python datetime object.
      Args:
        feed (feedparser.FeedParserDict): Feed from which to extract a logo URL.
    """
    try:
      if "href" in feed["image"].keys():
        return feed["image"]["href"]
      else:
        return feed["image"]["link"]
    except Exception:
      return None

  @staticmethod
  def feed_to_object(parsed_feed):
    """Given a feed, returned from feedparser, return a uniform object.
      Args:
        parsed_feed (feedparser.FeedParserDict): Parsed feed, returned from feedparser.
    """
    return {
      "name": parsed_feed.feed.title,
      "logo": NewsAggregator.get_feed_logo(parsed_feed.feed),
      "subtitle": parsed_feed.feed.subtitle,
      "entries": [
        {
          "title": entry.title,
          "thumbnail": NewsAggregator.get_thumbnail(entry),
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
