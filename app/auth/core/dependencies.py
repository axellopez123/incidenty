from fastapi import Depends, HTTPException, WebSocket, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from app.auth.core.utils import decode_token
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.auth.models.user import UserDB
from app.database import get_db
from fastapi import Request
import urllib.parse
from datetime import datetime


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado (falta token en cookies)")

    try:
        payload = decode_token(token)
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Token inválido")

        result = await db.execute(select(UserDB).where(UserDB.username == username))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.auth.models.user import UserDB, UserRole
from app.auth.core.utils import hash_password


async def create_user(
    db: AsyncSession,
    username: str,
    password: str,
    email: str | None = None,
    role: UserRole = UserRole.CLIENTE,
    company_id: int | None = None
) -> UserDB:
    """
    Crea un usuario en la base de datos.
    """

    # 🔎 Verificar si ya existe username
    result = await db.execute(
        select(UserDB).where(UserDB.username == username)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El username ya existe"
        )

    # 🔐 Hashear contraseña
    hashed_password = hash_password(password)

    # 👤 Crear usuario
    new_user = UserDB(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role=role,
        company_id=company_id
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user
