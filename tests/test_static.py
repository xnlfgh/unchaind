import unittest

from unchaind import static as unchaind_static


class StaticTest(unittest.TestCase):
    def test__static_connections__count(self) -> None:
        self.assertEqual(len(unchaind_static.connections), 3917)

    def test__static_systems__count(self) -> None:
        self.assertEqual(len(unchaind_static.systems), 8285)

    def test__static_truesec__count(self) -> None:
        self.assertEqual(len(unchaind_static.truesec), 8285)

    def test__static_truesec__value(self) -> None:
        self.assertAlmostEqual(unchaind_static.truesec[30_002_187], 1.0)