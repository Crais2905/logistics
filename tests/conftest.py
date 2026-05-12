import pytest
import pytest_asyncio
from decouple import config

from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.main import app
from app.db.models import Base, User
from app.db.session import get_session
from app.schemas.enums.enums import UserRole

engine = create_async_engine(config("DATABASE_URL"), future=True)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with engine.connect() as connection:
        transaction = await connection.begin()

        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        yield session

        await session.close()
        await transaction.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"Content-Type": "application/json"},
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def authorized_client(client: AsyncClient) -> AsyncClient:
    resp = await client.post(
        "/auth/register/",
        json={
            "firstname": "First",
            "lastname": "Name",
            "email": "test@gmail.com",
            "password": "testpassword",
        },
    )
    assert resp.status_code == 201, resp.text

    resp = await client.post(
        "/auth/login/",
        json={"email": "test@gmail.com", "password": "testpassword"},
    )
    assert resp.status_code == 200, resp.text

    client.headers.update({"Authorization": f"Bearer {resp.json()['access_token']}"})
    return client


@pytest_asyncio.fixture
async def admin_client(client: AsyncClient, db_session: AsyncSession) -> AsyncClient:
    resp = await client.post(
        "/auth/register/",
        json={
            "firstname": "Admin",
            "lastname": "User",
            "email": "admin@gmail.com",
            "password": "adminpassword",
        },
    )
    assert resp.status_code == 201, resp.text

    result = await db_session.execute(
        select(User).where(User.email == "admin@gmail.com")
    )
    user = result.scalar_one()

    user.role = UserRole.admin.value

    await db_session.commit()
    await db_session.refresh(user)

    resp = await client.post(
        "/auth/login/",
        json={"email": "admin@gmail.com", "password": "adminpassword"},
    )
    assert resp.status_code == 200, resp.text

    client.headers.update({"Authorization": f"Bearer {resp.json()['access_token']}"})
    return client



