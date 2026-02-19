from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.database import get_db
from app.categories.models.category import Category
from app.categories.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryOut
)
from app.auth.core.permissions import RequireRoles
from app.auth.models.user import UserDB
import slugify


router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

@router.post("/", response_model=CategoryOut)
async def create_category(
    data: CategoryCreate,
    current_user: UserDB = Depends(RequireRoles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):
    slug = slugify.slugify(data.name)

    # validar slug único
    result = await db.execute(
        select(Category).where(Category.slug == slug)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(400, "Ya existe una categoría con ese nombre")

    category = Category(**data.model_dump(), slug=slug)

    db.add(category)
    await db.commit()
    await db.refresh(category)

    return category


@router.get("/", response_model=List[CategoryOut])
async def list_categories(
    gender: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(True),
    db: AsyncSession = Depends(get_db)
):
    query = select(Category)

    if gender:
        query = query.where(Category.gender == gender)

    if is_active is not None:
        query = query.where(Category.is_active == is_active)

    result = await db.execute(query)
    categories = result.scalars().all()

    return categories


@router.get("/{category_id}", response_model=CategoryOut)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )

    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(404, "Categoría no encontrada")

    return category


@router.put("/{category_id}", response_model=CategoryOut)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    current_user: UserDB = Depends(RequireRoles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )

    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(404, "Categoría no encontrada")

    update_data = data.model_dump(exclude_unset=True)

    # Si actualizan nombre, regenerar slug
    if "name" in update_data:
        update_data["slug"] = slugify.slugify(update_data["name"])

    for key, value in update_data.items():
        setattr(category, key, value)

    await db.commit()
    await db.refresh(category)

    return category


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    current_user: UserDB = Depends(RequireRoles("admin", "superadmin")),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )

    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(404, "Categoría no encontrada")

    category.is_active = False

    await db.commit()

    return {"message": "Categoría desactivada correctamente"}