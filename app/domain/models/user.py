from datetime import datetime, timezone
from typing import Optional

from advanced_alchemy.base import BigIntAuditBase
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column


class User(BigIntAuditBase):
    __tablename__ = "users"
    
    name: Mapped[str] = mapped_column(Text, nullable=False)
    surname: Mapped[str] = mapped_column(Text, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
