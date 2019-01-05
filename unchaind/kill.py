"""Functions to interface with killboards."""
import logging
import json
import re

from typing import Dict, Any, List, Callable
from asyncio import gather

from unchaind.http import HTTPSession
from unchaind.universe import System, Universe
from unchaind.sink import sinks


log = logging.getLogger(__name__)


async def loop(config: Dict[str, Any], universe: Universe) -> None:
    """Run a single iteration of the zkillboard RedisQ API which lists all
       kills then we filter those kills."""

    http = HTTPSession()

    response = await http.request(
        url="https://redisq.zkillboard.com/listen.php", method="GET"
    )

    if response.status_code != 200:
        log.warning(
            "loop: received response code %s, content %s",
            response.status_code,
            response.content,
        )
    # responses sometimes lack .body but they always have .content

    try:
        data = json.loads(response.body.decode("utf-8"))
    except (ValueError):
        # ValueError is raised when we get invalid JSON
        log.warning(
            "loop: received invalid json (%r)", response.body.decode("utf-8")
        )
        return

    if "package" not in data:
        log.warning("loop: response did not contain 'package' key")
        return

    package = data.get("package", None)

    if not package:
        log.debug("loop: the package was empty")
        return

    try:
        killmail = package["killmail"]
    except KeyError:
        log.warning("loop: received unparseable killmail from zkillboard")
        return

    kill_id = killmail["killmail_id"]
    message = f"https://zkillboard.com/kill/{kill_id}/"

    # Find any matching notifiers
    matches = await match_killmail(config, universe, package)

    if not matches:
        log.debug(f"loop: no matches for %d", kill_id)
        return

    await gather(*[sinks[match["type"]](match, message) for match in matches])


async def _match_location(
    value: str, package: Dict[str, Any], universe: Universe
) -> bool:
    killmail = package["killmail"]
    solar_system = System(killmail.get("solar_system_id", None))

    if value == "chain":
        return solar_system in universe.systems

    if value == "wspace":
        return bool(re.match(r"J\d{6}", solar_system.name))

    return value.lower() == solar_system.name.lower()


async def _match_alliance(
    value: int, package: Dict[str, Any], universe: Universe
) -> bool:
    return await _match_alliance_loss(
        value, package, universe
    ) or await _match_alliance_kill(value, package, universe)


async def _match_alliance_kill(
    value: int, package: Dict[str, Any], universe: Universe
) -> bool:
    killmail = package["killmail"]
    attackers = killmail.get("attackers", [])
    return any(a.get("alliance_id", None) == value for a in attackers)


async def _match_alliance_loss(
    value: int, package: Dict[str, Any], universe: Universe
) -> bool:
    killmail = package["killmail"]
    return bool(killmail["victim"]["alliance_id"] == value)


async def _match_corporation(
    value: int, package: Dict[str, Any], universe: Universe
) -> bool:
    return await _match_corporation_loss(
        value, package, universe
    ) or await _match_corporation_kill(value, package, universe)


async def _match_corporation_kill(
    value: int, package: Dict[str, Any], universe: Universe
) -> bool:
    killmail = package["killmail"]
    attackers = killmail.get("attackers", [])
    return any(c.get("corporation_id", None) == value for c in attackers)


async def _match_corporation_loss(
    value: int, package: Dict[str, Any], universe: Universe
) -> bool:
    killmail = package["killmail"]
    return bool(killmail["victim"]["corporation_id"] == value)


async def _match_character(
    value: int, package: Dict[str, Any], universe: Universe
) -> bool:
    return await _match_character_loss(
        value, package, universe
    ) or await _match_character_kill(value, package, universe)


async def _match_character_kill(
    value: int, package: Dict[str, Any], universe: Universe
) -> bool:
    killmail = package["killmail"]
    attackers = killmail.get("attackers", [])
    return any(c.get("character_id", None) == value for c in attackers)


async def _match_character_loss(
    value: int, package: Dict[str, Any], universe: Universe
) -> bool:
    killmail = package["killmail"]
    return bool(killmail["victim"]["character_id"] == value)


async def _match_minimum_value(
    value: int, package: Dict[str, Any], universe: Universe
) -> bool:
    kill_value = package["zkb"]["totalValue"]
    return bool(kill_value >= value)


# I gave up on trying to type this properly...
matchers: Dict[str, Any] = {
    "location": _match_location,
    "alliance": _match_alliance,
    "character": _match_character,
    "alliance_kill": _match_alliance_kill,
    "alliance_loss": _match_alliance_loss,
    "corporation": _match_corporation,
    "corporation_kill": _match_corporation_kill,
    "corporation_loss": _match_corporation_loss,
    "character_kill": _match_character_kill,
    "character_loss": _match_character_loss,
    "minimum_value": _match_minimum_value,
}


async def match_killmail(
    config: Dict[str, Any], universe: Universe, package: Dict[str, Any]
) -> List[Dict[str, Any]]:

    """Filter a killmail with its set of notifier filters. Returns the notifier
       if there's a match for it."""

    matches = []

    killmail_id = package["killmail"]["killmail_id"]

    # Now let's see if any kill notifiers' filters match
    for index, notifier in enumerate(config["notifier"]):
        log.debug(
            "considering killmail id %s for notifier %s", killmail_id, index
        )
        if notifier["subscribes_to"] != "kill":
            log.debug(
                "notifier %s does not subscribe to kills; skipping", index
            )
            continue

        async def apply_matchers(section: str) -> List[bool]:
            rv = []
            for d in notifier["filter"].get(section, []):
                for name, value in d.items():
                    filter_result = await matchers[name](
                        value, package, universe
                    )
                    log.debug(
                        "notifier %s killmail %s: %s: considered %s(%s) --> %s",
                        index,
                        killmail_id,
                        section,
                        name,
                        value,
                        filter_result,
                    )
                    rv.append(filter_result)
            return rv

        sections: Dict[str, Callable[..., bool]] = {
            "require_all_of": all,
            "require_any_of": any,
            "exclude_if_any": lambda x: not any,
            "exclude_if_all": lambda x: not all,
        }

        rv = True

        for section, aggregator in sections.items():
            section_results = await apply_matchers(section)
            rv = rv and (
                len(section_results) == 0 or aggregator(section_results)
            )

        if rv:
            log.debug(
                "notifier %s killmail %s: it's a match!", index, killmail_id
            )
            matches.append(notifier)
        else:
            log.debug(
                "notifier %s killmail %s: filtered away", index, killmail_id
            )

    return matches
