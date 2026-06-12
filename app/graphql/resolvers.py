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
