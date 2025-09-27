import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta

class TestBookingConflicts:
    """Test booking conflict resolution."""
    
    async def test_booking_conflict_detection(self, client: AsyncClient, test_user, test_service):
        """Test that overlapping bookings are rejected."""
        # Create first booking
        booking1_data = {
            "service_id": test_service["id"],
            "start_time": "2024-02-01T10:00:00Z",
            "end_time": "2024-02-01T11:00:00Z"
        }
        
        response = await client.post("/bookings", json=booking1_data, headers=test_user["headers"])
        assert response.status_code == 201
        
        # Try to create overlapping booking
        booking2_data = {
            "service_id": test_service["id"],
            "start_time": "2024-02-01T10:30:00Z",  # Overlaps with first booking
            "end_time": "2024-02-01T11:30:00Z"
        }
        
        response = await client.post("/bookings", json=booking2_data, headers=test_user["headers"])
        assert response.status_code == 409
        assert "overlaps" in response.json()["detail"].lower()
    
    async def test_booking_no_conflict_different_services(self, client: AsyncClient, test_user, test_admin):
        """Test that bookings for different services don't conflict."""
        # Create second service
        service2_data = {
            "title": "Another Service",
            "description": "A different service",
            "price": 75.0,
            "duration_minutes": 90,
            "is_active": True
        }
        
        response = await client.post("/services", json=service2_data, headers=test_admin["headers"])
        assert response.status_code == 201
        service2 = response.json()
        
        # Create first booking for service 1
        booking1_data = {
            "service_id": 1,  # First service
            "start_time": "2024-02-01T10:00:00Z",
            "end_time": "2024-02-01T11:00:00Z"
        }
        
        response = await client.post("/bookings", json=booking1_data, headers=test_user["headers"])
        assert response.status_code == 201
        
        # Create overlapping booking for different service - should succeed
        booking2_data = {
            "service_id": service2["id"],
            "start_time": "2024-02-01T10:30:00Z",
            "end_time": "2024-02-01T11:30:00Z"
        }
        
        response = await client.post("/bookings", json=booking2_data, headers=test_user["headers"])
        assert response.status_code == 201
    
    async def test_booking_no_conflict_different_times(self, client: AsyncClient, test_user, test_service):
        """Test that non-overlapping bookings are allowed."""
        # Create first booking
        booking1_data = {
            "service_id": test_service["id"],
            "start_time": "2024-02-01T10:00:00Z",
            "end_time": "2024-02-01T11:00:00Z"
        }
        
        response = await client.post("/bookings", json=booking1_data, headers=test_user["headers"])
        assert response.status_code == 201
        
        # Create non-overlapping booking
        booking2_data = {
            "service_id": test_service["id"],
            "start_time": "2024-02-01T12:00:00Z",  # No overlap
            "end_time": "2024-02-01T13:00:00Z"
        }
        
        response = await client.post("/bookings", json=booking2_data, headers=test_user["headers"])
        assert response.status_code == 201
    
    async def test_booking_cancelled_does_not_conflict(self, client: AsyncClient, test_user, test_service):
        """Test that cancelled bookings don't cause conflicts."""
        # Create and cancel first booking
        booking1_data = {
            "service_id": test_service["id"],
            "start_time": "2024-02-01T10:00:00Z",
            "end_time": "2024-02-01T11:00:00Z"
        }
        
        response = await client.post("/bookings", json=booking1_data, headers=test_user["headers"])
        assert response.status_code == 201
        booking1_id = response.json()["id"]
        
        # Cancel the booking
        cancel_data = {"cancel": True}
        response = await client.patch(f"/bookings/{booking1_id}", json=cancel_data, headers=test_user["headers"])
        assert response.status_code == 200
        
        # Create overlapping booking - should succeed since first is cancelled
        booking2_data = {
            "service_id": test_service["id"],
            "start_time": "2024-02-01T10:30:00Z",
            "end_time": "2024-02-01T11:30:00Z"
        }
        
        response = await client.post("/bookings", json=booking2_data, headers=test_user["headers"])
        assert response.status_code == 201
