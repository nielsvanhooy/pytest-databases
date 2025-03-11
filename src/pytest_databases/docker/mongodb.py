from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pymongo
import pytest

from pytest_databases.helpers import get_xdist_worker_num
from pytest_databases.types import ServiceContainer

if TYPE_CHECKING:
    from collections.abc import Generator

    import pymongo

    from pytest_databases._service import DockerService


@dataclass
class MongoDBService(ServiceContainer):
    username: str
    password: str

    @property
    def url(self) -> str:
        return f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}"


@pytest.fixture(scope="session")
def mongodb_7_image() -> str:
    return "mongo:7.0"


@pytest.fixture(scope="session")
def mongodb_8_image() -> str:
    return "mongo:8.0"


def _create_mongodb_service(docker_service: DockerService, image: str) -> Generator[MongoDBService, None, None]:
    username = "pytest"
    password = "pytest"

    with docker_service.run(
        image=image,
        name=f"pytest_databases_mongodb_{get_xdist_worker_num() or 0}",
        container_port=27017,
        env={
            "MONGO_INITDB_ROOT_USERNAME": username,
            "MONGO_INITDB_ROOT_PASSWORD": password,
        },
        wait_for_log="Waiting for connections",
        transient=True,
    ) as service:
        yield MongoDBService(
            host=service.host,
            port=service.port,
            username=username,
            password=password,
        )


@pytest.fixture(scope="session")
def mongodb_7_service(docker_service: DockerService, mongodb_7_image: str) -> Generator[MongoDBService, None, None]:
    yield from _create_mongodb_service(docker_service, mongodb_7_image)


@pytest.fixture(scope="session")
def mongodb_8_service(docker_service: DockerService, mongodb_8_image: str) -> Generator[MongoDBService, None, None]:
    yield from _create_mongodb_service(docker_service, mongodb_8_image)


def _create_mongodb_connection(service: MongoDBService) -> Generator[pymongo.MongoClient, None, None]:
    client = pymongo.MongoClient(service.url)
    try:
        yield client
    finally:
        client.close()


@pytest.fixture(scope="session")
def mongodb_7_connection(mongodb_7_service: MongoDBService) -> Generator[pymongo.MongoClient, None, None]:
    yield from _create_mongodb_connection(mongodb_7_service)


@pytest.fixture(scope="session")
def mongodb_8_connection(mongodb_8_service: MongoDBService) -> Generator[pymongo.MongoClient, None, None]:
    yield from _create_mongodb_connection(mongodb_8_service)
