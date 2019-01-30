"""Functions to extract data from killmail JSON dicts."""
import logging
import dateutil.parser
import millify
import collections
import operator

from typing import Dict, Any, Optional, Awaitable

from asyncio import gather, ensure_future, Future

import unchaind.esi_util as esi_util
from unchaind.universe import Universe, System

log = logging.getLogger(__name__)


async def get_payload_for_killmail(
    notifier: Dict[str, Any], package: Dict[str, Any], universe: Universe
) -> Optional[Dict[str, Any]]:
    """Given a notifier and a killmail, attempt to format a pretty payload for it."""
    if notifier["type"] == "slack":
        return await _slack_payload_for_killmail(notifier, package, universe)

    return None


async def char_name_with_ticker(char: Dict[str, Any]) -> str:
    """Given a zkb attacker or victim, return character name
    or something close."""
    try:
        if "character_id" in char:
            details, entity = await gather(
                *[
                    esi_util.character_details(char["character_id"]),
                    entity_ticker_for_char(char),
                ]
            )
            return f"{details['name']} [{entity}]"
        if "faction_id" in char:
            return "NPC"
    except:
        pass
    return "???"


async def entity_ticker_for_char(char: Dict[str, Any]) -> str:
    """Given a zkb attacker or victim, return alliance/corp ticker
    or something close."""
    try:
        if "alliance_id" in char:
            alliance = await esi_util.alliance_details(char["alliance_id"])
            return str(alliance["ticker"])
        elif "corporation_id" in char:
            corp = await esi_util.corporation_details(char["corporation_id"])
            return str(corp["ticker"])
        elif "faction_id" in char:
            return "{NPC}"
    except:
        pass
    return "?????"


def _stringify_counter_by_popularity(c: collections.Counter) -> str:
    """Given a counter, give a string summary in descending popularity."""
    return ", ".join(
        [
            f"{v} {k}"
            for k, v in sorted(
                c.items(), reverse=True, key=operator.itemgetter(1)
            )
        ]
    )


async def _slack_payload_for_killmail(
    notifier: Dict[str, Any], package: Dict[str, Any], universe: Universe
) -> Optional[Dict[str, Any]]:
    tasks = []

    def promise(t: Awaitable) -> Future:
        """Given an awaitable, make sure it is a Future, and write it down in our list
        of pending tasks."""
        fut = ensure_future(t)
        tasks.append(fut)
        return fut

    victim_ship_type = package["killmail"]["victim"]["ship_type_id"]
    victim_moniker = promise(
        char_name_with_ticker(package["killmail"]["victim"])
    )
    victim_ship = promise(esi_util.type_details(victim_ship_type))
    system_name = promise(
        universe.system_name(System(package["killmail"]["solar_system_id"]))
    )
    final_blow = promise(
        char_name_with_ticker(
            next(
                filter(
                    lambda x: x["final_blow"], package["killmail"]["attackers"]
                )
            )
        )
    )
    top_dmg = promise(
        char_name_with_ticker(
            max(
                package["killmail"]["attackers"], key=lambda x: x["damage_done"]
            )
        )
    )
    attacker_entities = promise(
        gather(
            *[
                entity_ticker_for_char(x)
                for x in package["killmail"]["attackers"]
            ]
        )
    )
    attacker_ships = promise(
        gather(
            *[
                (esi_util.type_details(x["ship_type_id"]))
                for x in package["killmail"]["attackers"]
            ]
        )
    )

    await gather(*tasks)

    text = f"{victim_moniker.result()} lost a {victim_ship.result()['name']} "
    text += f"worth {millify.millify(package['zkb']['totalValue'], precision=2)} ISK "
    text += f"\nin *{system_name.result()}* "

    summarized_entities = _stringify_counter_by_popularity(
        collections.Counter(attacker_entities.result())
    )
    summarized_ships = _stringify_counter_by_popularity(
        collections.Counter(
            map(operator.itemgetter("name"), attacker_ships.result())
        )
    )

    rv = {
        "attachments": [
            {
                "fallback": text,
                "text": text,
                "footer": f"https://zkillboard.com/kill/{package['killID']}/",
                "footer_icon": "https://zkillboard.com/img/wreck.png",
                "ts": int(
                    dateutil.parser.parse(
                        package["killmail"]["killmail_time"]
                    ).timestamp()
                ),
                "thumb_url": f"https://imageserver.eveonline.com/Render/{victim_ship_type}_128.png",
                "fields": [
                    {
                        "short": True,
                        "title": "The attackers",
                        "value": summarized_entities,
                    },
                    {
                        "short": True,
                        "title": "were flying",
                        "value": summarized_ships,
                    },
                ],
            }
        ]
    }

    if notifier.get("output", None) and notifier["output"].get(
        "include_vanity_stats", False
    ):
        rv["attachments"][0]["fields"].extend(  # type: ignore
            [
                {"short": True, "title": "Final blow", "value": final_blow.result()},
                {"short": True, "title": "Top damage", "value": top_dmg.result()},
            ]
        )

    return rv
