from pydantic import BaseModel

class AppointmentCreate(BaseModel):
    user: str
    time: str

class AppointmentUpdate(BaseModel):
    time: str

class AppointmentResponse(BaseModel):
    id: int
    user: str
    time: str
    status: str