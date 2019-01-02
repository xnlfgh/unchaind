import unittest
import asyncio

from unchaind import universe as unchaind_universe
from unchaind import path as unchaind_path

loop = asyncio.get_event_loop()


class UniverseTest(unittest.TestCase):
    def test_path__path__straight_path(self) -> None:
        universe1 = loop.run_until_complete(
            unchaind_universe.Universe.from_eve()
        )
        universe2 = loop.run_until_complete(
            unchaind_universe.Universe.from_empty()
        )

        multiverse1 = loop.run_until_complete(
            unchaind_universe.Multiverse.from_universes(universe1, universe2)
        )

        path1 = unchaind_path.path(
            unchaind_universe.System(30_002_187),
            unchaind_universe.System(30_000_142),
            multiverse1,
        )

        if path1 is None:
            raise AssertionError

        self.assertEqual(len(path1.path), 9)

    def test_path__path__wormhole_path(self) -> None:
        universe1 = loop.run_until_complete(
            unchaind_universe.Universe.from_eve()
        )
        universe2 = loop.run_until_complete(
            unchaind_universe.Universe.from_empty()
        )

        state1 = unchaind_universe.State()
        conn1 = unchaind_universe.Connection(
            unchaind_universe.System(30_002_187),
            unchaind_universe.System(30_000_142),
            state1,
        )

        loop.run_until_complete(universe2.connect(conn1))

        multiverse1 = loop.run_until_complete(
            unchaind_universe.Multiverse.from_universes(universe1, universe2)
        )

        path1 = unchaind_path.path(
            unchaind_universe.System(30_002_187),
            unchaind_universe.System(30_000_142),
            multiverse1,
        )

        if path1 is None:
            raise AssertionError

        self.assertEqual(len(path1.path), 1)
