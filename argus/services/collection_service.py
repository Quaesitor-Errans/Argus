from argus.acquisition import (
    AcquisitionMode,
    DiscoveryRequest,
)
from argus.collector.rss_connector import RSSConnector
from argus.config import RSS_FEEDS
from argus.database import session_manager
from argus.logging.logger import get_logger
from argus.models import Article
from argus.storage.article_repository import ArticleRepository
from argus.storage.source_repository import SourceRepository

logger = get_logger(__name__)


def collect_articles() -> None:
    new_articles_count = 0
    failed_feeds_count = 0
    discovery_request = DiscoveryRequest(
        mode=AcquisitionMode.CONTINUOUS,
    )

    with session_manager.session() as session:
        repository = ArticleRepository(session)

        source_repository = SourceRepository(session)

        for feed in RSS_FEEDS:
            logger.info(
                "Collecting feed: %s",
                feed.name,
            )

            try:
                connector = RSSConnector(feed)
                candidates = connector.discover(
                    discovery_request
                )

            except Exception:
                failed_feeds_count += 1

                logger.exception(
                    "Feed collection failed: %s",
                    feed.name,
                )
                continue

            collected_from_feed = 0

            source = source_repository.get_or_create(
                identifier=(
                    feed.effective_source_identifier
                ),
                name=feed.name,
                source_type=feed.source_type,
                primary_jurisdiction=feed.country,
                default_language=feed.language,
            )
            session.commit()

            for candidate in candidates:
                title = candidate.title
                url = candidate.location

                if not title or not url:
                    logger.warning(
                        "Skipping invalid RSS entry from %s",
                        feed.name,
                    )
                    continue

                if repository.get_by_url(url) is not None:
                    continue

                article = Article(
                    url=url,
                    title=title,
                    source_id=source.id,
                    source=feed.name,
                    language=candidate.language,
                    published_at=candidate.published_at,
                    content=None,
                )

                repository.save(article)

                new_articles_count += 1
                collected_from_feed += 1

            logger.info(
                "Feed collected: %s; new articles: %s",
                feed.name,
                collected_from_feed,
            )

    logger.info(
        "Collection finished; new articles: %s; failed feeds: %s",
        new_articles_count,
        failed_feeds_count,
    )
