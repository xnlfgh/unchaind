import logging
import json
import os

from typing import Dict, Any


log = logging.getLogger(__name__)


def parse_config(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        log.critical("Config %s is not a file", path)
        raise SystemExit(1)

    with open(path) as handle:
        return dict(json.load(handle))
