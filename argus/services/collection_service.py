from argus.acquisition import (
    AcquisitionMode,
    DiscoveryRequest,
)
from argus.collector.rss_connector import (
    RSS_CONNECTOR_ID,
    RSSConnector,
)
from argus.config import RSS_FEEDS
from argus.database import session_manager
from argus.endpoints import EndpointType
from argus.logging.logger import get_logger
from argus.models import Article
from argus.storage.article_repository import ArticleRepository
from argus.storage.candidate_repository import (
    AcquisitionCandidateRepository,
)
from argus.storage.endpoint_repository import (
    CollectionEndpointRepository,
)
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
        endpoint_repository = CollectionEndpointRepository(
            session
        )
        candidate_repository = AcquisitionCandidateRepository(
            session
        )

        for feed in RSS_FEEDS:
            logger.info(
                "Collecting feed: %s",
                feed.name,
            )

            try:
                source = source_repository.get_or_create(
                    identifier=(
                        feed.effective_source_identifier
                    ),
                    name=feed.name,
                    source_type=feed.source_type,
                    primary_jurisdiction=feed.country,
                    default_language=feed.language,
                )
                endpoint = endpoint_repository.get_or_create(
                    identifier=(
                        feed.effective_endpoint_identifier
                    ),
                    endpoint_type=EndpointType.RSS,
                    connector_id=RSS_CONNECTOR_ID,
                    url=feed.url,
                    source_id=source.id,
                    language=feed.language,
                )
                session.commit()

                connector = RSSConnector(feed)
                candidates = connector.discover(
                    discovery_request
                )

            except Exception:
                session.rollback()
                failed_feeds_count += 1

                logger.exception(
                    "Feed collection failed: %s",
                    feed.name,
                )
                continue

            collected_from_feed = 0

            for candidate in candidates:
                title = candidate.title
                url = candidate.location
                article = None

                if not title:
                    logger.warning(
                        "RSS candidate has no title: %s",
                        feed.name,
                    )
                else:
                    article = repository.get_by_url(url)

                    if article is None:
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

                candidate_repository.get_or_create(
                    endpoint=endpoint,
                    candidate=candidate,
                    article_id=(
                        article.id
                        if article is not None
                        else None
                    ),
                )
                session.commit()

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
