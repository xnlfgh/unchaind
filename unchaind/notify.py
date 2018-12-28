"""Functions to talk to chat programs such as Slack and Discord."""

import json

from typing import Dict, Any

from unchaind.http import HTTPSession


async def discord(notifier: Dict[str, Any], killmail: Dict[str, Any]) -> None:
    """Send a discord message to the configured channel."""
    http = HTTPSession()

    kill_id = killmail["killmail_id"]

    message = f"https://zkillboard.com/kill/{kill_id}/"

    await http.request(
        url=notifier["webhook"],
        method="POST",
        body=json.dumps({"content": message}),
    )


types = {"discord": discord}
