import logging

from typing import Dict, Any

from unchaind.universe import Universe, Delta


log = logging.getLogger(__name__)

# Our own universe which is umpdated every now and then
_universe: Universe = Universe.from_empty_sync()


async def periodic(config: Dict[str, Any], universe: Universe) -> None:
    """Periodically compare a given universe with our version of it after which
       we update our version to the newest. This allows us to see differences
       between the two and act accordingly."""

    if len(_universe.systems) == 0:
        log.debug("periodic: universe is empty, skip")
    else:
        delta = Delta.from_universes(_universe, universe)

        # Then let's see if there's any new connection
        for connection in delta.connections_add:
            log.info("periodic: new connection found %r", connection)

            # Let's see if the connection matches anything
            # XXX same filtering as killmail really...

    # Now that we've processed the new connections we can update *our*
    # univesre
    await _universe.update_with(universe)
