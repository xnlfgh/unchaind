"""Configure Python's logging module for use by unchaind."""

from typing import Any

import logging
import sys


def setup_log() -> None:
    """Setup logging when ran as a command instead of used as a library."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s",
        handlers=[
            logging.FileHandler("unchaind.log"),
            logging.StreamHandler(),
        ],
    )

    # XXX the type hander is a bit weird
    sys.excepthook = exc_handler  # type: ignore


# XXX this shouldn't be any I guess?
def app_log() -> Any:
    """Get an app_log instance which for now is the default logger."""
    return logging


def exc_handler(typ: BaseException, exc: BaseException, tb: Any) -> None:
    """Generic exception handling for uncaught exceptions to be logged."""
    app_log().exception(f"Uncaught exception {exc}")
    raise exc
