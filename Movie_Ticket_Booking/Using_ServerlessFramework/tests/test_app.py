import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import importlib
import sys

class TestMainApp:
    """Test cases for the main FastAPI application."""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint returns correct response."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Movie Booking API is running"
        assert data["version"] == "1.0.0"
    
    def test_health_check_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "movie-booking-api"
    
    def test_cors_headers_with_get(self, client):
        """Test CORS headers are properly set with GET request."""
        response = client.get("/")
        assert response.status_code == 200
        # Check if CORS middleware is working by making a request with origin
        response = client.get("/", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
    
    def test_cors_headers_preflight(self, client):
        """Test CORS preflight request."""
        # FastAPI handles OPTIONS automatically for CORS
        response = client.request(
            "OPTIONS", 
            "/api/ticket",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        # Should return 200 for preflight
        assert response.status_code == 200
    
    @patch('mangum.Mangum')
    def test_mangum_handler_creation(self, mock_mangum):
        """Test that Mangum handler is properly created."""
        # Remove app from modules if it exists to force reimport
        if 'app' in sys.modules:
            del sys.modules['app']
        
        # Import after patching to ensure the mock is used
        import app
        
        # Verify Mangum was called with correct parameters
        mock_mangum.assert_called_once()
        args, kwargs = mock_mangum.call_args
        assert kwargs.get('lifespan') == 'off'
    
    def test_app_title_and_description(self, client):
        """Test FastAPI app metadata."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        openapi_data = response.json()
        assert openapi_data["info"]["title"] == "Movie Booking API"
        assert "movie ticket booking" in openapi_data["info"]["description"].lower()
        assert openapi_data["info"]["version"] == "1.0.0"
    
    def test_invalid_endpoint_404(self, client):
        """Test that invalid endpoints return 404."""
        response = client.get("/invalid-endpoint")
        assert response.status_code == 404
