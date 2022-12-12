"""Tests for `here_routing.here_routing`."""
import os
from datetime import datetime

import aiohttp
import pytest

from here_routing.exceptions import (
    HERERoutingError,
    HERERoutingTooManyRequestsError,
    HERERoutingUnauthorizedError,
)
from here_routing.here_routing import API_HOST, API_VERSION, ROUTES_PATH, HERERoutingApi
from here_routing.model import Place, Return, Spans, TransportMode


@pytest.mark.asyncio
async def test_car_route(aresponses):
    """Test getting user information with a timed out token."""
    aresponses.add(
        API_HOST,
        f"{API_VERSION}/{ROUTES_PATH}",
        "GET",
        aresponses.Response(
            text=load_json_fixture("car_route_response.json"),
            status=200,
            content_type="application/json",
        ),
    )
    async with aiohttp.ClientSession() as session:
        here_api = HERERoutingApi(api_key="key", session=session)
        response = await here_api.route(
            transport_mode=TransportMode.CAR,
            origin=Place(latitude=50.12778680095556, longitude=8.582081794738771),
            destination=Place(latitude=50.060940891421765, longitude=8.336477279663088),
            return_values=[Return.SUMMARY, Return.POLYINE],
            spans=[Spans.NAMES],
            via=[Place(latitude=50.12778630095556, longitude=8.582081734738771)],
            departure_time=datetime.now(),
        )

        assert response["routes"][0]["sections"][0]["summary"]["duration"] == 1085


@pytest.mark.asyncio
async def test_invalid_key(aresponses):
    """Test that an invalid api_key throws HERERoutingUnauthorizedError."""
    aresponses.add(
        API_HOST,
        f"{API_VERSION}/{ROUTES_PATH}",
        "GET",
        aresponses.Response(
            text=load_json_fixture("invalid_key_response.json"),
            status=401,
            content_type="application/json",
        ),
    )
    async with aiohttp.ClientSession() as session:
        with pytest.raises(HERERoutingUnauthorizedError):
            here_api = HERERoutingApi(api_key="invalid", session=session)
            await here_api.route(
                transport_mode=TransportMode.CAR,
                origin=Place(latitude=50.12778680095556, longitude=8.582081794738771),
                destination=Place(
                    latitude=50.060940891421765, longitude=8.336477279663088
                ),
            )


@pytest.mark.asyncio
async def test_malformed_request(aresponses):
    """Test that a malformed request throws HERERoutingError."""
    aresponses.add(
        API_HOST,
        f"{API_VERSION}/{ROUTES_PATH}",
        "GET",
        aresponses.Response(
            text=load_json_fixture("malformed_request_response.json"),
            status=400,
            content_type="application/json",
        ),
    )
    async with aiohttp.ClientSession() as session:
        with pytest.raises(HERERoutingError):
            here_api = HERERoutingApi(api_key="key", session=session)
            await here_api.route(
                transport_mode=TransportMode.CAR,
                origin=Place(latitude=50.12778680095556, longitude=8.582081794738771),
                destination=Place(
                    latitude=50.060940891421765, longitude=8.336477279663088
                ),
            )


@pytest.mark.asyncio
async def test_invalid_request(aresponses):
    """Test that a invalid request throws HERERoutingError."""
    aresponses.add(
        API_HOST,
        f"{API_VERSION}/{ROUTES_PATH}",
        "GET",
        aresponses.Response(
            text=load_json_fixture("invalid_request_response.json"),
            status=400,
            content_type="application/json",
        ),
    )
    async with aiohttp.ClientSession() as session:
        with pytest.raises(HERERoutingError) as error:
            here_api = HERERoutingApi(api_key="key", session=session)
            await here_api.route(
                transport_mode=TransportMode.CAR,
                origin=Place(latitude=50.12778680095556, longitude=8.582081794738771),
                destination=Place(
                    latitude=50.060940891421765, longitude=8.336477279663088
                ),
            )
        assert "Spans requested but no polyline requested" in str(error.value)


@pytest.mark.asyncio
async def test_429_too_many_requests(aresponses):
    """Test that a invalid request throws HERETransitTooManyRequestsError."""
    aresponses.add(
        API_HOST,
        f"{API_VERSION}/{ROUTES_PATH}",
        "GET",
        aresponses.Response(
            text=load_json_fixture("too_many_requests_response.json"),
            status=429,
            content_type="application/json",
        ),
    )
    async with aiohttp.ClientSession() as session:
        with pytest.raises(HERERoutingTooManyRequestsError) as error:
            here_api = HERERoutingApi(api_key="key", session=session)
            await here_api.route(
                transport_mode=TransportMode.CAR,
                origin=Place(latitude=150.12778680095556, longitude=8.582081794738771),
                destination=Place(
                    latitude=50.060940891421765, longitude=8.336477279663088
                ),
            )
        assert "Rate limit for this service has been reached" in str(error.value)


@pytest.mark.asyncio
async def test_no_route_found(aresponses):
    """Test that a no route found response throws HERERoutingError."""
    aresponses.add(
        API_HOST,
        f"{API_VERSION}/{ROUTES_PATH}",
        "GET",
        aresponses.Response(
            text=load_json_fixture("no_route_response.json"),
            status=200,
            content_type="application/json",
        ),
    )
    async with aiohttp.ClientSession() as session:
        with pytest.raises(HERERoutingError) as error:
            here_api = HERERoutingApi(api_key="key", session=session)
            await here_api.route(
                transport_mode=TransportMode.CAR,
                origin=Place(latitude=50.12778680095556, longitude=8.582081794738771),
                destination=Place(
                    latitude=50.060940891421765, longitude=8.336477279663088
                ),
            )
        assert "Couldn't find a route" in str(error.value)


def load_json_fixture(filename: str) -> str:
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path, encoding="utf-8") as fptr:
        return fptr.read()
