from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from core.settings import get_settings
from schema.mongo import Dialogue


async def sharding_collections(
    client: AsyncIOMotorClient,
) -> None:
    admin_db = client.admin
    settings = get_settings()

    shard_keys: dict = {
        settings.mongo_dialogue_collection: {"_id": "hashed"},
    }

    for collection, shard_key in shard_keys.items():
        await admin_db.command(
            {
                "shardCollection": f"{settings.mongo_db_name}.{collection}",
                "key": shard_key,
            }
        )


async def mongo_init() -> None:
    settings = get_settings()

    client = AsyncIOMotorClient(settings.mongo_dsn_1)
    database: AsyncIOMotorDatabase = client[settings.mongo_db_name]

    await init_beanie(database=database, document_models=[Dialogue])

    await sharding_collections(client)
