"""
Event Service — main entry point.

Connects to RabbitMQ and starts consuming events from configured queues.
"""
import asyncio
import aio_pika
from app.config import settings
from app.database import connect_db
from app.consumers import handle_user_activity, handle_reco_invalidate


async def main():
    """Start the event consumer service."""
    print("🚀 Event Service starting...")

    # Connect to MongoDB
    await connect_db()

    # Connect to RabbitMQ with retry
    connection = None
    for attempt in range(30):
        try:
            connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            print("✅ Event Service connected to RabbitMQ")
            break
        except Exception as e:
            print(f"⏳ Waiting for RabbitMQ (attempt {attempt + 1}/30): {e}")
            await asyncio.sleep(2)

    if not connection:
        print("❌ Could not connect to RabbitMQ after 30 attempts")
        return

    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)

    # Declare exchange
    exchange = await channel.declare_exchange(
        "jrs.events", aio_pika.ExchangeType.TOPIC, durable=True
    )

    # Declare and bind queues
    # Queue 1: User activity events
    activity_queue = await channel.declare_queue("user.activity", durable=True)
    await activity_queue.bind(exchange, routing_key="user.activity")
    await activity_queue.consume(handle_user_activity)
    print("📡 Listening on queue: user.activity")

    # Queue 2: Recommendation invalidation events
    invalidate_queue = await channel.declare_queue("reco.invalidate", durable=True)
    await invalidate_queue.bind(exchange, routing_key="reco.invalidate")
    await invalidate_queue.consume(handle_reco_invalidate)
    print("📡 Listening on queue: reco.invalidate")

    print("🎯 Event Service is running and consuming events...")

    # Keep the service running
    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        pass
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
