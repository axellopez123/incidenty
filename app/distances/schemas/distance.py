from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# 🔹 Base
class DistanceBase(BaseModel):
    name: str = Field(..., max_length=100, example="10K")
    meters: int = Field(..., gt=0, example=10000)
    description: Optional[str] = Field(None, max_length=300)
    is_active: Optional[bool] = True


# 🔹 Create
class DistanceCreate(DistanceBase):
    pass


# 🔹 Update
class DistanceUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    meters: Optional[int] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=300)
    is_active: Optional[bool]


# 🔹 Response
class DistanceResponse(DistanceBase):
    id: int

    class Config:
        from_attributes = True
