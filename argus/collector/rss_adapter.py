import feedparser


def fetch_rss_entries(feed: dict) -> list[dict]:
    parsed_feed = feedparser.parse(feed["url"])

    entries = []

    for entry in parsed_feed.entries:
        entries.append(
            {
                "title": entry.get("title"),
                "link": entry.get("link"),
                "published": entry.get("published"),
                "source": feed["name"],
                "language": feed.get("language"),
                "country": feed.get("country"),
            }
        )

    return entries