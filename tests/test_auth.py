import pytest
from httpx import AsyncClient

class TestAuth:
    """Test authentication endpoints."""
    
    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        user_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepassword123"
        }
        
        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert "password" not in data
    
    async def test_register_duplicate_email(self, client: AsyncClient):
        """Test registration with duplicate email fails."""
        user_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepassword123"
        }
        
        # First registration should succeed
        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        
        # Second registration with same email should fail
        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"]
    
    async def test_login_success(self, client: AsyncClient):
        """Test successful login."""
        # First register a user
        user_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepassword123"
        }
        await client.post("/auth/register", json=user_data)
        
        # Then login
        login_data = {
            "email": "john@example.com",
            "password": "securepassword123"
        }
        response = await client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials fails."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = await client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    async def test_refresh_token(self, client: AsyncClient):
        """Test token refresh."""
        # Register and login
        user_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepassword123"
        }
        await client.post("/auth/register", json=user_data)
        
        login_response = await client.post("/auth/login", json={
            "email": "john@example.com",
            "password": "securepassword123"
        })
        refresh_token = login_response.json()["refresh_token"]
        
        # Use refresh token
        response = await client.post("/auth/refresh", headers={
            "Authorization": f"Bearer {refresh_token}"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    async def test_refresh_invalid_token(self, client: AsyncClient):
        """Test refresh with invalid token fails."""
        response = await client.post("/auth/refresh", headers={
            "Authorization": "Bearer invalid_token"
        })
        assert response.status_code == 401
    
    async def test_logout(self, client: AsyncClient):
        """Test logout endpoint."""
        response = await client.post("/auth/logout")
        assert response.status_code == 204
