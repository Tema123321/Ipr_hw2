from datetime import datetime, timezone
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from src.database import Base


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True)
    original_url = Column(String, nullable=False)
    short_id = Column(String, nullable=False, unique=True, index=True)
    custom_alias = Column(String, unique=True, index=True, nullable=True)
    click_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    expire_at = Column(DateTime(timezone=True), nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    user = relationship("User", back_populates="links", lazy="selectin")