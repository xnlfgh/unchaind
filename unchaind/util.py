"""Minor utilities for unchaind."""

import json

from typing import Dict, Union, Type

from unchaind.http import HTTPSession
from unchaind.universe import System

from unchaind.mapper.siggy import (
    Map as SiggyMapper,
    Transport as SiggyTransport,
)


name_cache: Dict[System, str] = {}


async def system_name(system: System) -> str:
    """Convert a system to a name using the ESI public API. This is cached in
       a non-persistent way in the process forever."""

    if system in name_cache:
        return name_cache[system]

    http = HTTPSession()

    response = await http.request(
        url=f"https://esi.evetech.net/latest/universe/systems/{system.identifier}/?datasource=tranquility&language=en-us",
        method="GET",
    )

    try:
        data = json.loads(response.body.decode("utf8"))
    except ValueError:
        return "Unknown"

    name_cache[system] = data.get("name", "Unknown")
    return name_cache[system]


def get_mapper(name: str) -> Union[Type[SiggyMapper]]:
    """Get a mapper for a name from the configuration."""
    return {"siggy": SiggyMapper}[name]


def get_transport(name: str) -> Union[Type[SiggyTransport]]:
    """Get a transport for a name from the configuration."""
    return {"siggy": SiggyTransport}[name]
