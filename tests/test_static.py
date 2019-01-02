import unittest

from unchaind import static as unchaind_static


class StaticTest(unittest.TestCase):
    def test__static_connections__count(self) -> None:
        self.assertEqual(len(unchaind_static.connections), 3917)

    def test__static_systems__count(self) -> None:
        self.assertEqual(len(unchaind_static.systems), 8285)
