from fastapi import FastAPI
from app.db.db_client import database
from app.routes import appointments
from ariadne.asgi import GraphQL
from app.graphql.schema import schema

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

app.include_router(appointments.router)

# GraphQL endpoint
graphql_app = GraphQL(schema, debug=True)
app.add_route("/graphql", graphql_app)
