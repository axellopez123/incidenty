from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

from app.categories.schemas.category import CategoryOut
from app.distances.schemas.distance import DistanceResponse
from app.phases.schemas.phase import EventCategoryPhaseOut
# =========================
# EventCategory Base
# =========================

class EventCategoryBase(BaseModel):

    price: Optional[int] = 0

    max_participants: Optional[int] = None

    registered_count: Optional[int] = 0

    start_time: Optional[datetime] = None

    end_time: Optional[datetime] = None

    registration_deadline: Optional[datetime] = None

    registration_open: Optional[bool] = True

    status: Optional[str] = "active"


# =========================
# Create
# =========================

class EventCategoryCreate(EventCategoryBase):

    category_id: int
    distance_id: int

# =========================
# Update
# =========================

class EventCategoryUpdate(BaseModel):

    id: Optional[int] = None

    category_id: int
    distance_id: int
    
    price: Optional[int] = None

    max_participants: Optional[int] = None

    start_time: Optional[datetime] = None

    end_time: Optional[datetime] = None

    registration_deadline: Optional[datetime] = None

    registration_open: Optional[bool] = None

    status: Optional[str] = None


# =========================
# Output (CRÍTICO)
# =========================

class EventCategoryOut(EventCategoryBase):

    id: int

    created_at: datetime

    category: CategoryOut
    distance: DistanceResponse

    model_config = ConfigDict(from_attributes=True)
