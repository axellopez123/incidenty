from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.events.models.event import Event
from app.events.schemas.event import EventCreate, EventUpdate, EventOut
from app.auth.models.user import UserDB
from app.auth.core.permissions import RequireRoles
from app.company.models.company import Company
from typing import List, Optional
import os
import uuid
from datetime import datetime

STORAGE_PATH = "storage/events"

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/")
async def create_event(
    name: str = Form(...),
    description: str = Form(None),
    date: datetime = Form(...),
    company_id: int = Form(...),

    logo: Optional[UploadFile] = File(None),
    gallery: Optional[List[UploadFile]] = File(None),

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

    # Crear carpeta del evento
    event_folder = f"{STORAGE_PATH}/{new_event.id}"
    os.makedirs(event_folder, exist_ok=True)


    # Guardar logo
    if logo:

        ext = logo.filename.split(".")[-1]
        filename = f"logo.{ext}"

        path = f"{event_folder}/{filename}"

        with open(path, "wb") as buffer:
            buffer.write(await logo.read())

        db.add(EventImage(
            event_id=new_event.id,
            image_url=path,
            is_logo=True
        ))


    # Guardar galería
    if gallery:

        for index, image in enumerate(gallery):

            ext = image.filename.split(".")[-1]
            filename = f"{uuid.uuid4()}.{ext}"

            path = f"{event_folder}/{filename}"

            with open(path, "wb") as buffer:
                buffer.write(await image.read())

            db.add(EventImage(
                event_id=new_event.id,
                image_url=path,
                order=index
            ))


    await db.commit()

    return {
        "message": "Evento creado correctamente",
        "event_id": new_event.id
    }

async def save_upload_file(file: UploadFile, folder: str):

    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"

    path = f"{folder}/{filename}"

    with open(path, "wb") as buffer:
        buffer.write(await file.read())

    return path

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

@router.get("/pagination/", response_model=list[EventOut])
async def list_events(
    skip: int = 0,
    limit: int = Query(default=20, le=100),
    sport_type: str | None = None,
    status: str | None = None,
    company_id: int | None = None,

    current_user: UserDB = Depends(
        RequireRoles("admin", "superadmin", "cliente")
    ),

    db: AsyncSession = Depends(get_db)
):

    query = select(Event).options(
        selectinload(Event.company),
        selectinload(Event.sponsors),
        selectinload(Event.images)
    )

    filters = []

    # permisos
    if current_user.role != "superadmin":
        filters.append(Event.company_id == current_user.company_id)

    # filtros opcionales
    if sport_type:
        filters.append(Event.sport_type == sport_type)

    if status:
        filters.append(Event.status == status)

    if company_id and current_user.role == "superadmin":
        filters.append(Event.company_id == company_id)

    if filters:
        query = query.where(and_(*filters))

    query = query.offset(skip).limit(limit).order_by(Event.created_at.desc())

    result = await db.execute(query)

    return result.scalars().all()


@router.get("/{event_id}", response_model=EventOut)
async def get_event(
    event_id: int,
    current_user: UserDB = Depends(RequireRoles("admin", "superadmin", "cliente")),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Event)
        .options(
            selectinload(Event.company),
            selectinload(Event.images),
            selectinload(Event.sponsors)
        )
        .where(Event.id == event_id)
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