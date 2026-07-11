from argus.database import SessionLocal, create_database
from argus.parsers.article_parser import extract_article_text
from argus.storage.article_repository import ArticleRepository


def parse_articles(limit: int = 20) -> None:
    create_database()

    session = SessionLocal()
    repository = ArticleRepository(session)

    parsed_count = 0
    failed_count = 0

    try:
        articles = repository.get_without_content(limit=limit)

        if not articles:
            print("No articles require parsing.")
            return

        for article in articles:
            print(f"\nExtracting: {article.title}")

            content = extract_article_text(article.url)

            if not content:
                failed_count += 1
                print("Failed to extract content.")
                continue

            repository.update_content(article, content)
            parsed_count += 1

            print(f"Saved content: {len(content)} characters")

    finally:
        session.close()

    print("\nParsing finished.")
    print(f"Parsed: {parsed_count}")
    print(f"Failed: {failed_count}")