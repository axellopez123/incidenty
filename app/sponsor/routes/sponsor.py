from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List

from app.database import get_db
from app.auth.models.user import UserDB, UserRole
from app.auth.core.dependencies import get_current_user
from app.auth.core.permissions import RequireRoles

from app.sponsor.models.sponsor import Sponsor
from app.sponsor.schemas.sponsor import (
    SponsorCreate,
    SponsorUpdate,
    SponsorOut
)

router = APIRouter(
    prefix="/sponsors",
    tags=["Sponsors"]
)


@router.post(
    "/",
    response_model=SponsorOut,
    dependencies=[Depends(RequireRoles("admin", "superadmin"))]
)
async def create_sponsor(
    data: SponsorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):

    if current_user.role == UserRole.ADMIN:
        company_id = current_user.company_id

    elif current_user.role == UserRole.SUPERADMIN:

        if not current_user.company_id:
            raise HTTPException(
                status_code=400,
                detail="Superadmin debe seleccionar company"
            )

        company_id = current_user.company_id

    sponsor = Sponsor(
        name=data.name,
        logo_url=data.logo_url,
        company_id=company_id
    )

    db.add(sponsor)

    await db.commit()
    await db.refresh(sponsor)

    return sponsor


@router.get(
    "/",
    response_model=List[SponsorOut],
    dependencies=[Depends(RequireRoles("admin", "superadmin"))]
)
async def get_sponsors(
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):

    if current_user.role == UserRole.ADMIN:
        company_id = current_user.company_id

    else:
        company_id = current_user.company_id

    result = await db.execute(
        select(Sponsor).where(
            Sponsor.company_id == company_id
        )
    )

    sponsors = result.scalars().all()

    return sponsors


@router.get(
    "/{sponsor_id}",
    response_model=SponsorOut,
    dependencies=[Depends(RequireRoles("admin", "superadmin"))]
)
async def get_sponsor(
    sponsor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):

    result = await db.execute(
        select(Sponsor).where(
            Sponsor.id == sponsor_id,
            Sponsor.company_id == current_user.company_id
        )
    )

    sponsor = result.scalar_one_or_none()

    if not sponsor:
        raise HTTPException(404, "Sponsor no encontrado")

    return sponsor


@router.put(
    "/{sponsor_id}",
    response_model=SponsorOut,
    dependencies=[Depends(RequireRoles("admin", "superadmin"))]
)
async def update_sponsor(
    sponsor_id: int,
    data: SponsorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):

    result = await db.execute(
        select(Sponsor).where(
            Sponsor.id == sponsor_id,
            Sponsor.company_id == current_user.company_id
        )
    )

    sponsor = result.scalar_one_or_none()

    if not sponsor:
        raise HTTPException(404, "Sponsor no encontrado")

    if data.name is not None:
        sponsor.name = data.name

    if data.logo_url is not None:
        sponsor.logo_url = data.logo_url

    await db.commit()
    await db.refresh(sponsor)

    return sponsor

@router.delete(
    "/{sponsor_id}",
    dependencies=[Depends(RequireRoles("admin", "superadmin"))]
)
async def delete_sponsor(
    sponsor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):

    result = await db.execute(
        select(Sponsor).where(
            Sponsor.id == sponsor_id,
            Sponsor.company_id == current_user.company_id
        )
    )

    sponsor = result.scalar_one_or_none()

    if not sponsor:
        raise HTTPException(404, "Sponsor no encontrado")

    await db.delete(sponsor)

    await db.commit()

    return {"message": "Sponsor eliminado correctamente"}