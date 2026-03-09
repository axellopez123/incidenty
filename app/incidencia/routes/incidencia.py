from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import io
import os
from docxtpl import DocxTemplate

from app.database import get_db as get_session
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


@router.get("/{incidencia_id}/download")
async def download_incidencia_word(
    incidencia_id: int,
    db: AsyncSession = Depends(get_session)
):
    # Fetch the incident with student information
    result = await db.execute(
        select(Incidencia)
        .options(selectinload(Incidencia.student))
        .where(Incidencia.id == incidencia_id)
    )
    incid = result.scalar_one_or_none()

    if not incid:
        raise HTTPException(404, "Incidencia not found")

    # Define the template path
    template_path = os.path.join(
        os.getcwd(), "app", "templates", "incidencia_template.docx"
    )

    if not os.path.exists(template_path):
        raise HTTPException(500, f"Template not found at {template_path}")

    # Prepare data for the template
    context = {
        "student_name": incid.student.name,
        "grade": incid.student.grade,
        "group": incid.student.group,
        "date": incid.date.strftime("%d/%m/%Y") if incid.date else "N/A",
        "description": incid.description or "",
        "disciplinary": incid.disciplinary or "",
        "acuerdos_compromisos": incid.acuerdos_compromisos or ""
    }

    # Generate document using docxtpl
    doc = DocxTemplate(template_path)
    doc.render(context)

    # Save to memory instead of temporary file
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    
    file_name = f"Reporte_{incid.student.name}_{incidencia_id}.docx".replace(" ", "_")

    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
    )
