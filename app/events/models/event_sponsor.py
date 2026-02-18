from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database import Base


event_sponsors = Table(
    "event_sponsors",
    Base.metadata,
    Column(
        "event_id",
        Integer,
        ForeignKey("events.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "sponsor_id",
        Integer,
        ForeignKey("sponsors.id", ondelete="CASCADE"),
        primary_key=True
    )
)
