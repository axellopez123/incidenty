from pydantic import BaseModel
from typing import Optional


class StudentBase(BaseModel):

    name: str
    grade: Optional[str]
    group: Optional[str]


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):

    name: Optional[str]
    grade: Optional[str]
    group: Optional[str]


class StudentResponse(StudentBase):

    id: int

    class Config:
        from_attributes = True