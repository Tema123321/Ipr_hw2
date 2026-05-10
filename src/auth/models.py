import uuid
from datetime import datetime, timezone
from typing import List

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from src.database import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    email: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String, nullable=False
    )
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    links: Mapped[List["Link"]] = relationship(
        "Link",
        back_populates="user",
        lazy="selectin")