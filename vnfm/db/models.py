import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, Enum as SQLAlchemyEnum, JSON
from sqlmodel import SQLModel, Field, Relationship

from vnfm.common.constants import (
    InstantiationState,
    TaskState,
    LcmOperationType,
    LcmOperationStatus,
    ResourceType,
    VimType,
)


class VnfPackage(SQLModel, table=True):
    __tablename__ = "vnf_package"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(max_length=255, index=True)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    version: str = Field(default="1.0", max_length=64)
    provider: Optional[str] = Field(default=None, max_length=255)
    vnfd_id: str = Field(max_length=255, unique=True, index=True)
    vnf_product_name: Optional[str] = Field(default=None, max_length=255)
    vnf_provider: Optional[str] = Field(default=None, max_length=255)
    vnf_software_version: Optional[str] = Field(default=None, max_length=64)
    vnfd_version: Optional[str] = Field(default=None, max_length=64)
    onboarding_state: str = Field(default="CREATED", max_length=64)
    operational_state: str = Field(default="DISABLED", max_length=64)
    usage_state: str = Field(default="NOT_IN_USE", max_length=64)
    tosca_template: Optional[str] = Field(default=None, sa_column=Column(Text))
    tosca_csar: Optional[str] = Field(default=None, sa_column=Column(Text))
    extra_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow))

    instances: List["VnfInstance"] = Relationship(back_populates="vnf_package")


class VnfInstance(SQLModel, table=True):
    __tablename__ = "vnf_instance"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(max_length=255, index=True)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    vnf_instance_name: Optional[str] = Field(default=None, max_length=255)
    vnf_instance_description: Optional[str] = Field(default=None, sa_column=Column(Text))
    vnf_package_id: Optional[str] = Field(default=None, foreign_key="vnf_package.id", index=True)
    vnfd_id: str = Field(max_length=255, index=True)
    vnf_provider: Optional[str] = Field(default=None, max_length=255)
    vnf_product_name: Optional[str] = Field(default=None, max_length=255)
    vnf_software_version: Optional[str] = Field(default=None, max_length=64)
    vnfd_version: Optional[str] = Field(default=None, max_length=64)
    instantiation_state: InstantiationState = Field(default=InstantiationState.NOT_INSTANTIATED, sa_column=Column(SQLAlchemyEnum(InstantiationState)))
    task_state: TaskState = Field(default=TaskState.PENDING, sa_column=Column(SQLAlchemyEnum(TaskState)))
    vim_id: Optional[str] = Field(default=None, foreign_key="vim_auth.id")
    tenant_id: Optional[str] = Field(default=None, max_length=255, index=True)
    extra_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow))

    vnf_package: Optional[VnfPackage] = Relationship(back_populates="instances")
    resources: List["VnfResource"] = Relationship(back_populates="vnf_instance")
    lifecycle_events: List["LifecycleEvent"] = Relationship(back_populates="vnf_instance")
    vim: Optional["VimAuth"] = Relationship(back_populates="vnf_instances")


class VnfResource(SQLModel, table=True):
    __tablename__ = "vnf_resource"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    vnf_instance_id: str = Field(foreign_key="vnf_instance.id", index=True)
    resource_type: ResourceType = Field(sa_column=Column(SQLAlchemyEnum(ResourceType)))
    resource_name: str = Field(max_length=255)
    resource_id: Optional[str] = Field(default=None, max_length=255)
    vim_resource_id: Optional[str] = Field(default=None, max_length=255)
    vim_resource_type: Optional[str] = Field(default=None, max_length=255)
    vim_resource_name: Optional[str] = Field(default=None, max_length=255)
    extra_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow))

    vnf_instance: VnfInstance = Relationship(back_populates="resources")


class VimAuth(SQLModel, table=True):
    __tablename__ = "vim_auth"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(max_length=255, index=True)
    vim_type: VimType = Field(sa_column=Column(SQLAlchemyEnum(VimType)))
    vim_url: str = Field(max_length=512)
    auth_url: Optional[str] = Field(default=None, max_length=512)
    username: Optional[str] = Field(default=None, max_length=255)
    password: Optional[str] = Field(default=None, max_length=255)
    tenant_name: Optional[str] = Field(default=None, max_length=255)
    project_name: Optional[str] = Field(default=None, max_length=255)
    domain_name: Optional[str] = Field(default=None, max_length=255)
    region_name: Optional[str] = Field(default=None, max_length=255)
    access_token: Optional[str] = Field(default=None, sa_column=Column(Text))
    certificate: Optional[str] = Field(default=None, sa_column=Column(Text))
    extra: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    is_default: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow))

    vnf_instances: List[VnfInstance] = Relationship(back_populates="vim")


class LifecycleEvent(SQLModel, table=True):
    __tablename__ = "lifecycle_event"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    vnf_instance_id: str = Field(foreign_key="vnf_instance.id", index=True)
    operation: LcmOperationType = Field(sa_column=Column(SQLAlchemyEnum(LcmOperationType)))
    operation_status: LcmOperationStatus = Field(default=LcmOperationStatus.STARTING, sa_column=Column(SQLAlchemyEnum(LcmOperationStatus)))
    start_time: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow))
    end_time: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))
    user_id: Optional[str] = Field(default=None, max_length=255)
    tenant_id: Optional[str] = Field(default=None, max_length=255)
    params: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    error: Optional[str] = Field(default=None, sa_column=Column(Text))
    resource_changes: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, default=datetime.utcnow))

    vnf_instance: VnfInstance = Relationship(back_populates="lifecycle_events")
