from argus.collector.rss_adapter import fetch_rss_entries
from argus.config import RSS_FEEDS
from argus.database import create_database, session_manager
from argus.logging.logger import get_logger
from argus.models import Article
from argus.storage.article_repository import ArticleRepository


logger = get_logger(__name__)


def collect_articles() -> None:
    create_database()

    new_articles_count = 0
    failed_feeds_count = 0

    with session_manager.session() as session:
        repository = ArticleRepository(session)

        for feed in RSS_FEEDS:
            feed_name = feed["name"]

            logger.info(
                "Collecting feed: %s",
                feed_name,
            )

            try:
                entries = fetch_rss_entries(feed)

            except Exception:
                failed_feeds_count += 1

                logger.exception(
                    "Feed collection failed: %s",
                    feed_name,
                )
                continue

            collected_from_feed = 0

            for entry in entries:
                title = entry.get("title")
                url = entry.get("link")

                if not title or not url:
                    logger.warning(
                        "Skipping invalid RSS entry from %s",
                        feed_name,
                    )
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
                collected_from_feed += 1

            logger.info(
                "Feed collected: %s; new articles: %s",
                feed_name,
                collected_from_feed,
            )

    logger.info(
        "Collection finished; new articles: %s; failed feeds: %s",
        new_articles_count,
        failed_feeds_count,
    )