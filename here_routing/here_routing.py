"""A module to query the HERE Routing API v8."""

from __future__ import annotations

import asyncio
import json
import socket
from datetime import datetime
from importlib import metadata
from typing import Any
from collections.abc import MutableMapping

import aiohttp
import async_timeout
from yarl import URL

from .exceptions import (
    HERERoutingConnectionError,
    HERERoutingError,
    HERERoutingTooManyRequestsError,
    HERERoutingUnauthorizedError,
)
from .model import Place, Return, RoutingMode, Spans, TransportMode, UnitSystem

SCHEME = "https"
API_HOST = "router.hereapi.com"
API_VERSION = "/v8"
ROUTES_PATH = "routes"

LIB_VERSION = metadata.version(__package__)


class HERERoutingApi:
    """Main class for handling connections with the HERE Routing API v8."""

    def __init__(
        self,
        api_key: str,
        request_timeout: int = 10,
        session: aiohttp.client.ClientSession | None = None,
        user_agent: str | None = None,
    ) -> None:
        """Initialize connection with HERE Routing."""
        self._session = session
        self._api_key = api_key
        self._close_session = False

        self.request_timeout = request_timeout
        self.user_agent = user_agent

        if user_agent is None:
            self.user_agent = f"here_routing/{LIB_VERSION}"

    async def request(
        self,
        uri: str,
        params: MutableMapping[str, str | list[str]],
        method: str = "GET",
    ) -> Any:
        """Handle a request to the HERE Routing API.

        Make a request against the HERE Routing API and handles the response.
        Args:
            uri: The request URI on the HERE Routing API to call.
            method: HTTP method to use for the request; e.g., GET, POST.
            data: RAW HTTP request data to send with the request.
            json_data: Dictionary of data to send as JSON with the request.
            params: Mapping of request parameters to send with the request.

        Returns:
            The response from the API. In case the response is a JSON response,
            the method will return a decoded JSON response as a Python
            dictionary. In other cases, it will return the RAW text response.

        Raises:
            HERERoutingConnectionError: An error occurred while communicating
                with the HERE API (connection issues).
            HERERoutingError: An error occurred while processing the
                response from the HERE API (invalid data).

        """
        url = URL.build(scheme=SCHEME, host=API_HOST, path=API_VERSION) / uri

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
            "DNT": "1",
        }
        params["apiKey"] = self._api_key

        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._close_session = True

        try:
            async with async_timeout.timeout(self.request_timeout):
                response = await self._session.request(
                    method,
                    url,
                    params=params,
                    headers=headers,
                )
        except asyncio.TimeoutError as exception:
            raise HERERoutingConnectionError(
                "Timeout occurred while connecting to the HERE Routing API."
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise HERERoutingConnectionError(
                "Error occurred while communicating with the HERE Routing API."
            ) from exception

        content_type = response.headers.get("Content-Type", "")
        contents = await response.read()
        decoded_contents = contents.decode("utf8")
        if "application/json" not in content_type:
            raise HERERoutingError(response.status, {"message": decoded_contents})
        if response.status // 100 in [4, 5]:
            response.close()

            if response.status == 401:
                raise HERERoutingUnauthorizedError(json.loads(decoded_contents)["error_description"])
            if response.status == 429:
                raise HERERoutingTooManyRequestsError(json.loads(decoded_contents)["error_description"])

            raise HERERoutingError(response.status, json.loads(decoded_contents))

        return await response.json()

    async def route(  # pylint: disable=too-many-arguments
        self,
        transport_mode: TransportMode,
        origin: Place,
        destination: Place,
        routing_mode: RoutingMode = RoutingMode.FAST,
        alternatives: int = 0,
        units: UnitSystem = UnitSystem.METRIC,
        lang: str = "en-US",
        return_values: list[Return] | None = None,
        spans: list[Spans] | None = None,
        via: list[Place] | None = None,
        departure_time: datetime | None = None,
        arrival_time: datetime | None = None,
    ) -> Any:
        """Get the route.

        Args:
            transport_mode: The TransportMode to use.
            origin: Latitude and longitude of the origin.
            destination: Latitude and longitude of the destination.
            routing_mode: Routing Mode to use. Defaults to RoutingMode.FAST.
            alternatives: Number of alternative routes to return.
            units: Unitsystem to use.
            lang: IETF BCP 47 compatible language identifier.
            return_values: HERE Routing API return values to request.
            spans: Information for Spans to request.
            via: List of waypoints the route should route over.
            departure_time: Departure time.
            arrival_time: Arrival time.

        Returns:
            The response from the API.

        Raises:
            HERERoutingConnectionError: An error occurred while communicating
                with the HERE API (connection issues).
            HERERoutingError: An error occurred while processing the
                response from the HERE API (invalid data).

        """
        params: MutableMapping[str, str | list[str]] = {
            "transportMode": transport_mode.value,
            "origin": f"{origin.latitude},{origin.longitude}",
            "destination": f"{destination.latitude},{destination.longitude}",
            "routingMode": routing_mode.value,
            "alternatives": str(alternatives),
            "units": units.value,
            "lang": lang,
        }
        if return_values is not None:
            params["return"] = ",".join(r.value for r in return_values)
        if spans is not None:
            params["spans"] = ",".join(s.value for s in spans)
        if via is not None:
            params["via"] = [f"{v.latitude},{v.longitude}" for v in via]
        if departure_time is not None:
            params["departureTime"] = departure_time.isoformat(timespec="seconds")
        if arrival_time is not None:
            params["arrivalTime"] = arrival_time.isoformat(timespec="seconds")

        response = await self.request(uri=ROUTES_PATH, params=params)

        if len(response["routes"]) < 1:
            raise HERERoutingError(",".join(notice["title"] for notice in response["notices"]))
        return response

    async def close(self) -> None:
        """Close open client session."""
        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self) -> HERERoutingApi:
        """Async enter."""
        return self

    async def __aexit__(self, *_exc_info) -> None:
        """Async exit."""
        await self.close()
