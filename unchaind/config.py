import json
import os

from typing import Dict, Any

from unchaind.log import app_log


def parse_config(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        app_log().critical("Config %s is not a file", path)
        raise SystemExit(1)

    with open(path) as handle:
        return dict(json.load(handle))
