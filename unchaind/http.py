"""Provides a HTTP class which can be used from to make cookies persist
   over requests and add some additional logging."""

from typing import Dict, Any
from http.cookies import SimpleCookie

from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPResponse

from unchaind.constant import DEFAULT_HEADERS


class HTTPSession:
    """Small HTTP session wrapper to keep cookie state over multiple
       requests."""

    cookies: Dict[str, str]
    http_client: AsyncHTTPClient
    referer: str

    def __init__(self) -> None:
        self.cookies = {}
        self.http_client = AsyncHTTPClient()
        self.referer = ""

    async def request(self, *args: str, **kwargs: Any) -> HTTPResponse:
        """Perform a request with cookies from the session and following
           redirects ourselves."""
        kwargs["headers"] = dict(DEFAULT_HEADERS)
        kwargs["headers"].update(
            {
                "Origin": "https://siggy.borkedlabs.com",
                "Referer": self.referer,
                "Cookie": self.cookie_header,
                "X-CSRF-Token": self.cookies.get("XSRF-TOKEN", ""),
            }
        )

        request: HTTPRequest = HTTPRequest(*args, **kwargs)

        response: HTTPResponse = await self.http_client.fetch(
            request, raise_error=False
        )

        self.referer = kwargs["url"]
        self.cookie_parse(response)

        if 300 <= response.code < 400:
            response = await self.request(url=response.headers.get("Location"))

        return response

    @property
    def cookie_header(self) -> str:
        """Create a cookie header from our cookies. There's a dumb workaround
           here to make sure Tornado only sends one cookie header instead of
           multiple which a lot of frameworks don't grok."""

        return "; ".join(
            f"{cookie}={value}" for cookie, value in self.cookies.items()
        )

    def cookie_parse(self, response: HTTPResponse) -> None:
        """Parse multiple set-header cookies into cookies."""

        cookies = SimpleCookie()
        for cookie in response.headers.get_list("Set-Cookie"):
            cookies.load(cookie)

        for cookie, morsel in cookies.items():
            self.cookies[cookie] = morsel.value
