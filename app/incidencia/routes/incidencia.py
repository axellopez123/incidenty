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

    payload = data.model_dump()

    # convertir arrays a string si vienen como lista
    for field in ["leve_faction", "grave_faction", "muy_grave_faction"]:
        if payload.get(field) and isinstance(payload[field], list):
            payload[field] = ",".join(payload[field])

    incidencia = Incidencia(**payload)

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

    payload = data.model_dump(exclude_unset=True)

    # convertir arrays a string si vienen en el update
    for field in ["leve_faction", "grave_faction", "muy_grave_faction"]:
        if field in payload and payload[field] is not None:
            if isinstance(payload[field], list):
                payload[field] = ",".join(payload[field])

    for key, value in payload.items():
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
        "incidencia_id": incid.id,
        "description": incid.description or "",
        "disciplinary": incid.disciplinary or "",
        "acuerdos_compromisos": incid.acuerdos_compromisos or "",
        "leve_faction": incid.leve_faction.split(",") if (incid.leve_faction and isinstance(incid.leve_faction, str)) else [],
        "leve_other": incid.leve_other or "",
        "grave_faction": incid.grave_faction.split(",") if (incid.grave_faction and isinstance(incid.grave_faction, str)) else [],
        "grave_other": incid.grave_other or "",
        "muy_grave_faction": incid.muy_grave_faction.split(",") if (incid.muy_grave_faction and isinstance(incid.muy_grave_faction, str)) else [],
        "muy_grave_other": incid.muy_grave_other or "",
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
