# here_routing

Asynchronous Python client for the HERE Routing V8 API

[![GitHub Actions](https://github.com/eifinger/here_routing/workflows/CI/badge.svg)](https://github.com/eifinger/here_routing/actions?workflow=CI)
[![PyPi](https://img.shields.io/pypi/v/here_routing.svg)](https://pypi.python.org/pypi/here_routing)
[![PyPi](https://img.shields.io/pypi/l/here_routing.svg)](https://github.com/eifinger/here_routing/blob/master/LICENSE)
[![codecov](https://codecov.io/gh/eifinger/here_routing/branch/master/graph/badge.svg)](https://codecov.io/gh/eifinger/here_routing)
[![Downloads](https://pepy.tech/badge/here_routing)](https://pepy.tech/project/here_routing)

## Installation

```bash
pip install here_routing
```

## Usage

```python
import asyncio

from here_routing import HERERoutingApi, Place, Return, TransportMode

API_KEY = "<YOUR_API_KEY>"


async def main() -> None:
    """Show example how to get duration of your route."""
    async with HERERoutingApi(api_key=API_KEY) as here_routing:
        response = await here_routing.route(
            transport_mode=TransportMode.CAR,
            origin=Place(latitude=50.12778680095556, longitude=8.582081794738771),
            destination=Place(latitude=50.060940891421765, longitude=8.336477279663088),
            return_values=[Return.SUMMARY],
        )
        print(
            f"Duration is: {response['routes'][0]['sections'][0]['summary']['duration']}"
        )


if __name__ == "__main__":
    asyncio.run(main())
```
