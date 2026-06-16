from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

def test_create_appointment_success():
    test_data = {
        "user": "John Doe",
        "time": "2023-10-25T10:00:00"
    }
    test_response = {
        "id": 1,
        "user": "John Doe",
        "time": "2023-10-25T10:00:00",
        "status": "Scheduled"
    }
    with patch("app.services.booking_service.book_appointment", return_value=test_response):
        response = client.post("/appointments/", json=test_data)
        assert response.status_code == 201
        assert response.json() == test_response

def test_create_appointment_invalid_data():
    test_data = {
        "user": "John Doe"
        # Missing "time"
    }
    response = client.post("/appointments/", json=test_data)
    assert response.status_code == 422  # Automatic validation failure
