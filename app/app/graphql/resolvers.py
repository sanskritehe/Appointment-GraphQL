import strawberry
from fastapi import HTTPException
from app.services.booking_service import get_appointment_by_id as get_appointment_by_id_service


def resolve_appointment_by_id(id: int):
    if not isinstance(id, int):  # Validate the ID type
        raise HTTPException(status_code=400, detail="Invalid ID type")

    appointment = get_appointment_by_id_service(appointment_id=id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return appointment
