"""
RabbitMQ event publisher for API Gateway.
"""
import json
import aio_pika


async def publish_event(rabbitmq_url: str, event_type: str, user_id: str, data: dict = None):
    """Publish an event to RabbitMQ."""
    try:
        connection = await aio_pika.connect_robust(rabbitmq_url)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                "jrs.events", aio_pika.ExchangeType.TOPIC, durable=True
            )
            message_body = json.dumps({
                "event_type": event_type,
                "user_id": user_id,
                "data": data or {},
            })
            routing_key = "user.activity" if event_type in ("job_clicked", "job_applied", "job_searched") else "reco.invalidate"
            await exchange.publish(
                aio_pika.Message(body=message_body.encode(), content_type="application/json"),
                routing_key=routing_key,
            )
    except Exception as e:
        print(f"⚠️ Event publish failed: {e}")
