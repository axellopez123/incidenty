from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from app.database import get_db
from datetime import datetime
from sqlalchemy import select

from app.phases.models.phase import EventCategoryPhase


async def get_current_price(
    db: AsyncSession = Depends(get_db)
    event_category_id: int
) -> int:

    now = datetime.utcnow()

    result = await db.execute(
        select(EventCategoryPhase)
        .where(
            EventCategoryPhase.event_category_id == event_category_id,
            EventCategoryPhase.start_date <= now,
            EventCategoryPhase.end_date >= now,
            EventCategoryPhase.is_active == True
        )
        .order_by(EventCategoryPhase.start_date.desc())
    )

    phase = result.scalars().first()

    if not phase:
        raise Exception("No hay fase activa actualmente")

    return phase.price