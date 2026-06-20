"""Linear API client using GraphQL with wait+retry."""

import contextlib
from datetime import UTC, datetime
from typing import cast

import httpx
from pydantic import BaseModel, Field
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

# HTTP status codes
_STATUS_SERVER_ERROR = 500
_STATUS_TOO_MANY_REQUESTS = 429
_STATUS_UNAUTHORIZED = 401

# Identifier format: TEAM-NUMBER (e.g. TEAM-123)
_MIN_IDENTIFIER_PARTS = 2


class LinearClientError(Exception):
    """Base exception for Linear client errors."""


class LinearRateLimitError(LinearClientError):
    """Rate limit exceeded."""

    def __init__(self, reset_at: datetime | None = None, message: str = "Rate limit exceeded") -> None:
        """Initialize Linear rate limit error.

        Args:
            reset_at: Optional reset time
            message: Error message
        """
        self.reset_at = reset_at
        super().__init__(message)


class LinearAuthError(LinearClientError):
    """Authentication error."""


class LinearNotFoundError(LinearClientError):
    """Resource not found."""


# ==================== PYDANTIC MODELS ====================


class IssueCreateRequest(BaseModel):
    """Request model for creating an issue."""

    team_id: str = Field(..., description="Team ID to create issue in")
    title: str = Field(..., description="Issue title")
    description: str | None = Field(None, description="Issue description")
    priority: int | None = Field(None, ge=0, le=4, description="Issue priority (0-4)")
    assignee_id: str | None = Field(None, description="User ID to assign issue to")
    state_id: str | None = Field(None, description="Workflow state ID")
    parent_id: str | None = Field(None, description="Parent issue ID")
    label_ids: list[str] | None = Field(None, description="List of label IDs")
    estimate: int | None = Field(None, ge=0, description="Issue estimate")
    due_date: str | None = Field(None, description="ISO date string for due date")

    def to_linear_input(self) -> dict[str, object]:
        """Convert to Linear API input format."""
        data: dict[str, object] = {
            "teamId": self.team_id,
            "title": self.title,
        }
        if self.description:
            data["description"] = self.description
        if self.priority is not None:
            data["priority"] = self.priority
        if self.assignee_id:
            data["assigneeId"] = self.assignee_id
        if self.state_id:
            data["stateId"] = self.state_id
        if self.parent_id:
            data["parentId"] = self.parent_id
        if self.label_ids:
            data["labelIds"] = self.label_ids
        if self.estimate is not None:
            data["estimate"] = self.estimate
        if self.due_date:
            data["dueDate"] = self.due_date
        return data


class IssueUpdateRequest(BaseModel):
    """Request model for updating an issue."""

    issue_id: str = Field(..., description="Issue ID to update")
    title: str | None = Field(None, description="New issue title")
    description: str | None = Field(None, description="New issue description")
    priority: int | None = Field(None, ge=0, le=4, description="New priority (0-4)")
    assignee_id: str | None = Field(None, description="New assignee user ID")
    state_id: str | None = Field(None, description="New workflow state ID")
    label_ids: list[str] | None = Field(None, description="New list of label IDs")
    estimate: int | None = Field(None, ge=0, description="New estimate")
    due_date: str | None = Field(None, description="New ISO date string for due date")

    def to_linear_input(self) -> dict[str, object]:
        """Convert to Linear API input format (only set fields)."""
        data: dict[str, object] = {}
        if self.title is not None:
            data["title"] = self.title
        if self.description is not None:
            data["description"] = self.description
        if self.priority is not None:
            data["priority"] = self.priority
        if self.assignee_id is not None:
            data["assigneeId"] = self.assignee_id
        if self.state_id is not None:
            data["stateId"] = self.state_id
        if self.label_ids is not None:
            data["labelIds"] = self.label_ids
        if self.estimate is not None:
            data["estimate"] = self.estimate
        if self.due_date is not None:
            data["dueDate"] = self.due_date
        return data


