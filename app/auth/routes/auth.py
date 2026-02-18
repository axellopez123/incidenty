from fastapi import APIRouter, Depends, HTTPException, status, Body, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.auth.schemas.auth import UserRole, UserRegister, AdminCreate, UserOut, UserSelfUpdate, UserAdminUpdate, UserRoleUpdate, Token, LoginRequest
from app.auth.core.utils import hash_password, verify_password, create_access_token
from app.database import get_db
from app.auth.models.user import UserDB, UserRole
from app.company.models.company import Company
from app.auth.core.dependencies import get_current_user
from sqlalchemy.orm import selectinload
from fastapi.responses import JSONResponse
from sqlalchemy import or_
from typing import List


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
async def register(user: UserRegister, db: AsyncSession = Depends(get_db)):

    # Normalizar email
    email = user.email.lower()

    # Verificar si ya existe username o email
    result = await db.execute(
        select(UserDB).where(
            or_(
                UserDB.username == user.username,
                UserDB.email == email
            )
        )
    )

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Usuario o email ya registrado"
        )

    # Crear usuario como CLIENTE (forzado desde backend)
    new_user = UserDB(
        username=user.username,
        email=email,
        hashed_password=hash_password(user.password),
        role=UserRole.CLIENTE,
        company_id=None,
        disabled=False
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Crear JWT con info necesaria
    token = create_access_token({
        "sub": new_user.username,
        "role": new_user.role,
        "company_id": new_user.company_id
    })

    response = JSONResponse(
        content={"message": "Registro exitoso"}
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,      # solo HTTPS en producción
        samesite="None",  # o "Strict" si frontend y backend mismo dominio
        max_age=1800,
        path="/"
    )

    return response


@router.post("/register/admin")
async def create_admin(
    admin_data: AdminCreate,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    # 🔐 Solo SUPER_ADMIN
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=403,
            detail="Solo el superadmin puede crear administradores"
        )

    # verificar company
    result = await db.execute(
        select(Company).where(Company.id == admin_data.company_id)
    )

    # Verificar email duplicado
    result = await db.execute(
        select(UserDB).where(UserDB.email == admin_data.email.lower())
    )

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Email ya registrado"
        )

    # Crear admin
    new_admin = UserDB(
        username=admin_data.username,
        email=admin_data.email.lower(),
        hashed_password=hash_password(admin_data.password),
        role=UserRole.ADMIN,
        company_id=admin_data.company_id,
        disabled=False
    )

    db.add(new_admin)
    await db.commit()
    await db.refresh(new_admin)

    return {"message": "Administrador creado correctamente"}



async def authenticate_user(
    db: AsyncSession,
    username: str,
    password: str
) -> UserDB | None:

    result = await db.execute(
        select(UserDB).where(UserDB.username == username)
    )

    user = result.scalar_one_or_none()

    if not user:
        return None
        
    if not verify_password(password, user.hashed_password):
        return None
        

    if user.disabled:
        return None
        

    return user


@router.post("/api/client/login")
async def login_client(
    data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):

    user = await authenticate_user(db, data.username, data.password)

    if not user:
        raise HTTPException(401, "Credenciales incorrectas")

    # permitir solo cliente y superadmin
    if user.role not in ["cliente", "superadmin"]:
        raise HTTPException(403, "No autorizado para sistema cliente")

    token = create_access_token({
        "sub": user.username,
        "user_id": user.id,
        "role": user.role,
        "company_id": user.company_id,
        "system": "client"
    })

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax"
    )

    return {
        "message": "Login cliente exitoso",
        "role": user.role
    }


@router.post("/api/admin/login")
async def login_admin(
    data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):

    user = await authenticate_user(db, data.username, data.password)

    if not user:
        raise HTTPException(401, "Credenciales incorrectas")

    # permitir solo admin y superadmin
    if user.role not in ["admin", "superadmin"]:
        raise HTTPException(403, "No autorizado para sistema admin")

    token = create_access_token({
        "sub": user.username,
        "user_id": user.id,
        "role": user.role,
        "company_id": user.company_id,
        "system": "admin"
    })

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax"
    )

    return {
        "message": "Login admin exitoso",
        "role": user.role
    }
    
    
    
@router.get("/me")
async def get_session_info(
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    # cargar company si existe
    company = None

    if current_user.company_id:
        result = await db.execute(
            select(Company).where(Company.id == current_user.company_id)
        )
        company = result.scalar_one_or_none()

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,

        "company": {
            "id": company.id,
            "name": company.name,
            "rfc": company.rfc
        } if company else None,

        "company_id": current_user.company_id,

        "is_active": current_user.is_active
    }