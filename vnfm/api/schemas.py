from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from vnfm.common.constants import (
    InstantiationState,
    TaskState,
    LcmOperationType,
    LcmOperationStatus,
    VimType,
    ResourceType,
)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserLogin(BaseModel):
    username: str
    password: str


class VnfPackageCreate(BaseModel):
    name: str
    description: Optional[str] = None
    version: str = "1.0"
    provider: Optional[str] = None
    vnfd_id: str
    vnf_product_name: Optional[str] = None
    vnf_provider: Optional[str] = None
    vnf_software_version: Optional[str] = None
    vnfd_version: Optional[str] = None
    tosca_template: Optional[str] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class VnfPackageResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    vnfd_id: str
    onboarding_state: str
    operational_state: str
    usage_state: str
    created_at: datetime

    class Config:
        from_attributes = True


class VnfInstanceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    vnf_package_id: str
    vnfd_id: str
    vim_id: Optional[str] = None
    tenant_id: Optional[str] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class VnfInstanceResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    vnf_package_id: Optional[str]
    vnfd_id: str
    instantiation_state: InstantiationState
    task_state: TaskState
    vim_id: Optional[str]
    tenant_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LcmOperationRequest(BaseModel):
    params: Optional[Dict[str, Any]] = {}


class LifecycleEventResponse(BaseModel):
    id: str
    vnf_instance_id: str
    operation: LcmOperationType
    operation_status: LcmOperationStatus
    start_time: datetime
    end_time: Optional[datetime]
    user_id: Optional[str]
    error: Optional[str]

    class Config:
        from_attributes = True


class VimAuthCreate(BaseModel):
    name: str
    vim_type: VimType
    vim_url: str
    auth_url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    tenant_name: Optional[str] = None
    project_name: Optional[str] = None
    domain_name: Optional[str] = None
    region_name: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None
    is_default: bool = False


class VimAuthResponse(BaseModel):
    id: str
    name: str
    vim_type: VimType
    vim_url: str
    is_default: bool
    created_at: datetime

    class Config:
        from_attributes = True


class VnfResourceResponse(BaseModel):
    id: str
    vnf_instance_id: str
    resource_type: ResourceType
    resource_name: str
    resource_id: Optional[str]
    vim_resource_id: Optional[str]
    vim_resource_type: Optional[str]

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[Any]
