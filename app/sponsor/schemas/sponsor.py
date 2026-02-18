from pydantic import BaseModel
from typing import Optional


class SponsorCreate(BaseModel):
    name: str
    logo_url: Optional[str] = None


class SponsorUpdate(BaseModel):
    name: Optional[str] = None
    logo_url: Optional[str] = None


class SponsorOut(BaseModel):
    id: int
    name: str
    logo_url: Optional[str]
    company_id: int

    class Config:
        from_attributes = True
