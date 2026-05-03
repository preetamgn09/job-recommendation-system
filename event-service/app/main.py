"""
Event Service — main entry point.

Runs as a web service (for Render free tier compatibility) with a background
RabbitMQ consumer task. The HTTP server provides health checks while the
background task processes events.
"""
import asyncio
import os
import aio_pika
from aiohttp import web
from app.config import settings
from app.database import connect_db
from app.consumers import handle_user_activity, handle_reco_invalidate


async def start_consumer():
    """Start the RabbitMQ consumer in the background."""
    print("🚀 Event Consumer starting...")

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


# ── Health check HTTP server ─────────────────────────────────

async def health_handler(request):
    return web.json_response({"status": "healthy", "service": "event-service"})


async def on_startup(app):
    """Start the RabbitMQ consumer as a background task."""
    app["consumer_task"] = asyncio.create_task(start_consumer())


async def on_cleanup(app):
    """Cancel the consumer task on shutdown."""
    app["consumer_task"].cancel()
    try:
        await app["consumer_task"]
    except asyncio.CancelledError:
        pass


def create_app():
    app = web.Application()
    app.router.add_get("/health", health_handler)
    app.router.add_get("/", health_handler)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    return app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8004))
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=port)
