import unittest
from unittest.mock import patch

from typer.testing import CliRunner

from argus.interface.cli import app


runner = CliRunner()


class CLITests(unittest.TestCase):
    @patch("argus.interface.cli.collect_articles")
    @patch("argus.interface.cli.upgrade_database")
    def test_database_is_upgraded_before_command(
            self,
            upgrade_database,
            collect_articles,
    ):
        calls: list[str] = []

        upgrade_database.side_effect = (
            lambda: calls.append("upgrade")
        )
        collect_articles.side_effect = (
            lambda: calls.append("collect")
        )

        result = runner.invoke(app, ["collect"])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(calls, ["upgrade", "collect"])


if __name__ == "__main__":
    unittest.main()