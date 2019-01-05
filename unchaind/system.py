from typing import Dict, Any

from unchaind.universe import Universe


async def periodic(config: Dict[str, Any], universe: Universe) -> None:
    print(universe)
