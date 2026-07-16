import unittest
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import httpx

from argus.acquisition import (
    AcquisitionMode,
    CandidateRecord,
    Connector,
    DiscoveryRequest,
    RetrievalOutcome,
)
from argus.collector.rss_connector import RSSConnector
from argus.config import RSSFeedConfig


class RSSConnectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(
            2026,
            7,
            16,
            12,
            0,
            tzinfo=timezone.utc,
        )
        self.feed = RSSFeedConfig(
            name="Example News",
            url="https://example.com/feed.xml",
            language="en",
            country="Example Country",
            source_identifier="example-news",
        )
        self.connector = RSSConnector(
            self.feed,
            clock=lambda: self.now,
        )

    def create_candidate(self) -> CandidateRecord:
        return CandidateRecord(
            connector_id=self.connector.connector_id,
            connector_version=(
                self.connector.connector_version
            ),
            location="https://example.com/article",
            discovered_at=self.now,
            source_identifier="example-news",
        )

    def test_connector_implements_contract(self) -> None:
        self.assertIsInstance(
            self.connector,
            Connector,
        )

    @patch(
        "argus.collector.rss_connector.feedparser.parse"
    )
    def test_discover_normalizes_feed_entry(
            self,
            parse_mock: Mock,
    ) -> None:
        parse_mock.return_value.entries = [
            {
                "id": "article-1",
                "title": "Energy policy changed",
                "link": "https://example.com/article",
                "published": (
                    "Thu, 16 Jul 2026 10:00:00 GMT"
                ),
            }
        ]

        candidates = self.connector.discover(
            DiscoveryRequest(
                mode=AcquisitionMode.CONTINUOUS,
            )
        )

        self.assertEqual(len(candidates), 1)

        candidate = candidates[0]

        self.assertEqual(
            candidate.connector_id,
            "rss",
        )
        self.assertEqual(
            candidate.external_identifier,
            "article-1",
        )
        self.assertEqual(
            candidate.source_identifier,
            "example-news",
        )
        self.assertEqual(
            candidate.published_at,
            datetime(
                2026,
                7,
                16,
                10,
                0,
                tzinfo=timezone.utc,
            ),
        )
        self.assertEqual(
            candidate.discovered_at,
            self.now,
        )

    @patch(
        "argus.collector.rss_connector.feedparser.parse"
    )
    def test_discover_applies_query_and_limit(
            self,
            parse_mock: Mock,
    ) -> None:
        parse_mock.return_value.entries = [
            {
                "title": "Unrelated article",
                "link": "https://example.com/1",
            },
            {
                "title": "Energy policy one",
                "link": "https://example.com/2",
            },
            {
                "title": "Energy policy two",
                "link": "https://example.com/3",
            },
        ]

        candidates = self.connector.discover(
            DiscoveryRequest(
                mode=AcquisitionMode.INVESTIGATION,
                query="energy policy",
                limit=1,
            )
        )

        self.assertEqual(
            [candidate.location for candidate in candidates],
            ["https://example.com/2"],
        )

    def test_discover_rejects_cursor(self) -> None:
        with self.assertRaisesRegex(
                ValueError,
                "does not support cursors",
        ):
            self.connector.discover(
                DiscoveryRequest(
                    mode=AcquisitionMode.CONTINUOUS,
                    cursor="next-page",
                )
            )

    @patch("argus.collector.rss_connector.httpx.get")
    def test_retrieve_returns_successful_content(
            self,
            get_mock: Mock,
    ) -> None:
        get_mock.return_value = httpx.Response(
            200,
            content=b"Article bytes",
            headers={
                "content-type": "text/html; charset=utf-8",
            },
            request=httpx.Request(
                "GET",
                "https://example.com/article",
            ),
        )

        result = self.connector.retrieve(
            self.create_candidate()
        )

        self.assertEqual(
            result.outcome,
            RetrievalOutcome.SUCCEEDED,
        )
        self.assertEqual(result.content, b"Article bytes")
        self.assertEqual(result.response_status, "200")

    @patch("argus.collector.rss_connector.httpx.get")
    def test_retrieve_distinguishes_restricted_content(
            self,
            get_mock: Mock,
    ) -> None:
        get_mock.return_value = httpx.Response(
            403,
            request=httpx.Request(
                "GET",
                "https://example.com/article",
            ),
        )

        result = self.connector.retrieve(
            self.create_candidate()
        )

        self.assertEqual(
            result.outcome,
            RetrievalOutcome.ACCESS_RESTRICTED,
        )
        self.assertIsNone(result.content)

    @patch("argus.collector.rss_connector.httpx.get")
    def test_retrieve_records_transport_failure(
            self,
            get_mock: Mock,
    ) -> None:
        get_mock.side_effect = httpx.ConnectError(
            "connection failed"
        )

        result = self.connector.retrieve(
            self.create_candidate()
        )

        self.assertEqual(
            result.outcome,
            RetrievalOutcome.FAILED,
        )
        self.assertEqual(
            result.error,
            "connection failed",
        )


if __name__ == "__main__":
    unittest.main()