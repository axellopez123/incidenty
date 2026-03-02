from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class EventCategoryPhaseBase(BaseModel):
    name: str
    price: int
    start_date: datetime
    end_date: datetime
    is_active: Optional[bool] = True

class EventCategoryPhaseCreate(EventCategoryPhaseBase):
    event_category_id: int

class EventCategoryPhaseUpdate(BaseModel):
    name: Optional[str]
    price: Optional[int]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    is_active: Optional[bool]

class EventCategoryPhaseOut(EventCategoryPhaseBase):
    id: int
    status: str   # 🔥 dinámico

    model_config = ConfigDict(from_attributes=True)