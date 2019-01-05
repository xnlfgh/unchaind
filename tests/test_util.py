import unittest

from unchaind import util as unchaind_util

from unchaind.mapper import siggy as unchaind_mapper_siggy
from unchaind.mapper import evescout as unchaind_mapper_evescout


class UtilTest(unittest.TestCase):
    def test_get_mapper(self) -> None:
        obj = unchaind_util.get_mapper("siggy")
        self.assertEqual(unchaind_mapper_siggy.Map, obj)

        obj = unchaind_util.get_mapper("evescout")
        self.assertEqual(unchaind_mapper_evescout.Map, obj)

    def test_get_transport(self) -> None:
        obj = unchaind_util.get_transport("siggy")
        self.assertEqual(unchaind_mapper_siggy.Transport, obj)

        obj = unchaind_util.get_transport("evescout")
        self.assertEqual(unchaind_mapper_evescout.Transport, obj)
