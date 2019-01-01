"""Functions to talk to chat programs such as Slack and Discord."""

import json
import logging

from typing import Dict, Any

from unchaind.http import HTTPSession


log = logging.getLogger(__name__)


async def discord(notifier: Dict[str, Any], message: str) -> None:
    """Send a Discord message to the configured channel."""
    http = HTTPSession()

    await http.request(
        url=notifier["webhook"],
        method="POST",
        body=json.dumps({"content": message}),
    )


async def console(notifier: Dict[str, Any], message: str) -> None:
    """Log a message.  Intended for debugging use."""
    log.info("NOTIFICATION: " + message)


async def slack(notifier: Dict[str, Any], message: str) -> None:
    """Send a Slack message to the configured channel."""
    http = HTTPSession()

    await http.request(
        url=notifier["webhook"],
        method="POST",
        body=json.dumps({"text": message}),
    )


sinks = {"discord": discord, "console": console, "slack": slack}
