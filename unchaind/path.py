from typing import List, Optional

from unchaind.universe import Multiverse, System


class Path:
    """Describes a Path between two Systems. Because connections in unchaind
       are bidirectional some special care needs to be taken.

       Path also gives some handy features such as 'max-size' and 'max-life'
       methods to determine how long a certain Path will exist."""

    path: List[System]
    multiverse: Multiverse

    def __init__(self) -> None:
        self.path = []

    @classmethod
    def from_path(cls, systems: List[System], multiverse: Multiverse) -> "Path":
        instance = cls()

        instance.path = systems
        instance.multiverse = multiverse

        return instance

    def as_string(self) -> str:
        """Get a string representation of our connections."""
        text = f"*{self.path[0].name}* to *{self.path[-1].name}*\n"

        for prev, goto in zip(self.path, self.path[1:]):
            # Get the connection(s) for this jump
            conn = self.multiverse.connections[frozenset([prev, goto])]

            text += f"- {prev.name} -({conn.type})-> {goto.name}\n"

        return text


# XXX roll this into the Path class.
def path(left: System, right: System, multiverse: Multiverse) -> Optional[Path]:
    """Calculate a Path between two different Systems."""
    graph = multiverse.graph
    queue = [(left, [left])]

    while queue:
        vertex, path = queue.pop(0)

        for goto in set(graph[vertex]) - set(path):
            if goto == right:
                return Path.from_path(path + [goto], multiverse)
            else:
                queue.append((goto, path + [goto]))

    return None
