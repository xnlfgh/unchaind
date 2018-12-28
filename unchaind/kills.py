"""Functions to interface with killboards."""

import json
import re

from typing import Dict, Any, List
from asyncio import gather

from unchaind.http import HTTPSession
from unchaind.universe import System, Universe
from unchaind.notify import discord
from unchaind.util import system_name
from unchaind.log import app_log


async def loop(config: Dict[str, Any], universe: Universe) -> None:

    """Run a single iteration of the zkillboard RedisQ API which lists all
       kills then we filter those kills."""

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
        killmail = package["killmail"]
    except KeyError:
        app_log().warning("Received unparseable killmail from zkillboard")
        return

    # Find any matching notifiers
    matches = await match_killmail(config, universe, killmail)

    if not matches:
        return

    await gather(*[discord(match, killmail) for match in matches])


async def _filter_location(
    values: List[str], killmail: Dict[str, Any], universe: Universe
) -> bool:
    solar_system = System(killmail.get("solar_system_id", None))

    if "chain" in values:
        if solar_system in universe.systems:
            return False
        else:
            app_log().debug(
                "Killmail %s was filtered due to not being in chain",
                killmail["killmail_id"],
            )

    if "wspace" in values:
        # XXX do this mapping based on system id so this lookup doesn't need
        # XXX to happen for every kill
        solar_system_name = await system_name(solar_system)

        if re.match(r"J\d{6}", solar_system_name):
            return False
        else:
            app_log().debug(
                "Killmail %s was filtered due to not being in wspace",
                killmail["killmail_id"],
            )

    return True


async def _filter_alliance(
    values: List[int], killmail: Dict[str, Any], universe: Universe
) -> bool:
    """For the alliance filter the victim or any of the attackers have to be
       in the list of alliances."""

    loss = await _filter_alliance_kill(values, killmail, universe)

    if not loss:
        return False

    kill = await _filter_alliance_kill(values, killmail, universe)

    if not kill:
        return False

    return True


async def _filter_alliance_kill(
    values: List[int], killmail: Dict[str, Any], universe: Universe
) -> bool:
    """For the alliance filter the victim or any of the attackers have to be
       in the list of alliances."""

    attackers = killmail.get("attackers", [])

    for value in values:
        if any(a.get("alliance_id", None) == value for a in attackers):
            return False

    app_log().debug(
        "Killmail %s was filtered due to no alliance in %s",
        killmail["killmail_id"],
        values,
    )

    return True


async def _filter_alliance_loss(
    values: List[int], killmail: Dict[str, Any], universe: Universe
) -> bool:
    """For the alliance filter the victim or any of the attackers have to be
       in the list of alliances."""

    victim = killmail.get("victim", {})

    for value in values:
        if victim.get("alliance_id", None) == value:
            return False

    app_log().debug(
        "Killmail %s was filtered due to no alliance in %s",
        killmail["killmail_id"],
        values,
    )

    return True


async def _filter_corporation(
    values: List[int], killmail: Dict[str, Any], universe: Universe
) -> bool:
    """For the corporation filter the victim or any of the attackers have to be
       in the list of corporations."""

    loss = await _filter_corporation_kill(values, killmail, universe)

    if not loss:
        return False

    kill = await _filter_corporation_kill(values, killmail, universe)

    if not kill:
        return False

    return True


async def _filter_corporation_kill(
    values: List[int], killmail: Dict[str, Any], universe: Universe
) -> bool:
    """For the corporation filter the victim or any of the attackers have to be
       in the list of corporations."""

    attackers = killmail.get("attackers", [])

    for value in values:
        if any(a.get("corporation_id", None) == value for a in attackers):
            return False

    app_log().debug(
        "Killmail %s was filtered due to no corporation in %s",
        killmail["killmail_id"],
        values,
    )

    return True


async def _filter_corporation_loss(
    values: List[int], killmail: Dict[str, Any], universe: Universe
) -> bool:
    """For the corporation filter the victim or any of the attackers have to be
       in the list of corporations."""

    victim = killmail.get("victim", {})

    for value in values:
        if victim.get("corporation_id", None) == value:
            return False

    app_log().debug(
        "Killmail %s was filtered due to no corporation in %s",
        killmail["killmail_id"],
        values,
    )

    return True


# I gave up on trying to type this properly...
filters: Dict[str, Any] = {
    "location": _filter_location,
    "alliance": _filter_alliance,
    "alliance_kill": _filter_alliance_kill,
    "alliance_loss": _filter_alliance_loss,
    "corporation": _filter_corporation,
    "corporation_kill": _filter_corporation_kill,
    "corporation_loss": _filter_corporation_loss,
}


async def match_killmail(
    config: Dict[str, Any], universe: Universe, killmail: Dict[str, Any]
) -> List[Dict[str, Any]]:

    """Filter a killmail with its set of notifier filters. Returns the notifier
       if there's a match for it."""

    matches = []

    # Now let's see if any kill notifiers' filters match
    for notifier in config["notifiers"]:
        if notifier["subscribes_to"] != "kill":
            continue

        # This reads a bit difficult but this checks if all filters for this
        # notifier were False. If they were then that notifier would like to
        # receive this kill!
        results = await gather(
            *[
                filters[name](values, killmail, universe)
                for name, values in notifier["filter"].items()
            ]
        )

        if not all(results):
            matches.append(notifier)

    return matches
