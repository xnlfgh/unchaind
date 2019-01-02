import os

from typing import Dict, List


systems: Dict[int, str] = {}
connections: Dict[int, List[int]] = {}

with open(os.path.join(os.path.dirname(__file__), "data", "system.txt")) as f:
    for line in f:
        a, b = line.strip().split("|")

        systems[int(a)] = b


_seen: List[frozenset] = []

with open(
    os.path.join(os.path.dirname(__file__), "data", "connection.txt")
) as f:
    for line in f:
        a, b = line.strip().split("|")

        if frozenset((a, b)) in _seen:
            continue

        connections[int(a)] = connections.get(int(a), []) + [int(b)]

        _seen.append(frozenset((a, b)))
