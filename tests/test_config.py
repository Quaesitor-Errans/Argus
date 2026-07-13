import unittest
from dataclasses import FrozenInstanceError

from argus.config import (
        DATABASE_PATH,
        LOG_FILE,
        PROJECT_ROOT,
        RSS_FEEDS,
        RSSFeedConfig,
    )


class ConfigTests(unittest.TestCase):
    def test_project_paths_are_derived_from_project_root(
            self,
    ) -> None:
        self.assertEqual(
            DATABASE_PATH,
            PROJECT_ROOT / "data" / "database" / "argus.db",
            )
        self.assertEqual(
            LOG_FILE,
            PROJECT_ROOT / "logs" / "argus.log",
            )

    def test_rss_feeds_are_stored_as_tuple(self) -> None:
        self.assertIsInstance(RSS_FEEDS, tuple)
        self.assertGreater(len(RSS_FEEDS), 0)

    def test_rss_feed_has_required_metadata(self) -> None:
        feed = RSS_FEEDS[0]

        self.assertIsInstance(feed, RSSFeedConfig)
        self.assertTrue(feed.name)
        self.assertTrue(feed.url)
        self.assertTrue(feed.language)
        self.assertTrue(feed.country)

    def test_rss_feed_config_is_immutable(self) -> None:
        feed = RSS_FEEDS[0]

        with self.assertRaises(FrozenInstanceError):
            setattr(
                feed,
                "name",
                "Changed name",
            )


if __name__ == "__main__":
    unittest.main()