from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_session
from app.incidencia.models.incidencia import Incidencia
from app.student.models.student import Student

from app.incidencia.schemas.incidencia import (
    IncidenciaCreate,
    IncidenciaUpdate,
    IncidenciaResponse
)

router = APIRouter(prefix="/incidencias", tags=["Incidencias"])


@router.post("/", response_model=IncidenciaResponse)
async def create_incidencia(
    data: IncidenciaCreate,
    db: AsyncSession = Depends(get_session)
):

    student = await db.get(Student, data.student_id)

    if not student:
        raise HTTPException(404, "Student not found")

    incidencia = Incidencia(**data.model_dump())

    db.add(incidencia)
    await db.commit()
    await db.refresh(incidencia)

    return incidencia


@router.get("/", response_model=list[IncidenciaResponse])
async def list_incidencias(
    db: AsyncSession = Depends(get_session)
):

    result = await db.execute(select(Incidencia))

    return result.scalars().all()


@router.get("/{incidencia_id}", response_model=IncidenciaResponse)
async def get_incidencia(
    incidencia_id: int,
    db: AsyncSession = Depends(get_session)
):

    result = await db.execute(
        select(Incidencia).where(Incidencia.id == incidencia_id)
    )

    incidencia = result.scalar_one_or_none()

    if not incidencia:
        raise HTTPException(404, "Incidencia not found")

    return incidencia


@router.put("/{incidencia_id}", response_model=IncidenciaResponse)
async def update_incidencia(
    incidencia_id: int,
    data: IncidenciaUpdate,
    db: AsyncSession = Depends(get_session)
):

    result = await db.execute(
        select(Incidencia).where(Incidencia.id == incidencia_id)
    )

    incidencia = result.scalar_one_or_none()

    if not incidencia:
        raise HTTPException(404, "Incidencia not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(incidencia, key, value)

    await db.commit()
    await db.refresh(incidencia)

    return incidencia


@router.delete("/{incidencia_id}")
async def delete_incidencia(
    incidencia_id: int,
    db: AsyncSession = Depends(get_session)
):

    result = await db.execute(
        select(Incidencia).where(Incidencia.id == incidencia_id)
    )

    incidencia = result.scalar_one_or_none()

    if not incidencia:
        raise HTTPException(404, "Incidencia not found")

    await db.delete(incidencia)
    await db.commit()

    return {"message": "Incidencia deleted"}