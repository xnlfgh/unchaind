"""Contains pollers for various EVE Online wormhole space mappers. These
   pollers provide the means to authenticate and fetch information about
   their current state online, then map that state onto an internal
   Universe representation.

   They also allow for callbacks when changes occur in their internal state."""

import json
import logging

from typing import Dict, Any, Optional, List

import marshmallow

from unchaind.universe import Universe, System, Connection, State
from unchaind.http import HTTPSession
from unchaind.schema import evescout as schema


log = logging.getLogger(__name__)


class Map:
    """Uses the Transport to read data from Siggy into a universe."""

    universe: Optional[Universe]

    def __init__(self, transport: "Transport") -> None:
        self.transport = transport
        self.universe = None

    async def update(self) -> Universe:
        """Update our internal Universe with a new Universe."""

        data = await self.transport.update()

        if self.universe is None:
            self.universe: Universe = await Universe.from_empty()

        universe: Universe = await Universe.from_empty()

        for connection in data:
            state = State()

            await universe.connect(
                Connection(
                    System(connection["source_solar_system"]["id"]),
                    System(connection["destination_solar_system"]["id"]),
                    state,
                )
            )

        self.universe = universe

        return self.universe


class Transport:
    """Represents an EVE scout connection to be used to read raw data from Siggy."""

    http: HTTPSession
    config: Dict[str, Any]

    def __init__(self, config: Dict[str, Any]) -> None:
        self.http = HTTPSession()
        self.config = config

    @classmethod
    async def from_config(cls, config: Dict[str, Any]) -> "Transport":
        instance = cls(config)
        await instance.update()
        return instance

    async def update(self) -> List[Dict[str, Any]]:
        """Update our internal Universe from evescout."""
        update_response = await self.http.request(
            url="https://www.eve-scout.com/api/wormholes", method="GET"
        )

        try:
            return list(
                schema.Item().loads(
                    update_response.body, unknown=marshmallow.RAISE, many=True
                )
            )
        except (ValueError, AttributeError, json.decoder.JSONDecodeError):
            log.critical("update: failed to parse EVEScout reply")
            raise SystemExit(1)
