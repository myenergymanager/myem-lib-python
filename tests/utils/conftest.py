import asyncio
from typing import AsyncGenerator

import httpx
import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def created_app():
    app = FastAPI()
    yield app


@pytest.fixture(scope="module")
def get_test_client():
    async def _get_test_client(app: FastAPI) -> AsyncGenerator[httpx.AsyncClient, None]:
        async with LifespanManager(app):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
                app=app,
                base_url="http://app.io",
            ) as test_client:
                yield test_client

    return _get_test_client


@pytest.fixture(scope="module")
@pytest.mark.asyncio
async def client(get_test_client, created_app) -> AsyncGenerator[httpx.AsyncClient, None]:
    async for client in get_test_client(created_app):
        yield client
