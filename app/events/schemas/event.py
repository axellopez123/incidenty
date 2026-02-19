from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.events.schemas.event_category import EventCategoryOut


# =========================
# Event Image
# =========================

class EventImageOut(BaseModel):

    id: int
    image_url: str

    is_logo: bool
    is_cover: bool

    order: int

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================
# Event Base
# =========================

class EventBase(BaseModel):

    name: str
    short_name: Optional[str] = None
    description: Optional[str] = None

    status: Optional[str] = "draft"

    start_date: datetime
    end_date: Optional[datetime] = None

    registration_deadline: Optional[datetime] = None

    sport_type: Optional[str] = None
    gender: Optional[str] = None

    max_participants: Optional[int] = None

    location_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

    latitude: Optional[str] = None
    longitude: Optional[str] = None

    registration_open: Optional[bool] = True

    price: Optional[int] = None

    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

    rules: Optional[str] = None
    terms_and_conditions: Optional[str] = None

    company_id: int


# =========================
# Create
# =========================

class EventCreate(EventBase):
    pass


# =========================
# Update
# =========================

class EventUpdate(BaseModel):

    name: Optional[str] = None
    short_name: Optional[str] = None
    description: Optional[str] = None

    status: Optional[str] = None

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    registration_deadline: Optional[datetime] = None

    sport_type: Optional[str] = None
    gender: Optional[str] = None

    max_participants: Optional[int] = None

    location_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

    latitude: Optional[str] = None
    longitude: Optional[str] = None

    registration_open: Optional[bool] = None

    price: Optional[int] = None

    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

    rules: Optional[str] = None
    terms_and_conditions: Optional[str] = None


# =========================
# Output
# =========================

class EventOut(EventBase):

    id: int
    slug: Optional[str]

    banner_url: Optional[str]

    created_at: datetime

    images: List[EventImageOut] = []

    event_categories: List[EventCategoryOut] = []

    model_config = ConfigDict(from_attributes=True)