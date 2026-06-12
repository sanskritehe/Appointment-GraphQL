from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from app.routes import appointments
from app.graphql.schema import schema

app = FastAPI(title="Appointment Service")

# Include existing REST router
app.include_router(appointments.router)

# Include new GraphQL router
graphql_router = GraphQLRouter(schema)
app.include_router(graphql_router, prefix="/graphql")
