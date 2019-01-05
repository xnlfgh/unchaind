"""Minor utilities for unchaind."""

from typing import Union, Type, Dict

from unchaind.mapper.siggy import (
    Map as SiggyMapper,
    Transport as SiggyTransport,
)

from unchaind.mapper.evescout import (
    Map as EVEScoutMapper,
    Transport as EVEScoutTransport,
)


_mappers: Dict[str, Union[Type[EVEScoutMapper], Type[SiggyMapper]]] = {
    "siggy": SiggyMapper,
    "evescout": EVEScoutMapper,
}

_transports: Dict[str, Union[Type[EVEScoutTransport], Type[SiggyTransport]]] = {
    "siggy": SiggyTransport,
    "evescout": EVEScoutTransport,
}


def get_mapper(name: str) -> Union[Type[EVEScoutMapper], Type[SiggyMapper]]:
    """Get a mapper for a name from the configuration."""
    return _mappers[name]


def get_transport(
    name: str
) -> Union[Type[EVEScoutTransport], Type[SiggyTransport]]:
    """Get a transport for a name from the configuration."""
    return _transports[name]
