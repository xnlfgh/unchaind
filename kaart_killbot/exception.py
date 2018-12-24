"""Exceptions for use by kaart_killbot."""


class NotLoggedIn(Exception):
    """Exception when a call is made with an invalid token to any of the map
       providers."""

    pass


class ConnectionDuplicate(Exception):
    pass


class ConnectionNonexistent(Exception):
    pass
