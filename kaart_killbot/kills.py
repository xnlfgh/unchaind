"""Functions to interface with killboards."""

from typing import Optional, Callable, Dict, Awaitable, Any

import json

from kaart_killbot.http import HTTPSession
from kaart_killbot.universe import System, Universe
from kaart_killbot.notify import discord
from kaart_killbot.util import system_name
from kaart_killbot.log import app_log


async def loop_zkillboard(
    universe: Universe,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[bool]]] = None,
) -> None:

    """Run a single iteration of the zkillboard RedisQ API which lists all
       kills then compare them to the systems currently in the universe.

       If any kill happened in a system in that universe then send a
       notification."""

    http = HTTPSession()

    response = await http.request(
        url="https://redisq.zkillboard.com/listen.php", method="GET"
    )

    try:
        data = json.loads(response.body.decode("utf-8"))
    except (ValueError, AttributeError):
        # ValueError is raised when we get invalid JSON, AttributeError
        # is in case we have a `None` body
        return

    if "package" not in data:
        return

    package = data.get("package", None)

    if not package:
        return

    try:
        kill_id = package["killID"]
        kill_mail = package["killmail"]

        system = System(kill_mail["solar_system_id"])
    except KeyError:
        app_log().warning("Received unparseable killmail from zkillboard")
        return

    if system in universe.systems:
        if callback:
            filtered = await callback(kill_mail)
            if filtered:
                return

        app_log().warning("Killmail in chain")

        name = await system_name(system)
        await discord(
            f"Chain kill ({name}) https://zkillboard.com/kill/{kill_id}/"
        )
