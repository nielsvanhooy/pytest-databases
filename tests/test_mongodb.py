from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest


def test_service_fixture(pytester: pytest.Pytester) -> None:
    pytester.makepyfile("""
    import pymongo
    
    pytest_plugins = ["pytest_databases.docker.mongodb"]

    def test_mongodb_service(mongodb_service) -> None:
        client = pymongo.MongoClient(
            host=mongodb_service.url,
        )
        
        # Test basic connection and operation
        db = client.test_database
        collection = db.test_collection
        collection.insert_one({"test": 1})
        
        result = collection.find_one({"test": 1})
        assert result["test"] == 1
        
        client.close()
    """)

    result = pytester.runpytest("-vv")
    result.assert_outcomes(passed=1)


def test_mongodb_connection(pytester: pytest.Pytester) -> None:
    pytester.makepyfile("""
    import pymongo
    pytest_plugins = ["pytest_databases.docker.mongodb"]

    def test(mongodb_connection) -> None:
        assert isinstance(mongodb_connection, pymongo.MongoClient)
    """)

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
