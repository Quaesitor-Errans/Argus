from argus.collector.rss_adapter import fetch_rss_entries
from argus.config import RSS_FEEDS
from argus.database import SessionLocal, create_database
from argus.models import Article
from argus.parsers.article_parser import extract_article_text
from argus.storage.article_repository import ArticleRepository


def run_article_pipeline(parse_limit: int = 10) -> None:
    create_database()

    session = SessionLocal()
    repository = ArticleRepository(session)

    new_articles_count = 0
    parsed_articles_count = 0

    try:
        for feed in RSS_FEEDS:
            print(f"\nCollecting: {feed['name']}")

            entries = fetch_rss_entries(feed)

            for entry in entries:
                title = entry.get("title")
                url = entry.get("link")

                if not title or not url:
                    continue

                existing_article = repository.get_by_url(url)

                if existing_article is not None:
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

        articles = repository.get_without_content(limit=parse_limit)

        for article in articles:
            if article.content:
                continue

            print(f"Extracting: {article.title}")

            content = extract_article_text(article.url)

            if not content:
                print("Failed to extract content.")
                continue

            repository.update_content(article, content)
            parsed_articles_count += 1

            print(f"Saved content: {len(content)} characters")

    finally:
        session.close()

    print("\nPipeline finished.")
    print(f"New articles: {new_articles_count}")
    print(f"Articles parsed: {parsed_articles_count}")