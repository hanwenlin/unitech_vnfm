import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

from vnfm.api.schemas import (
    VnfInstanceCreate,
    VnfInstanceResponse,
    LcmOperationRequest,
    PaginatedResponse,
)
from vnfm.api.routes.auth import get_current_user
from vnfm.api.services.vnf_lcm import vnf_lcm_manager
from vnfm.db.session import get_db
from vnfm.db.models import VnfInstance, VnfPackage, LifecycleEvent
from vnfm.common.exceptions import VnfInstanceConflictState, VnfNotFound

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/vnflcm", tags=["vnf-lcm"])


def _ensure_tenant_access(user: dict, instance: VnfInstance) -> None:
    """Reject the request when the caller's tenant does not own the VNF."""
    if user.get("role") == "admin":
        return
    user_tenant = user.get("tenant_id")
    if instance.tenant_id and instance.tenant_id != user_tenant:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied for this tenant")


@router.post("/vnf_instances", response_model=VnfInstanceResponse, status_code=status.HTTP_201_CREATED)
async def create_vnf_instance(
    body: VnfInstanceCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    pkg_result = await db.execute(select(VnfPackage).where(VnfPackage.id == body.vnf_package_id))
    pkg = pkg_result.scalar_one_or_none()
    if not pkg:
        raise HTTPException(status_code=404, detail="VNF package not found")

    tenant_id = body.tenant_id if user.get("role") == "admin" and body.tenant_id else user.get("tenant_id")

    instance = VnfInstance(
        name=body.name,
        description=body.description,
        vnf_package_id=body.vnf_package_id,
        vnfd_id=body.vnfd_id,
        vim_id=body.vim_id,
        tenant_id=tenant_id,
        extra_metadata=body.extra_metadata,
        vnf_provider=pkg.vnf_provider,
        vnf_product_name=pkg.vnf_product_name,
        vnf_software_version=pkg.vnf_software_version,
        vnfd_version=pkg.vnfd_version,
    )
    db.add(instance)
    await db.commit()
    await db.refresh(instance)
    return instance


@router.get("/vnf_instances", response_model=PaginatedResponse)
async def list_vnf_instances(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    base_query = select(VnfInstance)
    count_query = select(func.count(VnfInstance.id))
    if user.get("role") != "admin":
        tenant_filter = VnfInstance.tenant_id == user.get("tenant_id")
        base_query = base_query.where(tenant_filter)
        count_query = count_query.where(tenant_filter)

    total_result = await db.execute(count_query)
    total = total_result.scalar()
    result = await db.execute(
        base_query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .order_by(VnfInstance.created_at.desc())
    )
    items = result.scalars().all()
    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.get("/vnf_instances/{vnf_id}", response_model=VnfInstanceResponse)
async def get_vnf_instance(
    vnf_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await db.execute(select(VnfInstance).where(VnfInstance.id == vnf_id))
    instance = result.scalar_one_or_none()
    if not instance:
        raise HTTPException(status_code=404, detail="VNF instance not found")
    _ensure_tenant_access(user, instance)
    return instance


@router.post("/vnf_instances/{vnf_id}/instantiate")
async def instantiate_vnf(
    vnf_id: str,
    body: LcmOperationRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await db.execute(select(VnfInstance).where(VnfInstance.id == vnf_id))
    instance = result.scalar_one_or_none()
    if not instance:
        raise HTTPException(status_code=404, detail="VNF instance not found")
    _ensure_tenant_access(user, instance)

    try:
        return await vnf_lcm_manager.instantiate(
            instance, body, user["username"], instance.tenant_id
        )
    except VnfInstanceConflictState as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/vnf_instances/{vnf_id}/terminate")
async def terminate_vnf(
    vnf_id: str,
    body: LcmOperationRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await db.execute(select(VnfInstance).where(VnfInstance.id == vnf_id))
    instance = result.scalar_one_or_none()
    if not instance:
        raise HTTPException(status_code=404, detail="VNF instance not found")
    _ensure_tenant_access(user, instance)

    try:
        return await vnf_lcm_manager.terminate(
            instance, body, user["username"], instance.tenant_id
        )
    except VnfInstanceConflictState as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/vnf_instances/{vnf_id}/scale")
async def scale_vnf(
    vnf_id: str,
    body: LcmOperationRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await db.execute(select(VnfInstance).where(VnfInstance.id == vnf_id))
    instance = result.scalar_one_or_none()
    if not instance:
        raise HTTPException(status_code=404, detail="VNF instance not found")
    _ensure_tenant_access(user, instance)

    try:
        return await vnf_lcm_manager.scale(
            instance, body, user["username"], instance.tenant_id
        )
    except VnfInstanceConflictState as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/vnf_instances/{vnf_id}/update")
async def update_vnf(
    vnf_id: str,
    body: LcmOperationRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await db.execute(select(VnfInstance).where(VnfInstance.id == vnf_id))
    instance = result.scalar_one_or_none()
    if not instance:
        raise HTTPException(status_code=404, detail="VNF instance not found")
    _ensure_tenant_access(user, instance)

    try:
        return await vnf_lcm_manager.update(
            instance, body, user["username"], instance.tenant_id
        )
    except VnfInstanceConflictState as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/vnf_instances/{vnf_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vnf(
    vnf_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await db.execute(select(VnfInstance).where(VnfInstance.id == vnf_id))
    instance = result.scalar_one_or_none()
    if not instance:
        raise HTTPException(status_code=404, detail="VNF instance not found")
    _ensure_tenant_access(user, instance)

    try:
        await vnf_lcm_manager.delete(instance, db)
    except VnfInstanceConflictState as e:
        raise HTTPException(status_code=409, detail=str(e))
    return None


@router.get("/vnf_instances/{vnf_id}/lifecycle", response_model=PaginatedResponse)
async def list_lifecycle_events(
    vnf_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    inst_result = await db.execute(select(VnfInstance).where(VnfInstance.id == vnf_id))
    instance = inst_result.scalar_one_or_none()
    if not instance:
        raise HTTPException(status_code=404, detail="VNF instance not found")
    _ensure_tenant_access(user, instance)

    total_result = await db.execute(select(func.count(LifecycleEvent.id)).where(LifecycleEvent.vnf_instance_id == vnf_id))
    total = total_result.scalar()
    result = await db.execute(
        select(LifecycleEvent)
        .where(LifecycleEvent.vnf_instance_id == vnf_id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .order_by(LifecycleEvent.created_at.desc())
    )
    items = result.scalars().all()
    return {"total": total, "page": page, "page_size": page_size, "items": items}
