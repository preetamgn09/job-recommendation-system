"""
RabbitMQ event publisher — used by API Gateway and services to publish events.
"""
import json
import aio_pika
from app.config import settings


async def publish_event(event_type: str, user_id: str, data: dict = None):
    """Publish an event to RabbitMQ."""
    try:
        connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            
            # Declare exchange
            exchange = await channel.declare_exchange(
                "jrs.events", aio_pika.ExchangeType.TOPIC, durable=True
            )
            
            # Build message
            message_body = json.dumps({
                "event_type": event_type,
                "user_id": user_id,
                "data": data or {},
            })
            
            # Determine routing key
            if event_type in ("job_clicked", "job_applied", "job_searched"):
                routing_key = "user.activity"
            else:
                routing_key = "reco.invalidate"
            
            await exchange.publish(
                aio_pika.Message(
                    body=message_body.encode(),
                    content_type="application/json",
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=routing_key,
            )
            print(f"📤 Published event: {event_type} for user {user_id}")
    except Exception as e:
        print(f"❌ Failed to publish event: {e}")
