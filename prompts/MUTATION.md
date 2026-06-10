# AI Coding Agent – GraphQL Mutation Implementation

You are an AI coding agent. Your task is to implement a GraphQL Mutation resolver.

## Step 1 – GraphQL Schema and Resolvers
- Add the Mutation to your GraphQL schema (e.g. create, update, delete operations).
- Implement the resolver, executing updates or inserts via the database layer.
- Follow existing patterns in the repository.

## Step 2 – Implement Automated Tests
- You MUST generate/update a test file at `tests/test_graphql.py`.
- Use `fastapi.testclient.TestClient` to send a POST request with the mutation payload.
- Verify status code is 200, check for any validation errors in the response, and assert data changes in the database.