from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class CategoryBase(BaseModel):

    name: str

    description: Optional[str] = None

    gender: Optional[str] = None

    min_age: Optional[int] = None

    max_age: Optional[int] = None


class CategoryCreate(CategoryBase):

    pass


class CategoryOut(BaseModel):

    id: int

    name: str

    slug: str

    description: Optional[str]

    gender: Optional[str]

    min_age: Optional[int]

    max_age: Optional[int]

    is_active: bool

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)