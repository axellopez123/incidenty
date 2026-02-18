from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.events.models.event import Event
from app.events.schemas.event import EventCreate, EventUpdate, EventOut
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


@router.get("/", response_model=list[EventOut])
async def list_events(
    current_user: UserDB = Depends(RequireRoles("admin", "superadmin", "cliente")),
    db: AsyncSession = Depends(get_db)
):

    query = select(Event)

    # Admin solo su company
    if current_user.role == "admin":
        query = query.where(Event.company_id == current_user.company_id)

    # Cliente solo su company
    if current_user.role == "cliente":
        query = query.where(Event.company_id == current_user.company_id)

    result = await db.execute(query)
    events = result.scalars().all()

    return events


@router.get("/{event_id}", response_model=EventOut)
async def get_event(
    event_id: int,
    current_user: UserDB = Depends(RequireRoles("admin", "superadmin", "cliente")),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )

    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(404, "Evento no encontrado")

    # admin / cliente solo su company
    if current_user.role != "superadmin":
        if event.company_id != current_user.company_id:
            raise HTTPException(403, "No autorizado")

    return event

@router.put("/{event_id}", response_model=EventOut)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    current_user: UserDB = Depends(RequireRoles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )

    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(404, "Evento no encontrado")

    # admin solo su company
    if current_user.role == "admin":
        if event.company_id != current_user.company_id:
            raise HTTPException(403, "No autorizado")

    for key, value in event_data.dict(exclude_unset=True).items():
        setattr(event, key, value)

    await db.commit()
    await db.refresh(event)

    return event

@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    current_user: UserDB = Depends(RequireRoles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )

    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(404, "Evento no encontrado")

    if current_user.role == "admin":
        if event.company_id != current_user.company_id:
            raise HTTPException(403, "No autorizado")

    await db.delete(event)
    await db.commit()

    return {"message": "Evento eliminado correctamente"}