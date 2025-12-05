from datetime import datetime, timezone

import msgspec
from aio_pika import Connection, Message, connect_robust
from aio_pika.abc import AbstractChannel

from app.core import settings
from app.infrastructure.logging import get_logger
from app.infrastructure.messaging.events import EventType, UserEvent

logger = get_logger(__name__)


class EventProducer:
    def __init__(self):
        self.connection: Connection | None = None
        self.channel: AbstractChannel | None = None
        self.exchange_name = "user_events"
    
    async def connect(self):
        self.connection = await connect_robust(settings.rabbitmq_url)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(
            self.exchange_name,
            durable=True
        )
        logger.info("EventProducer connected to RabbitMQ")
    
    async def disconnect(self):
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()
        logger.info("EventProducer disconnected from RabbitMQ")
    
    async def publish_event(
        self,
        event_type: EventType,
        user_id: int,
        trace_id: str,
        data: dict | None = None
    ):
        if not self.channel or not self.exchange:
            logger.warning("Cannot publish event: not connected")
            return
        
        event = UserEvent(
            event_type=event_type,
            user_id=user_id,
            trace_id=trace_id,
            timestamp=datetime.now(timezone.utc),
            data=data
        )
        
        message_body = msgspec.json.encode(event)
        message = Message(
            body=message_body,
            content_type="application/json",
            headers={"trace_id": trace_id}
        )
        
        await self.exchange.publish(
            message,
            routing_key=event_type.value
        )
        
        logger.info(
            "Event published",
            event_type=event_type.value,
            user_id=user_id,
            trace_id=trace_id
        )


event_producer = EventProducer()
