from unchaind import util as unchaind_util

from unchaind.mapper import siggy as unchaind_mapper_siggy


def test_get_mapper() -> None:
    obj = unchaind_util.get_mapper("siggy")
    assert isinstance(obj, unchaind_mapper_siggy.Map) is True


def test_get_transport() -> None:
    obj = unchaind_util.get_transport("siggy")
    assert isinstance(obj, unchaind_mapper_siggy.Transport) is True
