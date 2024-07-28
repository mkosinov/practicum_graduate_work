import pytest
from config import test_settings
from pymongo import MongoClient

mongo_client = MongoClient(
    test_settings.mongo_dsn_1,
)


@pytest.fixture(scope="session", autouse=True)
def clean_mongo_database():
    """Flushes all collections in mongo database before each test session"""
    settings = test_settings()
    mongo_client.drop_database(settings.mongo_db_name)


@pytest.fixture(scope="function")
def save_dialogue_to_mongo(test_dialogue):
    """Save dialogue to mongo db"""
    settings = test_settings()
    database = mongo_client[settings.mongo_db_name]
    collection = database[settings.mongo_dialogue_collection]
    collection.insert_one(test_dialogue.dict())
    client.close()
    yield
    collection.delete_one({"_id": test_dialogue.id})


@pytest.fixture(scope="function")
def read_document_from_mongo(test_dialogue):
    """Read document from mongo sharded collection using MongoClient"""
    settings = test_settings()
    client = MongoClient(settings.mongo_dsn_1)
    database = client[settings.mongo_db_name]
    collection = database[settings.mongo_dialogue_collection]
    document = collection.find_one({"_id": test_dialogue.id})
    assert document is not None
    client.close()
    yield document
