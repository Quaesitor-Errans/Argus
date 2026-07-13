from typing import TypedDict

import feedparser

from argus.config import RSSFeedConfig


class RSSFeedEntry(TypedDict):
    """Normalized metadata extracted from one RSS entry."""

    title: str | None
    link: str | None
    published: str | None
    source: str
    language: str
    country: str


def fetch_rss_entries(
        feed: RSSFeedConfig,
) -> list[RSSFeedEntry]:
    parsed_feed = feedparser.parse(feed.url)

    entries: list[RSSFeedEntry] = []

    for entry in parsed_feed.entries:
        entries.append(
            RSSFeedEntry(
                title=entry.get("title"),
                link=entry.get("link"),
                published=entry.get("published"),
                source=feed.name,
                language=feed.language,
                country=feed.country,
            )
        )

    return entries