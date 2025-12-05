from datetime import datetime
from enum import Enum

from msgspec import Struct


class EventType(str, Enum):
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"


class UserEvent(Struct):
    event_type: EventType
    user_id: int
    trace_id: str
    timestamp: datetime
    data: dict | None = None
