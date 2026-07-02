"""Centralized logging configuration."""

import logging
import sys

from app.core.config import settings


def configure_logging() -> None:
    root = logging.getLogger()
    if root.handlers:
        # Already configured (e.g. re-imported under --reload).
        root.setLevel(settings.log_level.upper())
        return

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)
    root.setLevel(settings.log_level.upper())

    # Quiet down noisy third-party loggers while keeping our own verbose.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("google_genai").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
