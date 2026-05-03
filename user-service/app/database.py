"""
MongoDB async client for User Service using Motor.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client: AsyncIOMotorClient = None
db = None


async def connect_db():
    """Initialize MongoDB connection."""
    global client, db
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.MONGO_DB]
    # Create indexes
    await db.users.create_index("email", unique=True)
    print(f"✅ User Service connected to MongoDB: {settings.MONGO_URL}")


async def close_db():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        print("🔌 User Service disconnected from MongoDB")


def get_db():
    """Get the database instance."""
    return db
