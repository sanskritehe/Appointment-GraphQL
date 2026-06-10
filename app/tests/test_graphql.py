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
