"""Classes and types describing our Universe and the parts it consists of."""

from typing import Dict, Optional, Set, Callable, Awaitable, FrozenSet
from itertools import chain

from unchaind.exception import ConnectionDuplicate, ConnectionNonexistent


class State:
    """A Connection can have a few states some of which can be there at the
       same time."""

    stargate: bool
    critical_mass: bool
    end_of_life: bool
    frigate_sized: bool

    def __init__(self) -> None:
        self.stargate = False
        self.critical_mass = False
        self.frigate_sized = False
        self.end_of_life = False


class Connection:
    """The Connection object describes two Systems linked together."""

    left: "System"
    right: "System"
    state: State

    def __init__(self, left: "System", right: "System", state: State) -> None:
        self.left = left
        self.right = right
        self.state = state


class System(object):
    """Represents a system from its identifier and name, can have a list of
       of connections and belongs to a Universe."""

    identifier: int
    _name: Optional[str]

    def __init__(self, identifier: int) -> None:
        self.identifier = identifier
        self._name = None

    def __hash__(self) -> int:
        """The identity of a System uses its identifier for uniqueness."""
        return self.identifier

    def __eq__(self, other) -> bool:  # type: ignore
        return bool(self.identifier == other.identifier)

    def __repr__(self) -> str:
        return f"System(identifier={self.identifier!r})"


class Universe:
    """Representation of a universe. A universe consists of a set of
       connections and flattened connections into systems."""

    connections: Dict[FrozenSet[System], Connection]

    def __init__(
        self,
        cb_add_connection: Optional[
            Callable[[Connection], Awaitable[None]]
        ] = None,
        cb_del_connection: Optional[
            Callable[[Connection], Awaitable[None]]
        ] = None,
    ) -> None:

        self.connections = {}

        self.cb_add_connection = cb_add_connection
        self.cb_del_connection = cb_del_connection

    @classmethod
    def from_empty(cls) -> "Universe":
        """Create an empty universe ready to be populated."""
        return cls()

    @property
    def systems(self) -> Set[System]:
        return set(chain.from_iterable(self.connections))

    async def add_connection(
        self, connection: Connection, init: bool = False
    ) -> None:
        """Add a connection as long as it doesn't exist."""

        key = frozenset([connection.left, connection.right])

        if key in self.connections:
            raise ConnectionDuplicate()

        if not init and self.cb_add_connection:
            await self.cb_add_connection(connection)

        self.connections[key] = connection

    async def del_connection(
        self, connection: Connection, init: bool = False
    ) -> None:
        """Delete a connection as long as it exist."""

        key = frozenset([connection.left, connection.right])

        if key not in self.connections:
            raise ConnectionNonexistent()

        del self.connections[key]

    async def update_with(
        self, universe: "Universe", init: bool = False
    ) -> None:
        """Adjust this universe based on another universe adding all
           connections and removing those which aren't in the other
           Universe.

           This ignores nonexistent and filtered exceptions to make workflow
           as normal as possible."""

        delta = Delta.from_universes(self, universe)

        for connection in delta.connections_add:
            try:
                await self.add_connection(connection, init=init)
            except ConnectionNonexistent:
                continue

        for connection in delta.connections_del:
            try:
                await self.del_connection(connection, init=init)
            except ConnectionNonexistent:
                continue


class Delta:
    """Represents the difference between two Universes with added, removed,
       and changed connections."""

    connections_add: Set[Connection]
    connections_del: Set[Connection]

    def __init__(self) -> None:
        self.connections_add = set()
        self.connections_del = set()

    @classmethod
    def from_universes(cls, left: Universe, right: Universe) -> "Delta":
        """Build a Delta object from two Universes."""

        instance = cls()

        for connection in set(right.connections.keys()) - set(
            left.connections.keys()
        ):
            instance.connections_add.add(right.connections[connection])

        for connection in set(left.connections.keys()) - set(
            right.connections.keys()
        ):
            instance.connections_del.add(left.connections[connection])

        return instance
