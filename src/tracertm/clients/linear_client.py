"""Linear API client using GraphQL."""

from datetime import datetime
from typing import Any, Optional

import httpx


class LinearClientError(Exception):
    """Base exception for Linear client errors."""

    pass


class LinearRateLimitError(LinearClientError):
    """Rate limit exceeded."""

    def __init__(self, reset_at: datetime | None = None, message: str = "Rate limit exceeded"):
        self.reset_at = reset_at
        super().__init__(message)


class LinearAuthError(LinearClientError):
    """Authentication error."""

    pass


class LinearNotFoundError(LinearClientError):
    """Resource not found."""

    pass


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
    ):
        """Initialize Linear client.

        Args:
            api_key: Linear API key.
            timeout: Request timeout in seconds.
        """
        self.api_key = api_key
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

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

    async def _query(
        self,
        query: str,
        variables: dict | None = None,
    ) -> dict:
        """Execute a GraphQL query."""
        client = await self._get_client()

        response = await client.post(
            self.GRAPHQL_URL,
            json={"query": query, "variables": variables or {}},
        )

        # Handle rate limiting
        if response.status_code == 429:
            reset_after = response.headers.get("Retry-After")
            reset_at = None
            if reset_after:
                try:
                    reset_at = datetime.fromtimestamp(float(reset_after))
                except (ValueError, TypeError):
                    pass
            raise LinearRateLimitError(reset_at)

        # Handle auth errors
        if response.status_code == 401:
            raise LinearAuthError("Invalid API key")

        response.raise_for_status()

        result = response.json()

        # Check for GraphQL errors
        if "errors" in result:
            errors = result["errors"]
            if any(e.get("extensions", {}).get("code") == "UNAUTHENTICATED" for e in errors):
                raise LinearAuthError("Invalid API key")
            if any(e.get("message", "").lower().find("not found") >= 0 for e in errors):
                raise LinearNotFoundError(errors[0].get("message", "Resource not found"))
            raise LinearClientError(errors[0].get("message", "GraphQL error"))

        return result.get("data", {})

    # ==================== VIEWER & AUTH ====================

    async def get_viewer(self) -> dict:
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
        return result.get("viewer", {})

    async def validate_api_key(self) -> dict[str, Any]:
        """Validate the API key and return viewer info."""
        viewer = await self.get_viewer()
        return {
            "valid": True,
            "viewer": viewer,
        }

    # ==================== ORGANIZATION & TEAMS ====================

    async def get_organization(self) -> dict:
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
        return result.get("organization", {})

    async def list_teams(self) -> list[dict]:
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
        return result.get("teams", {}).get("nodes", [])

    async def get_team(self, team_id: str) -> dict:
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
        return result.get("team", {})

    # ==================== WORKFLOW STATES ====================

    async def list_workflow_states(self, team_id: str | None = None) -> list[dict]:
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
        return result.get("workflowStates", {}).get("nodes", [])

    # ==================== ISSUES ====================

    async def list_issues(
        self,
        team_id: str | None = None,
        state_filter: str | None = None,
        first: int = 50,
        after: str | None = None,
    ) -> dict:
        """List issues, optionally filtered by team and state."""
        filter_parts = []
        if team_id:
            filter_parts.append(f'team: {{ id: {{ eq: "{team_id}" }} }}')
        if state_filter:
            filter_parts.append(f'state: {{ type: {{ eq: {state_filter} }} }}')

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

    async def get_issue(self, issue_id: str) -> dict:
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
        return result.get("issue", {})

    async def get_issue_by_identifier(self, identifier: str) -> dict:
        """Get an issue by identifier (e.g., 'TEAM-123')."""
        # Parse the identifier
        parts = identifier.split("-")
        if len(parts) < 2:
            raise ValueError(f"Invalid issue identifier: {identifier}")

        team_key = parts[0]
        issue_number = int(parts[1])

        query = """
        query($teamKey: String!, $number: Float!) {
            issue(id: $teamKey, number: $number) {
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
            }
        }
        """
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
                }
            },
        )
        issues = result.get("issues", {}).get("nodes", [])
        if not issues:
            raise LinearNotFoundError(f"Issue {identifier} not found")
        return issues[0]

    async def create_issue(
        self,
        team_id: str,
        title: str,
        description: str | None = None,
        priority: int | None = None,
        assignee_id: str | None = None,
        state_id: str | None = None,
        parent_id: str | None = None,
        label_ids: list[str] | None = None,
        estimate: int | None = None,
        due_date: str | None = None,
    ) -> dict:
        """Create a new issue."""
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
        input_data: dict[str, Any] = {
            "teamId": team_id,
            "title": title,
        }
        if description:
            input_data["description"] = description
        if priority is not None:
            input_data["priority"] = priority
        if assignee_id:
            input_data["assigneeId"] = assignee_id
        if state_id:
            input_data["stateId"] = state_id
        if parent_id:
            input_data["parentId"] = parent_id
        if label_ids:
            input_data["labelIds"] = label_ids
        if estimate is not None:
            input_data["estimate"] = estimate
        if due_date:
            input_data["dueDate"] = due_date

        result = await self._query(query, {"input": input_data})
        return result.get("issueCreate", {}).get("issue", {})

    async def update_issue(
        self,
        issue_id: str,
        title: str | None = None,
        description: str | None = None,
        priority: int | None = None,
        assignee_id: str | None = None,
        state_id: str | None = None,
        label_ids: list[str] | None = None,
        estimate: int | None = None,
        due_date: str | None = None,
    ) -> dict:
        """Update an existing issue."""
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
        input_data: dict[str, Any] = {}
        if title is not None:
            input_data["title"] = title
        if description is not None:
            input_data["description"] = description
        if priority is not None:
            input_data["priority"] = priority
        if assignee_id is not None:
            input_data["assigneeId"] = assignee_id
        if state_id is not None:
            input_data["stateId"] = state_id
        if label_ids is not None:
            input_data["labelIds"] = label_ids
        if estimate is not None:
            input_data["estimate"] = estimate
        if due_date is not None:
            input_data["dueDate"] = due_date

        result = await self._query(query, {"id": issue_id, "input": input_data})
        return result.get("issueUpdate", {}).get("issue", {})

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
        return result.get("issueArchive", {}).get("success", False)

    async def add_comment(self, issue_id: str, body: str) -> dict:
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
        return result.get("commentCreate", {}).get("comment", {})

    # ==================== PROJECTS ====================

    async def list_projects(self) -> list[dict]:
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
        return result.get("projects", {}).get("nodes", [])

    async def get_project(self, project_id: str) -> dict:
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
        return result.get("project", {})

    # ==================== LABELS ====================

    async def list_labels(self, team_id: str | None = None) -> list[dict]:
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
            return result.get("team", {}).get("labels", {}).get("nodes", [])
        else:
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
            return result.get("issueLabels", {}).get("nodes", [])

    # ==================== WEBHOOKS ====================

    async def create_webhook(
        self,
        url: str,
        team_id: str | None = None,
        label: str | None = None,
        resource_types: list[str] | None = None,
    ) -> dict:
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
        input_data: dict[str, Any] = {"url": url}
        if team_id:
            input_data["teamId"] = team_id
        if label:
            input_data["label"] = label
        if resource_types:
            input_data["resourceTypes"] = resource_types

        result = await self._query(query, {"input": input_data})
        return result.get("webhookCreate", {}).get("webhook", {})

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
        return result.get("webhookDelete", {}).get("success", False)

    async def list_webhooks(self) -> list[dict]:
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
        return result.get("webhooks", {}).get("nodes", [])

    # ==================== SEARCH ====================

    async def search_issues(
        self,
        query_text: str,
        first: int = 20,
    ) -> list[dict]:
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
        return result.get("searchIssues", {}).get("nodes", [])
