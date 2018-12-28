import unittest

from unchaind import util as unchaind_util

from unchaind.mapper import siggy as unchaind_mapper_siggy


class UtilTest(unittest.TestCase):
    def test_get_mapper(self) -> None:
        obj = unchaind_util.get_mapper("siggy")
        self.assertEqual(unchaind_mapper_siggy.Map, obj)

    def test_get_transport(self) -> None:
        obj = unchaind_util.get_transport("siggy")
        self.assertEqual(unchaind_mapper_siggy.Transport, obj)
