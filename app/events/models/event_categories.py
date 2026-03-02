from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.distances.models.distance import Distance
from app.categories.models.category import Category


class EventCategory(Base):

    __tablename__ = "event_categories"

    id = Column(Integer, primary_key=True)

    event_id = Column(
        Integer,
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False
    )
    
    distance_id = Column(
        Integer,
        ForeignKey("distances.id", ondelete="RESTRICT"),
        nullable=False
    )
    
    # configuración específica
    price = Column(Integer, default=0)

    max_participants = Column(Integer)

    registered_count = Column(Integer, default=0)

    # horarios específicos
    start_time = Column(DateTime)

    end_time = Column(DateTime)

    registration_deadline = Column(DateTime)

    # control
    registration_open = Column(Boolean, default=True)

    status = Column(String(50), default="active")
    # active, sold_out, closed, cancelled

    created_at = Column(DateTime, default=datetime.utcnow)

    # relaciones
    event = relationship(
        "Event",
        back_populates="event_categories"
    )

    category = relationship(
        "Category",
        back_populates="event_categories"
    )
    
    distance = relationship(
        "Distance",
        back_populates="event_categories"
    )