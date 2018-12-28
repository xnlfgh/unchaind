"""Configure Python's logging module for use by unchaind."""

from typing import Any, Optional, List, Union

import logging
import sys


def setup_log(
    level: int = logging.CRITICAL, path: Optional[str] = None
) -> None:
    """Setup logging when ran as a command instead of used as a library."""

    handlers: List[Union[logging.StreamHandler, logging.FileHandler]] = [
        logging.StreamHandler()
    ]

    if path is not None:
        handlers = [logging.FileHandler(path)]

    logging.basicConfig(
        level=level,
        format="%(asctime)s:%(levelname)s:%(message)s",
        handlers=handlers,
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
