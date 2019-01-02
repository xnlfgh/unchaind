import unittest
import asyncio

from unchaind import universe as unchaind_universe
from unchaind import exception as unchaind_exception

loop = asyncio.get_event_loop()


class UniverseTest(unittest.TestCase):
    def test_universe_connection_add(self) -> None:
        universe = loop.run_until_complete(
            unchaind_universe.Universe.from_empty()
        )

        state = unchaind_universe.State()

        system1 = unchaind_universe.System(30_000_492)
        system2 = unchaind_universe.System(30_000_493)

        conn1 = unchaind_universe.Connection(system1, system2, state)

        loop.run_until_complete(universe.connect(conn1))

        self.assertEqual(len(universe.systems), 2)

        system3 = unchaind_universe.System(30_000_494)

        conn2 = unchaind_universe.Connection(system1, system3, state)

        loop.run_until_complete(universe.connect(conn2))

        self.assertEqual(len(universe.systems), 3)

    def test_universe_double_connection_add(self) -> None:
        universe = loop.run_until_complete(
            unchaind_universe.Universe.from_empty()
        )

        state = unchaind_universe.State()

        system1 = unchaind_universe.System(30_000_492)
        system2 = unchaind_universe.System(30_000_493)

        conn1 = unchaind_universe.Connection(system1, system2, state)
        conn2 = unchaind_universe.Connection(system1, system2, state)

        with self.assertRaises(unchaind_exception.ConnectionDuplicate):
            loop.run_until_complete(universe.connect(conn1))
            loop.run_until_complete(universe.connect(conn2))

        self.assertEqual(len(universe.systems), 2)

    def test_delta(self) -> None:
        universe1 = loop.run_until_complete(
            unchaind_universe.Universe.from_empty()
        )
        universe2 = loop.run_until_complete(
            unchaind_universe.Universe.from_empty()
        )

        state = unchaind_universe.State()

        system1 = unchaind_universe.System(30_000_492)
        system2 = unchaind_universe.System(30_000_493)
        system3 = unchaind_universe.System(30_000_494)

        conn1 = unchaind_universe.Connection(system1, system2, state)
        conn2 = unchaind_universe.Connection(system1, system3, state)
        conn3 = unchaind_universe.Connection(system2, system3, state)

        loop.run_until_complete(universe1.connect(conn1))
        loop.run_until_complete(universe1.connect(conn2))
        loop.run_until_complete(universe1.connect(conn3))

        self.assertEqual(len(universe1.systems), 3)

        delta1 = unchaind_universe.Delta.from_universes(universe1, universe2)

        self.assertEqual(len(delta1.connections_add), 0)
        self.assertEqual(len(delta1.connections_del), 3)

        delta2 = unchaind_universe.Delta.from_universes(universe2, universe1)

        self.assertEqual(len(delta2.connections_add), 3)
        self.assertEqual(len(delta2.connections_del), 0)

    def test_universe_update_with(self) -> None:
        universe1 = loop.run_until_complete(
            unchaind_universe.Universe.from_empty()
        )
        universe2 = loop.run_until_complete(
            unchaind_universe.Universe.from_empty()
        )

        state = unchaind_universe.State()

        system1 = unchaind_universe.System(30_000_492)
        system2 = unchaind_universe.System(30_000_493)
        system3 = unchaind_universe.System(30_000_494)

        conn1 = unchaind_universe.Connection(system1, system2, state)
        conn2 = unchaind_universe.Connection(system1, system3, state)
        conn3 = unchaind_universe.Connection(system2, system3, state)

        loop.run_until_complete(universe1.connect(conn1))
        loop.run_until_complete(universe1.connect(conn2))
        loop.run_until_complete(universe1.connect(conn3))

        self.assertEqual(len(universe1.systems), 3)
        self.assertEqual(len(universe2.systems), 0)

        loop.run_until_complete(universe2.update_with(universe1))

        self.assertEqual(len(universe1.systems), 3)
        self.assertEqual(len(universe2.systems), 3)

    def test_universe_system_name(self) -> None:
        system1 = unchaind_universe.System(30_000_492)

        self.assertEqual(system1.name, "O3-4MN")

        with self.assertRaises(KeyError):
            unchaind_universe.System(1)
