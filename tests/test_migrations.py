import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from argus.config import ALEMBIC_CONFIG_PATH
from argus.storage.migrations import upgrade_database


EXPECTED_TABLES = {
    "acquisition_candidates",
    "alembic_version",
    "analysis_evidence",
    "articles",
    "collection_endpoints",
    "document_versions",
    "documents",
    "discourse_analysis_results",
    "processing_states",
    "raw_artifacts",
    "retrieval_attempts",
    "sources",
}

class MigrationServiceTests(unittest.TestCase):
    @patch("argus.storage.migrations.command.upgrade")
    @patch("argus.storage.migrations.Config")
    def test_upgrade_database_applies_head_revision(
        self,
        config_class,
        upgrade,
    ):
        config = config_class.return_value

        upgrade_database()

        config_class.assert_called_once_with(
            str(ALEMBIC_CONFIG_PATH)
        )
        upgrade.assert_called_once_with(config, "head")


class MigrationIntegrationTests(unittest.TestCase):
    def test_initial_migration_creates_current_schema(self):
        with TemporaryDirectory() as temporary_directory:
            database_path = (
                Path(temporary_directory) / "migration_test.db"
            )
            database_url = (
                f"sqlite:///{database_path.as_posix()}"
            )
            config = Config(str(ALEMBIC_CONFIG_PATH))

            with patch.dict(
                os.environ,
                {"ARGUS_ALEMBIC_DATABASE_URL": database_url},
            ):
                command.upgrade(config, "head")

            test_engine = create_engine(database_url)

            try:
                table_names = set(
                    inspect(test_engine).get_table_names()
                )
            finally:
                test_engine.dispose()

        self.assertEqual(table_names, EXPECTED_TABLES)

    def test_source_migration_backfills_legacy_articles(
        self,
    ) -> None:
        with TemporaryDirectory() as temporary_directory:
            database_path = (
                Path(temporary_directory) / "legacy_test.db"
            )
            database_url = (
                f"sqlite:///{database_path.as_posix()}"
            )
            config = Config(str(ALEMBIC_CONFIG_PATH))

            with patch.dict(
                os.environ,
                {"ARGUS_ALEMBIC_DATABASE_URL": database_url},
            ):
                command.upgrade(
                    config,
                    "deef19cb438c",
                )

                legacy_engine = create_engine(database_url)

                try:
                    with legacy_engine.begin() as connection:
                        connection.execute(
                            text(
                                """
                                INSERT INTO articles (
                                    url,
                                    title,
                                    source,
                                    language,
                                    fetched_at
                                )
                                VALUES (
                                           :url,
                                           :title,
                                           :source,
                                           :language,
                                           CURRENT_TIMESTAMP
                                       )
                                """
                            ),
                            {
                                "url": "https://example.com/legacy",
                                "title": "Legacy article",
                                "source": "Legacy News",
                                "language": "en",
                            },
                        )
                finally:
                    legacy_engine.dispose()
                command.upgrade(config, "head")

            result_engine = create_engine(database_url)

            try:
                with result_engine.connect() as connection:
                    source = connection.execute(
                        text(
                            """
                            SELECT
                                id,
                                identifier,
                                name,
                                source_type,
                                primary_jurisdiction,
                                default_language
                            FROM sources
                            """
                        )
                    ).mappings().one()

                    article_source_id = connection.execute(
                        text(
                            """
                            SELECT source_id
                            FROM articles
                            WHERE url = :url
                            """
                        ),
                        {
                            "url": "https://example.com/legacy",
                        },
                    ).scalar_one()
            finally:
                result_engine.dispose()
        self.assertEqual(
            source["identifier"],
            "Legacy News",
        )
        self.assertEqual(source["name"], "Legacy News")
        self.assertEqual(
            source["source_type"],
            "news_media",
        )
        self.assertIsNone(
            source["primary_jurisdiction"]
        )
        self.assertEqual(
            source["default_language"],
            "en",
        )
        self.assertEqual(
            article_source_id,
            source["id"],
        )

    def test_source_migration_downgrades_to_baseline(
        self,
    ) -> None:
        with TemporaryDirectory() as temporary_directory:
            database_path = (
                Path(temporary_directory) / "downgrade_test.db"
            )
            database_url = (
                f"sqlite:///{database_path.as_posix()}"
            )
            config = Config(str(ALEMBIC_CONFIG_PATH))

            with patch.dict(
                os.environ,
                {"ARGUS_ALEMBIC_DATABASE_URL": database_url},
            ):
                command.upgrade(config, "head")
                command.downgrade(
                    config,
                    "deef19cb438c",
                )
            test_engine = create_engine(database_url)

            try:
                inspector = inspect(test_engine)
                table_names = set(
                    inspector.get_table_names()
                )
                article_columns = {
                    column["name"]
                    for column in inspector.get_columns(
                        "articles"
                    )
                }
            finally:
                test_engine.dispose()

        self.assertNotIn("sources", table_names)
        self.assertNotIn("source_id", article_columns)
        self.assertIn("source", article_columns)

    def test_endpoint_migration_downgrades_to_source_schema(
        self,
    ) -> None:
        with TemporaryDirectory() as temporary_directory:
            database_path = (
                Path(temporary_directory) / "endpoint_downgrade_test.db"
            )
            database_url = (
                f"sqlite:///{database_path.as_posix()}"
            )
            config = Config(str(ALEMBIC_CONFIG_PATH))

            with patch.dict(
                os.environ,
                {"ARGUS_ALEMBIC_DATABASE_URL": database_url},
            ):
                command.upgrade(config, "head")
                command.downgrade(
                    config,
                    "214ca03fb3ed",
                )

            test_engine = create_engine(database_url)

            try:
                table_names = set(
                    inspect(test_engine).get_table_names()
                )
            finally:
                test_engine.dispose()

        self.assertNotIn(
            "collection_endpoints",
            table_names,
        )
        self.assertIn("sources", table_names)

    def test_retrieval_migration_downgrades_to_endpoint_schema(
        self,
    ) -> None:
        with TemporaryDirectory() as temporary_directory:
            database_path = (
                Path(temporary_directory) / "retrieval_downgrade_test.db"
            )
            database_url = (
                f"sqlite:///{database_path.as_posix()}"
            )
            config = Config(str(ALEMBIC_CONFIG_PATH))

            with patch.dict(
                os.environ,
                {"ARGUS_ALEMBIC_DATABASE_URL": database_url},
            ):
                command.upgrade(config, "head")
                command.downgrade(
                    config,
                    "85db1d6a8b3a",
                )

            test_engine = create_engine(database_url)

            try:
                table_names = set(
                    inspect(test_engine).get_table_names()
                )
            finally:
                test_engine.dispose()

        self.assertNotIn(
            "retrieval_attempts",
            table_names,
        )
        self.assertIn(
            "collection_endpoints",
            table_names,
        )

    def test_raw_artifact_migration_downgrades_to_retrieval_schema(
        self,
    ) -> None:
        with TemporaryDirectory() as temporary_directory:
            database_path = (
                Path(temporary_directory) / "artifact_downgrade_test.db"
            )
            database_url = (
                f"sqlite:///{database_path.as_posix()}"
            )
            config = Config(str(ALEMBIC_CONFIG_PATH))

            with patch.dict(
                os.environ,
                {"ARGUS_ALEMBIC_DATABASE_URL": database_url},
            ):
                command.upgrade(config, "head")
                command.downgrade(
                    config,
                    "2aa55e015b7d",
                )

            test_engine = create_engine(database_url)

            try:
                inspector = inspect(test_engine)
                table_names = set(
                    inspector.get_table_names()
                )
                retrieval_columns = {
                    column["name"]
                    for column in inspector.get_columns(
                        "retrieval_attempts"
                    )
                }
            finally:
                test_engine.dispose()

        self.assertNotIn("raw_artifacts", table_names)
        self.assertIn("retrieval_attempts", table_names)
        self.assertNotIn(
            "raw_artifact_id",
            retrieval_columns,
        )

    def test_candidate_migration_downgrades_to_artifact_schema(
            self,
    ) -> None:
        with TemporaryDirectory() as temporary_directory:
            database_path = (
                Path(temporary_directory) / "candidate_downgrade_test.db"
            )
            database_url = f"sqlite:///{database_path.as_posix()}"
            config = Config(str(ALEMBIC_CONFIG_PATH))

            with patch.dict(
                os.environ,
                {"ARGUS_ALEMBIC_DATABASE_URL": database_url},
            ):
                command.upgrade(config, "b22c36e940db")
                command.downgrade(config, "cb3e06323fb8")

            test_engine = create_engine(database_url)

            try:
                inspector = inspect(test_engine)
                table_names = set(inspector.get_table_names())
                retrieval_columns = {
                    column["name"]
                    for column in inspector.get_columns(
                        "retrieval_attempts"
                    )
                }
            finally:
                test_engine.dispose()

        self.assertNotIn(
            "acquisition_candidates",
            table_names,
        )
        self.assertNotIn("candidate_id", retrieval_columns)
        self.assertIn("raw_artifacts", table_names)

    def test_document_migration_downgrades_to_candidate_schema(
            self,
    ) -> None:
        with TemporaryDirectory() as temporary_directory:
            database_path = (
                Path(temporary_directory) / "document_downgrade_test.db"
            )
            database_url = f"sqlite:///{database_path.as_posix()}"
            config = Config(str(ALEMBIC_CONFIG_PATH))

            with patch.dict(
                os.environ,
                {"ARGUS_ALEMBIC_DATABASE_URL": database_url},
            ):
                command.upgrade(config, "head")
                command.downgrade(config, "b22c36e940db")

            test_engine = create_engine(database_url)

            try:
                table_names = set(
                    inspect(test_engine).get_table_names()
                )
            finally:
                test_engine.dispose()

        self.assertNotIn("documents", table_names)
        self.assertNotIn("document_versions", table_names)
        self.assertIn("acquisition_candidates", table_names)

    def test_document_ingestion_link_downgrades_to_document_schema(
            self,
    ) -> None:
        with TemporaryDirectory() as temporary_directory:
            database_path = (
                Path(temporary_directory) / "ingestion_link_test.db"
            )
            database_url = f"sqlite:///{database_path.as_posix()}"
            config = Config(str(ALEMBIC_CONFIG_PATH))

            with patch.dict(
                os.environ,
                {"ARGUS_ALEMBIC_DATABASE_URL": database_url},
            ):
                command.upgrade(config, "head")
                command.downgrade(config, "7f3a1c9d2e4b")

            test_engine = create_engine(database_url)

            try:
                inspector = inspect(test_engine)
                table_names = set(inspector.get_table_names())
                retrieval_columns = {
                    column["name"]
                    for column in inspector.get_columns(
                        "retrieval_attempts"
                    )
                }
            finally:
                test_engine.dispose()

        self.assertNotIn(
            "document_version_id",
            retrieval_columns,
        )
        self.assertIn("documents", table_names)
        self.assertIn("document_versions", table_names)

    def test_legacy_article_migration_backfills_document_link(
            self,
    ) -> None:
        with TemporaryDirectory() as temporary_directory:
            database_path = (
                Path(temporary_directory) / "article_document_test.db"
            )
            database_url = f"sqlite:///{database_path.as_posix()}"
            config = Config(str(ALEMBIC_CONFIG_PATH))

            with patch.dict(
                os.environ,
                {"ARGUS_ALEMBIC_DATABASE_URL": database_url},
            ):
                command.upgrade(config, "c91d6e8f42a7")
                legacy_engine = create_engine(database_url)

                try:
                    with legacy_engine.begin() as connection:
                        connection.execute(
                            text(
                                """
                                INSERT INTO articles (
                                    url,
                                    title,
                                    source,
                                    language,
                                    fetched_at
                                ) VALUES (
                                    :url,
                                    :title,
                                    :source,
                                    :language,
                                    CURRENT_TIMESTAMP
                                )
                                """
                            ),
                            {
                                "url": "https://example.com/legacy-doc",
                                "title": "Legacy document",
                                "source": "Legacy News",
                                "language": "en",
                            },
                        )
                finally:
                    legacy_engine.dispose()

                command.upgrade(config, "head")

            result_engine = create_engine(database_url)

            try:
                with result_engine.connect() as connection:
                    row = connection.execute(
                        text(
                            """
                            SELECT
                                articles.document_id,
                                documents.identifier_scheme,
                                documents.identifier_value,
                                documents.document_type,
                                documents.title,
                                documents.language
                            FROM articles
                            JOIN documents
                              ON documents.id = articles.document_id
                            WHERE articles.url = :url
                            """
                        ),
                        {"url": "https://example.com/legacy-doc"},
                    ).mappings().one()
            finally:
                result_engine.dispose()

        self.assertIsNotNone(row["document_id"])
        self.assertEqual(row["identifier_scheme"], "uri")
        self.assertEqual(
            row["identifier_value"],
            "https://example.com/legacy-doc",
        )
        self.assertEqual(row["document_type"], "article")
        self.assertEqual(row["title"], "Legacy document")
        self.assertEqual(row["language"], "en")

    def test_legacy_article_link_downgrades_to_ingestion_schema(
            self,
    ) -> None:
        with TemporaryDirectory() as temporary_directory:
            database_path = (
                Path(temporary_directory) / "article_link_down.db"
            )
            database_url = f"sqlite:///{database_path.as_posix()}"
            config = Config(str(ALEMBIC_CONFIG_PATH))

            with patch.dict(
                os.environ,
                {"ARGUS_ALEMBIC_DATABASE_URL": database_url},
            ):
                command.upgrade(config, "head")
                command.downgrade(config, "c91d6e8f42a7")

            test_engine = create_engine(database_url)

            try:
                article_columns = {
                    column["name"]
                    for column in inspect(test_engine).get_columns(
                        "articles"
                    )
                }
            finally:
                test_engine.dispose()

        self.assertNotIn("document_id", article_columns)


if __name__ == "__main__":
    unittest.main()
