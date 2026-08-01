"""
Application-wide logging configuration.

Kept intentionally simple in Milestone 1 (stdlib logging, human-readable
format). This is the seam where we'd later swap in structured JSON logging
for production observability (e.g. when deployed on Render) without
touching any call site — every module just does `logging.getLogger(__name__)`.
"""

import logging
import sys


def configure_logging(debug: bool = True) -> None:
    level = logging.DEBUG if debug else logging.INFO

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = [handler]
