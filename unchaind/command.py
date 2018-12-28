"""The command you can actually run from your command line."""
import logging

from asyncio import gather
from typing import List, Dict, Any, Optional

import click

from tornado import ioloop

from unchaind.mapper.siggy import Map as SiggyMap

from unchaind.universe import Universe
from unchaind.kills import loop as loop_kills
from unchaind.util import get_mapper, get_transport
from unchaind.log import app_log, setup_log
from unchaind.config import parse_config


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


class Command:
    """The running command that wraps everything to read configuration and
       setup all the mappers."""

    universe: Universe
    mappers: List[SiggyMap]

    def __init__(self, config: Dict[str, Any]) -> None:
        self.universe = Universe.from_empty()
        self.mappers = []
        self.config = config

    async def initialize(self) -> None:
        """Start by initializing all our mappers and setting them up with
           their login credentials."""

        if len(self.config["mappers"]):
            app_log().info(
                "`unchaind` with {} mappers.".format(
                    len(self.config["mappers"])
                )
            )

            for mapper in self.config["mappers"]:
                transport = await get_transport(mapper["type"]).from_config(
                    mapper["credentials"]
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

        # Check if any notifiers subscribe to kills
        if len(
            [
                n
                for n in self.config["notifiers"]
                if n["subscribes_to"] == "kill"
            ]
        ):
            app_log().info(
                "`unchaind` with {} notifiers[kill].".format(
                    len(
                        [
                            n
                            for n in self.config["notifiers"]
                            if n["subscribes_to"] == "kill"
                        ]
                    )
                )
            )

            loop: ioloop.IOLoop = ioloop.IOLoop.current()
            loop.add_callback(self.loop_kills)
        else:
            app_log().warning("Did not find any notifiers subscribed to kills")

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
    help="Logfile to log to. Normally `unchaind` logs to stdout.",
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
