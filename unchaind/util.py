"""Minor utilities for unchaind."""

from typing import Union, Type

from unchaind.mapper.siggy import (
    Map as SiggyMapper,
    Transport as SiggyTransport,
)


def get_mapper(name: str) -> Union[Type[SiggyMapper]]:
    """Get a mapper for a name from the configuration."""
    return {"siggy": SiggyMapper}[name]


def get_transport(name: str) -> Union[Type[SiggyTransport]]:
    """Get a transport for a name from the configuration."""
    return {"siggy": SiggyTransport}[name]
