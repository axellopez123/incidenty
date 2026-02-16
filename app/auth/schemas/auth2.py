from pydantic import BaseModel
from typing import List
from enum import Enum
from typing import Optional

class UserRole(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    CLIENTE = "cliente"
    
    
class UserRegister(BaseModel):
    username: str
    email: Optional[str]
    password: str
    
class AdminCreate(BaseModel):
    username: str
    email: Optional[str]
    password: str
    company_id: int
    
class UserCreate(BaseModel):
    username: str
    password: str
    
class UserOut(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    role: UserRole
    disabled: bool

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None
    disabled: Optional[bool] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
