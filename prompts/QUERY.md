# AI Coding Agent – GraphQL Query Implementation

You are an AI coding agent. Your task is to implement a GraphQL Query resolver.

## Step 1 – GraphQL Schema and Resolvers
- Add the Query to your GraphQL type definitions (schema).
- Implement the resolver function under the service layer, fetching data from the database.
- Follow existing GraphQL patterns in the repository.

## Step 2 – Implement Automated Tests
- You MUST generate/update a test file at `tests/test_graphql.py`.
- Use `fastapi.testclient.TestClient` to test the query.
- Assert the HTTP status is 200, the `"errors"` block is absent, and the `"data"` field matches the database.