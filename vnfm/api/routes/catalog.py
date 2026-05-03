from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

from vnfm.api.schemas import VnfPackageCreate, VnfPackageResponse, PaginatedResponse
from vnfm.api.routes.auth import get_current_user
from vnfm.db.session import get_db
from vnfm.db.models import VnfPackage
from vnfm.parser.parser import tosca_parser
from vnfm.common.settings import settings

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.post("/vnf_packages", response_model=VnfPackageResponse, status_code=status.HTTP_201_CREATED)
async def create_vnf_package(
    body: VnfPackageCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if body.tosca_template:
        try:
            parsed = tosca_parser.parse_yaml(body.tosca_template)
            body.extra_metadata = parsed
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"TOSCA validation failed: {e}")

    pkg = VnfPackage(
        name=body.name,
        description=body.description,
        version=body.version,
        provider=body.provider,
        vnfd_id=body.vnfd_id,
        vnf_product_name=body.vnf_product_name,
        vnf_provider=body.vnf_provider,
        vnf_software_version=body.vnf_software_version,
        vnfd_version=body.vnfd_version,
        tosca_template=body.tosca_template,
        extra_metadata=body.extra_metadata,
        onboarding_state="ONBOARDED",
        operational_state="ENABLED",
    )
    db.add(pkg)
    await db.commit()
    await db.refresh(pkg)
    return pkg


@router.get("/vnf_packages", response_model=PaginatedResponse)
async def list_vnf_packages(
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.default_page_size, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    total_result = await db.execute(select(func.count(VnfPackage.id)))
    total = total_result.scalar()
    result = await db.execute(
        select(VnfPackage)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .order_by(VnfPackage.created_at.desc())
    )
    items = result.scalars().all()
    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.get("/vnf_packages/{pkg_id}", response_model=VnfPackageResponse)
async def get_vnf_package(
    pkg_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await db.execute(select(VnfPackage).where(VnfPackage.id == pkg_id))
    pkg = result.scalar_one_or_none()
    if not pkg:
        raise HTTPException(status_code=404, detail="VNF package not found")
    return pkg


@router.delete("/vnf_packages/{pkg_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vnf_package(
    pkg_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await db.execute(select(VnfPackage).where(VnfPackage.id == pkg_id))
    pkg = result.scalar_one_or_none()
    if not pkg:
        raise HTTPException(status_code=404, detail="VNF package not found")
    await db.delete(pkg)
    await db.commit()
    return None
