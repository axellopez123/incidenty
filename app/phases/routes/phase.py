from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime

from app.database import get_db
from app.events.models.event_category import EventCategory
from app.events.models.event_category_phase import EventCategoryPhase
from app.events.schemas.event_category_phase import (
    EventCategoryPhaseCreate,
    EventCategoryPhaseUpdate,
    EventCategoryPhaseOut
)

router = APIRouter(
    prefix="/phases",
    tags=["Event Category Phases"]
)

@router.post("/", response_model=EventCategoryPhaseOut, status_code=201)
async def create_phase(
    data: EventCategoryPhaseCreate,
    db: AsyncSession = Depends(get_db)
):

    # Validar que exista EventCategory
    result = await db.execute(
        select(EventCategory).where(
            EventCategory.id == data.event_category_id
        )
    )
    event_category = result.scalar_one_or_none()

    if not event_category:
        raise HTTPException(404, "EventCategory no existe")

    # Validar traslape
    result = await db.execute(
        select(EventCategoryPhase).where(
            EventCategoryPhase.event_category_id == data.event_category_id,
            EventCategoryPhase.start_date <= data.end_date,
            EventCategoryPhase.end_date >= data.start_date
        )
    )

    existing = result.scalars().first()

    if existing:
        raise HTTPException(
            400,
            "Las fechas se traslapan con otra fase"
        )

    phase = EventCategoryPhase(**data.model_dump())

    db.add(phase)
    await db.commit()
    await db.refresh(phase)

    return phase

@router.get("/", response_model=List[EventCategoryPhaseOut])
async def get_phases(db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(EventCategoryPhase))
    return result.scalars().all()


@router.put("/{phase_id}", response_model=EventCategoryPhaseOut)
async def update_phase(
    phase_id: int,
    data: EventCategoryPhaseUpdate,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(EventCategoryPhase).where(
            EventCategoryPhase.id == phase_id
        )
    )

    phase = result.scalar_one_or_none()

    if not phase:
        raise HTTPException(404, "Phase no encontrada")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(phase, field, value)

    await db.commit()
    await db.refresh(phase)

    return phase


@router.delete("/{phase_id}", status_code=204)
async def delete_phase(
    phase_id: int,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(EventCategoryPhase).where(
            EventCategoryPhase.id == phase_id
        )
    )

    phase = result.scalar_one_or_none()

    if not phase:
        raise HTTPException(404, "Phase no encontrada")

    await db.delete(phase)
    await db.commit()

    return

