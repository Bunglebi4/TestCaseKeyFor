import msgspec
from aio_pika import Connection, connect_robust
from aio_pika.abc import AbstractIncomingMessage

from app.core import settings
from app.infrastructure.logging import bind_trace_id, get_logger
from app.infrastructure.messaging.events import UserEvent

logger = get_logger(__name__)


class EventConsumer:
    def __init__(self):
        self.connection: Connection | None = None
        self.exchange_name = "user_events"
    
    async def connect(self):
        self.connection = await connect_robust(settings.rabbitmq_url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=10)
        
        self.exchange = await self.channel.declare_exchange(
            self.exchange_name,
            durable=True
        )
        
        self.queue = await self.channel.declare_queue(
            "user_events_queue",
            durable=True
        )
        
        await self.queue.bind(self.exchange, routing_key="user.*")
        
        logger.info("EventConsumer connected to RabbitMQ")
    
    async def start_consuming(self):
        if not self.queue:
            logger.error("Cannot start consuming: not connected")
            return
        
        await self.queue.consume(self._process_message)
        logger.info("EventConsumer started consuming messages")
    
    async def _process_message(self, message: AbstractIncomingMessage):
        async with message.process():
            try:
                event = msgspec.json.decode(message.body, type=UserEvent)
                
                bind_trace_id(event.trace_id)
                
                logger.info(
                    "Event received",
                    event_type=event.event_type,
                    user_id=event.user_id,
                    timestamp=event.timestamp.isoformat()
                )
                
            except Exception as e:
                logger.error("Error processing message", error=str(e))
    
    async def disconnect(self):
        if self.connection:
            await self.connection.close()
        logger.info("EventConsumer disconnected from RabbitMQ")


event_consumer = EventConsumer()
