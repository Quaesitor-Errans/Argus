import logging
from pathlib import Path

from argus.database import PROJECT_ROOT


LOG_DIRECTORY = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIRECTORY / "argus.log"

LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | "
    "%(name)s | %(message)s"
)


def configure_logging(
        level: int = logging.INFO,
) -> None:
    """Configure Argus console and file logging."""

    LOG_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    root_logger = logging.getLogger()

    if root_logger.handlers:
        return

    root_logger.setLevel(level)

    formatter = logging.Formatter(
        LOG_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Return a named Argus logger."""

    return logging.getLogger(name)