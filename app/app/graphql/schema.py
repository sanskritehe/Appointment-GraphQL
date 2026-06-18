from ariadne import QueryType, make_executable_schema, gql, GraphQLError
from app.services.appointment_service import AppointmentService
from app.services.github_service import GitHubService

type_defs = gql("""
    type Repository {
        id: Int!
        name: String!
        description: String
        stars: Int!
    }

    type Query {
        appointmentById(id: Int!): Appointment
        microsoftRepos: [Repository!]!
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
    # Validate that id is in an acceptable range
    if not isinstance(id, int) or id < 1 or id > 100000:  # Example range
        raise GraphQLError("Invalid ID. Must be a positive integer between 1 and 100000.")

    appointment_service = info.context["appointment_service"]
    appointment = await appointment_service.get_appointment_by_id(id)
    if not appointment:
        raise GraphQLError("Appointment not found")
    return appointment

@query.field("microsoftRepos")
async def resolve_microsoft_repos(_, info):
    github_service = info.context["github_service"]
    try:
        repositories = await github_service.get_repositories_by_org("microsoft")
    except httpx.HTTPStatusError as e:
        raise GraphQLError(f"GitHub API error: {e.response.status_code} - {e.response.json().get('message', 'Unknown error')}")
    except httpx.RequestError as e:
        raise GraphQLError(f"Network error while accessing GitHub API: {str(e)}")
    except ValueError as e:
        raise GraphQLError("Failed to parse response from GitHub API.")
    return repositories

schema = make_executable_schema(type_defs, query)
