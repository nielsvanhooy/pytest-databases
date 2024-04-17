from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError

if TYPE_CHECKING:
    from pytest_databases.docker import DockerServiceRegistry


async def mongo_responsive(host: str, mongo_url: str) -> bool:
    try:
        client: AsyncIOMotorClient = AsyncIOMotorClient(mongo_url)
        return bool(await client.server_info())
    except ServerSelectionTimeoutError:
        return False


@pytest.fixture()
def mongo_db_user() -> str:
    return "pytest"


@pytest.fixture()
def mongo_db_password() -> str:
    return "pytest"


@pytest.fixture()
def mongo_db_port() -> str:
    return "17017"


@pytest.fixture()
def mongo_url(mongo_db_user: str, mongo_db_password: str, mongo_db_port: str) -> str:
    return f"mongodb://{mongo_db_user}:{mongo_db_password}@localhost:{mongo_db_port}"


@pytest.fixture(autouse=False)
async def mongo_service(docker_services: DockerServiceRegistry, mongo_db_port: str, mongo_url: str) -> None:
    os.environ["MONGO_PORT"] = str(mongo_db_port)
    await docker_services.start("mongo", check=mongo_responsive, mongo_url=mongo_url)
