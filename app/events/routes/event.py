from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_
from app.database import get_db
from app.events.models.event import Event, EventImage
from app.events.schemas.event import EventCreate, EventUpdate, EventOut
from app.auth.models.user import UserDB
from app.events.models.event_categories import EventCategory
from app.categories.models.category import Category
from app.auth.core.permissions import RequireRoles
from app.company.models.company import Company
from typing import List, Optional
import os
import uuid
from datetime import datetime
import slugify
import json
import app.events.schemas.event_category import EventCategoryCreate

STORAGE_PATH = "storage/events"

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/", response_model=EventOut)
async def create_event(

    name: str = Form(...),
    short_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),

    status: Optional[str] = Form("draft"),

    start_date: datetime = Form(...),
    end_date: Optional[datetime] = Form(None),

    registration_deadline: Optional[datetime] = Form(None),

    sport_type: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),

    max_participants: Optional[int] = Form(None),

    location_name: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    country: Optional[str] = Form(None),

    latitude: Optional[str] = Form(None),
    longitude: Optional[str] = Form(None),

    registration_open: Optional[bool] = Form(True),

    price: Optional[int] = Form(None),

    contact_email: Optional[str] = Form(None),
    contact_phone: Optional[str] = Form(None),

    rules: Optional[str] = Form(None),
    terms_and_conditions: Optional[str] = Form(None),

    company_id: int = Form(...),
    categories: Optional[str] = Form(None),
    logo: Optional[UploadFile] = File(None),
    cover: Optional[UploadFile] = File(None),
    gallery: Optional[List[UploadFile]] = File(None),

    current_user: UserDB = Depends(RequireRoles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)

):

    # validar company
    result = await db.execute(
        select(Company).where(Company.id == company_id)
    )

    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(404, "Company no existe")

    if current_user.role == "admin":
        if current_user.company_id != company_id:
            raise HTTPException(403, "No autorizado")

    # crear slug
    slug = slugify.slugify(name)

    new_event = Event(

        name=name,
        slug=slug,
        short_name=short_name,
        description=description,

        status=status,

        start_date=start_date,
        end_date=end_date,

        registration_deadline=registration_deadline,

        sport_type=sport_type,
        gender=gender,

        max_participants=max_participants,

        location_name=location_name,
        address=address,
        city=city,
        state=state,
        country=country,

        latitude=latitude,
        longitude=longitude,

        registration_open=registration_open,

        price=price,

        contact_email=contact_email,
        contact_phone=contact_phone,

        rules=rules,
        terms_and_conditions=terms_and_conditions,

        company_id=company_id

    )

    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)


    if categories:

        categories_data = [
            EventCategoryCreate(**item)
            for item in json.loads(categories)
        ]

        for item in categories_data:

            # validar category existe
            result = await db.execute(
                select(Category).where(
                    Category.id == item["category_id"]
                )
            )

            category = result.scalar_one_or_none()

            if not category:
                raise HTTPException(
                    404,
                    f"Category {item['category_id']} no existe"
                )

            event_category = EventCategory(

                event_id=new_event.id,
                category_id=item["category_id"],

                price=item.get("price"),
                max_participants=item.get("max_participants"),

                start_time=item.get("start_time"),
                end_time=item.get("end_time"),

                registration_deadline=item.get(
                    "registration_deadline"
                )
            )

            db.add(event_category)
            

    event_folder = f"{STORAGE_PATH}/{new_event.id}"
    os.makedirs(event_folder, exist_ok=True)

    # LOGO
    if logo:

        path = await save_upload_file(logo, event_folder)

        db.add(EventImage(
            event_id=new_event.id,
            image_url=path,
            is_logo=True
        ))

    # COVER
    if cover:

        path = await save_upload_file(cover, event_folder)

        db.add(EventImage(
            event_id=new_event.id,
            image_url=path,
            is_cover=True
        ))

        new_event.banner_url = path

    # GALLERY
    if gallery:

        for index, image in enumerate(gallery):

            path = await save_upload_file(image, event_folder)

            db.add(EventImage(
                event_id=new_event.id,
                image_url=path,
                order=index
            ))

    await db.commit()
    await db.refresh(new_event)

    return new_event

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