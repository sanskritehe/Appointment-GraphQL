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
