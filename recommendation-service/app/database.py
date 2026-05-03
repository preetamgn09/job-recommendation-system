"""
MongoDB async client for Recommendation Service.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client = None
db = None


async def connect_db():
    global client, db
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.MONGO_DB]
    print(f"✅ Recommendation Service connected to MongoDB")


async def close_db():
    global client
    if client:
        client.close()


def get_db():
    return db
