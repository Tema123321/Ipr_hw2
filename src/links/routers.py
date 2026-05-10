from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from src.database import get_db
from src.auth.manager import current_user, current_optional_user
from src.auth.models import User
from . import crud, schemas
from .exceptions import NotUniqueAliasError, AliasLengthError

router = APIRouter(prefix="/links", tags=["links"])


# 1. Создание ссылки (доступно всем)
@router.post("/shorten", response_model=schemas.LinkResponse)
async def create_short_link(
        link_data: schemas.LinkCreate,
        db: AsyncSession = Depends(get_db),
        user: Optional[User] = Depends(current_optional_user)
):
    try:
        return await crud.create_link(
            db=db,
            original_url=str(link_data.original_url),
            custom_alias=link_data.custom_alias,
            expire_at=link_data.expire_at,
            user_id=user.id if user else None
        )
    except (NotUniqueAliasError, AliasLengthError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))


# 2. Редирект (доступно всем)
@router.get("/{short_id}")
async def redirect_link(
        short_id: str,
        db: AsyncSession = Depends(get_db)
):
    link = await crud.get_link_by_short_id(db, short_id)
    if not link:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Link not found")
    await crud.increment_click_count(db, link)
    return RedirectResponse(url=link.original_url)


# 3. Статистика (только для авторизованных)
@router.get("/{short_id}/stats", response_model=schemas.LinkStatsResponse)
async def get_link_stats(
        short_id: str,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(current_user)
):
    link = await crud.get_link_by_short_id(db, short_id)
    if not link or link.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Link not found")

    return {
        "original_url": link.original_url,
        "short_id": link.short_id,
        "custom_alias": link.custom_alias,
        "created_at": link.created_at,
        "expire_at": link.expire_at,
        "click_count": link.click_count,
    }


# 4. Поиск (только для авторизованных)
@router.get("/search/", response_model=list[schemas.LinkResponse])
async def search_links(
        original_url: str = Query(..., min_length=3),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(current_user)
):
    return await crud.search_links(db, original_url, user.id)


# 5. Удаление (только для авторизованных)
@router.delete("/{short_id}")
async def delete_link(
        short_id: str,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(current_user)
):
    link = await crud.get_link_by_short_id(db, short_id)
    if not link or link.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Link not found")

    await crud.delete_link(db, link)
    return {"status": "success"}


# 6. Обновление (только для авторизованных)
@router.put("/{short_id}", response_model=schemas.LinkResponse)
async def update_link(
        short_id: str,
        update_data: schemas.LinkUpdate,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(current_user)
):
    link = await crud.get_link_by_short_id(db, short_id)
    if not link or link.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Link not found")

    return await crud.update_link(db, link, str(update_data.original_url))