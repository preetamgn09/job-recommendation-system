"""
RabbitMQ event consumers — process events asynchronously.

Handles:
- user.activity: job_clicked, job_applied, job_searched → update user profile
- reco.invalidate: user_updated → invalidate recommendation cache
"""
import json
from datetime import datetime, timezone
from bson import ObjectId
import aio_pika
import httpx
import redis.asyncio as redis
from app.config import settings
from app.database import get_db


async def handle_user_activity(message: aio_pika.IncomingMessage):
    """Process user activity events."""
    async with message.process():
        try:
            event = json.loads(message.body.decode())
            event_type = event.get("event_type")
            user_id = event.get("user_id")
            data = event.get("data", {})

            print(f"📥 Processing activity: {event_type} for user {user_id}")

            db = get_db()

            # Build activity entry
            activity_entry = {
                "activity_type": event_type,
                "job_id": data.get("job_id"),
                "search_query": data.get("search_query"),
                "metadata": data.get("metadata", {}),
                "timestamp": datetime.now(timezone.utc),
            }

            # Update user's activity log (keep last 100)
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$push": {"activity": {"$each": [activity_entry], "$slice": -100}}}
            )

            # Invalidate recommendation cache for this user
            try:
                redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
                await redis_client.delete(f"reco:{user_id}")
                await redis_client.close()
                print(f"🗑️ Invalidated cache for user {user_id}")
            except Exception as e:
                print(f"⚠️ Redis cache invalidation failed: {e}")

            # If job_applied, trigger recommendation recalculation
            if event_type == "job_applied":
                try:
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        await client.post(
                            f"{settings.RECOMMENDATION_SERVICE_URL}/recommendations/{user_id}/recalculate"
                        )
                    print(f"🔄 Triggered reco recalculation for user {user_id}")
                except Exception as e:
                    print(f"⚠️ Reco recalculation trigger failed: {e}")

            print(f"✅ Processed: {event_type} for user {user_id}")

        except Exception as e:
            print(f"❌ Error processing activity event: {e}")


async def handle_reco_invalidate(message: aio_pika.IncomingMessage):
    """Process recommendation invalidation events."""
    async with message.process():
        try:
            event = json.loads(message.body.decode())
            user_id = event.get("user_id")

            print(f"📥 Invalidating recommendations for user {user_id}")

            # Invalidate cache
            try:
                redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
                await redis_client.delete(f"reco:{user_id}")
                await redis_client.close()
            except Exception:
                pass

            print(f"✅ Invalidated recommendations for user {user_id}")

        except Exception as e:
            print(f"❌ Error processing invalidation event: {e}")
