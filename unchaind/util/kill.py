"""Functions to extract data from killmail JSON dicts."""
import logging
import dateutil.parser
import millify
import collections
import operator

from typing import Dict, Any, Optional, Callable

from asyncio import gather
from tornado.gen import multi

from dataclasses import dataclass

import unchaind.util.esi as esi_util
from unchaind.universe import Universe, System

log = logging.getLogger(__name__)


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
        elif "corporation_id" in char:
            # Some kills (e.g. POS modules) have no char id, but
            # still belong to a corp/alliance
            return await entity_ticker_for_char(char)
        elif "faction_id" in char:
            # If we have none of the above, just a faction, it was an NPC
            return "NPC"
    except Exception as e:
        log.exception(e)

    return "?????"


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
    except Exception as e:
        log.exception(e)

    return "?????"


def _stringify_counter_by_popularity(c: collections.Counter) -> str:
    """Given a counter, give a string summary in descending popularity."""
    return ", ".join(
        f"{v} {k}"
        for k, v in sorted(c.items(), reverse=True, key=operator.itemgetter(1))
    )


@dataclass(frozen=True)
class KillmailStats:
    kill_id: int
    timestamp: int
    victim_moniker: str
    victim_ship: str
    victim_ship_typeid: int
    final_blow_moniker: str
    top_damage_moniker: str
    attacker_entities_summary: str
    attacker_ships_summary: str
    isk_value: int
    solar_system_id: int
    solar_system_name: str

    def zkb_url(self) -> str:
        return f"https://zkillboard.com/kill/{self.kill_id}/"

    def victim_ship_thumb_url(self) -> str:
        return f"https://imageserver.eveonline.com/Render/{self.victim_ship_typeid}_128.png"

    def pretty_isk_value(self) -> str:
        return str(millify.millify(self.isk_value, precision=2))


async def stats_for_killmail(
    package: Dict[str, Any], universe: Universe
) -> Optional[KillmailStats]:

    try:
        victim_ship_typeid: int = int(
            package["killmail"]["victim"]["ship_type_id"]
        )
        solar_system_id: int = int(package["killmail"]["solar_system_id"])

        d = {
            "victim_moniker": char_name_with_ticker(
                package["killmail"]["victim"]
            ),
            "victim_ship": esi_util.type_details(victim_ship_typeid),
            "final_blow_moniker": char_name_with_ticker(
                next(
                    filter(
                        lambda x: x["final_blow"],
                        package["killmail"]["attackers"],
                    )
                )
            ),
            "top_damage_moniker": char_name_with_ticker(
                max(
                    package["killmail"]["attackers"],
                    key=lambda x: x["damage_done"],
                )
            ),
            "attacker_entities": gather(
                *[
                    entity_ticker_for_char(x)
                    for x in package["killmail"]["attackers"]
                ]
            ),
            "attacker_ships": gather(
                *[
                    (esi_util.type_details(x["ship_type_id"]))
                    for x in package["killmail"]["attackers"]
                ]
            ),
            "solar_system_name": universe.system_name(System(solar_system_id)),
        }

        d = await multi(d)

        d["victim_ship"] = d["victim_ship"]["name"]
        d["attacker_entities_summary"] = _stringify_counter_by_popularity(
            collections.Counter(d["attacker_entities"])
        )
        d["attacker_ships_summary"] = _stringify_counter_by_popularity(
            collections.Counter(
                map(operator.itemgetter("name"), d["attacker_ships"])
            )
        )

        d.pop("attacker_entities", None)
        d.pop("attacker_ships", None)

        d["timestamp"] = int(
            dateutil.parser.parse(
                package["killmail"]["killmail_time"]
            ).timestamp()
        )
        d["victim_ship_typeid"] = victim_ship_typeid
        d["kill_id"] = package["killID"]
        d["isk_value"] = package["zkb"]["totalValue"]
        d["solar_system_id"] = solar_system_id

        return KillmailStats(**d)
    except Exception as e:
        log.exception(e)

    return None


async def _slack_payload_for_killmail(
    notifier: Dict[str, Any], package: Dict[str, Any], universe: Universe
) -> Optional[Dict[str, Any]]:

    stats = await stats_for_killmail(package, universe)

    if not stats:
        log.warn("_slack_payload_for_killmail: failed to aquire stats")
        return None

    text = f"{stats.victim_moniker} lost a {stats.victim_ship} "
    text += f"worth {stats.pretty_isk_value()} ISK "
    text += f"\nin *{stats.solar_system_name}* "

    rv = {
        "attachments": [
            {
                "fallback": text,
                "text": text,
                "footer": stats.zkb_url(),
                "footer_icon": "https://zkillboard.com/img/wreck.png",
                "ts": stats.timestamp,
                "thumb_url": stats.victim_ship_thumb_url(),
                "fields": [
                    {
                        "short": True,
                        "title": "The attackers",
                        "value": stats.attacker_entities_summary,
                    },
                    {
                        "short": True,
                        "title": "were flying",
                        "value": stats.attacker_ships_summary,
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
                {
                    "short": True,
                    "title": "Final blow",
                    "value": stats.final_blow_moniker,
                },
                {
                    "short": True,
                    "title": "Top damage",
                    "value": stats.top_damage_moniker,
                },
            ]
        )

    return rv
async def _discord_payload_for_killmail(
    notifier: Dict[str, Any], package: Dict[str, Any], universe: Universe
) -> Optional[Dict[str, Any]]:

    stats = await stats_for_killmail(package, universe)

    if not stats:
        log.warn("_discord_payload_for_killmail: failed to aquire stats")
        return None

    text = f"{stats.victim_moniker} lost a {stats.victim_ship} "
    text += f"worth {stats.pretty_isk_value()} ISK "
    text += f"\nin *{stats.solar_system_name}* "

    rv = {
        "embeds": [
            {
                "title": text,
                "description": "[zKill]("+stats.zkb_url()+")",
                "color": 7471618,
                "thumbnail": {
                  "url": stats.victim_ship_thumb_url(),
                             },
                "footer": {
                   "icon_url": "https://zkillboard.com/img/wreck.png",
                   "text": stats.zkb_url(),
                          },
                "fields": [
                    {
                        "inline": True,
                        "name": "The attackers",
                        "value": stats.attacker_entities_summary,
                    },
                    {
                        "inline": True,
                        "name": "were flying",
                        "value": stats.attacker_ships_summary,
                    },

                ],

            }
        ]
    }



    return rv

payload_for_killmail: Dict[str, Callable] = {
    "slack": _slack_payload_for_killmail,
    "discord": _discord_payload_for_killmail
}
