from typing import List, Optional

from unchaind.universe import Multiverse, System


class Path:
    @classmethod
    def from_path(cls, path: List[System], multiverse: Multiverse) -> "Path":
        instance = cls()

        for p, n in zip(path, path[1:]):
            print(multiverse.connections[frozenset([p, n])])

        return instance


def path(left: System, right: System, multiverse: Multiverse) -> Optional[Path]:
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
