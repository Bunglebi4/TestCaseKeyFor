from datetime import datetime
from typing import Optional

from msgspec import Struct


class UserCreate(Struct):
    name: str
    surname: str
    password: str


class UserUpdate(Struct):
    name: Optional[str] = None
    surname: Optional[str] = None
    password: Optional[str] = None


class UserResponse(Struct):
    id: int
    name: str
    surname: str
    created_at: datetime
    updated_at: datetime
