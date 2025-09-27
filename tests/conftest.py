import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.db.session import get_session
from app.core.config import settings

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://bookit_user:bookit_password@localhost:5432/bookit_test"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_session():
    """Create a fresh database session for each test."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestSessionLocal() as session:
        yield session
    
    # Clean up
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def client(db_session):
    """Create a test client with database session override."""
    def override_get_session():
        return db_session
    
    app.dependency_overrides[get_session] = override_get_session
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

@pytest.fixture
async def test_user(client):
    """Create a test user and return auth token."""
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    # Register user
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    
    # Login to get token
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    
    token_data = response.json()
    return {
        "user_id": 1,  # First user will have ID 1
        "token": token_data["access_token"],
        "headers": {"Authorization": f"Bearer {token_data['access_token']}"}
    }

@pytest.fixture
async def test_admin(client):
    """Create a test admin user and return auth token."""
    # First create a regular user
    user_data = {
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "adminpassword123"
    }
    
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    
    # Manually set role to admin in database
    from app.models.user import User, UserRole
    from sqlalchemy import select
    
    # Get the session from the client
    session = client.app.dependency_overrides[get_session]()
    user = (await session.execute(select(User).where(User.email == "admin@example.com"))).scalar_one()
    user.role = UserRole.admin
    await session.commit()
    
    # Login to get token
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    
    token_data = response.json()
    return {
        "user_id": user.id,
        "token": token_data["access_token"],
        "headers": {"Authorization": f"Bearer {token_data['access_token']}"}
    }

@pytest.fixture
async def test_service(client, test_admin):
    """Create a test service."""
    service_data = {
        "title": "Test Service",
        "description": "A test service for booking",
        "price": 50.0,
        "duration_minutes": 60,
        "is_active": True
    }
    
    response = await client.post("/services", json=service_data, headers=test_admin["headers"])
    assert response.status_code == 201
    
    return response.json()
