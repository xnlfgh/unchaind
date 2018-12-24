from kaart_killbot import util as kaart_killbot_util

from kaart_killbot.mapper import siggy as kaart_killbot_mapper_siggy


def test_get_mapper() -> None:
    obj = kaart_killbot_util.get_mapper("siggy")
    assert isinstance(obj, kaart_killbot_mapper_siggy.Map) is True


def test_get_transport() -> None:
    obj = kaart_killbot_util.get_transport("siggy")
    assert isinstance(obj, kaart_killbot_mapper_siggy.Transport) is True
