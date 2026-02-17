# app/company/routes/company.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.company.models.company import Company
from app.company.schemas.company import CompanyCreate
from app.auth.models.user import UserDB, UserRole
from app.auth.core.dependencies import get_current_user

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("/")
async def create_company(
    company_data: CompanyCreate,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    # 🔐 Solo SUPERADMIN puede crear companies
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=403,
            detail="Solo el superadmin puede crear companies"
        )

    # Verificar que no exista
    result = await db.execute(
        select(Company).where(Company.name == company_data.name)
    )

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Company ya existe"
        )

    new_company = Company(name=company_data.name)

    db.add(new_company)
    await db.commit()
    await db.refresh(new_company)

    return {
        "message": "Company creada correctamente",
        "company_id": new_company.id
    }
