from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, Generator
from pathlib import Path

import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError


from pytest_databases.helpers import simple_string_hash
from pytest_databases.docker import DockerServiceRegistry


COMPOSE_PROJECT_NAME: str = f"pytest-databases-mongo-{simple_string_hash(__file__)}"


async def mongo_responsive(host: str, mongo_url: str) -> bool:
    try:
        client: AsyncIOMotorClient = AsyncIOMotorClient(mongo_url)
        return bool(await client.server_info())
    except ServerSelectionTimeoutError:
        return False


@pytest.fixture(scope="session")
def mongo_compose_project_name() -> str:
    return os.environ.get("COMPOSE_PROJECT_NAME", COMPOSE_PROJECT_NAME)


@pytest.fixture(autouse=False, scope="session")
def mongo_docker_services(
    mongo_compose_project_name: str, worker_id: str = "main"
) -> Generator[DockerServiceRegistry, None, None]:
    if os.getenv("GITHUB_ACTIONS") == "true" and sys.platform != "linux":
        pytest.skip("Docker not available on this platform")

    registry = DockerServiceRegistry(worker_id, compose_project_name=mongo_compose_project_name)
    try:
        yield registry
    finally:
        registry.down()

@pytest.fixture()
def mongo_db_port() -> str:
    return "17017"

@pytest.fixture()
def mongo_db_user() -> str:
    return "pytest"

@pytest.fixture()
def mongo_db_password() -> str:
    return "pytest"

@pytest.fixture()
def mongo_url(mongo_db_user: str, mongo_db_password: str, mongo_db_port: str) -> str:
    return f"mongodb://{mongo_db_user}:{mongo_db_password}@localhost:{mongo_db_port}"


@pytest.fixture(scope="session")
def mongo_docker_compose_files() -> list[Path]:
    return [Path(Path(__file__).parent / "docker-compose.mongodb.yml")]

@pytest.fixture(scope="session")
def default_mongo_service_name() -> str:
    return "mongo"

@pytest.fixture(scope="session")
def mongo_docker_ip(mongo_docker_services: DockerServiceRegistry) -> str:
    return mongo_docker_services.docker_ip



@pytest.fixture(autouse=False)
async def mongo_service(
        mongo_docker_services: DockerServiceRegistry,
        default_mongo_service_name: str,
        mongo_docker_compose_files: list[Path],
        mongo_db_port: str,
        mongo_url: str
) -> None:
    os.environ["MONGO_PORT"] = str(mongo_db_port)
    await mongo_docker_services.start(
        name=default_mongo_service_name,
        docker_compose_files=mongo_docker_compose_files,
        check=mongo_responsive,
        mongo_url=mongo_url
    )
