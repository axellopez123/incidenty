from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Category(Base):

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    slug = Column(String(120), unique=True, index=True)

    description = Column(String(300))

    # clasificación
    gender = Column(String(20))  # male, female, mixed

    min_age = Column(Integer)

    max_age = Column(Integer)

    # control
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # relación pivote
    event_categories = relationship(
        "EventCategory",
        back_populates="category",
        cascade="all, delete-orphan",
        lazy="selectin"
    )