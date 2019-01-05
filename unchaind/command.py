"""The command you can actually run from your command line."""
import logging

from asyncio import gather
from typing import List, Dict, Any, Optional

import click

from tornado import ioloop

from unchaind.mapper.siggy import Map as SiggyMap

from unchaind.universe import Universe
from unchaind.notifier.kill import loop as loop_kills
from unchaind.notifier.system import periodic as periodic_systems
from unchaind.util import get_mapper, get_transport
from unchaind.log import setup_log
from unchaind.config import parse_config


log = logging.getLogger(__name__)


async def universe_cleanup(universe: Universe) -> Universe:
    """Clean up a universe instance according to some filters to remove
       connections to systems that are used by corps to `pin to map`."""

    # First we delete all connections where one of these goes towards a
    # filtered destination
    await gather(
        *[
            universe.disconnect(universe.connections[c])
            for c in universe.connections
            if any(s.identifier == 30_000_362 for s in c)
        ]
    )

    return universe


class Command:
    """The running command that wraps everything to read configuration and
       setup all the mappers."""

    universe: Universe
    mappers: List[SiggyMap]

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    async def initialize(self) -> None:
        """Start by initializing all our mappers and setting them up with
           their login credentials."""

        self.universe = await Universe.from_empty()
        self.mappers = []

        loop: ioloop.IOLoop = ioloop.IOLoop.current()

        # Check if any notifiers subscribe to kills
        if "notifier" in self.config and len(
            [n for n in self.config["notifier"] if n["subscribes_to"] == "kill"]
        ):
            log.info(
                "initialize: `unchaind` with {} notifier[kill].".format(
                    len(
                        [
                            n
                            for n in self.config["notifier"]
                            if n["subscribes_to"] == "kill"
                        ]
                    )
                )
            )

            loop.add_callback(self.loop_kills)
        else:
            log.warning(
                "initialize: did not find any notifier subscribed to kills"
            )

        # Check if any notifiers subscribe to systems
        if "notifier" in self.config and len(
            [
                n
                for n in self.config["notifier"]
                if n["subscribes_to"] == "system"
            ]
        ):
            log.info(
                "initialize: `unchaind` with {} notifier[system].".format(
                    len(
                        [
                            n
                            for n in self.config["notifier"]
                            if n["subscribes_to"] == "system"
                        ]
                    )
                )
            )

            poll_systems: ioloop.PeriodicCallback = ioloop.PeriodicCallback(
                self.periodic_systems, 5000
            )
            poll_systems.start()
        else:
            log.warning(
                "initialize: did not find any notifier subscribed to systems"
            )

        if "mapper" in self.config and len(self.config["mapper"]):
            log.info(
                "initialize: `unchaind` with {} mappers.".format(
                    len(self.config["mapper"])
                )
            )

            for mapper in self.config["mapper"]:
                transport = await get_transport(mapper["type"]).from_config(
                    mapper["credentials"]
                )
                mapper = get_mapper(mapper["type"])(transport)
                self.mappers.append(mapper)

            log.info("initialize: mappers initialized, starting initial pass.")

            # Run our initial pass to get all the results without firing their
            # callbacks since we're booting
            await self.periodic_mappers()

            log.info(
                "initialize: mappers finished, got {} systems and {} connections.".format(
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

        log.debug("periodic_mappers: running")

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

        await gather(*[self.universe.update_with(result) for result in results])

        log.debug(
            "periodic_mappers: finished, got {} sys and {} conn.".format(
                len(self.universe.systems), len(self.universe.connections)
            )
        )

    async def periodic_systems(self) -> None:
        """Call loop for our systems with our current Universe."""
        log.debug("periodic_systems: running")
        await periodic_systems(self.config, self.universe)

    async def loop_kills(self) -> None:
        """Call loop for our killboard provider with our current Universe. The
           killboard provider matches kills to systems in the Universe and can
           notify channels if anything happens."""

        while True:
            log.debug("loop_kills: running")
            await loop_kills(self.config, self.universe)


@click.command()
@click.option(
    "--config",
    "-c",
    required=True,
    type=click.Path(exists=True),
    help="Config file to use.",
)
@click.option(
    "--verbosity",
    "-v",
    count=True,
    help="Logging verbosity, passing more heightens the verbosity. ",
)
@click.option(
    "--log-file",
    "-l",
    type=click.Path(exists=False),
    help="Logfile to log to. Normally `unchaind` logs to stderr.",
)
def main(config: str, verbosity: int, log_file: Optional[str]) -> None:
    """This is the ``unchaind`` EVE online tool. It allows for interactivity
       between wormhole space and your Discord.

       Report issues at: https://github.com/supakeen/unchaind"""

    # Convert the verbose count to a number
    level = logging.CRITICAL - (verbosity * 10)

    # Setup some logging shenanigans; our exception handler and our default
    # log setup
    setup_log(level, log_file)

    # Parse configuration
    command = Command(config=parse_config(config))

    loop: ioloop.IOLoop = ioloop.IOLoop.current()
    loop.add_callback(command.initialize)

    loop.start()


if __name__ == "__main__":
    main()
