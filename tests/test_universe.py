import aiounittest

from unchaind import universe as unchaind_universe
from unchaind import exception as unchaind_exception


class UniverseTest(aiounittest.AsyncTestCase):
    async def test_universe_connection_add(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        state = unchaind_universe.State()

        system1 = unchaind_universe.System(1)
        system2 = unchaind_universe.System(2)

        conn1 = unchaind_universe.Connection(system1, system2, state)

        await universe.add_connection(conn1)

        self.assertEqual(len(universe.systems), 2)

        system3 = unchaind_universe.System(3)

        conn2 = unchaind_universe.Connection(system1, system3, state)

        await universe.add_connection(conn2)

        self.assertEqual(len(universe.systems), 3)

    async def test_universe_double_connection_add(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        state = unchaind_universe.State()

        system1 = unchaind_universe.System(1)
        system2 = unchaind_universe.System(2)

        conn1 = unchaind_universe.Connection(system1, system2, state)
        conn2 = unchaind_universe.Connection(system1, system2, state)

        with self.assertRaises(unchaind_exception.ConnectionDuplicate):
            await universe.add_connection(conn1)
            await universe.add_connection(conn2)

        self.assertEqual(len(universe.systems), 2)

    async def test_delta(self) -> None:
        universe1 = unchaind_universe.Universe.from_empty()
        universe2 = unchaind_universe.Universe.from_empty()

        state = unchaind_universe.State()

        system1 = unchaind_universe.System(1)
        system2 = unchaind_universe.System(2)
        system3 = unchaind_universe.System(3)

        conn1 = unchaind_universe.Connection(system1, system2, state)
        conn2 = unchaind_universe.Connection(system1, system3, state)
        conn3 = unchaind_universe.Connection(system2, system3, state)

        await universe1.add_connection(conn1)
        await universe1.add_connection(conn2)
        await universe1.add_connection(conn3)

        self.assertEqual(len(universe1.systems), 3)

        delta1 = unchaind_universe.Delta.from_universes(
            universe1, universe2
        )

        self.assertEquals(len(delta1.connections_add), 0)
        self.assertEquals(len(delta1.connections_del), 3)

        delta2 = unchaind_universe.Delta.from_universes(
            universe2, universe1
        )

        self.assertEquals(len(delta2.connections_add), 3)
        self.assertEquals(len(delta2.connections_del), 0)

    async def test_universe_update_with(self) -> None:
        universe1 = unchaind_universe.Universe.from_empty()
        universe2 = unchaind_universe.Universe.from_empty()

        state = unchaind_universe.State()

        system1 = unchaind_universe.System(1)
        system2 = unchaind_universe.System(2)
        system3 = unchaind_universe.System(3)

        conn1 = unchaind_universe.Connection(system1, system2, state)
        conn2 = unchaind_universe.Connection(system1, system3, state)
        conn3 = unchaind_universe.Connection(system2, system3, state)

        await universe1.add_connection(conn1)
        await universe1.add_connection(conn2)
        await universe1.add_connection(conn3)

        self.assertEqual(len(universe1.systems), 3)
        self.assertEqual(len(universe2.systems), 0)

        await universe2.update_with(universe1)

        self.assertEqual(len(universe1.systems), 3)
        self.assertEqual(len(universe2.systems), 3)
