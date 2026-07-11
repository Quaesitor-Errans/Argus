from argus.collector.rss_adapter import fetch_rss_entries
from argus.config import RSS_FEEDS
from argus.database import SessionLocal, create_database
from argus.models import Article
from argus.storage.article_repository import ArticleRepository


def collect_articles() -> None:
    create_database()

    session = SessionLocal()
    repository = ArticleRepository(session)

    new_articles_count = 0

    try:
        for feed in RSS_FEEDS:
            print(f"\nCollecting: {feed['name']}")

            entries = fetch_rss_entries(feed)

            for entry in entries:
                title = entry.get("title")
                url = entry.get("link")

                if not title or not url:
                    continue

                if repository.get_by_url(url) is not None:
                    continue

                article = Article(
                    url=url,
                    title=title,
                    source=entry.get("source"),
                    language=entry.get("language"),
                    content=None,
                )

                repository.save(article)
                new_articles_count += 1

    finally:
        session.close()

    print("\nCollection finished.")
    print(f"New articles: {new_articles_count}")