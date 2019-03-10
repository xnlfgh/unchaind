"""The command you can actually run from your command line."""
import logging

from asyncio import gather
from typing import Dict, Any, Optional, Union

import click
import functools

from tornado import ioloop

from unchaind.mapper.siggy import Map as SiggyMapper
from unchaind.mapper.evescout import Map as EVEScoutMapper

from unchaind.universe import Universe, State, Connection, System
from unchaind.notifier.kill import loop as loop_kills
from unchaind.notifier.kill import process_one_killmail as oneshot_kill
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

    universes: Dict[str, Universe]
    mappers: Dict[str, Union[SiggyMapper, EVEScoutMapper]]

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    async def _initialize(self) -> None:
        """Configures initial universe, loads mappers and runs one iteration,
        does not start any periodic callbacks or loops.

        Prereq of daemon() and killmail_oneshot()."""
        self.universes = {}
        self.mappers = {}

        # Path is a custom universe where users can add jumpbridges or other
        # custom connections. If it is in use we create a universe for it and
        # add all custom connections.
        if "path" in self.config and len(self.config["path"]):
            self.universes["_path"] = await Universe.from_empty()

            for path in self.config["path"]:
                state = State()
                setattr(state, path["type"], True)

                left = System(path["from"])
                right = System(path["to"])

                connection = Connection(left, right, state)

                await self.universes["_path"].connect(connection)

        if "mapper" in self.config and len(self.config["mapper"]):
            log.info(
                "initialize: `unchaind` with {} mappers.".format(
                    len(self.config["mapper"])
                )
            )

            for index, mapper in enumerate(self.config["mapper"]):
                mapper.update({"home_system": self.config.get("home_system")})

                transport = await get_transport(mapper["type"]).from_config(
                    mapper
                )

                if transport is None:
                    log.warn(
                        "initialize: failed to create %s mapper", mapper["type"]
                    )
                else:
                    # The transport has been created, we can now create a name
                    # and universe for this mapper.
                    self.universes[
                        f"_{mapper['type']}_{index}"
                    ] = await Universe.from_empty()
                    self.mappers[f"_{mapper['type']}_{index}"] = get_mapper(
                        mapper["type"]
                    )(transport)

            log.info(
                "initialize: %d mappers initialized, starting initial pass.",
                len(self.mappers),
            )

            # Run our initial pass to get all the results without firing their
            # callbacks since we're booting
            await self.periodic_mappers()

            # XXX
            # log.info(
            #    "initialize: mappers finished, got {} systems and {} connections.".format(
            #        len(self.universe.systems), len(self.universe.connections)
            #    )
            # )

    async def killmail_oneshot(self, killmail_str: str) -> None:
        """Given a string of zkb JSON data, performs one run of the mappers
        to load up our Universe, then runs kill notifiers/matchers as configured.
        Intended for debugging/testing/development."""
        await self._initialize()
        await oneshot_kill(killmail_str, self.config, self.universes)

    async def daemon(self) -> None:
        """Long-running loop that periodically runs all configured mappers,
        subscribers, and notifiers."""
        await self._initialize()

        loop: ioloop.IOLoop = ioloop.IOLoop.current()

        if self.mappers:
            poll_mappers: ioloop.PeriodicCallback = ioloop.PeriodicCallback(
                self.periodic_mappers, 5000
            )
            poll_mappers.start()

        # XXX this is all very ugly!
        # Check if any notifiers subscribe to kills
        if "notifier" in self.config and len(
            [n for n in self.config["notifier"] if n["subscribes_to"] == "kill"]
        ):
            log.info(
                "daemon: `unchaind` with {} notifier[kill].".format(
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
            log.warning("daemon: did not find any notifier subscribed to kills")

        # Check if any notifiers subscribe to systems
        if "notifier" in self.config and len(
            [
                n
                for n in self.config["notifier"]
                if n["subscribes_to"] == "system"
            ]
        ):
            log.info(
                "daemon: `unchaind` with {} notifier[system].".format(
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
                "daemon: did not find any notifier subscribed to systems"
            )

    async def periodic_mappers(self, init: bool = True) -> None:
        """Run all of our mappers periodically. This means we call .update on
           the mapper instances and update their related universes."""

        log.debug("periodic_mappers: running")

        for name, mapper in self.mappers.items():
            universe = await mapper.update()
            await self.universes[name].update_with(universe)

        log.debug("periodic_mappers: done")

    async def periodic_systems(self) -> None:
        """Call loop for our systems with our current Universes."""
        log.debug("periodic_systems: running")
        await periodic_systems(self.config, self.universes)
        log.debug("periodic_systems: done")

    async def loop_kills(self) -> None:
        """Call loop for our killboard provider with our current Universe. The
           killboard provider matches kills to systems in the Universe and can
           notify channels if anything happens."""

        while True:
            log.debug("loop_kills: running")
            await loop_kills(self.config, self.universes)


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
@click.option(
    "--oneshot-killmail-file",
    type=click.Path(exists=True),
    help="If true, instead of starting the daemon loop, run a single iteration for a given file containing killmail JSON.",
)
def main(
    config: str,
    verbosity: int,
    log_file: Optional[str],
    oneshot_killmail_file: Optional[str],
) -> None:
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

    if oneshot_killmail_file is not None:
        with open(oneshot_killmail_file) as f:
            loop.run_sync(functools.partial(command.killmail_oneshot, f.read()))
            return

    loop.add_callback(command.daemon)

    loop.start()


if __name__ == "__main__":
    main()
