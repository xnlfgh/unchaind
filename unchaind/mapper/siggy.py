"""Contains pollers for various EVE Online wormhole space mappers. These
   pollers provide the means to authenticate and fetch information about
   their current state online, then map that state onto an internal
   Universe representation.

   They also allow for callbacks when changes occur in their internal state."""

import json

from typing import Dict, Any
from io import StringIO
from urllib.parse import urlencode

from lxml import etree

from unchaind.universe import Universe, System, Connection, State
from unchaind.http import HTTPSession
from unchaind.log import app_log


class Map:
    """Uses the Transport to read data from Siggy into a universe."""

    universe: Universe

    def __init__(self, transport: "Transport") -> None:
        self.transport = transport
        self.universe = Universe.from_empty()

    async def update(self) -> Universe:
        """Update our internal Universe with a new Universe."""

        data = await self.transport.update()

        universe: Universe = Universe.from_empty()

        chain = data["chainMap"]

        connections = chain["wormholes"]

        for connection in connections.values():
            state = State()
            state.end_of_life = bool(connection.get("eol", 0))

            await universe.add_connection(
                Connection(
                    System(connection["from_system_id"]),
                    System(connection["to_system_id"]),
                    state,
                )
            )

        self.universe = universe

        return self.universe

    def reset(self) -> None:
        """Reset our internal universe."""
        self.universe = Universe.from_empty()


class Transport:
    """Represents a Siggy connection to be used to read raw data from Siggy."""

    http: HTTPSession

    def __init__(self) -> None:
        self.http = HTTPSession()

    @classmethod
    async def from_credentials(
        cls, username: str, password: str
    ) -> "Transport":
        """Create an initial instance of a Siggy class, this logs in with the
           provided username and password and does an initial fill of the
           universe."""

        instance = cls()

        await instance.login(username, password)
        await instance.update()

        return instance

    async def login(self, username: str, password: str) -> None:
        """Send a login request to the Siggy website. To do so we execute
           a first request to get a valid CSRF token and then a second one
           with the actual login form.

           The login form handler returns us a cookie which we can use for
           future requests and is stored into `self.token`.

           If this method is called multiple times on the same instance the
           old token will be replaced."""

        csrf_response = await self.http.request(
            url="https://siggy.borkedlabs.com/account/login", method="GET"
        )

        tree = etree.parse(
            StringIO(csrf_response.body.decode("utf8")), etree.HTMLParser()
        )

        csrf_token = tree.xpath("//input[@name='_token']/@value")[0]

        await self.http.request(
            url="https://siggy.borkedlabs.com/account/login",
            method="POST",
            follow_redirects=False,
            body=urlencode(
                {
                    "username": username,
                    "password": password,
                    "_token": csrf_token,
                    "remember": 0,
                }
            ),
        )

    async def update(self) -> Dict[str, Any]:
        """Update our internal Universe from siggy."""
        update_response = await self.http.request(
            url="https://siggy.borkedlabs.com/siggy/siggy",
            method="POST",
            body=urlencode(
                {
                    "systemID": 31_002_238,
                    "mapLastUpdate": 0,
                    "lastUpdate": 0,
                    "mapOpen": "true",
                    "forceUpdate": "true",
                }
            ),
        )

        try:
            return dict(json.loads(update_response.body.decode("utf8")))
        except (ValueError, AttributeError, json.decoder.JSONDecodeError):
            app_log().warning("Received invalid json from Siggy")
            raise ValueError()  # Fix this
