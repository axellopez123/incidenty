# app/company/schemas/company.py

from pydantic import BaseModel

class CompanyCreate(BaseModel):
    name: str
    rfc: str
