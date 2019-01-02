import os

from typing import Dict, List


systems: Dict[int, str] = {}
connections: Dict[int, List[int]] = {}

with open(os.path.join(os.path.dirname(__file__), "data", "system.txt")) as f:
    for line in f:
        a, b = line.strip().split("|")

        systems[int(a)] = b


with open(
    os.path.join(os.path.dirname(__file__), "data", "connection.txt")
) as f:
    for line in f:
        a, b = line.strip().split("|")

        connections[int(a)] = connections.get(int(a), []) + [int(b)]
