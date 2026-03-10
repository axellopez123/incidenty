from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, List


class IncidenciaBase(BaseModel):
    student_id: int
    date: datetime

    leve_faction: Optional[List[str]] = None
    leve_other: Optional[str] = None

    grave_faction: Optional[List[str]] = None
    grave_other: Optional[str] = None

    muy_grave_faction: Optional[List[str]] = None
    muy_grave_other: Optional[str] = None

    description: Optional[str] = None
    disciplinary: Optional[str] = None
    acuerdos_compromisos: Optional[str] = None


class IncidenciaCreate(IncidenciaBase):
    pass


class IncidenciaUpdate(BaseModel):
    date: Optional[datetime] = None
    leve_faction: Optional[List[str]] = None
    leve_other: Optional[str] = None
    grave_faction: Optional[List[str]] = None
    grave_other: Optional[str] = None
    muy_grave_faction: Optional[List[str]] = None
    muy_grave_other: Optional[str] = None
    description: Optional[str] = None
    disciplinary: Optional[str] = None
    acuerdos_compromisos: Optional[str] = None


class IncidenciaResponse(IncidenciaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

    @field_validator("leve_faction", "grave_faction", "muy_grave_faction", mode="before")
    @classmethod
    def split_string(cls, v):
        if isinstance(v, str) and v:
            return v.split(",")
        if isinstance(v, list):
            return v
        return []