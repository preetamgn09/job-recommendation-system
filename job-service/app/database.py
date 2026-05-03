"""
MongoDB async client for Job Service.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client = None
db = None


async def connect_db():
    global client, db
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.MONGO_DB]
    # Create text index for search
    await db.jobs.create_index([
        ("title", "text"),
        ("description", "text"),
        ("required_skills", "text"),
    ])
    print(f"✅ Job Service connected to MongoDB: {settings.MONGO_URL}")


async def close_db():
    global client
    if client:
        client.close()
        print("🔌 Job Service disconnected from MongoDB")


def get_db():
    return db
