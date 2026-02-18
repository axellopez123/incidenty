from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class EventCreate(BaseModel):

    name: str
    description: str | None = None

    start_date: datetime
    end_date: datetime | None = None

    sport_type: str | None = None

    category: str | None = None

    location_name: str | None = None

    city: str | None = None

    country: str | None = None

    company_id: int


class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None


class EventOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    date: datetime
    company_id: int

    class Config:
        from_attributes = True