from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from app.events.models.event_categories import EventCategory

class Distance(Base):
    __tablename__ = "distances"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)  # Ej: 5K, 10K, Medio Maratón
    meters = Column(Integer, nullable=False)   # 5000, 10000, 21097
    description = Column(String(300))

    is_active = Column(Boolean, default=True)

    # relaciones
    event_categories = relationship("EventCategory", back_populates="distance")