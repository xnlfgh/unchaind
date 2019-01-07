import unittest
import asyncio

from typing import Dict, Any

from unchaind import universe as unchaind_universe
from unchaind.notifier import kill as unchaind_kill

loop = asyncio.get_event_loop()


# Some conventions for the standard killmail:
# Attackers have 1s in their ids
# Victim has 2s
# No one has 9s
def standard_package() -> Dict[str, Any]:
    return {
        "killmail": {
            "killmail_id": 1,
            "solar_system_id": 30_002_187,  # Amarr
            "victim": {
                "alliance_id": 2,
                "corporation_id": 20,
                "character_id": 200,
            },
            "attackers": [
                {"alliance_id": 1, "corporation_id": 10, "character_id": 100},
                {"alliance_id": 1, "corporation_id": 11, "character_id": 101},
                {
                    "alliance_id": 1111,
                    "corporation_id": 111_110,
                    "character_id": 1_111_100,
                },
            ],
        },
        "zkb": {"totalValue": 999_999.99},
    }


def empty_universe() -> unchaind_universe.Universe:
    return loop.run_until_complete(unchaind_universe.Universe.from_empty())


class NotifierKillTest(unittest.TestCase):
    def test__match_alliance_no_matches(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_alliance(
                    123, standard_package(), empty_universe()
                )
            ),
            False,
        )

    def test__match_alliance_victim_match(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_alliance(
                    2, standard_package(), empty_universe()
                )
            ),
            True,
        )

    def test__match_alliance_attacker_match(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_alliance(
                    1, standard_package(), empty_universe()
                )
            ),
            True,
        )

    def test__match_alliance_kill_no_matches(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_alliance_kill(
                    2, standard_package(), empty_universe()
                )
            ),
            False,
        )

    def test__match_alliance_kill_victim_match(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_alliance_kill(
                    1, standard_package(), empty_universe()
                )
            ),
            True,
        )

    def test__match_alliance_kill_attacker_match(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_alliance_kill(
                    1, standard_package(), empty_universe()
                )
            ),
            True,
        )

    def test__match_alliance_loss_no_matches(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_alliance_loss(
                    999, standard_package(), empty_universe()
                )
            ),
            False,
        )

    def test__match_alliance_loss_victim_match(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_alliance_loss(
                    2, standard_package(), empty_universe()
                )
            ),
            True,
        )

    def test__match_alliance_loss_attacker_match(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_alliance_loss(
                    1, standard_package(), empty_universe()
                )
            ),
            False,
        )

    def test__match_corporation_no_matches(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_corporation(
                    999, standard_package(), empty_universe()
                )
            ),
            False,
        )

    def test__match_corporation_victim_match(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_corporation(
                    20, standard_package(), empty_universe()
                )
            ),
            True,
        )

    def test__match_corporation_attacker_match(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_corporation(
                    10, standard_package(), empty_universe()
                )
            ),
            True,
        )

    def test__match_corporation_kill_no_matches(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_corporation_kill(
                    999, standard_package(), empty_universe()
                )
            ),
            False,
        )

    def test__match_corporation_kill_victim_match(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_corporation_kill(
                    20, standard_package(), empty_universe()
                )
            ),
            False,
        )

    def test__match_corporation_kill_attacker_match(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_corporation_kill(
                    10, standard_package(), empty_universe()
                )
            ),
            True,
        )
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_corporation_kill(
                    11, standard_package(), empty_universe()
                )
            ),
            True,
        )

    def test__match_corporation_loss_no_matches(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_corporation_loss(
                    999, standard_package(), empty_universe()
                )
            ),
            False,
        )

    def test__match_corporation_loss_victim_match(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_corporation_loss(
                    20, standard_package(), empty_universe()
                )
            ),
            True,
        )

    def test__match_corporation_loss_attacker_match(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_corporation_loss(
                    10, standard_package(), empty_universe()
                )
            ),
            False,
        )

    def test__match_character_no_matches(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_character(
                    999, standard_package(), empty_universe()
                )
            ),
            False,
        )

    def test__match_character_victim_match(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_character(
                    200, standard_package(), empty_universe()
                )
            ),
            True,
        )

    def test__match_character_attacker_match(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_character(
                    100, standard_package(), empty_universe()
                )
            ),
            True,
        )

    def test__match_character_kill_no_matches(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_character_kill(
                    999, standard_package(), empty_universe()
                )
            ),
            False,
        )

    def test__match_character_kill_victim_match(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_character_kill(
                    200, standard_package(), empty_universe()
                )
            ),
            False,
        )

    def test__match_character_kill_attacker_match(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_character_kill(
                    100, standard_package(), empty_universe()
                )
            ),
            True,
        )
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_character_kill(
                    101, standard_package(), empty_universe()
                )
            ),
            True,
        )

    def test__match_character_loss_no_matches(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_character_loss(
                    999, standard_package(), empty_universe()
                )
            ),
            False,
        )

    def test__match_character_loss_victim_match(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_character_loss(
                    200, standard_package(), empty_universe()
                )
            ),
            True,
        )

    def test__match_character_loss_attacker_match(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_character_loss(
                    100, standard_package(), empty_universe()
                )
            ),
            False,
        )

    def test__match_minimum_value_no_match(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_minimum_value(
                    1_000_000, standard_package(), empty_universe()
                )
            ),
            False,
        )

    def test__match_minimum_value_match(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_minimum_value(
                    100_000, standard_package(), empty_universe()
                )
            ),
            True,
        )

    def test__match_location_amarr(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_location(
                    "Amarr", standard_package(), empty_universe()
                )
            ),
            True,
        )

        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_location(
                    "Jita", standard_package(), empty_universe()
                )
            ),
            False,
        )

    def test__match_location_wspace(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_location(
                    "J100820", standard_package(), empty_universe()
                )
            ),
            False,
        )

        package = standard_package()
        package["killmail"]["solar_system_id"] = 31_002_479  # J100820
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_location(
                    "J100820", package, empty_universe()
                )
            ),
            True,
        )
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_location(
                    "wspace", package, empty_universe()
                )
            ),
            True,
        )

    def test__match_security_high(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_security_status(
                    "high", standard_package(), empty_universe()
                )
            ),
            True,
        )

        package = standard_package()
        package["killmail"]["solar_system_id"] = 30_002_718  # Rancer
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_security_status(
                    "high", package, empty_universe()
                )
            ),
            False,
        )

        package["killmail"]["solar_system_id"] = 30_003_704  # 9-F0B2
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_security_status(
                    "high", package, empty_universe()
                )
            ),
            False,
        )

        package["killmail"]["solar_system_id"] = 31_002_479  # J100820
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_security_status(
                    "high", package, empty_universe()
                )
            ),
            False,
        )

    def test__match_security_low(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_security_status(
                    "low", standard_package(), empty_universe()
                )
            ),
            False,
        )

        package = standard_package()
        package["killmail"]["solar_system_id"] = 30_002_718  # Rancer
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_security_status(
                    "low", package, empty_universe()
                )
            ),
            True,
        )

        package["killmail"]["solar_system_id"] = 30_003_704  # 9-F0B2
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_security_status(
                    "low", package, empty_universe()
                )
            ),
            False,
        )

        package["killmail"]["solar_system_id"] = 31_002_479  # J100820
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_security_status(
                    "low", package, empty_universe()
                )
            ),
            False,
        )

    def test__match_security_null(self) -> None:
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_security_status(
                    "null", standard_package(), empty_universe()
                )
            ),
            False,
        )

        package = standard_package()
        package["killmail"]["solar_system_id"] = 30_002_718  # Rancer
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_security_status(
                    "null", package, empty_universe()
                )
            ),
            False,
        )

        package["killmail"]["solar_system_id"] = 30_003_704  # 9-F0B2
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_security_status(
                    "null", package, empty_universe()
                )
            ),
            True,
        )

        package["killmail"]["solar_system_id"] = 31_002_479  # J100820
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill._match_security_status(
                    "null", package, empty_universe()
                )
            ),
            True,
        )


