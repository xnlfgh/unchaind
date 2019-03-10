import logging

from typing import Dict, Any

from unchaind.universe import Universe, Delta, Multiverse


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

        # Then let's see if there's any new connection
        for connection in delta.connections_add:
            log.info("periodic: new connection found %r", connection)

            # Let's see if the connection matches anything
            # XXX same filtering as killmail really...

    # Now that we've processed the new connections we can update *our*
    # univesre
    await _universe.update_with(multiverse)
