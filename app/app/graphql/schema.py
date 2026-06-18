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
