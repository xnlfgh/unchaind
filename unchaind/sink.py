"""Functions to talk to chat programs such as Slack and Discord."""

import json
import logging

from typing import Dict, Any, Optional

from unchaind.http import HTTPSession


log = logging.getLogger(__name__)


async def discord(
    notifier: Dict[str, Any],
    message: str,
    *,
    payload: Optional[Dict[str, Any]] = None,
) -> None:
    """Send a Discord message to the configured channel."""
    if payload is not None:
       http = HTTPSession()

       await http.request(
         url=notifier["webhook"],
         method="POST",
         body=json.dumps(payload)
       )
    else:
        http = HTTPSession()

        await http.request(
         url=notifier["webhook"],
         method="POST",
         body=json.dumps({"content": message}),
       )


async def console(
    notifier: Dict[str, Any],
    message: str,
    *,
    payload: Optional[Dict[str, Any]] = None,
) -> None:
    """Log a message.  Intended for debugging use."""
    log.info("NOTIFICATION: " + message)


async def slack(
    notifier: Dict[str, Any],
    message: str,
    *,
    payload: Optional[Dict[str, Any]] = None,
) -> None:
    """Send a Slack message to the configured channel.  If payload was provided,
    it's JSONified and used as the body of the request to Slack.  Otherwise, message
    will be displayed."""

    if payload is not None:
        http = HTTPSession()

        await http.request(
            url=notifier["webhook"], method="POST", body=json.dumps(payload)
        )
    else:
        await slack(notifier, message, payload={"text": message})


sinks = {"discord": discord, "console": console, "slack": slack}
