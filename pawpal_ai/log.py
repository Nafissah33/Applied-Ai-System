"""Logging setup: INFO-level activity goes to logs/pawpal.log (git-ignored); warnings also reach the console."""

import logging
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "pawpal.log"


def get_logger() -> logging.Logger:
    logger = logging.getLogger("pawpal_ai")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        try:
            LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
            file_handler.setFormatter(fmt)
            logger.addHandler(file_handler)
        except OSError:
            pass  # read-only filesystem: fall back to console only
        console = logging.StreamHandler()
        console.setLevel(logging.WARNING)
        console.setFormatter(fmt)
        logger.addHandler(console)
        logger.propagate = False
    return logger
