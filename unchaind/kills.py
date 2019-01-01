"""Functions to interface with killboards."""

import json
import re

from typing import Dict, Any, List
from asyncio import gather

from unchaind.http import HTTPSession
from unchaind.universe import System, Universe
from unchaind.notify import sinks
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
        app_log().debug("empty reply from zkb")
        return

    try:
        killmail = package["killmail"]
    except KeyError:
        app_log().warning("Received unparseable killmail from zkillboard")
        return

    kill_id = killmail["killmail_id"]
    message = f"https://zkillboard.com/kill/{kill_id}/"

    # Find any matching notifiers
    matches = await match_killmail(config, universe, package)

    if not matches:
        app_log().debug(f"no matches for {kill_id}")
        return

    await gather(*[sinks[match["type"]](match, message) for match in matches])


async def _filter_location(
    values: List[Any], package: Dict[str, Any], universe: Universe
) -> bool:
    killmail = package["killmail"]
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

    if solar_system.identifier in values:
        app_log().debug(
            "Killmail %s: found %s in %s",
            killmail["killmail_id"],
            str(solar_system),
            repr(values),
        )
        return False

    return True


async def _filter_alliance(
    values: List[int], package: Dict[str, Any], universe: Universe
) -> bool:
    """For the alliance filter the victim or any of the attackers have to be
       in the list of alliances."""

    loss = await _filter_alliance_kill(values, package, universe)

    if not loss:
        return False

    kill = await _filter_alliance_kill(values, package, universe)

    if not kill:
        return False

    return True


async def _filter_alliance_kill(
    values: List[int], package: Dict[str, Any], universe: Universe
) -> bool:
    """For the alliance filter the victim or any of the attackers have to be
       in the list of alliances."""

    killmail = package["killmail"]

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
    values: List[int], package: Dict[str, Any], universe: Universe
) -> bool:
    """For the alliance filter the victim or any of the attackers have to be
       in the list of alliances."""

    killmail = package["killmail"]

    victim = killmail.get("victim", {})

    print(repr(victim.get("alliance_id")), repr(values))
    for value in values:
        print(repr(victim.get("alliance_id")), repr(value))
        if victim.get("alliance_id", None) == value:
            return False

    app_log().debug(
        "Killmail %s was filtered due to no alliance in %s",
        killmail["killmail_id"],
        values,
    )

    return True


async def _filter_corporation(
    values: List[int], package: Dict[str, Any], universe: Universe
) -> bool:
    """For the corporation filter the victim or any of the attackers have to be
       in the list of corporations."""

    loss = await _filter_corporation_kill(values, package, universe)

    if not loss:
        return False

    kill = await _filter_corporation_kill(values, package, universe)

    if not kill:
        return False

    return True


async def _filter_corporation_kill(
    values: List[int], package: Dict[str, Any], universe: Universe
) -> bool:
    """For the corporation filter the victim or any of the attackers have to be
       in the list of corporations."""

    killmail = package["killmail"]

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
    values: List[int], package: Dict[str, Any], universe: Universe
) -> bool:
    """For the corporation filter the victim or any of the attackers have to be
       in the list of corporations."""

    killmail = package["killmail"]

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


async def _filter_character(
    values: List[int], package: Dict[str, Any], universe: Universe
) -> bool:
    """For the character filter the victim or any of the attackers have to be
       in the list of characters."""

    loss = await _filter_character_kill(values, package, universe)

    if not loss:
        return False

    kill = await _filter_character_kill(values, package, universe)

    if not kill:
        return False

    return True


async def _filter_character_kill(
    values: List[int], package: Dict[str, Any], universe: Universe
) -> bool:
    """For the character filter the victim or any of the attackers have to be
       in the list of characters."""

    killmail = package["killmail"]

    attackers = killmail.get("attackers", [])

    for value in values:
        if any(a.get("character_id", None) == value for a in attackers):
            return False

    app_log().debug(
        "Killmail %s was filtered due to no character in %s",
        killmail["killmail_id"],
        values,
    )

    return True


async def _filter_character_loss(
    values: List[int], package: Dict[str, Any], universe: Universe
) -> bool:
    """For the character filter the victim or any of the attackers have to be
       in the list of characters."""

    killmail = package["killmail"]

    victim = killmail.get("victim", {})

    for value in values:
        if victim.get("character_id", None) == value:
            return False

    app_log().debug(
        "Killmail %s was filtered due to no character in %s",
        killmail["killmail_id"],
        values,
    )

    return True


async def _filter_minimum_value(
    values: List[int], package: Dict[str, Any], universe: Universe
) -> bool:
    """Filter kills that are not of at least a minimum value."""

    kill_value = package["zkb"]["totalValue"]
    minimum = values[0]

    rv = minimum > kill_value
    if rv:
        app_log().debug(
            "Killmail %s was filtered due to value less than threshold (%s < %s)",
            package["killmail"]["killmail_id"],
            kill_value,
            minimum,
        )

    return bool(minimum > kill_value)


# I gave up on trying to type this properly...
filters: Dict[str, Any] = {
    "location": _filter_location,
    "alliance": _filter_alliance,
    "character": _filter_character,
    "alliance_kill": _filter_alliance_kill,
    "alliance_loss": _filter_alliance_loss,
    "corporation": _filter_corporation,
    "corporation_kill": _filter_corporation_kill,
    "corporation_loss": _filter_corporation_loss,
    "character_kill": _filter_character_kill,
    "character_loss": _filter_character_loss,
    "minimum_value": _filter_minimum_value,
}


async def match_killmail(
    config: Dict[str, Any], universe: Universe, package: Dict[str, Any]
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
        require_all_of_results = await gather(
            *[
                filters[name](values, package, universe)
                for name, values in notifier["filter"]
                .get("require_all_of", {})
                .items()
            ]
        )

        exclude_if_any_results = await gather(
            *[
                filters[name](values, package, universe)
                for name, values in notifier["filter"]
                .get("exclude_if_any", {})
                .items()
            ]
        )

        # XXX invert the boolean senses of filters, this is horrifying and could be
        # so much easier to read and reason about.
        if (not any(require_all_of_results)) and all(exclude_if_any_results):
            matches.append(notifier)

    return matches
