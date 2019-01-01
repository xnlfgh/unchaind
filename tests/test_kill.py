import unittest
import asyncio

from unchaind import universe as unchaind_universe
from unchaind import kills as unchaind_kills

loop = asyncio.get_event_loop()


class NotifierKillTest(unittest.TestCase):
    def test__filter_alliance_no_matches(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"alliance_id": 2},
                "attackers": [{"alliance_id": 2}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_alliance([1], package, universe)
            ),
            True,
        )

    def test__filter_alliance_victim_match(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"alliance_id": 1},
                "attackers": [{"alliance_id": 2}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_alliance([1], package, universe)
            ),
            False,
        )

    def test__filter_alliance_attacker_match(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"alliance_id": 2},
                "attackers": [{"alliance_id": 1}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_alliance([1], package, universe)
            ),
            False,
        )

    def test__filter_alliance_kill_no_matches(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"alliance_id": 2},
                "attackers": [{"alliance_id": 2}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_alliance_kill([1], package, universe)
            ),
            True,
        )

    def test__filter_alliance_kill_victim_match(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"alliance_id": 1},
                "attackers": [{"alliance_id": 1234}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_alliance_kill([1], package, universe)
            ),
            True,
        )

    def test__filter_alliance_kill_attacker_match(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"alliance_id": 2},
                "attackers": [{"alliance_id": 1}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_alliance_kill([1], package, universe)
            ),
            False,
        )

    def test__filter_alliance_loss_no_matches(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"alliance_id": 2},
                "attackers": [{"alliance_id": 2}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_alliance_loss([1], package, universe)
            ),
            True,
        )

    def test__filter_alliance_loss_victim_match(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"alliance_id": 1},
                "attackers": [{"alliance_id": 1234}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_alliance_loss([1], package, universe)
            ),
            False,
        )

    def test__filter_alliance_loss_attacker_match(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"alliance_id": 2},
                "attackers": [{"alliance_id": 1}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_alliance_loss([1], package, universe)
            ),
            True,
        )

    def test__filter_corporation_no_matches(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"corporation_id": 2},
                "attackers": [{"corporation_id": 2}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_corporation([1], package, universe)
            ),
            True,
        )

    def test__filter_corporation_victim_match(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"corporation_id": 1},
                "attackers": [{"corporation_id": 2}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_corporation([1], package, universe)
            ),
            False,
        )

    def test__filter_corporation_attacker_match(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"corporation_id": 2},
                "attackers": [{"corporation_id": 1}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_corporation([1], package, universe)
            ),
            False,
        )

    def test__filter_corporation_kill_no_matches(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"corporation_id": 2},
                "attackers": [{"corporation_id": 2}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_corporation_kill([1], package, universe)
            ),
            True,
        )

    def test__filter_corporation_kill_victim_match(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"corporation_id": 1},
                "attackers": [{"corporation_id": 1234}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_corporation_kill([1], package, universe)
            ),
            True,
        )

    def test__filter_corporation_kill_attacker_match(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"corporation_id": 2},
                "attackers": [{"corporation_id": 1}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_corporation_kill([1], package, universe)
            ),
            False,
        )

    def test__filter_corporation_loss_no_matches(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"corporation_id": 2},
                "attackers": [{"corporation_id": 2}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_corporation_loss([1], package, universe)
            ),
            True,
        )

    def test__filter_corporation_loss_victim_match(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"corporation_id": 1},
                "attackers": [{"corporation_id": 1234}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_corporation_loss([1], package, universe)
            ),
            False,
        )

    def test__filter_corporation_loss_attacker_match(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"corporation_id": 2},
                "attackers": [{"corporation_id": 1}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_corporation_loss([1], package, universe)
            ),
            True,
        )

    def test__filter_character_no_matches(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"character_id": 2},
                "attackers": [{"character_id": 2}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_character([1], package, universe)
            ),
            True,
        )

    def test__filter_character_victim_match(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"character_id": 1},
                "attackers": [{"character_id": 2}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_character([1], package, universe)
            ),
            False,
        )

    def test__filter_character_attacker_match(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"character_id": 2},
                "attackers": [{"character_id": 1}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_character([1], package, universe)
            ),
            False,
        )

    def test__filter_character_kill_no_matches(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"character_id": 2},
                "attackers": [{"character_id": 2}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_character_kill([1], package, universe)
            ),
            True,
        )

    def test__filter_character_kill_victim_match(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"character_id": 1},
                "attackers": [{"character_id": 1234}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_character_kill([1], package, universe)
            ),
            True,
        )

    def test__filter_character_kill_attacker_match(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"character_id": 2},
                "attackers": [{"character_id": 1}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_character_kill([1], package, universe)
            ),
            False,
        )

    def test__filter_character_loss_no_matches(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"character_id": 2},
                "attackers": [{"character_id": 2}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_character_loss([1], package, universe)
            ),
            True,
        )

    def test__filter_character_loss_victim_match(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"character_id": 1},
                "attackers": [{"character_id": 1234}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_character_loss([1], package, universe)
            ),
            False,
        )

    def test__filter_character_loss_attacker_match(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"character_id": 2},
                "attackers": [{"character_id": 1}],
            }
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_character_loss([1], package, universe)
            ),
            True,
        )

    def test__filter_minimum_value_no_match(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"character_id": 2},
                "attackers": [{"character_id": 1}],
            },
            "zkb": {"totalValue": 999_999.99},
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_minimum_value(
                    [1_000_000], package, universe
                )
            ),
            True,
        )

    def test__filter_minimum_value_match(self) -> None:
        universe = unchaind_universe.Universe.from_empty()

        package = {
            "killmail": {
                "killmail_id": 1,
                "victim": {"character_id": 2},
                "attackers": [{"character_id": 1}],
            },
            "zkb": {"totalValue": 999_999.99},
        }

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kills._filter_minimum_value(
                    [100_000], package, universe
                )
            ),
            False,
        )
