import aiounittest

from kaart_killbot import universe as kaart_killbot_universe
from kaart_killbot import exception as kaart_killbot_exception


class UniverseTest(aiounittest.AsyncTestCase):
    async def test_universe_connection_add(self) -> None:
        universe = kaart_killbot_universe.Universe.from_empty()

        state = kaart_killbot_universe.State()

        system1 = kaart_killbot_universe.System(1)
        system2 = kaart_killbot_universe.System(2)

        conn1 = kaart_killbot_universe.Connection(system1, system2, state)

        await universe.add_connection(conn1)

        self.assertEqual(len(universe.systems), 2)

        system3 = kaart_killbot_universe.System(3)

        conn2 = kaart_killbot_universe.Connection(system1, system3, state)

        await universe.add_connection(conn2)

        self.assertEqual(len(universe.systems), 3)

    async def test_universe_double_connection_add(self) -> None:
        universe = kaart_killbot_universe.Universe.from_empty()

        state = kaart_killbot_universe.State()

        system1 = kaart_killbot_universe.System(1)
        system2 = kaart_killbot_universe.System(2)

        conn1 = kaart_killbot_universe.Connection(system1, system2, state)
        conn2 = kaart_killbot_universe.Connection(system1, system2, state)

        with self.assertRaises(kaart_killbot_exception.ConnectionDuplicate):
            await universe.add_connection(conn1)
            await universe.add_connection(conn2)

        self.assertEqual(len(universe.systems), 2)

    async def test_delta(self) -> None:
        universe1 = kaart_killbot_universe.Universe.from_empty()
        universe2 = kaart_killbot_universe.Universe.from_empty()

        state = kaart_killbot_universe.State()

        system1 = kaart_killbot_universe.System(1)
        system2 = kaart_killbot_universe.System(2)
        system3 = kaart_killbot_universe.System(3)

        conn1 = kaart_killbot_universe.Connection(system1, system2, state)
        conn2 = kaart_killbot_universe.Connection(system1, system3, state)
        conn3 = kaart_killbot_universe.Connection(system2, system3, state)

        await universe1.add_connection(conn1)
        await universe1.add_connection(conn2)
        await universe1.add_connection(conn3)

        self.assertEqual(len(universe1.systems), 3)

        delta1 = kaart_killbot_universe.Delta.from_universes(
            universe1, universe2
        )

        self.assertEquals(len(delta1.connections_add), 0)
        self.assertEquals(len(delta1.connections_del), 3)

        delta2 = kaart_killbot_universe.Delta.from_universes(
            universe2, universe1
        )

        self.assertEquals(len(delta2.connections_add), 3)
        self.assertEquals(len(delta2.connections_del), 0)

    async def test_universe_update_with(self) -> None:
        universe1 = kaart_killbot_universe.Universe.from_empty()
        universe2 = kaart_killbot_universe.Universe.from_empty()

        state = kaart_killbot_universe.State()

        system1 = kaart_killbot_universe.System(1)
        system2 = kaart_killbot_universe.System(2)
        system3 = kaart_killbot_universe.System(3)

        conn1 = kaart_killbot_universe.Connection(system1, system2, state)
        conn2 = kaart_killbot_universe.Connection(system1, system3, state)
        conn3 = kaart_killbot_universe.Connection(system2, system3, state)

        await universe1.add_connection(conn1)
        await universe1.add_connection(conn2)
        await universe1.add_connection(conn3)

        self.assertEqual(len(universe1.systems), 3)
        self.assertEqual(len(universe2.systems), 0)

        await universe2.update_with(universe1)

        self.assertEqual(len(universe1.systems), 3)
        self.assertEqual(len(universe2.systems), 3)
