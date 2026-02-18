
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    date = Column(DateTime, nullable=False)

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="events")

    sponsors = relationship(
        "Sponsor",
        secondary="event_sponsors",
        back_populates="events"
    )