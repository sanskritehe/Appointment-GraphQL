from app.db_client import create_appointment, get_all_appointments, update_appointment, cancel_appointment, get_appointment_by_id


def book_appointment(data):
    # Add business rules or validation if needed
    return create_appointment(data)


def list_appointments():
    return get_all_appointments()


def update_booking(appointment_id: int, data):
    return update_appointment(appointment_id, data)


def cancel_booking(appointment_id: int):
    return cancel_appointment(appointment_id)


def get_appointment_by_id(appointment_id: int):
    return get_appointment_by_id(appointment_id)
