from pydantic import BaseModel

class AppointmentResponse(BaseModel):
    id: int
    user: str
    time: str
    status: str
