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
    email: str
    password: str


class AdminCreate(BaseModel):
    username: str
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: Optional[str]
    role: UserRole
    is_active: bool
    company_id: Optional[int]

    class Config:
        from_attributes = True


class UserSelfUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None


class UserAdminUpdate(BaseModel):
    is_active: Optional[bool] = None


class UserRoleUpdate(BaseModel):
    role: UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

