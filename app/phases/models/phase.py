from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class EventCategoryPhase(Base):

    __tablename__ = "event_category_phases"

    id = Column(Integer, primary_key=True)

    event_category_id = Column(
        Integer,
        ForeignKey("event_categories.id", ondelete="CASCADE"),
        nullable=False
    )

    name = Column(String(100), nullable=False)  # Preventa, Regular, Late

    price = Column(Integer, nullable=False)

    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    event_category = relationship(
        "EventCategory",
        back_populates="phases"
    )