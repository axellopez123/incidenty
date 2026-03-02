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
from app.distances.models.distance import Distance
from app.auth.core.permissions import RequireRoles
from app.company.models.company import Company
from typing import List, Optional
import os
import uuid
from datetime import datetime
import slugify
import json
from app.events.schemas.event_category import EventCategoryCreate, EventCategoryUpdate

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
    # await db.refresh(new_event)
    await db.flush()   # para obtener IDs


    if categories:

        categories_data = [
            EventCategoryCreate(**item)
            for item in json.loads(categories)
        ]

        for item in categories_data:

            # validar category existe
            result = await db.execute(
                select(Category).where(
                    Category.id == item.category_id
                )
            )

            category = result.scalar_one_or_none()

            if not category:
                raise HTTPException(
                    404,
                    f"Category {item.category_id} no existe"
                )
                
                
            result = await db.execute(
                select(Distance).where(Distance.id == item.distance_id)
            )

            distance = result.scalar_one_or_none()

            if not distance:
                raise HTTPException(
                    404,
                    f"Distance {item.distance_id} no existe"
                )
                
            result = await db.execute(
                select(EventCategory).where(
                    EventCategory.event_id == new_event.id,
                    EventCategory.category_id == item.category_id,
                    EventCategory.distance_id == item.distance_id
                )
            )

            existing = result.scalar_one_or_none()

            if existing:
                raise HTTPException(
                    400,
                    "Esta combinación de categoría y distancia ya existe para este evento"
                )
                
            event_category = EventCategory(
                event_id=new_event.id,
                category_id=item.category_id,
                distance_id=item.distance_id,
                
                price=item.price,
                max_participants=item.max_participants,

                start_time=item.start_time,
                end_time=item.end_time,

                registration_deadline=item.registration_deadline
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
    # await db.refresh(new_event)

    # return new_event
    result = await db.execute(
        select(Event)
        .options(
            selectinload(Event.event_categories)
            .selectinload(EventCategory.category),

            selectinload(Event.images)
        )
        .where(Event.id == new_event.id)
    )

    event_full = result.scalar_one()

    return event_full
    

async def save_upload_file(file: UploadFile, folder: str):

    ext = file.filename.split(".")[-1]

    filename = f"{uuid.uuid4()}.{ext}"

    path = f"{folder}/{filename}"

    with open(path, "wb") as buffer:
        buffer.write(await file.read())

    return path

@router.get("/", response_model=list[EventOut])
async def list_events(
    current_user: UserDB = Depends(RequireRoles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):

    query = select(Event).options(
        selectinload(Event.event_categories)
        .selectinload(EventCategory.category),
        
        selectinload(Event.images)
        )



    # Admin solo su company
    if current_user.role == "admin":
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
        selectinload(Event.event_categories)
        .selectinload(EventCategory.category),
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
            selectinload(Event.event_categories)
            .selectinload(EventCategory.category),
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

    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),

    start_date: Optional[datetime] = Form(None),
    end_date: Optional[datetime] = Form(None),

    categories: Optional[str] = Form(None),
    sponsors: Optional[str] = Form(None),

    keep_gallery: Optional[str] = Form(None),

    logo: Optional[UploadFile] = File(None),
    cover: Optional[UploadFile] = File(None),
    gallery: Optional[List[UploadFile]] = File(None),

    current_user: UserDB = Depends(RequireRoles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)

):

    # async with db.begin():

    result = await db.execute(
        select(Event)
        .options(
            selectinload(Event.event_categories),
            selectinload(Event.images),
            selectinload(Event.sponsors)
        )
        .where(Event.id == event_id)
    )

    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(404, "Evento no encontrado")

    # permiso
    if current_user.role == "admin":
        if event.company_id != current_user.company_id:
            raise HTTPException(403, "No autorizado")


    # =========================
    # UPDATE BASIC FIELDS
    # =========================

    if name is not None:
        event.name = name

    if description is not None:
        event.description = description

    if start_date is not None:
        event.start_date = start_date

    if end_date is not None:
        event.end_date = end_date


    # =========================
    # SYNC CATEGORIES
    # =========================

    if categories is not None:

        incoming = [
            EventCategoryUpdate(**item)
            for item in json.loads(categories)
        ]

        incoming_ids = {
            item.id for item in incoming if item.id
        }

        existing = {
            ec.id: ec for ec in event.event_categories
        }


        # DELETE
        for ec_id, ec in existing.items():
            if ec_id not in incoming_ids:
                await db.delete(ec)


        # UPDATE / CREATE
        for item in incoming:

            if item.id and item.id in existing:

                ec = existing[item.id]

                ec.category_id = item.category_id
                ec.price = item.price
                ec.max_participants = item.max_participants
                ec.start_time = item.start_time
                ec.end_time = item.end_time
                ec.registration_deadline = item.registration_deadline
                ec.registration_open = item.registration_open
                ec.status = item.status

            else:

                db.add(EventCategory(
                    event_id=event.id,
                    category_id=item.category_id,
                    price=item.price,
                    max_participants=item.max_participants,
                    start_time=item.start_time,
                    end_time=item.end_time,
                    registration_deadline=item.registration_deadline,
                    registration_open=item.registration_open,
                    status=item.status
                ))


    # =========================
    # SYNC SPONSORS
    # =========================

    if sponsors is not None:

        sponsor_ids = json.loads(sponsors)

        result = await db.execute(
            select(Sponsor)
            .where(Sponsor.id.in_(sponsor_ids))
        )

        event.sponsors = result.scalars().all()


    # =========================
    # IMAGE FOLDER
    # =========================

    event_folder = f"{STORAGE_PATH}/{event.id}"
    os.makedirs(event_folder, exist_ok=True)


    # =========================
    # LOGO
    # =========================

    if logo:

        # eliminar anterior
        for img in event.images:
            if img.is_logo:
                await db.delete(img)

        path = await save_upload_file(logo, event_folder)

        db.add(EventImage(
            event_id=event.id,
            image_url=path,
            is_logo=True
        ))


    # =========================
    # COVER
    # =========================

    if cover:

        for img in event.images:
            if img.is_cover:
                await db.delete(img)

        path = await save_upload_file(cover, event_folder)

        db.add(EventImage(
            event_id=event.id,
            image_url=path,
            is_cover=True
        ))

        event.banner_url = path


    # =========================
    # GALLERY SYNC
    # =========================

    if keep_gallery is not None:

        keep_ids = set(json.loads(keep_gallery))

        for img in event.images:

            if (
                not img.is_logo
                and not img.is_cover
                and img.id not in keep_ids
            ):
                await db.delete(img)


    if gallery:

        for index, image in enumerate(gallery):

            path = await save_upload_file(image, event_folder)

            db.add(EventImage(
                event_id=event.id,
                image_url=path,
                order=index
            ))


    # reload fully hydrated object
    await db.commit()
    await db.refresh(event)

    result = await db.execute(
        select(Event)
        .options(
            selectinload(Event.images),
            selectinload(Event.event_categories)
            .selectinload(EventCategory.category),
            selectinload(Event.sponsors)
        )
        .where(Event.id == event.id)
    )

    return result.scalar_one()


# @router.put("/{event_id}", response_model=EventOut)
# async def update_event(
#     event_id: int,
#     event_data: EventUpdate,
#     current_user: UserDB = Depends(RequireRoles("admin", "superadmin")),
#     db: AsyncSession = Depends(get_db)
# ):

#     result = await db.execute(
#         select(Event).where(Event.id == event_id)
#     )

#     event = result.scalar_one_or_none()

#     if not event:
#         raise HTTPException(404, "Evento no encontrado")

#     # admin solo su company
#     if current_user.role == "admin":
#         if event.company_id != current_user.company_id:
#             raise HTTPException(403, "No autorizado")

#     for key, value in event_data.dict(exclude_unset=True).items():
#         setattr(event, key, value)

#     await db.commit()
#     await db.refresh(event)

#     return event

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