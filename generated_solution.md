### FILE: app/graphql/schema.py
```python
from ariadne import QueryType, make_executable_schema, gql, GraphQLError
from app.services.appointment_service import AppointmentService

type_defs = gql("""
    type Query {
        appointmentById(id: Int!): Appointment
    }

    type Appointment {
        id: Int!
        user: String!
        time: String!
        status: String!
    }
""")

query = QueryType()

@query.field("appointmentById")
async def resolve_appointment_by_id(_, info, id):
    # Validate that id is a positive integer
    if not isinstance(id, int) or id <= 0:
        raise GraphQLError("Invalid ID. Must be a positive integer.")

    appointment_service = info.context["appointment_service"]
    appointment = await appointment_service.get_appointment_by_id(id)
    if not appointment:
        raise GraphQLError("Appointment not found")
    return appointment

schema = make_executable_schema(type_defs, query)
```

### FILE: tests/test_graphql.py
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.db_client import database
from app.db.db_client import DatabaseClient
from app.services.appointment_service import AppointmentService

client = TestClient(app)

@pytest.fixture(autouse=True)
async def setup_database():
    # Ensure database is connected and set up for tests using db_client abstraction
    db_client = DatabaseClient(database_instance=database)
    await db_client.connect()

    await db_client.database.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY,
            user TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    # Prepopulate test data
    await db_client.database.execute("INSERT INTO appointments (id, user, time, status) VALUES (1, 'John Doe', '2023-10-05T10:00:00', 'Confirmed')")
    await db_client.database.execute("INSERT INTO appointments (id, user, time, status) VALUES (2, 'Jane Smith', '2023-10-06T14:30:00', 'Pending')")

    yield

    # Cleanup database
    await db_client.database.execute("DROP TABLE appointments")
    await db_client.disconnect()

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
    variables = {"id": 1}
    response = client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    assert "errors" not in response.json()
    assert response.json()["data"]["appointmentById"] == {
        "id": 1,
        "user": "John Doe",
        "time": "2023-10-05T10:00:00",
        "status": "Confirmed",
    }

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
    variables = {"id": 999}  # ID does not exist in the DB
    response = client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    assert "errors" in response.json()
    assert response.json()["errors"][0] == {
        "message": "Appointment not found",
        "locations": [{"line": 3, "column": 9}],
        "path": ["appointmentById"]
    }

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
    response = client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    assert "errors" in response.json()
    assert response.json()["errors"][0] == {
        "message": "Invalid ID. Must be a positive integer.",
        "locations": [{"line": 3, "column": 9}],
        "path": ["appointmentById"]
    }
```