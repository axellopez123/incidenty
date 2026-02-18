from pydantic import BaseModel
from datetime import datetime

class EventCreate(BaseModel):
    name: str
    description: str | None = None
    date: datetime
    company_id: int