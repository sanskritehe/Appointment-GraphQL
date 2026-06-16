from fastapi import APIRouter, HTTPException, Depends
from app.models import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from app.services.booking_service import (
    book_appointment,
    list_appointments,
    update_booking,
    cancel_booking,
    get_appointment_by_id
)

router = APIRouter(prefix="/appointments", tags=["Appointment"])


# Create a new appointment
@router.post("/", response_model=AppointmentResponse, status_code=201)
def create_appointment(req: AppointmentCreate, booking_service=Depends(book_appointment)):
    appointment = booking_service(req.dict())
    if not appointment:
        raise HTTPException(status_code=400, detail="Invalid appointment data")
    return appointment


# Get all appointments
@router.get("/")
def get_appointments(booking_service=Depends(list_appointments)):
    return booking_service()


# Get an appointment by ID
@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment_by_id_route(appointment_id: int, booking_service=Depends(get_appointment_by_id)):
    appointment = booking_service(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


# Update an appointment by ID
@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment_by_id(
    appointment_id: int, req: AppointmentUpdate, booking_service=Depends(update_booking)
):
    updated_appointment = booking_service(appointment_id, req.dict())
    if not updated_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return updated_appointment


# Cancel an appointment by ID
@router.delete("/{appointment_id}")
def cancel_appointment_by_id(appointment_id: int, booking_service=Depends(cancel_booking)):
    result = booking_service(appointment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return result