class LinearClient:
    """Linear API client using GraphQL.

    Linear uses GraphQL exclusively, so all operations are done through
    GraphQL queries and mutations.
    """

    GRAPHQL_URL = "https://api.linear.app/graphql"

    def __init__(
        self,
        api_key: str,
        timeout: float = 30.0,
    ) -> None:
        """Initialize Linear client.

        Args:
            api_key: Linear API key.
            timeout: Request timeout in seconds.
        """
        self.api_key = api_key
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers={
                    "Authorization": self.api_key,
                    "Content-Type": "application/json",
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
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception(
            lambda e: (
                isinstance(e, (httpx.NetworkError, httpx.TimeoutException))
                or (isinstance(e, httpx.HTTPStatusError) and e.response.status_code >= _STATUS_SERVER_ERROR)
            ),
        ),
        reraise=True,
    )
    async def _query_once(
        self,
        query: str,
        variables: dict[str, object] | None = None,
    ) -> httpx.Response:
        """Execute one GraphQL request; raises on 5xx so tenacity can retry."""
        client = await self._get_client()
        response = await client.post(
            self.GRAPHQL_URL,
            json={"query": query, "variables": variables or {}},
        )
        if response.status_code >= _STATUS_SERVER_ERROR:
            response.raise_for_status()
        return response

    async def _query(
        self,
        query: str,
        variables: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Execute a GraphQL query (with wait+retry on 5xx/network)."""
        response = await self._query_once(query, variables)

        # Handle rate limiting
        if response.status_code == _STATUS_TOO_MANY_REQUESTS:
            reset_after = response.headers.get("Retry-After")
            reset_at = None
            if reset_after:
                with contextlib.suppress(ValueError, TypeError):
                    reset_at = datetime.fromtimestamp(float(reset_after), tz=UTC)
            raise LinearRateLimitError(reset_at)

        # Handle auth errors
        if response.status_code == _STATUS_UNAUTHORIZED:
            msg = "Invalid API key"
            raise LinearAuthError(msg)

        response.raise_for_status()

        result = response.json()

        # Check for GraphQL errors
        if "errors" in result:
            errors = result["errors"]
            if any(cast("dict[str, object]", e.get("extensions", {})).get("code") == "UNAUTHENTICATED" for e in errors):
                msg = "Invalid API key"
                raise LinearAuthError(msg)
            if any(e.get("message", "").lower().find("not found") >= 0 for e in errors):
                raise LinearNotFoundError(errors[0].get("message", "Resource not found"))
            raise LinearClientError(errors[0].get("message", "GraphQL error"))

        data = cast("dict[str, object]", result.get("data", {}))
        return data if isinstance(data, dict) else {}

    # ==================== VIEWER & AUTH ====================

    async def get_viewer(self) -> dict[str, object]:
        """Get the authenticated user's profile."""
        query = """
        query {
            viewer {
                id
                name
                email
                displayName
                avatarUrl
                active
                createdAt
            }
        }
        """
        result = await self._query(query)
        value = cast("dict[str, object]", result.get("viewer", {}))
        return value if isinstance(value, dict) else dict[str, object]()

    async def validate_api_key(self) -> dict[str, object]:
        """Validate the API key and return viewer info."""
        viewer = await self.get_viewer()
        return {
            "valid": True,
            "viewer": viewer,
        }

    # ==================== ORGANIZATION & TEAMS ====================

    async def get_organization(self) -> dict[str, object]:
        """Get the organization for the API key."""
        query = """
        query {
            organization {
                id
                name
                urlKey
                logoUrl
                createdAt
            }
        }
        """
        result = await self._query(query)
        value = cast("dict[str, object]", result.get("organization", {}))
        return value if isinstance(value, dict) else dict[str, object]()

    async def list_teams(self) -> list[dict[str, object]]:
        """List all teams in the organization."""
        query = """
        query {
            teams {
                nodes {
                    id
                    name
                    key
                    description
                    icon
                    color
                    private
                    createdAt
                    updatedAt
                }
            }
        }
        """
        result = await self._query(query)
        outer = cast("dict[str, object]", result.get("teams", {}))
        if not isinstance(outer, dict):
            return []
        inner = cast("list[dict[str, object]]", outer.get("nodes", []))
        return inner if isinstance(inner, list) else []

    async def get_team(self, team_id: str) -> dict[str, object]:
        """Get a team by ID."""
        query = """
        query($id: String!) {
            team(id: $id) {
                id
                name
                key
                description
                icon
                color
                private
                createdAt
                updatedAt
            }
        }
        """
        result = await self._query(query, {"id": team_id})
        value = cast("dict[str, object]", result.get("team", {}))
        return value if isinstance(value, dict) else dict[str, object]()

    # ==================== WORKFLOW STATES ====================

    async def list_workflow_states(self, team_id: str | None = None) -> list[dict[str, object]]:
        """List workflow states, optionally filtered by team."""
        query = """
        query($teamId: String) {
            workflowStates(filter: { team: { id: { eq: $teamId } } }) {
                nodes {
                    id
                    name
                    color
                    type
                    position
                    team {
                        id
                        key
                    }
                }
            }
        }
        """
        result = await self._query(query, {"teamId": team_id})
        outer = cast("dict[str, object]", result.get("workflowStates", {}))
        if not isinstance(outer, dict):
            return []
        inner = cast("list[dict[str, object]]", outer.get("nodes", []))
        return inner if isinstance(inner, list) else []

    # ==================== ISSUES ====================

    async def list_issues(
        self,
        team_id: str | None = None,
        state_filter: str | None = None,
        first: int = 50,
        after: str | None = None,
    ) -> dict[str, object]:
        """List issues, optionally filtered by team and state."""
        filter_parts = []
        if team_id:
            filter_parts.append(f'team: {{ id: {{ eq: "{team_id}" }} }}')
        if state_filter:
            filter_parts.append(f"state: {{ type: {{ eq: {state_filter} }} }}")

        filter_str = ", ".join(filter_parts)
        filter_arg = f"filter: {{ {filter_str} }}" if filter_parts else ""

        query = f"""
        query($first: Int!, $after: String) {{
            issues({filter_arg}, first: $first, after: $after, orderBy: updatedAt) {{
                nodes {{
                    id
                    identifier
                    title
                    description
                    priority
                    priorityLabel
                    estimate
                    url
                    createdAt
                    updatedAt
                    completedAt
                    canceledAt
                    dueDate
                    state {{
                        id
                        name
                        type
                    }}
                    assignee {{
                        id
                        name
                        email
                    }}
                    team {{
                        id
                        key
                        name
                    }}
                    labels {{
                        nodes {{
                            id
                            name
                            color
                        }}
                    }}
                    parent {{
                        id
                        identifier
                    }}
                }}
                pageInfo {{
                    hasNextPage
                    endCursor
                }}
            }}
        }}
        """
        return await self._query(query, {"first": first, "after": after})

    async def get_issue(self, issue_id: str) -> dict[str, object]:
        """Get an issue by ID."""
        query = """
        query($id: String!) {
            issue(id: $id) {
                id
                identifier
                title
                description
                priority
                priorityLabel
                estimate
                url
                createdAt
                updatedAt
                completedAt
                canceledAt
                dueDate
                state {
                    id
                    name
                    type
                }
                assignee {
                    id
                    name
                    email
                }
                team {
                    id
                    key
                    name
                }
                labels {
                    nodes {
                        id
                        name
                        color
                    }
                }
                parent {
                    id
                    identifier
                }
                comments {
                    nodes {
                        id
                        body
                        createdAt
                        user {
                            id
                            name
                        }
                    }
                }
            }
        }
        """
        result = await self._query(query, {"id": issue_id})
        value = cast("dict[str, object]", result.get("issue", {}))
        return value if isinstance(value, dict) else dict[str, object]()

    async def get_issue_by_identifier(self, identifier: str) -> dict[str, object]:
        """Get an issue by identifier (e.g., 'TEAM-123')."""
        # Parse the identifier (e.g. TEAM-123 => team_key + issue_number)
        parts = identifier.split("-")
        if len(parts) < _MIN_IDENTIFIER_PARTS:
            msg = f"Invalid issue identifier: {identifier}"
            raise ValueError(msg)

        team_key = parts[0]
        issue_number = int(parts[1])

        # This doesn't quite work - Linear needs different approach
        # Use search instead
        search_query = """
        query($filter: IssueFilter!) {
            issues(filter: $filter, first: 1) {
                nodes {
                    id
                    identifier
                    title
                    description
                    priority
                    priorityLabel
                    url
                    createdAt
                    updatedAt
                    state {
                        id
                        name
                        type
                    }
                    assignee {
                        id
                        name
                    }
                    team {
                        id
                        key
                        name
                    }
                }
            }
        }
        """
        result = await self._query(
            search_query,
            {
                "filter": {
                    "team": {"key": {"eq": team_key}},
                    "number": {"eq": issue_number},
                },
            },
        )
        issues_obj = cast("dict[str, object]", result.get("issues", {}))
        nodes = cast("list[dict[str, object]]", issues_obj.get("nodes", []))
        if not nodes:
            msg = f"Issue {identifier} not found"
            raise LinearNotFoundError(msg)
        return nodes[0]

    async def create_issue(self, request: IssueCreateRequest) -> dict[str, object]:
        """Create a new issue.

        Args:
            request: IssueCreateRequest model with issue details

        Returns:
            Created issue object with id, identifier, url, etc.
        """
        query = """
        mutation($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue {
                    id
                    identifier
                    title
                    url
                    state {
                        id
                        name
                    }
                    team {
                        id
                        key
                    }
                }
            }
        }
        """
        input_data = request.to_linear_input()
        result = await self._query(query, {"input": input_data})
        value = cast("dict[str, object]", result.get("issueCreate", {}))
        return value if isinstance(value, dict) else dict[str, object]().get("issue", {})

    async def update_issue(self, request: IssueUpdateRequest) -> dict[str, object]:
        """Update an existing issue.

        Args:
            request: IssueUpdateRequest model with update details

        Returns:
            Updated issue object
        """
        query = """
        mutation($id: String!, $input: IssueUpdateInput!) {
            issueUpdate(id: $id, input: $input) {
                success
                issue {
                    id
                    identifier
                    title
                    url
                    state {
                        id
                        name
                    }
                    updatedAt
                }
            }
        }
        """
        input_data = request.to_linear_input()
        result = await self._query(query, {"id": request.issue_id, "input": input_data})
        value = cast("dict[str, object]", result.get("issueUpdate", {}))
        return value if isinstance(value, dict) else dict[str, object]().get("issue", {})

    async def archive_issue(self, issue_id: str) -> bool:
        """Archive an issue."""
        query = """
        mutation($id: String!) {
            issueArchive(id: $id) {
                success
            }
        }
        """
        result = await self._query(query, {"id": issue_id})
        archive_result = cast("dict[str, object]", result.get("issueArchive", {}))
        if not isinstance(archive_result, dict):
            return False
        return cast("bool", archive_result.get("success", False))

    async def add_comment(self, issue_id: str, body: str) -> dict[str, object]:
        """Add a comment to an issue."""
        query = """
        mutation($input: CommentCreateInput!) {
            commentCreate(input: $input) {
                success
                comment {
                    id
                    body
                    createdAt
                    user {
                        id
                        name
                    }
                }
            }
        }
        """
        result = await self._query(query, {"input": {"issueId": issue_id, "body": body}})
        value = cast("dict[str, object]", result.get("commentCreate", {}))
        return value if isinstance(value, dict) else dict[str, object]().get("comment", {})

    # ==================== PROJECTS ====================

    async def list_projects(self) -> list[dict[str, object]]:
        """List all projects."""
        query = """
        query {
            projects(first: 100) {
                nodes {
                    id
                    name
                    description
                    icon
                    color
                    state
                    url
                    progress
                    startDate
                    targetDate
                    createdAt
                    updatedAt
                    teams {
                        nodes {
                            id
                            key
                            name
                        }
                    }
                }
            }
        }
        """
        result = await self._query(query)
        outer = cast("dict[str, object]", result.get("projects", {}))
        if not isinstance(outer, dict):
            return []
        inner = cast("list[dict[str, object]]", outer.get("nodes", []))
        return inner if isinstance(inner, list) else []

    async def get_project(self, project_id: str) -> dict[str, object]:
        """Get a project by ID."""
        query = """
        query($id: String!) {
            project(id: $id) {
                id
                name
                description
                icon
                color
                state
                url
                progress
                startDate
                targetDate
                createdAt
                updatedAt
                teams {
                    nodes {
                        id
                        key
                        name
                    }
                }
                issues {
                    nodes {
                        id
                        identifier
                        title
                        state {
                            name
                            type
                        }
                    }
                }
            }
        }
        """
        result = await self._query(query, {"id": project_id})
        value = cast("dict[str, object]", result.get("project", {}))
        return value if isinstance(value, dict) else dict[str, object]()

    # ==================== LABELS ====================

    async def list_labels(self, team_id: str | None = None) -> list[dict[str, object]]:
        """List labels, optionally filtered by team."""
        if team_id:
            query = """
            query($teamId: String!) {
                team(id: $teamId) {
                    labels {
                        nodes {
                            id
                            name
                            color
                            description
                        }
                    }
                }
            }
            """
            result = await self._query(query, {"teamId": team_id})
            team_data = cast("dict[str, object]", result.get("team", {}))
            if not isinstance(team_data, dict):
                return []
            labels_data = cast("dict[str, object]", team_data.get("labels", {}))
            if not isinstance(labels_data, dict):
                return []
            nodes = cast("list[dict[str, object]]", labels_data.get("nodes", []))
            return nodes if isinstance(nodes, list) else []
        query = """
            query {
                issueLabels(first: 100) {
                    nodes {
                        id
                        name
                        color
                        description
                        team {
                            id
                            key
                        }
                    }
                }
            }
            """
        result = await self._query(query)
        outer = cast("dict[str, object]", result.get("issueLabels", {}))
        if not isinstance(outer, dict):
            return []
        inner = cast("list[dict[str, object]]", outer.get("nodes", []))
        return inner if isinstance(inner, list) else []

    # ==================== WEBHOOKS ====================

    async def create_webhook(
        self,
        url: str,
        team_id: str | None = None,
        label: str | None = None,
        resource_types: list[str] | None = None,
    ) -> dict[str, object]:
        """Create a webhook.

        Args:
            url: The webhook URL.
            team_id: Optional team ID to filter events.
            label: Optional label for the webhook.
            resource_types: Types of resources to subscribe to (Issue, Comment, etc.).
        """
        query = """
        mutation($input: WebhookCreateInput!) {
            webhookCreate(input: $input) {
                success
                webhook {
                    id
                    url
                    enabled
                    team {
                        id
                        key
                    }
                    resourceTypes
                    createdAt
                }
            }
        }
        """
        input_data: dict[str, object] = {"url": url}
        if team_id:
            input_data["teamId"] = team_id
        if label:
            input_data["label"] = label
        if resource_types:
            input_data["resourceTypes"] = resource_types

        result = await self._query(query, {"input": input_data})
        value = cast("dict[str, object]", result.get("webhookCreate", {}))
        return value if isinstance(value, dict) else dict[str, object]().get("webhook", {})

    async def delete_webhook(self, webhook_id: str) -> bool:
        """Delete a webhook."""
        query = """
        mutation($id: String!) {
            webhookDelete(id: $id) {
                success
            }
        }
        """
        result = await self._query(query, {"id": webhook_id})
        delete_result = cast("dict[str, object]", result.get("webhookDelete", {}))
        if not isinstance(delete_result, dict):
            return False
        return cast("bool", delete_result.get("success", False))

    async def list_webhooks(self) -> list[dict[str, object]]:
        """List all webhooks."""
        query = """
        query {
            webhooks {
                nodes {
                    id
                    url
                    enabled
                    label
                    resourceTypes
                    team {
                        id
                        key
                    }
                    createdAt
                }
            }
        }
        """
        result = await self._query(query)
        outer = cast("dict[str, object]", result.get("webhooks", {}))
        if not isinstance(outer, dict):
            return []
        inner = cast("list[dict[str, object]]", outer.get("nodes", []))
        return inner if isinstance(inner, list) else []

    # ==================== SEARCH ====================

    async def search_issues(
        self,
        query_text: str,
        first: int = 20,
    ) -> list[dict[str, object]]:
        """Search for issues by text."""
        query = """
        query($query: String!, $first: Int!) {
            searchIssues(query: $query, first: $first) {
                nodes {
                    id
                    identifier
                    title
                    description
                    url
                    state {
                        id
                        name
                        type
                    }
                    team {
                        id
                        key
                        name
                    }
                    assignee {
                        id
                        name
                    }
                    createdAt
                    updatedAt
                }
            }
        }
        """
        result = await self._query(query, {"query": query_text, "first": first})
        outer = cast("dict[str, object]", result.get("searchIssues", {}))
        if not isinstance(outer, dict):
            return []
        inner = cast("list[dict[str, object]]", outer.get("nodes", []))
        return inner if isinstance(inner, list) else []
