import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, AsyncMock

from vnfm.db.base import SQLModel
from vnfm.db.session import get_db
from vnfm.api.routes import auth, catalog, vnf_lcm, vim

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def engine():
    test_engine = create_async_engine(TEST_DATABASE_URL, future=True)
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield test_engine
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def app(db_session):
    async def override_get_db():
        yield db_session

    test_app = FastAPI()
    test_app.include_router(auth.router, prefix="/api/v1")
    test_app.include_router(catalog.router, prefix="/api/v1")
    test_app.include_router(vnf_lcm.router, prefix="/api/v1")
    test_app.include_router(vim.router, prefix="/api/v1")
    test_app.dependency_overrides[get_db] = override_get_db

    yield test_app
    test_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_token(client):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def authorized_client(client, auth_token):
    client.headers.update({"Authorization": f"Bearer {auth_token}"})
    yield client


@pytest.fixture(autouse=True)
def mock_rabbitmq():
    with patch("aio_pika.connect_robust", new_callable=AsyncMock) as mock:
        mock_channel = AsyncMock()
        mock.return_value.channel = AsyncMock(return_value=mock_channel)
        mock.return_value.close = AsyncMock()
        yield mock
