
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.events.models.event_sponsor import event_sponsors
from app.events.models.event_categories import EventCategory
from app.categories.models.category import Category

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    # identidad
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, index=True)
    short_name = Column(String(100))
    description = Column(String)

    status = Column(String(50), default="draft")

    # fechas
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)

    registration_deadline = Column(DateTime)

    # deporte
    sport_type = Column(String(50))
    gender = Column(String(20))

    max_participants = Column(Integer)

    # ubicación
    location_name = Column(String(200))
    address = Column(String(300))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))

    latitude = Column(String(50))
    longitude = Column(String(50))

    registration_open = Column(Boolean, default=True)

    price = Column(Integer)

    contact_email = Column(String(200))
    contact_phone = Column(String(50))

    rules = Column(String)

    terms_and_conditions = Column(String)

    banner_url = Column(String)


    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    distance_id = Column(
        Integer,
        ForeignKey("distances.id", ondelete="RESTRICT"),
        nullable=False
    )
    
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="events")

    sponsors = relationship(
        "Sponsor",
        secondary="event_sponsors",
        back_populates="events"
    )

    images = relationship(
        "EventImage",
        back_populates="event",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    event_categories = relationship(
        "EventCategory",
        back_populates="event",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    distance = relationship(
        "Distance",
        back_populates="distance"
    )




class EventImage(Base):
    __tablename__ = "event_images"

    id = Column(Integer, primary_key=True)

    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"))

    image_url = Column(String(500))

    is_logo = Column(Boolean, default=False)
    is_cover = Column(Boolean, default=False)

    order = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("Event", back_populates="images")
