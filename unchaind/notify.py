"""Functions to talk to chat programs such as Slack and Discord."""

import json

from typing import Dict, Any

from unchaind.http import HTTPSession


async def discord(config: Dict[str, Any], message: str) -> None:
    """Send a discord message to the default configured channel."""
    http = HTTPSession()

    await http.request(
        url=config["notifiers"][0]["webhook"],
        method="POST",
        body=json.dumps({"content": message}),
    )
