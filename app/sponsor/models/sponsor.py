from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.events.models.event_sponsor import event_sponsors


class Sponsor(Base):
    __tablename__ = "sponsors"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)

    logo_url = Column(String(500), nullable=True)

    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False
    )

    # relaciones
    company = relationship("Company", back_populates="sponsors")

    events = relationship(
        "Event",
        secondary="event_sponsors",
        back_populates="sponsors"
    )