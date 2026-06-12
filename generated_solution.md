### FILE: app/graphql/schema.py
```python
import strawberry
from app.graphql.resolvers import resolve_appointment_by_id
from app.services.booking_service import (
    book_appointment,
    list_appointments,
    update_booking,
    cancel_booking,
)

@strawberry.type
class Appointment:
    id: int
    user: str
    time: str
    status: str

@strawberry.type
class Query:
    @strawberry.field(name="appointmentById")
    def appointment_by_id(self, id: int) -> Appointment:
        return resolve_appointment_by_id(id)

    @strawberry.field
    def appointments(self) -> list[Appointment]:
        raw_appointments = list_appointments()
        return [
            Appointment(
                id=appt["id"],
                user=appt["user"],
                time=appt["time"],
                status=appt["status"]
            )
            for appt in raw_appointments
        ]


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_appointment(self, user: str, time: str) -> Appointment:
        appt = book_appointment({"user": user, "time": time})
        return Appointment(
            id=appt["id"],
            user=appt["user"],
            time=appt["time"],
            status=appt["status"]
        )

    @strawberry.mutation
    def update_appointment(self, appointment_id: int, time: str) -> Appointment:
        appt = update_booking(appointment_id, {"time": time})
        return Appointment(
            id=appt["id"],
            user=appt["user"],
            time=appt["time"],
            status=appt["status"]
        )

    @strawberry.mutation
    def cancel_appointment(self, appointment_id: int) -> str:
        res = cancel_booking(appointment_id)
        if isinstance(res, dict):
            return res.get("message", "Appointment canceled")
        return str(res)

schema = strawberry.Schema(query=Query, mutation=Mutation)
```

### FILE: app/graphql/resolvers.py
```python
import strawberry
from app.services.booking_service import get_appointment_by_id as fetch_appointment_by_id

@strawberry.field
def resolve_appointment_by_id(id: int):
    if id < 0:
        raise strawberry.exceptions.GraphQLError("ID must be a non-negative integer")

    result = fetch_appointment_by_id(id)
    if not result:
        raise strawberry.exceptions.GraphQLError("Appointment not found")
    
    return {
        "id": result["id"],
        "user": result["user"],
        "time": result["time"],
        "status": result["status"]
    }
```

### FILE: tests/test_graphql.py
```python
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
```