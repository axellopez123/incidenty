from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_session
from app.student.models.student import Student
from app.student.schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentResponse
)

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/", response_model=StudentResponse)
async def create_student(
    data: StudentCreate,
    db: AsyncSession = Depends(get_session)
):

    student = Student(**data.model_dump())

    db.add(student)
    await db.commit()
    await db.refresh(student)

    return student


@router.get("/", response_model=list[StudentResponse])
async def list_students(
    db: AsyncSession = Depends(get_session)
):

    result = await db.execute(select(Student))

    return result.scalars().all()


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_session)
):

    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )

    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(404, "Student not found")

    return student


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    data: StudentUpdate,
    db: AsyncSession = Depends(get_session)
):

    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )

    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(404, "Student not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(student, key, value)

    await db.commit()
    await db.refresh(student)

    return student


@router.delete("/{student_id}")
async def delete_student(
    student_id: int,
    db: AsyncSession = Depends(get_session)
):

    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )

    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(404, "Student not found")

    await db.delete(student)
    await db.commit()

    return {"message": "Student deleted"}