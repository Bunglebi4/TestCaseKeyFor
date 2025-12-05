from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import User
from app.domain.repositories import AsyncUserRepository
from app.infrastructure.logging import get_logger, get_trace_id
from app.infrastructure.messaging import EventType, event_producer
from app.schemas import UserCreate, UserUpdate

logger = get_logger(__name__)


class UserService:
    def __init__(self, session: AsyncSession):
        self.repository = AsyncUserRepository(session)
        self.session = session
    
    async def create_user(self, user_data: UserCreate) -> User:
        user = User(
            name=user_data.name,
            surname=user_data.surname,
            password=user_data.password
        )
        
        user = await self.repository.create(user)
        await self.session.commit()
        
        logger.info("User created", user_id=user.id)
        
        trace_id = get_trace_id() or "unknown"
        await event_producer.publish_event(
            event_type=EventType.USER_CREATED,
            user_id=user.id,
            trace_id=trace_id,
            data={"name": user.name, "surname": user.surname}
        )
        
        return user
    
    async def get_user(self, user_id: int) -> Optional[User]:
        user = await self.repository.get_by_id(user_id)
        if user:
            logger.info("User retrieved", user_id=user_id)
        else:
            logger.warning("User not found", user_id=user_id)
        return user
    
    async def list_users(self, limit: int = 100, offset: int = 0) -> list[User]:
        users = await self.repository.get_all(limit=limit, offset=offset)
        logger.info("Users listed", count=len(users))
        return users
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        user = await self.repository.get_by_id(user_id)
        if not user:
            logger.warning("User not found for update", user_id=user_id)
            return None
        
        if user_data.name is not None:
            user.name = user_data.name
        if user_data.surname is not None:
            user.surname = user_data.surname
        if user_data.password is not None:
            user.password = user_data.password
        
        user = await self.repository.update(user)
        await self.session.commit()
        
        logger.info("User updated", user_id=user_id)
        
        trace_id = get_trace_id() or "unknown"
        await event_producer.publish_event(
            event_type=EventType.USER_UPDATED,
            user_id=user.id,
            trace_id=trace_id,
            data={"name": user.name, "surname": user.surname}
        )
        
        return user
    
    async def delete_user(self, user_id: int) -> bool:
        user = await self.repository.get_by_id(user_id)
        if not user:
            logger.warning("User not found for deletion", user_id=user_id)
            return False
        
        await self.repository.delete(user)
        await self.session.commit()
        
        logger.info("User deleted", user_id=user_id)
        
        trace_id = get_trace_id() or "unknown"
        await event_producer.publish_event(
            event_type=EventType.USER_DELETED,
            user_id=user_id,
            trace_id=trace_id
        )
        
        return True
