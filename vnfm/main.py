import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import select

from vnfm.common.settings import settings
from vnfm.db.session import engine, AsyncSessionLocal
from vnfm.db.base import SQLModel
from vnfm.db.models import User
from vnfm.api.routes import auth, catalog, vnf_lcm, vim, ws
from vnfm.api.auth.security import get_password_hash
from vnfm.api.middleware.audit import AuditMiddleware
from vnfm.api.middleware.tenant import TenantMiddleware
from vnfm.drivers.manager import vim_manager
from vnfm.drivers.k8s.driver import K8sVimDriver
from vnfm.drivers.openstack.driver import OpenStackVimDriver
from vnfm.conductor.manager import conductor_manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def _seed_bootstrap_admin() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.username == settings.bootstrap_admin_username)
        )
        if result.scalar_one_or_none():
            return
        admin = User(
            username=settings.bootstrap_admin_username,
            hashed_password=get_password_hash(settings.bootstrap_admin_password),
            role="admin",
            tenant_id=settings.bootstrap_admin_tenant,
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        logger.info(
            "Bootstrap admin user '%s' created (tenant=%s).",
            settings.bootstrap_admin_username,
            settings.bootstrap_admin_tenant,
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Registering VIM drivers...")
    vim_manager.register(K8sVimDriver())
    vim_manager.register(OpenStackVimDriver())
    logger.info("Registered drivers: %s", vim_manager.list_drivers())

    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("Database tables created.")

    await _seed_bootstrap_admin()

    logger.info("Starting conductor manager...")
    await conductor_manager.start()

    yield

    logger.info("Shutting down conductor manager...")
    await conductor_manager.stop()


app = FastAPI(
    title=settings.app_name,
    description="Lightweight Enterprise VNFM based on FastAPI and TOSCA",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuditMiddleware)
app.add_middleware(TenantMiddleware)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(catalog.router, prefix="/api/v1")
app.include_router(vnf_lcm.router, prefix="/api/v1")
app.include_router(vim.router, prefix="/api/v1")
app.include_router(ws.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.app_name}
