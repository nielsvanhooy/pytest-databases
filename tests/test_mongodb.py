from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    import pytest


@pytest.mark.parametrize(
    "service_fixture",
    [
        "mongodb_7_service",
        "mongodb_8_service",
    ],
)
def test_service_fixture(pytester: pytest.Pytester, service_fixture: str) -> None:
    pytester.makepyfile(f"""
    import pymongo
    
    pytest_plugins = ["pytest_databases.docker.mongodb"]

    def test_mongodb_service({service_fixture}) -> None:
        client = pymongo.MongoClient({service_fixture}.url)
        
        # Test basic connection and operation
        db = client.test_database
        collection = db.test_collection
        collection.insert_one({{"test": 1}})
        
        result = collection.find_one({{"test": 1}})
        assert result["test"] == 1
        
        client.close()
    """)

    result = pytester.runpytest("-vv")
    result.assert_outcomes(passed=1)


@pytest.mark.parametrize(
    "connection_fixture",
    [
        "mongodb_7_connection",
        "mongodb_8_connection",
    ],
)
def test_mongodb_connection(pytester: pytest.Pytester, connection_fixture: str) -> None:
    pytester.makepyfile(f"""
    import pymongo
    pytest_plugins = ["pytest_databases.docker.mongodb"]

    def test({connection_fixture}) -> None:
        assert isinstance({connection_fixture}, pymongo.MongoClient)
    """)

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
