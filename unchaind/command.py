"""The command you can actually run from your command line."""

import re

from asyncio import gather
from typing import List, Dict, Any

from tornado import ioloop

from unchaind.mapper.siggy import Map as SiggyMap

from unchaind.universe import Universe, System
from unchaind.kills import loop_zkillboard
from unchaind.util import get_mapper, get_transport, system_name
from unchaind.log import app_log, setup_log

from unchaind import config


async def universe_cleanup(universe: Universe) -> Universe:
    """Clean up a universe instance according to some filters to remove
       connections to systems that are used by corps to `pin to map`."""

    # First we delete all connections where one of these goes towards a
    # filtered destination
    await gather(
        *[
            universe.del_connection(universe.connections[c])
            for c in universe.connections
            if any(s.identifier == 30_000_362 for s in c)
        ]
    )

    return universe


async def killmail_cleanup(killmail: Dict[str, Any]) -> bool:
    """Filter any killmail that has a character from our corp on it. Return
       true when the killmail has to be filtered."""

    victim = killmail.get("victim", {})

    if victim.get("alliance_id", None) == 99_005_065:
        app_log().debug("Filtered kill; victim in alliance")
        return True

    solar_system_id = killmail.get("solar_system_id", None)

    if solar_system_id:
        solar_system = System(solar_system_id)
        solar_system_name = await system_name(solar_system)
        if not re.match(r"J\d{6}", solar_system_name):
            app_log().debug("Filtered kill; not in w-space")
            return True

    attackers = killmail.get("attackers", [])
    attackers = any(a.get("alliance_id", None) == 99_005_065 for a in attackers)

    if attackers:
        app_log().debug("Filtered kill; no attackers in alliance")

    return bool(attackers)


class Command:
    """The running command that wraps everything to read configuration and
       setup all the mappers."""

    universe: Universe
    mappers: List[SiggyMap]

    def __init__(self) -> None:
        self.universe = Universe.from_empty()
        self.mappers = []

    async def initialize(self) -> None:
        """Start by initializing all our mappers and setting them up with
           their login credentials."""

        app_log().info(
            "Starting `unchaind` with {} mappers.".format(
                len(config.mappers)
            )
        )

        for mapper in config.mappers:
            transport = await get_transport(mapper["type"]).from_credentials(
                **mapper["credentials"]
            )
            mapper = get_mapper(mapper["type"])(transport)
            self.mappers.append(mapper)

        app_log().info("Mappers initialized, starting initial pass.")

        # Run our initial pass to get all the results without firing their
        # callbacks since we're booting
        await self.periodic_mappers(init=False)

        app_log().info(
            "Initial finished, got {} systems and {} connections.".format(
                len(self.universe.systems), len(self.universe.connections)
            )
        )

        # We can keep calling our periodic mappers now
        poll_mappers: ioloop.PeriodicCallback = ioloop.PeriodicCallback(
            self.periodic_mappers, 5000
        )
        poll_mappers.start()

    async def periodic_mappers(self, init: bool = True) -> None:
        """Run all of our mappers periodically."""

        app_log().debug("periodic_mappers running")

        results = await gather(
            *[mapper.update() for mapper in self.mappers],
            return_exceptions=True,
        )

        results = tuple(
            result for result in results if not isinstance(result, Exception)
        )

        # We use a full filter over the universes returned from the mappers as
        # many groups use certain systems that make the maps filled with
        # non-existent connections
        results = await gather(
            *[universe_cleanup(result) for result in results]
        )

        await gather(
            *[
                self.universe.update_with(result, init=init)
                for result in results
            ]
        )

        app_log().debug(
            "periodic_mappers finished, got {} sys and {} conn.".format(
                len(self.universe.systems), len(self.universe.connections)
            )
        )

    async def loop_kills(self) -> None:
        """Call loop for our killboard provider with our current Universe. The
           killboard provider matches kills to systems in the Universe and can
           notify channels if anything happens."""

        while True:
            app_log().debug("loop_kills running")
            await loop_zkillboard(self.universe, callback=killmail_cleanup)


def main() -> None:
    """Run our main application."""

    # Setup some logging shenanigans; our exception handler and our default
    # log setup
    setup_log()

    command = Command()

    loop: ioloop.IOLoop = ioloop.IOLoop.current()
    loop.add_callback(command.initialize)
    loop.add_callback(command.loop_kills)

    loop.start()


if __name__ == "__main__":
    main()
