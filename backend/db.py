"""MongoDB connection factory. Reused across API routers and adapters."""
import os
from motor.motor_asyncio import AsyncIOMotorClient

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    return _client


def get_db():
    return get_client()[os.environ["DB_NAME"]]


async def close_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
