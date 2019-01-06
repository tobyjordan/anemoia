import sqlite3
from dateutil import parser
import pytz
import datetime


class DatabaseHandler:
    """Handle database functions for application.
    """

    def __init__(self):
        self.db = sqlite3.connect("data.db")
        self.c = self.db.cursor()

        self.c.execute("""CREATE TABLE IF NOT EXISTS latest_articles (
            date STRING,
            link STRING,
            logo STRING,
            score INTEGER,
            source STRING,
            summary STRING,
            title STRING,
            thumbnail STRING
        );""")
        self.c.execute("""CREATE TABLE IF NOT EXISTS curated_articles (
            date STRING,
            link STRING,
            logo STRING,
            score INTEGER,
            source STRING,
            summary STRING,
            title STRING,
            thumbnail STRING
        );""")
        self.c.execute("""CREATE TABLE IF NOT EXISTS top_articles (
            date STRING,
            link STRING,
            logo STRING,
            score INTEGER,
            source STRING,
            summary STRING,
            title STRING,
            thumbnail STRING
        );""")

        self.c.execute("""CREATE TABLE IF NOT EXISTS subscribers (
            email STRING,
            confirmed INTEGER
        );""")

    def datetime_from_string(self, date):
        """Given a string, return a python datetime object.
        Args:
            date (string): Formatted date string.
        """
        _date = date.replace("EDT", "UTC-5").replace("EST", "UTC-5")
        _date = parser.parse(_date).astimezone(pytz.utc)
        return _date

    def write_article(self, table, article_object):
        """Insert an article into the database.
        Args:
            table (string): Which table to insert into.
            article_object (dict): Article object to insert.
        """
        self.c.execute("""
            INSERT INTO {} (
                date, link, logo, score, source, summary, title, thumbnail
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """.format(table), (
            article_object["date"],
            article_object["link"],
            article_object["logo"],
            article_object[
                "score"] if "score" in article_object.keys() else None,
            article_object["source"],
            article_object["summary"],
            article_object["title"],
            article_object["thumbnail"]
        ))
        self.db.commit()

    def new_subscriber(self, email):
        """Insert subscriber into database.
        Args:
            email (string): Subscriber email to insert.
        """
        self.c.execute("""
            INSERT INTO subscribers (email, confirmed) VALUES (?, 0)""", (email,))
        self.db.commit()
        print("committed")

    def delete_from_table(self, table):
        """Delete contents of table
        Args:
            table (string): Name of table to delete contents.
        """
        self.c.execute("""DELETE FROM {}""".format(table))

    def get_from_table(self, table):
        """Pull articles from table.
        Args:
            table (string): Name of table to get.
        """
        self.c.execute("""SELECT * FROM {}_articles""".format(table))
        _res = self.c.fetchall()
        result = []
        for entry in _res:
            result.append({
                "date": self.datetime_from_string(entry[0]),
                "link": entry[1],
                "logo": entry[2],
                "score": entry[3],
                "source": entry[4],
                "summary": entry[5],
                "title": entry[6],
                "thumbnail": entry[7]
            })
        return result

    def close(self):
        """Close database connection.
        """
        self.c.close()
        self.db.close()
