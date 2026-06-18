### FILE: app/graphql/schema.py
```python
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
```

---

### FILE: app/services/github_service.py
```python
import httpx
from fastapi import Depends

class GitHubService:
    def __init__(self, http_client: httpx.AsyncClient = Depends(httpx.AsyncClient)):
        self.http_client = http_client

    async def get_repositories_by_org(self, org_name: str) -> list:
        """
        Fetch repositories for a given organization name from GitHub API.
        """
        url = f"https://api.github.com/orgs/{org_name}/repos"
        try:
            response = await self.http_client.get(url, timeout=10.0)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise Exception("GitHub organization not found.")
            else:
                raise Exception(f"GitHub API error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise Exception(f"Network error while accessing GitHub API: {str(e)}")

        # Parse the JSON response
        try:
            repos_data = response.json()
        except ValueError:
            raise Exception("Invalid JSON response received from GitHub API")
        
        # Verify and map the extracted data
        repositories = []
        for repo in repos_data:
            # Validate expected keys from the response
            if not all(key in repo for key in ["id", "name", "stargazers_count"]):
                raise Exception("Unexpected response structure from GitHub API")
            repositories.append({
                "id": repo["id"],
                "name": repo["name"],
                "description": repo.get("description", ""),
                "stars": repo["stargazers_count"],
            })

        return repositories
```

---

### FILE: tests/test_graphql.py
```python
import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_github_service(mocker):
    """
    Mock the GitHubService to simulate external API responses.
    """
    mocked_service = mocker.patch("app.services.github_service.GitHubService")
    mocked_client_instance = mocked_service.return_value
    mocked_client_instance.get_repositories_by_org = AsyncMock(return_value=[
        {
            "id": 1,
            "name": "Repo1",
            "description": "Test repository 1",
            "stars": 100,
        },
        {
            "id": 2,
            "name": "Repo2",
            "description": "Test repository 2",
            "stars": 200,
        },
    ])
    return mocked_client_instance

def test_microsoft_repos_success(mock_github_service):
    query = """
    query GetMicrosoftRepos {
        microsoftRepos {
            id
            name
            description
            stars
        }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    assert "errors" not in response.json()

    repos = response.json()["data"]["microsoftRepos"]
    assert repos == [
        {
            "id": 1,
            "name": "Repo1",
            "description": "Test repository 1",
            "stars": 100,
        },
        {
            "id": 2,
            "name": "Repo2",
            "description": "Test repository 2",
            "stars": 200,
        },
    ]

def test_microsoft_repos_http_status_error(mocker):
    """
    Test GitHubService when GitHub API returns an HTTPStatusError (e.g., 404 or 500).
    """
    mocker.patch(
        "app.services.github_service.GitHubService.get_repositories_by_org",
        side_effect=httpx.HTTPStatusError("Not Found", request=None, response=mocker.Mock(status_code=404, text="Not found"))
    )
    query = """
    query GetMicrosoftRepos {
        microsoftRepos {
            id
            name
            description
            stars
        }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    assert "errors" in response.json()
    assert response.json()["errors"][0]["message"] == "GitHub API error: 404 - Not found"

def test_microsoft_repos_request_error(mocker):
    """
    Test GitHubService when a network-related error occurs.
    """
    mocker.patch(
        "app.services.github_service.GitHubService.get_repositories_by_org",
        side_effect=httpx.RequestError("Timeout occurred", request=None)
    )
    query = """
    query GetMicrosoftRepos {
        microsoftRepos {
            id
            name
            description
            stars
        }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    assert "errors" in response.json()
    assert response.json()["errors"][0]["message"] == "Network error while accessing GitHub API: Timeout occurred"

def test_microsoft_repos_invalid_json_response(mocker):
    """
    Test GitHubService when GitHub API returns invalid JSON data.
    """
    mocker.patch(
        "app.services.github_service.GitHubService.get_repositories_by_org",
        side_effect=ValueError("Invalid JSON response")
    )
    query = """
    query GetMicrosoftRepos {
        microsoftRepos {
            id
            name
            description
            stars
        }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    assert "errors" in response.json()
    assert response.json()["errors"][0]["message"] == "Failed to parse response from GitHub API."

def test_appointment_by_id_validation():
    query = """
    query GetAppointmentById($id: Int!) {
        appointmentById(id: $id) {
            id
            user
            time
            status
        }
    }
    """
    response = client.post("/graphql", json={"query": query, "variables": {"id": -5}})
    assert response.status_code == 200
    assert "errors" in response.json()
    assert response.json()["errors"][0]["message"] == "Invalid ID. Must be a positive integer between 1 and 100000."

    response = client.post("/graphql", json={"query": query, "variables": {"id": 100001}})
    assert response.status_code == 200
    assert "errors" in response.json()
    assert response.json()["errors"][0]["message"] == "Invalid ID. Must be a positive integer between 1 and 100000."

    response = client.post("/graphql", json={"query": query, "variables": {"id": "abc"}})
    assert response.status_code == 200
    assert "errors" in response.json()
    assert response.json()["errors"][0]["message"] == "Invalid ID. Must be a positive integer between 1 and 100000."
```