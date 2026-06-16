from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)


def test_appointment_by_id_success():
    query = """
    query($id: Int!) {
        appointmentById(id: $id) {
            id
            user
            time
            status
        }
    }
    """
    test_id = 1
    test_response = {
        "id": 1,
        "user": "John Doe",
        "time": "2023-10-25T10:00:00",
        "status": "Scheduled"
    }
    with patch("app.services.booking_service.get_appointment_by_id", return_value=test_response):
        response = client.post("/graphql", json={"query": query, "variables": {"id": test_id}})
        assert response.status_code == 200
        assert "errors" not in response.json()
        data = response.json()["data"]["appointmentById"]
        assert data == {
            "id": test_response["id"],
            "user": test_response["user"],
            "time": test_response["time"],
            "status": test_response["status"]
        }
        assert set(data.keys()) == {"id", "user", "time", "status"}


def test_appointment_by_id_not_found():
    query = """
    query($id: Int!) {
        appointmentById(id: $id) {
            id
            user
            time
            status
        }
    }
    """
    test_id = 999
    with patch("app.services.booking_service.get_appointment_by_id", return_value=None):
        response = client.post("/graphql", json={"query": query, "variables": {"id": test_id}})
        assert response.status_code == 404
        assert "errors" in response.json()
        assert response.json()["errors"][0]["message"] == "Appointment not found"


def test_appointment_by_id_invalid_id_type():
    query = """
    query($id: Int!) {
        appointmentById(id: $id) {
            id
            user
            time
            status
        }
    }
    """
    test_id = "abc"  # Invalid ID type
    response = client.post("/graphql", json={"query": query, "variables": {"id": test_id}})
    assert response.status_code == 400
    assert "errors" in response.json()
    assert response.json()["errors"][0]["message"] == "Invalid ID type"
