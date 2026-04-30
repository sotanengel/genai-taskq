from __future__ import annotations

import logging
import sys

import structlog


def configure_logging() -> None:
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")
    structlog.configure(
        processors=[structlog.processors.TimeStamper(fmt="iso"), structlog.processors.JSONRenderer()],
        logger_factory=structlog.PrintLoggerFactory(),
    )
