import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from argus.config import ALEMBIC_CONFIG_PATH
from argus.storage.migrations import upgrade_database


EXPECTED_TABLES = {
    "alembic_version",
    "analysis_evidence",
    "articles",
    "discourse_analysis_results",
    "processing_states",
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


if __name__ == "__main__":
    unittest.main()