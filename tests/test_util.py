from unchaind import util as unchaind_util

from unchaind.mapper import siggy as unchaind_mapper_siggy


def test_get_mapper() -> None:
    obj = unchaind_util.get_mapper("siggy")
    assert unchaind_mapper_siggy.Map == obj


def test_get_transport() -> None:
    obj = unchaind_util.get_transport("siggy")
    assert unchaind_mapper_siggy.Transport == obj
