import requests
from app.config import DB_SERVICE_URL

def create_appointment(data: dict):
    response = requests.post(
        f"{DB_SERVICE_URL}/appointments",
        params=data
    )
    response.raise_for_status()
    return response.json()

def get_all_appointments():
    response = requests.get(f"{DB_SERVICE_URL}/appointments")
    response.raise_for_status()
    return response.json()

def update_appointment(appointment_id: int, data: dict):
    response = requests.put(
        f"{DB_SERVICE_URL}/appointments/{appointment_id}",
        json=data
    )
    response.raise_for_status()
    return response.json()

def cancel_appointment(appointment_id: int):
    response = requests.delete(
        f"{DB_SERVICE_URL}/appointments/{appointment_id}"
    )
    return response.json()

def get_appointment_by_id(appointment_id: int):
    response = requests.get(f"{DB_SERVICE_URL}/appointments/{appointment_id}")
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()
