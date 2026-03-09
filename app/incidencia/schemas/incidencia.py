from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class IncidenciaBase(BaseModel):

    student_id: int
    date: datetime

    leve_faction: Optional[str]
    leve_other: Optional[str]

    grave_faction: Optional[str]
    grave_other: Optional[str]

    muy_grave_faction: Optional[str]
    muy_grave_other: Optional[str]

    description: Optional[str]
    disciplinary: Optional[str]
    acuerdos_compromisos: Optional[str]


class IncidenciaCreate(IncidenciaBase):
    pass


class IncidenciaUpdate(BaseModel):

    description: Optional[str]
    disciplinary: Optional[str]
    acuerdos_compromisos: Optional[str]


class IncidenciaResponse(IncidenciaBase):

    id: int

    class Config:
        from_attributes = True