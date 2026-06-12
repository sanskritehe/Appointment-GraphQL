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
