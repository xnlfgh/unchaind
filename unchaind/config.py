import logging
import pytoml
import os

from typing import Dict, Any


log = logging.getLogger(__name__)


def parse_config(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        log.critical("parse_config: config %s is not a file", path)
        raise SystemExit(1)

    with open(path) as handle:
        return dict(pytoml.load(handle))
