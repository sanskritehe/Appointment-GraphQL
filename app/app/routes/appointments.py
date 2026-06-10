from fastapi import APIRouter, Depends, HTTPException, Path
from app.services.appointment_service import AppointmentService
from app.schemas.appointment import AppointmentResponse

router = APIRouter()

@router.get(
    "/appointments/{id}",
    response_model=AppointmentResponse,
    responses={
        404: {"description": "Appointment not found", "content": {"application/json": {"example": {"detail": "Appointment not found"}}}},
    },
)
async def get_appointment_by_id(
    id: int = Path(..., gt=0, description="The ID of the appointment (must be a positive integer)"),
    appointment_service: AppointmentService = Depends(AppointmentService),
):
    """
    Get a single appointment by ID.
    """
    appointment = await appointment_service.get_appointment_by_id(id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment
