"""Functions to query ESI with simple caching."""
import logging
import json

from typing import Dict, Any, List
from async_lru import alru_cache

from unchaind.http import HTTPSession

log = logging.getLogger(__name__)

_ESI = "https://esi.evetech.net/latest/"


@alru_cache(maxsize=8192)
async def character_details(character: int) -> Dict[str, Any]:
    rv = await _do_esi_request(f"{_ESI}characters/{character}/")
    return rv


@alru_cache(maxsize=4096)
async def corporation_details(corp: int) -> Dict[str, Any]:
    rv = await _do_esi_request(f"{_ESI}corporations/{corp}/")
    return rv


@alru_cache(maxsize=4096)
async def alliance_details(alliance: int) -> Dict[str, Any]:
    rv = await _do_esi_request(f"{_ESI}alliances/{alliance}/")
    return rv


@alru_cache(maxsize=4096)
async def type_details(type: int) -> Dict[str, Any]:
    rv = await _do_esi_request(f"{_ESI}universe/types/{type}/")
    return rv


async def _do_esi_request(url: str) -> Dict[str, Any]:
    http = HTTPSession()

    response = await http.request(url=url, method="GET")

    return dict(json.loads(response.body, encoding="utf-8"))
