from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

from vnfm.api.schemas import VimAuthCreate, VimAuthResponse, PaginatedResponse
from vnfm.api.routes.auth import get_current_user
from vnfm.db.session import get_db
from vnfm.db.models import VimAuth
from vnfm.common.settings import settings

router = APIRouter(prefix="/vim", tags=["vim"])


@router.post("/vim_auths", response_model=VimAuthResponse, status_code=status.HTTP_201_CREATED)
async def create_vim_auth(
    body: VimAuthCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    vim = VimAuth(
        name=body.name,
        vim_type=body.vim_type,
        vim_url=body.vim_url,
        auth_url=body.auth_url,
        username=body.username,
        password=body.password,
        tenant_name=body.tenant_name,
        project_name=body.project_name,
        domain_name=body.domain_name,
        region_name=body.region_name,
        extra=body.extra,
        is_default=body.is_default,
    )
    db.add(vim)
    await db.commit()
    await db.refresh(vim)
    return vim


@router.get("/vim_auths", response_model=PaginatedResponse)
async def list_vim_auths(
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.default_page_size, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    total_result = await db.execute(select(func.count(VimAuth.id)))
    total = total_result.scalar()
    result = await db.execute(
        select(VimAuth)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .order_by(VimAuth.created_at.desc())
    )
    items = result.scalars().all()
    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.get("/vim_auths/{vim_id}", response_model=VimAuthResponse)
async def get_vim_auth(
    vim_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await db.execute(select(VimAuth).where(VimAuth.id == vim_id))
    vim = result.scalar_one_or_none()
    if not vim:
        raise HTTPException(status_code=404, detail="VIM auth not found")
    return vim


@router.delete("/vim_auths/{vim_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vim_auth(
    vim_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await db.execute(select(VimAuth).where(VimAuth.id == vim_id))
    vim = result.scalar_one_or_none()
    if not vim:
        raise HTTPException(status_code=404, detail="VIM auth not found")
    await db.delete(vim)
    await db.commit()
    return None