class MatchKillmailTest(unittest.TestCase):
    def test__simple_match(self) -> None:
        config: Dict[str, Any] = {
            "notifier": [
                {
                    "subscribes_to": "kill",
                    "filter": {
                        "require_all_of": [
                            {"minimum_value": 100_000},
                            {"alliance_kill": 1},
                        ]
                    },
                }
            ]
        }
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill.match_killmail(
                    config, empty_universe(), standard_package()
                )
            ),
            config["notifier"],
        )

        config["notifier"][0]["filter"]["require_all_of"].append(
            {"alliance_kill": 1111}
        )
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill.match_killmail(
                    config, empty_universe(), standard_package()
                )
            ),
            config["notifier"],
        )

        config["notifier"][0]["filter"]["exclude_if_any"] = [
            {"corporation_loss": 9999}
        ]
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill.match_killmail(
                    config, empty_universe(), standard_package()
                )
            ),
            config["notifier"],
        )

        config["notifier"][0]["filter"]["require_any_of"] = [
            {"security": "low"}
        ]
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill.match_killmail(
                    config, empty_universe(), standard_package()
                )
            ),
            [],
        )

        config["notifier"][0]["filter"]["require_any_of"].append(
            {"security": "high"}
        )
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill.match_killmail(
                    config, empty_universe(), standard_package()
                )
            ),
            config["notifier"],
        )

        config["notifier"][0]["filter"]["exclude_if_any"] = [
            {"corporation_loss": 20}
        ]
        self.assertEqual(
            loop.run_until_complete(
                unchaind_kill.match_killmail(
                    config, empty_universe(), standard_package()
                )
            ),
            [],
        )
