"""GitHub API client with rate limiting, error handling, and wait+retry."""

import asyncio
import time
from dataclasses import dataclass
from datetime import UTC, datetime

import httpx
import jwt
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from tracertm.constants import (
    DEFAULT_PAGE_SIZE,
    GRAPHQL_FIRST_DEFAULT,
    HTTP_CREATED,
    HTTP_FORBIDDEN,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_NO_CONTENT,
    HTTP_NOT_FOUND,
    HTTP_UNAUTHORIZED,
    JWT_CLOCK_SKEW,
    JWT_EXPIRY_SHORT,
    MAX_RETRIES_DEFAULT,
    RETRY_BACKOFF_MAX,
    RETRY_BACKOFF_MIN,
    RETRY_BACKOFF_MULTIPLIER,
    TIMEOUT_DEFAULT,
    ZERO,
)


class GitHubClientError(Exception):
    """Base exception for GitHub client errors."""


class GitHubRateLimitError(GitHubClientError):
    """Rate limit exceeded."""

    def __init__(self, reset_at: datetime, message: str = "Rate limit exceeded") -> None:
        """Initialize rate limit error.

        Args:
            reset_at: When the rate limit will reset
            message: Error message
        """
        self.reset_at = reset_at
        super().__init__(message)


@dataclass(frozen=True)
class IssueListParams:
    """Parameters for listing issues."""

    state: str = "open"
    labels: list[str] | None = None
    sort: str = "updated"
    direction: str = "desc"
    per_page: int = DEFAULT_PAGE_SIZE
    page: int = 1


@dataclass(frozen=True)
class IssueUpdateParams:
    """Parameters for updating an issue."""

    title: str | None = None
    body: str | None = None
    state: str | None = None
    labels: list[str] | None = None
    assignees: list[str] | None = None
    milestone: int | None = None


@dataclass(frozen=True)
class PullRequestListParams:
    """Parameters for listing pull requests."""

    state: str = "open"
    sort: str = "updated"
    direction: str = "desc"
    per_page: int = DEFAULT_PAGE_SIZE
    page: int = 1


@dataclass(frozen=True)
class PullRequestUpdateParams:
    """Parameters for updating a pull request."""

    title: str | None = None
    body: str | None = None
    state: str | None = None
    base: str | None = None


@dataclass(frozen=True)
class RepoWebhookParams:
    """Parameters for repository webhooks."""

    webhook_url: str
    secret: str
    events: list[str] | None = None
    active: bool = True


class GitHubAuthError(GitHubClientError):
    """Authentication error."""


class GitHubNotFoundError(GitHubClientError):
    """Resource not found."""


