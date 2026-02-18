from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EventCreate(BaseModel):
    name: str
    description: str | None = None
    date: datetime
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