import json

from typing import Dict, Any


def parse_config(data: str) -> Dict[str, Any]:
    return dict(json.loads(data))
