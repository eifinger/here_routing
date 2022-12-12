"""Exceptions for here_routing."""


class HERERoutingError(Exception):
    """Generic HERE routing exception."""


class HERERoutingConnectionError(HERERoutingError):
    """HERE routing connection exception."""


class HERERoutingUnauthorizedError(HERERoutingError):
    """HERE routing unauthorized exception."""


class HERERoutingTooManyRequestsError(HERERoutingError):
    """HERE routing exception wrapping HTTP 429."""
