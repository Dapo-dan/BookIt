import pytest
from httpx import AsyncClient

class TestPermissions:
    """Test role-based permissions."""
    
    async def test_user_cannot_access_admin_routes(self, client: AsyncClient, test_user):
        """Test that regular users cannot access admin-only routes."""
        # Try to create a service (admin only)
        service_data = {
            "title": "Unauthorized Service",
            "description": "This should fail",
            "price": 50.0,
            "duration_minutes": 60,
            "is_active": True
        }
        
        response = await client.post("/services", json=service_data, headers=test_user["headers"])
        assert response.status_code == 403
        assert "Forbidden" in response.json()["detail"]
    
    async def test_user_can_access_own_bookings(self, client: AsyncClient, test_user, test_service):
        """Test that users can access their own bookings."""
        # Create a booking
        booking_data = {
            "service_id": test_service["id"],
            "start_time": "2024-02-01T10:00:00Z",
            "end_time": "2024-02-01T11:00:00Z"
        }
        
        response = await client.post("/bookings", json=booking_data, headers=test_user["headers"])
        assert response.status_code == 201
        booking_id = response.json()["id"]
        
        # Get the booking
        response = await client.get(f"/bookings/{booking_id}", headers=test_user["headers"])
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == booking_id
        assert data["user_id"] == test_user["user_id"]
    
    async def test_user_cannot_access_other_user_bookings(self, client: AsyncClient, test_user, test_service):
        """Test that users cannot access other users' bookings."""
        # Create another user
        user2_data = {
            "name": "Another User",
            "email": "another@example.com",
            "password": "password123"
        }
        await client.post("/auth/register", json=user2_data)
        
        login_response = await client.post("/auth/login", json={
            "email": "another@example.com",
            "password": "password123"
        })
        user2_token = login_response.json()["access_token"]
        user2_headers = {"Authorization": f"Bearer {user2_token}"}
        
        # User 2 creates a booking
        booking_data = {
            "service_id": test_service["id"],
            "start_time": "2024-02-01T10:00:00Z",
            "end_time": "2024-02-01T11:00:00Z"
        }
        
        response = await client.post("/bookings", json=booking_data, headers=user2_headers)
        assert response.status_code == 201
        booking_id = response.json()["id"]
        
        # User 1 tries to access user 2's booking
        response = await client.get(f"/bookings/{booking_id}", headers=test_user["headers"])
        assert response.status_code == 403
        assert "Not your booking" in response.json()["detail"]
    
    async def test_admin_can_access_all_bookings(self, client: AsyncClient, test_user, test_admin, test_service):
        """Test that admins can access all bookings."""
        # User creates a booking
        booking_data = {
            "service_id": test_service["id"],
            "start_time": "2024-02-01T10:00:00Z",
            "end_time": "2024-02-01T11:00:00Z"
        }
        
        response = await client.post("/bookings", json=booking_data, headers=test_user["headers"])
        assert response.status_code == 201
        booking_id = response.json()["id"]
        
        # Admin can access the booking
        response = await client.get(f"/bookings/{booking_id}", headers=test_admin["headers"])
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == booking_id
    
    async def test_admin_can_update_booking_status(self, client: AsyncClient, test_user, test_admin, test_service):
        """Test that admins can update booking status."""
        # User creates a booking
        booking_data = {
            "service_id": test_service["id"],
            "start_time": "2024-02-01T10:00:00Z",
            "end_time": "2024-02-01T11:00:00Z"
        }
        
        response = await client.post("/bookings", json=booking_data, headers=test_user["headers"])
        assert response.status_code == 201
        booking_id = response.json()["id"]
        
        # Admin updates status
        response = await client.patch(f"/bookings/{booking_id}/status?status=confirmed", headers=test_admin["headers"])
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "confirmed"
    
    async def test_user_cannot_update_booking_status(self, client: AsyncClient, test_user, test_service):
        """Test that regular users cannot update booking status."""
        # User creates a booking
        booking_data = {
            "service_id": test_service["id"],
            "start_time": "2024-02-01T10:00:00Z",
            "end_time": "2024-02-01T11:00:00Z"
        }
        
        response = await client.post("/bookings", json=booking_data, headers=test_user["headers"])
        assert response.status_code == 201
        booking_id = response.json()["id"]
        
        # User tries to update status (should fail)
        response = await client.patch(f"/bookings/{booking_id}/status?status=confirmed", headers=test_user["headers"])
        assert response.status_code == 403
        assert "Forbidden" in response.json()["detail"]
    
    async def test_unauthenticated_access_denied(self, client: AsyncClient):
        """Test that unauthenticated requests are denied."""
        # Try to access protected endpoint without token
        response = await client.get("/me")
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
        
        # Try to create booking without token
        booking_data = {
            "service_id": 1,
            "start_time": "2024-02-01T10:00:00Z",
            "end_time": "2024-02-01T11:00:00Z"
        }
        response = await client.post("/bookings", json=booking_data)
        assert response.status_code == 401
