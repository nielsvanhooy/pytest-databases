
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from pytest_databases.docker.mongodb import mongo_responsive

if TYPE_CHECKING:
    from pytest_databases.docker import DockerServiceRegistry

pytestmark = pytest.mark.anyio
pytest_plugins = [
    "pytest_databases.docker.mongodb",
]


def test_mongo_default_config(mongo_url: int) -> None:
    assert mongo_url == "mongodb://pytest:pytest@localhost:17017"


async def test_mongodb_service(
    mongo_docker_ip: str,
    mongo_service: DockerServiceRegistry,
    mongo_url: str,
) -> None:
    ping = await mongo_responsive(mongo_docker_ip, mongo_url)
    assert ping
