from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.distances.models.distance import Distance
from app.distances.schemas.distance import (
    DistanceCreate,
    DistanceUpdate,
    DistanceResponse
)

router = APIRouter(prefix="/distances", tags=["Distances"])

@router.post("/", response_model=DistanceResponse, status_code=status.HTTP_201_CREATED)
async def create_distance(
    data: DistanceCreate,
    db: AsyncSession = Depends(get_db)
):
    # Validar que no exista misma combinación name + meters
    result = await db.execute(
        select(Distance).where(
            Distance.name == data.name,
            Distance.meters == data.meters
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Distance already exists"
        )

    distance = Distance(**data.model_dump())
    db.add(distance)
    await db.commit()
    await db.refresh(distance)

    return distance

@router.get("/", response_model=List[DistanceResponse])
async def get_distances(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Distance))
    return result.scalars().all()

@router.get("/{id}", response_model=DistanceResponse)
async def get_distance(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Distance).where(Distance.id == id))
    distance = result.scalar_one_or_none()
    if not distance:
        raise HTTPException(status_code=404, detail="Distance not found")
    return distance

@router.put("/{id}", response_model=DistanceResponse)
async def update_distance(
    id: int,
    data: DistanceUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Distance).where(Distance.id == id))
    distance = result.scalar_one_or_none()
    if not distance:
        raise HTTPException(status_code=404, detail="Distance not found")

    # Validar que no exista otra distancia con el mismo nombre y metros
    result = await db.execute(
        select(Distance).where(
            Distance.name == data.name,
            Distance.meters == data.meters,
            Distance.id != id
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Another distance with the same name and meters already exists"
        )

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(distance, field, value)

    await db.commit()
    await db.refresh(distance)
    return distance

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_distance(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Distance).where(Distance.id == id))
    distance = result.scalar_one_or_none()
    if not distance:
        raise HTTPException(status_code=404, detail="Distance not found")

    distance.is_active = False
    await db.commit()
    return