"""Functions to talk to chat programs such as Slack and Discord."""

import json

from unchaind.http import HTTPSession
from unchaind import config


async def discord(message: str) -> None:
    """Send a discord message to the default configured channel."""
    http = HTTPSession()

    await http.request(
        url=config.notifiers[0]["url"],
        method="POST",
        body=json.dumps({"content": message}),
    )
