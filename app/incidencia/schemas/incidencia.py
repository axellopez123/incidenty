from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, List, Union, Any


class IncidenciaBase(BaseModel):
    student_id: int
    date: datetime

    # Usamos Union para ser extremadamente permisivos en la entrada
    leve_faction: Optional[Union[List[str], str]] = None
    leve_other: Optional[str] = None

    grave_faction: Optional[Union[List[str], str]] = None
    grave_other: Optional[str] = None

    muy_grave_faction: Optional[Union[List[str], str]] = None
    muy_grave_other: Optional[str] = None

    description: Optional[str] = None
    disciplinary: Optional[str] = None
    acuerdos_compromisos: Optional[str] = None


class IncidenciaCreate(IncidenciaBase):
    pass


class IncidenciaUpdate(BaseModel):
    date: Optional[datetime] = None
    leve_faction: Optional[Union[List[str], str]] = None
    leve_other: Optional[str] = None
    grave_faction: Optional[Union[List[str], str]] = None
    grave_other: Optional[str] = None
    muy_grave_faction: Optional[Union[List[str], str]] = None
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
        if v is None:
            return []
        if isinstance(v, str):
            return v.split(",") if v else []
        if isinstance(v, list):
            return v
        return []