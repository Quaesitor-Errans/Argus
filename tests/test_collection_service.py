import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from argus.acquisition import (
    AcquisitionMode,
    CandidateRecord,
    DiscoveryRequest,
)
from argus.config import RSSFeedConfig
from argus.database import Base, DatabaseSessionManager
from argus.models import Article, Source
from argus.services.collection_service import collect_articles
from argus.sources import SourceType


class CollectionServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite:///:memory:"
        )
        Base.metadata.create_all(self.engine)

        self.session_factory = sessionmaker(
            bind=self.engine
        )
        self.session_manager = DatabaseSessionManager(
            self.session_factory
        )

    def tearDown(self) -> None:
        self.engine.dispose()

    def test_collection_persists_normalized_source(
        self,
    ) -> None:
        feed = RSSFeedConfig(
            name="Example News",
            url="https://example.com/rss",
            language="en",
            country="Example Country",
            source_identifier="example-news",
            source_type=SourceType.NEWS_AGENCY,
        )
        published_at = datetime(
            2026,
            7,
            16,
            12,
            0,
            tzinfo=timezone.utc,
        )
        candidate = CandidateRecord(
            connector_id="rss",
            connector_version="1.0.0",
            location="https://example.com/article",
            discovered_at=published_at,
            external_identifier="article-1",
            title="Example article",
            source_identifier="example-news",
            language="en",
            published_at=published_at,
        )

        with (
            patch(
                "argus.services.collection_service.RSS_FEEDS",
                (feed,),
            ),
            patch(
                "argus.services.collection_service.RSSConnector"
            ) as connector_class,
            patch(
                "argus.services.collection_service.session_manager",
                self.session_manager,
            ),
        ):
            connector = connector_class.return_value
            connector.discover.return_value = [
                candidate
            ]

            collect_articles()

        connector_class.assert_called_once_with(feed)
        connector.discover.assert_called_once_with(
            DiscoveryRequest(
                mode=AcquisitionMode.CONTINUOUS,
            )
        )

        with self.session_factory() as session:
            source = session.scalar(
                select(Source)
            )
            article = session.scalar(
                select(Article)
            )

            self.assertIsNotNone(source)
            self.assertIsNotNone(article)

            self.assertEqual(
                source.identifier,
                "example-news",
            )
            self.assertEqual(
                source.source_type,
                SourceType.NEWS_AGENCY,
            )
            self.assertEqual(
                source.primary_jurisdiction,
                "Example Country",
            )
            self.assertEqual(
                source.default_language,
                "en",
            )

            self.assertEqual(
                article.source_id,
                source.id,
            )
            self.assertEqual(
                article.source,
                "Example News",
            )
            self.assertEqual(
                article.language,
                "en",
            )
            self.assertEqual(
                article.published_at,
                published_at.replace(tzinfo=None),
            )


if __name__ == "__main__":
    unittest.main()