class GitHubClient:
    """GitHub API client with rate limiting and error handling.

    Supports both OAuth tokens, Personal Access Tokens, and GitHub App installation tokens.
    """

    BASE_URL = "https://api.github.com"

    def __init__(
        self,
        token: str,
        timeout: float = TIMEOUT_DEFAULT,
        is_app_token: bool = False,
    ) -> None:
        """Initialize GitHub client.

        Args:
            token: OAuth token, Personal Access Token, or GitHub App installation token.
            timeout: Request timeout in seconds.
            is_app_token: Whether this is a GitHub App installation token.
        """
        self.token = token
        self.timeout = timeout
        self.is_app_token = is_app_token
        self._client: httpx.AsyncClient | None = None

    @classmethod
    async def from_app_installation(
        cls,
        app_id: str,
        private_key: str,
        installation_id: int,
    ) -> "GitHubClient":
        """Create a GitHub client from a GitHub App installation.

        Args:
            app_id: GitHub App ID.
            private_key: GitHub App private key (PEM format).
            installation_id: GitHub App installation ID.

        Returns:
            GitHubClient instance authenticated with installation token.
        """
        # Generate JWT for app authentication
        try:
            private_key_obj = load_pem_private_key(
                private_key.encode() if isinstance(private_key, str) else private_key,
                password=None,
            )
        except Exception as e:
            msg = f"Invalid private key: {e}"
            raise GitHubAuthError(msg) from e

        # Type narrow to RSAPrivateKey for jwt.encode
        if not isinstance(private_key_obj, RSAPrivateKey):
            msg = "GitHub App private key must be RSA"
            raise GitHubAuthError(msg)

        now = int(time.time())
        jwt_payload = {
            "iat": now - JWT_CLOCK_SKEW,
            "exp": now + JWT_EXPIRY_SHORT,
            "iss": app_id,
        }

        app_jwt = jwt.encode(jwt_payload, private_key_obj, algorithm="RS256")

        # Exchange JWT for installation token
        async with asyncio.timeout(TIMEOUT_DEFAULT):
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{cls.BASE_URL}/app/installations/{installation_id}/access_tokens",
                    headers={
                        "Authorization": f"Bearer {app_jwt}",
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28",
                    },
                )

                if response.status_code != HTTP_CREATED:
                    msg = f"Failed to get installation token: {response.text}"
                    raise GitHubAuthError(msg)

                token_data = response.json()
                installation_token = token_data.get("token")

        return cls(installation_token, is_app_token=True)

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                timeout=self.timeout,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @retry(
        stop=stop_after_attempt(MAX_RETRIES_DEFAULT),
        wait=wait_exponential(multiplier=RETRY_BACKOFF_MULTIPLIER, min=RETRY_BACKOFF_MIN, max=RETRY_BACKOFF_MAX),
        retry=retry_if_exception(
            lambda e: (
                isinstance(e, (httpx.NetworkError, httpx.TimeoutException))
                or (isinstance(e, httpx.HTTPStatusError) and e.response.status_code >= HTTP_INTERNAL_SERVER_ERROR)
            ),
        ),
        reraise=True,
    )
    async def _request_once(
        self,
        method: str,
        path: str,
        params: dict[str, str | int] | None = None,
        json: dict[str, object] | None = None,
    ) -> httpx.Response:
        """Perform one request; raises on 5xx so tenacity can retry."""
        client = await self._get_client()
        response = await client.request(method, path, params=params, json=json)
        if response.status_code >= HTTP_INTERNAL_SERVER_ERROR:
            response.raise_for_status()
        return response

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, str | int] | None = None,
        json: dict[str, object] | None = None,
    ) -> dict[str, object] | list[dict[str, object]] | None:
        """Make an authenticated request to GitHub API (with wait+retry on 5xx/network)."""
        response = await self._request_once(method, path, params=params, json=json)

        # Handle rate limiting
        if response.status_code == HTTP_FORBIDDEN and "X-RateLimit-Remaining" in response.headers:
            remaining = int(response.headers.get("X-RateLimit-Remaining", ZERO))
            if remaining == ZERO:
                reset_timestamp = int(response.headers.get("X-RateLimit-Reset", ZERO))
                reset_at = datetime.fromtimestamp(reset_timestamp, tz=UTC)
                raise GitHubRateLimitError(reset_at)

        # Handle auth errors
        if response.status_code == HTTP_UNAUTHORIZED:
            msg = "Invalid or expired token"
            raise GitHubAuthError(msg)

        # Handle not found
        if response.status_code == HTTP_NOT_FOUND:
            msg = f"Resource not found: {path}"
            raise GitHubNotFoundError(msg)

        # Raise for other errors
        response.raise_for_status()

        if response.status_code == HTTP_NO_CONTENT:
            return None

        result = response.json()
        # Type narrow for mypy
        if not isinstance(result, (dict, list, type(None))):
            msg = f"Unexpected response type: {type(result)}"
            raise GitHubClientError(msg)
        return result

    # ==================== USER & AUTH ====================

    async def get_authenticated_user(self) -> dict[str, object]:
        """Get the authenticated user's profile."""
        result = await self._request("GET", "/user")
        if not isinstance(result, dict):
            msg = "Expected dict response"
            raise GitHubClientError(msg)
        return result

    async def get_user(self, username: str) -> dict[str, object]:
        """Get a user's profile."""
        result = await self._request("GET", f"/users/{username}")
        if not isinstance(result, dict):
            msg = "Expected dict response"
            raise GitHubClientError(msg)
        return result

    async def validate_token(self) -> dict[str, object]:
        """Validate the token and return user info with scopes."""
        user = await self.get_authenticated_user()
        # Get scopes from a request
        client = await self._get_client()
        response = await client.get("/user")
        scopes = response.headers.get("X-OAuth-Scopes", "").split(", ")
        return {
            "valid": True,
            "user": user,
            "scopes": [s.strip() for s in scopes if s.strip()],
        }

    # ==================== REPOSITORIES ====================

    async def list_user_repos(
        self,
        sort: str = "updated",
        direction: str = "desc",
        per_page: int = DEFAULT_PAGE_SIZE,
        page: int = 1,
    ) -> list[dict[str, object]]:
        """List repositories for authenticated user."""
        result = await self._request(
            "GET",
            "/user/repos",
            params={
                "sort": sort,
                "direction": direction,
                "per_page": per_page,
                "page": page,
            },
        )
        if not isinstance(result, list):
            msg = "Expected list response"
            raise GitHubClientError(msg)
        return result

    async def list_org_repos(
        self,
        org: str,
        sort: str = "updated",
        direction: str = "desc",
        per_page: int = DEFAULT_PAGE_SIZE,
        page: int = 1,
    ) -> list[dict[str, object]]:
        """List repositories for an organization."""
        result = await self._request(
            "GET",
            f"/orgs/{org}/repos",
            params={
                "sort": sort,
                "direction": direction,
                "per_page": per_page,
                "page": page,
            },
        )
        if not isinstance(result, list):
            msg = "Expected list response"
            raise GitHubClientError(msg)
        return result

    async def get_repo(self, owner: str, repo: str) -> dict[str, object]:
        """Get repository details."""
        result = await self._request("GET", f"/repos/{owner}/{repo}")
        if not isinstance(result, dict):
            msg = "Expected dict response"
            raise GitHubClientError(msg)
        return result

    async def create_repo(
        self,
        name: str,
        description: str | None = None,
        private: bool = False,
        auto_init: bool = False,
        gitignore_template: str | None = None,
        license_template: str | None = None,
        org: str | None = None,
    ) -> dict[str, object]:
        """Create a new repository.

        Args:
            name: Repository name.
            description: Repository description.
            private: Whether the repository should be private.
            auto_init: Whether to initialize the repository with a README.
            gitignore_template: Gitignore template to use.
            license_template: License template to use.
            org: Organization name (if creating in an org).

        Returns:
            Repository data.
        """
        data: dict[str, object] = {
            "name": name,
            "private": private,
            "auto_init": auto_init,
        }
        if description:
            data["description"] = description
        if gitignore_template:
            data["gitignore_template"] = gitignore_template
        if license_template:
            data["license_template"] = license_template

        path = f"/orgs/{org}/repos" if org else "/user/repos"

        result = await self._request("POST", path, json=data)
        if not isinstance(result, dict):
            msg = "Expected dict response"
            raise GitHubClientError(msg)
        return result

    async def search_repos(
        self,
        query: str,
        sort: str = "updated",
        order: str = "desc",
        per_page: int = DEFAULT_PAGE_SIZE,
        page: int = 1,
    ) -> dict[str, object]:
        """Search repositories.

        Args:
            query: Search query (e.g., "language:python", "user:octocat").
            sort: Sort field (stars, forks, help-wanted-issues, updated).
            order: Sort order (asc, desc).
            per_page: Results per page.
            page: Page number.

        Returns:
            Search results with items list.
        """
        result = await self._request(
            "GET",
            "/search/repositories",
            params={
                "q": query,
                "sort": sort,
                "order": order,
                "per_page": per_page,
                "page": page,
            },
        )
        if not isinstance(result, dict):
            msg = "Expected dict response"
            raise GitHubClientError(msg)
        return result

    async def list_installation_repos(
        self,
        _installation_id: int | None = None,
        per_page: int = DEFAULT_PAGE_SIZE,
        page: int = 1,
    ) -> dict[str, object]:
        """List repositories accessible to a GitHub App installation.

        Args:
            installation_id: GitHub App installation ID (optional, uses current token's installation).
            per_page: Results per page.
            page: Page number.

        Returns:
            Dictionary with repositories list and pagination info.
        """
        # When using installation token, use /installation/repositories endpoint
        if self.is_app_token:
            result = await self._request(
                "GET",
                "/installation/repositories",
                params={
                    "per_page": per_page,
                    "page": page,
                },
            )
            if not isinstance(result, dict):
                msg = "Expected dict response"
                raise GitHubClientError(msg)
            # This endpoint returns { repositories: [...], total_count: ... }
            repos = result.get("repositories", [])
            if not isinstance(repos, list):
                repos = []
            return {"repositories": repos, "total_count": len(repos)}
        # Fallback to user repos if not using app token
        repos = await self.list_user_repos(per_page=per_page, page=page)
        return {"repositories": repos, "total_count": len(repos)}

    # ==================== ISSUES ====================

    async def list_issues(
        self,
        owner: str,
        repo: str,
        params: IssueListParams | None = None,
    ) -> list[dict[str, object]]:
        """List issues in a repository."""
        params_obj = params or IssueListParams()
        labels = params_obj.labels
        query_params: dict[str, str | int] = {
            "state": params_obj.state,
            "sort": params_obj.sort,
            "direction": params_obj.direction,
            "per_page": params_obj.per_page,
            "page": params_obj.page,
        }
        if labels:
            query_params["labels"] = ",".join(labels)

        result = await self._request("GET", f"/repos/{owner}/{repo}/issues", params=query_params)
        if not isinstance(result, list):
            msg = "Expected list response"
            raise GitHubClientError(msg)
        return result

    async def get_issue(self, owner: str, repo: str, issue_number: int) -> dict[str, object]:
        """Get a single issue."""
        result = await self._request("GET", f"/repos/{owner}/{repo}/issues/{issue_number}")
        if not isinstance(result, dict):
            msg = "Expected dict response"
            raise GitHubClientError(msg)
        return result

    async def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str | None = None,
        labels: list[str] | None = None,
        assignees: list[str] | None = None,
        milestone: int | None = None,
    ) -> dict[str, object]:
        """Create an issue."""
        data: dict[str, object] = {"title": title}
        if body:
            data["body"] = body
        if labels:
            data["labels"] = labels
        if assignees:
            data["assignees"] = assignees
        if milestone:
            data["milestone"] = milestone

        result = await self._request("POST", f"/repos/{owner}/{repo}/issues", json=data)
        if not isinstance(result, dict):
            msg = "Expected dict response"
            raise GitHubClientError(msg)
        return result

    async def update_issue(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        params: IssueUpdateParams | None = None,
    ) -> dict[str, object]:
        """Update an issue."""
        params = params or IssueUpdateParams()
        data: dict[str, object] = {}
        if params.title is not None:
            data["title"] = params.title
        if params.body is not None:
            data["body"] = params.body
        if params.state is not None:
            data["state"] = params.state
        if params.labels is not None:
            data["labels"] = params.labels
        if params.assignees is not None:
            data["assignees"] = params.assignees
        if params.milestone is not None:
            data["milestone"] = params.milestone

        result = await self._request("PATCH", f"/repos/{owner}/{repo}/issues/{issue_number}", json=data)
        if not isinstance(result, dict):
            msg = "Expected dict response"
            raise GitHubClientError(msg)
        return result

    async def add_issue_comment(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        body: str,
    ) -> dict[str, object]:
        """Add a comment to an issue."""
        result = await self._request(
            "POST",
            f"/repos/{owner}/{repo}/issues/{issue_number}/comments",
            json={"body": body},
        )
        if not isinstance(result, dict):
            msg = "Expected dict response"
            raise GitHubClientError(msg)
        return result

    # ==================== PULL REQUESTS ====================

    async def list_pull_requests(
        self,
        owner: str,
        repo: str,
        params: PullRequestListParams | None = None,
    ) -> list[dict[str, object]]:
        """List pull requests in a repository."""
        params = params or PullRequestListParams()
        result = await self._request(
            "GET",
            f"/repos/{owner}/{repo}/pulls",
            params={
                "state": params.state,
                "sort": params.sort,
                "direction": params.direction,
                "per_page": params.per_page,
                "page": params.page,
            },
        )
        if not isinstance(result, list):
            msg = "Expected list response"
            raise GitHubClientError(msg)
        return result

    async def get_pull_request(self, owner: str, repo: str, pull_number: int) -> dict[str, object]:
        """Get a single pull request."""
        result = await self._request("GET", f"/repos/{owner}/{repo}/pulls/{pull_number}")
        if not isinstance(result, dict):
            msg = "Expected dict response"
            raise GitHubClientError(msg)
        return result

    async def update_pull_request(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        params: PullRequestUpdateParams | None = None,
    ) -> dict[str, object]:
        """Update a pull request."""
        params = params or PullRequestUpdateParams()
        data: dict[str, object] = {}
        if params.title is not None:
            data["title"] = params.title
        if params.body is not None:
            data["body"] = params.body
        if params.state is not None:
            data["state"] = params.state
        if params.base is not None:
            data["base"] = params.base

        result = await self._request("PATCH", f"/repos/{owner}/{repo}/pulls/{pull_number}", json=data)
        if not isinstance(result, dict):
            msg = "Expected dict response"
            raise GitHubClientError(msg)
        return result

    # ==================== WEBHOOKS ====================

    async def list_repo_webhooks(self, owner: str, repo: str) -> list[dict[str, object]]:
        """List webhooks for a repository."""
        result = await self._request("GET", f"/repos/{owner}/{repo}/hooks")
        if not isinstance(result, list):
            msg = "Expected list response"
            raise GitHubClientError(msg)
        return result

    async def create_repo_webhook(
        self,
        owner: str,
        repo: str,
        params: RepoWebhookParams,
    ) -> dict[str, object]:
        """Create a repository webhook."""
        result = await self._request(
            "POST",
            f"/repos/{owner}/{repo}/hooks",
            json={
                "name": "web",
                "active": params.active,
                "events": params.events or ["push", "pull_request", "issues"],
                "config": {
                    "url": params.webhook_url,
                    "content_type": "json",
                    "secret": params.secret,
                    "insecure_ssl": "0",
                },
            },
        )
        if not isinstance(result, dict):
            msg = "Expected dict response"
            raise GitHubClientError(msg)
        return result

    async def delete_repo_webhook(self, owner: str, repo: str, hook_id: int) -> None:
        """Delete a repository webhook."""
        await self._request("DELETE", f"/repos/{owner}/{repo}/hooks/{hook_id}")

    # ==================== SEARCH ====================

    async def search_issues(
        self,
        query: str,
        sort: str = "updated",
        order: str = "desc",
        per_page: int = DEFAULT_PAGE_SIZE,
        page: int = 1,
    ) -> dict[str, object]:
        """Search issues and pull requests."""
        result = await self._request(
            "GET",
            "/search/issues",
            params={
                "q": query,
                "sort": sort,
                "order": order,
                "per_page": per_page,
                "page": page,
            },
        )
        if not isinstance(result, dict):
            msg = "Expected dict response"
            raise GitHubClientError(msg)
        return result

    # ==================== PROJECTS (V2 GraphQL) ====================

    async def graphql_query(self, query: str, variables: dict[str, object] | None = None) -> dict[str, object]:
        """Execute a GraphQL query against the GitHub API."""
        client = await self._get_client()
        response = await client.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": variables or {}},
        )
        response.raise_for_status()
        result = response.json()
        if not isinstance(result, dict):
            msg = "Expected dict response"
            raise GitHubClientError(msg)
        return result

    async def list_projects_graphql(self, owner: str, is_org: bool = True) -> list[dict[str, object]]:
        """List Projects v2 for an owner."""
        query = """
        query($owner: String!, $first: Int!) {
            %s(login: $owner) {
                projectsV2(first: $first) {
                    nodes {
                        id
                        title
                        shortDescription
                        url
                        closed
                        public
                        createdAt
                        updatedAt
                    }
                }
            }
        }
        """ % ("organization" if is_org else "user")

        result = await self.graphql_query(query, {"owner": owner, "first": GRAPHQL_FIRST_DEFAULT})
        key = "organization" if is_org else "user"
        data = result.get("data", {})
        if not isinstance(data, dict):
            return []
        owner_data = data.get(key, {})
        if not isinstance(owner_data, dict):
            return []
        projects_data = owner_data.get("projectsV2", {})
        if not isinstance(projects_data, dict):
            return []
        nodes = projects_data.get("nodes", [])
        return nodes if isinstance(nodes, list) else []

    async def get_project_items(self, project_id: str, first: int = GRAPHQL_FIRST_DEFAULT) -> list[dict[str, object]]:
        """Get items from a GitHub Project v2."""
        query = """
        query($projectId: ID!, $first: Int!) {
            node(id: $projectId) {
                ... on ProjectV2 {
                    items(first: $first) {
                        nodes {
                            id
                            type
                            content {
                                ... on Issue {
                                    id
                                    title
                                    number
                                    state
                                    url
                                }
                                ... on PullRequest {
                                    id
                                    title
                                    number
                                    state
                                    url
                                }
                                ... on DraftIssue {
                                    id
                                    title
                                }
                            }
                            fieldValues(first: 20) {
                                nodes {
                                    ... on ProjectV2ItemFieldTextValue {
                                        text
                                        field {
                                            ... on ProjectV2FieldCommon {
                                                name
                                            }
                                        }
                                    }
                                    ... on ProjectV2ItemFieldSingleSelectValue {
                                        name
                                        field {
                                            ... on ProjectV2FieldCommon {
                                                name
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        result = await self.graphql_query(query, {"projectId": project_id, "first": first})
        data = result.get("data", {})
        if not isinstance(data, dict):
            return []
        node = data.get("node", {})
        if not isinstance(node, dict):
            return []
        items = node.get("items", {})
        if not isinstance(items, dict):
            return []
        nodes = items.get("nodes", [])
        return nodes if isinstance(nodes, list) else []
