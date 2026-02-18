# app/event/routes/event.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.event.models.event import Event
from app.event.schemas.event import EventCreate
from app.auth.models.user import UserDB
from app.auth.core.permissions import RequireRoles
from app.company.models.company import Company

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/")
async def create_event(
    event_data: EventCreate,
    current_user: UserDB = Depends(RequireRoles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):

    # 🔐 Solo admin o superadmin
    if current_user.role not in ["admin", "superadmin"]:
        raise HTTPException(403, "No autorizado")

    # Verificar que la company exista
    result = await db.execute(
        select(Company).where(Company.id == event_data.company_id)
    )

    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(404, "Company no existe")

    # 🔐 Si es admin, solo puede crear en SU company
    if current_user.role == "admin":
        if current_user.company_id != event_data.company_id:
            raise HTTPException(403, "No puedes crear eventos para otra company")

    new_event = Event(
        name=event_data.name,
        description=event_data.description,
        date=event_data.date,
        company_id=event_data.company_id
    )

    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)

    return {
        "message": "Evento creado correctamente",
        "event_id": new_event.id
    }
