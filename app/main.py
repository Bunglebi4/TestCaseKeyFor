from contextlib import asynccontextmanager

from advanced_alchemy.extensions.litestar import AlembicCommands, SQLAlchemyPlugin
from litestar import Litestar
from litestar.openapi import OpenAPIConfig

from app.api.middleware import trace_id_middleware
from app.api.routes.users import UserController
from app.infrastructure.database import sqlalchemy_config
from app.infrastructure.logging import configure_logging, get_logger
from app.infrastructure.messaging import event_consumer, event_producer

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: Litestar):
    logger.info("Application starting")
    
    try:
        await event_producer.connect()
    except Exception as e:
        logger.error("Failed to connect event producer", error=str(e))
    
    try:
        await event_consumer.connect()
        await event_consumer.start_consuming()
    except Exception as e:
        logger.error("Failed to connect event consumer", error=str(e))
    
    yield
    
    logger.info("Application shutting down")
    
    try:
        await event_producer.disconnect()
    except Exception as e:
        logger.error("Error disconnecting event producer", error=str(e))
    
    try:
        await event_consumer.disconnect()
    except Exception as e:
        logger.error("Error disconnecting event consumer", error=str(e))


app = Litestar(
    route_handlers=[UserController],
    middleware=[trace_id_middleware],
    plugins=[SQLAlchemyPlugin(config=sqlalchemy_config)],
    openapi_config=OpenAPIConfig(
        title="User Management API",
        version="1.0.0",
        description="REST API for user management with LiteStar",
    ),
    lifespan=[lifespan],
    debug=True,
)
