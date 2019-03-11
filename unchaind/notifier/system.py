import logging

from typing import Dict, Any, List, Callable
from asyncio import gather

from unchaind.util.connection import payload_for_connection
from unchaind.universe import Universe, Delta, Multiverse, Connection
from unchaind.sink import sinks


log = logging.getLogger(__name__)

# Our own universe which is umpdated every now and then
_universe: Universe = Universe.from_empty_sync()


async def periodic(
    config: Dict[str, Any], universes: Dict[str, Universe]
) -> None:
    """Periodically compare our snapshot of the universe with all the universes
       in existence. Find deltas for new systems found."""

    multiverse = await Multiverse.from_universes(*universes.values())

    if len(_universe.systems) == 0:
        log.debug("periodic: universe is empty, fill")
    else:
        delta = Delta.from_universes(_universe, multiverse)

        for connection in delta.connections_del:
            log.info("periodic: connection deleted %r", connection)

        # Then let's see if there's any new connection
        for connection in delta.connections_add:
            log.info("periodic: new connection found %r", connection)
            matches = await match_connection(config, multiverse, connection)

            if not matches:
                log.debug(f"periodic: no matches for %r", connection)
                return

            message = f"New connection found {connection}"

            await gather(
                *[
                    sinks[match["type"]](
                        match,
                        message,
                        payload=await payload_for_connection[match["type"]](
                            match, connection, multiverse
                        )
                        if match["type"] in payload_for_connection
                        else None,
                    )
                    for match in matches
                ]
            )

    # Now that we've processed the new connections we can update *our*
    # univesre
    await _universe.update_with(multiverse)


async def match_connection(
    config: Dict[str, Any], universe: Universe, connection: Connection
) -> List[Dict[str, Any]]:

    """Filter a connection with its set of notifier filters. Returns the notifier
       if there's a match for it."""

    matches = []

    # Now let's see if any system notifiers' filters match
    for index, notifier in enumerate(config["notifier"]):
        log.debug(
            "considering connection id %s for notifier %s", connection, index
        )

        if notifier["subscribes_to"] != "system":
            log.debug(
                "notifier %s does not subscribe to systems; skipping", index
            )
            continue

        async def apply_matchers(section: str) -> List[bool]:
            rv = []
            for d in notifier.get("filter", {}).get(section, []):
                for name, value in d.items():
                    filter_result = await matchers[name](
                        value, connection, universe
                    )
                    rv.append(filter_result)
            return rv

        sections: Dict[str, Callable[..., bool]] = {
            "require_all_of": all,
            "require_any_of": any,
            "exclude_if_any": lambda x: not any(x),
            "exclude_if_all": lambda x: not all(x),
        }

        rv = True

        for section, aggregator in sections.items():
            section_results = await apply_matchers(section)
            rv = rv and (
                len(section_results) == 0 or aggregator(section_results)
            )

        if rv:
            log.debug("notifier %s system %s: it's a match!", index, connection)
            matches.append(notifier)
        else:
            log.debug("notifier %s system %s: filtered away", index, connection)

    return matches


async def _match_location(
    value: str, connection: Connection, universe: Universe
) -> bool:
    return False


matchers: Dict[str, Any] = {"location": _match_location}
