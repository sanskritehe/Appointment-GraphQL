from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

def test_appointment_by_id_success():
    query = """
    query GetAppointmentById($id: Int!) {
        appointmentById(id: $id) {
            id
            user
            time
            status
        }
    }
    """
    test_id = 1
    test_data = {
        "id": test_id,
        "user": "John Doe",
        "time": "2023-10-25T10:00:00",
        "status": "Scheduled"
    }
    with patch("app.services.booking_service.get_appointment_by_id", return_value=test_data):
        variables = {"id": test_id}
        response = client.post(
            "/graphql", json={"query": query, "variables": variables}
        )
        assert response.status_code == 200
        assert "errors" not in response.json()
        data = response.json()["data"]["appointmentById"]
        assert data["id"] == test_data["id"]
        assert data["user"] == test_data["user"]
        assert data["time"] == test_data["time"]
        assert data["status"] == test_data["status"]

def test_appointment_by_id_not_found():
    query = """
    query GetAppointmentById($id: Int!) {
        appointmentById(id: $id) {
            id
            user
            time
            status
        }
    }
    """
    test_id = 9999
    with patch("app.services.booking_service.get_appointment_by_id", return_value=None):
        variables = {"id": test_id}
        response = client.post(
            "/graphql", json={"query": query, "variables": variables}
        )
        assert response.status_code == 200
        assert response.json()["errors"]
        assert response.json()["errors"][0]["message"] == "Appointment not found"

def test_appointment_by_id_invalid_id():
    query = """
    query GetAppointmentById($id: Int!) {
        appointmentById(id: $id) {
            id
            user
            time
            status
        }
    }
    """
    variables = {"id": -1}  # Invalid ID
    response = client.post(
        "/graphql", json={"query": query, "variables": variables}
    )
    assert response.status_code == 200
    assert response.json()["errors"]
    assert response.json()["errors"][0]["message"] == "ID must be a non-negative integer"
