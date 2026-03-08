from __future__ import annotations
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.infrastructure.db.base import Base
import app.domain.models.models  # noqa: F401
from app.main import app
from app.infrastructure.db.session import get_db
import app.workers.background_worker as background_worker_module

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session, session_factory
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    session, session_factory = db_session

    async def override_get_db():
        yield session

    # Patch background worker to use the test session factory
    original_session_local = background_worker_module.AsyncSessionLocal
    background_worker_module.AsyncSessionLocal = session_factory

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
    background_worker_module.AsyncSessionLocal = original_session_local
