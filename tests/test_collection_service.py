import unittest
from unittest.mock import patch

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

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
        entries = [
            {
                "title": "Example article",
                "link": "https://example.com/article",
                "published": None,
                "source": "Example News",
                "source_identifier": "example-news",
                "source_type": SourceType.NEWS_AGENCY,
                "language": "en",
                "country": "Example Country",
            }
        ]

        with (
            patch(
                "argus.services.collection_service.RSS_FEEDS",
                (feed,),
            ),
            patch(
                "argus.services.collection_service.fetch_rss_entries",
                return_value=entries,
            ),
            patch(
                "argus.services.collection_service.session_manager",
                self.session_manager,
            ),
        ):
            collect_articles()

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


if __name__ == "__main__":
    unittest.main()