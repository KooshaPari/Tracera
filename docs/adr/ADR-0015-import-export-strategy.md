# ADR-0015: Import/Export Strategy

**Status:** Accepted
**Date:** 2026-02-10
**Deciders:** Development Team
**Supersedes:** N/A

---

## Context

TraceRTM needs to import/export requirements from existing systems:

1. **GitHub:** Issues, Pull Requests, Projects (alpha/beta)
2. **Jira:** Issues, Epics, Stories, Sub-tasks
3. **Linear:** Issues, Projects, Roadmaps
4. **OpenAPI specs:** Extract endpoints as requirements
5. **Markdown files:** Import/export for offline editing
6. **CSV/Excel:** Bulk import/export

Import requirements:
- **Preserve links:** Parent-child relationships, issue links
- **Map fields:** Title, description, status, priority, assignee
- **Handle duplicates:** Detect existing items by external ID
- **Incremental sync:** Import only new/changed items

Export requirements:
- **Multiple formats:** JSON, CSV, Markdown, PDF
- **Preserve structure:** Hierarchies, links, metadata
- **Customizable:** Select fields, filter items

## Decision

We will implement:
- **GitHub import:** GraphQL API + webhooks for real-time sync
- **Jira import:** REST API + polling (no webhooks in free tier)
- **Linear import:** GraphQL API + webhooks
- **OpenAPI import:** Parse OpenAPI 3.0/3.1 specs → endpoints as requirements
- **Markdown export:** Convert items to markdown (for Git versioning)
- **JSON export:** Full data dump (backup, migration)

**Import strategy:**
1. **One-time import:** Bulk import all items (initial migration)
2. **Incremental sync:** Poll/webhook for updates
3. **Bidirectional sync:** (future) Changes in TraceRTM → push to external system

## Rationale

### GitHub Import (GraphQL)

**Technology Stack:**
```python
# Python GitHub client
import httpx

async def import_github_issues(owner: str, repo: str, token: str):
    """Import GitHub issues via GraphQL API."""
    query = """
    query($owner: String!, $repo: String!, $cursor: String) {
      repository(owner: $owner, name: $repo) {
        issues(first: 100, after: $cursor) {
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            id
            number
            title
            body
            state
            labels(first: 10) {
              nodes { name }
            }
            assignees(first: 10) {
              nodes { login }
            }
            createdAt
            updatedAt
          }
        }
      }
    }
    """

    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": {"owner": owner, "repo": repo}},
            headers=headers,
        )
        data = response.json()
        issues = data["data"]["repository"]["issues"]["nodes"]

        # Convert to TraceRTM items
        items = []
        for issue in issues:
            items.append({
                "external_id": f"github:{owner}/{repo}#{issue['number']}",
                "title": issue["title"],
                "description": issue["body"],
                "status": issue["state"].lower(),
                "labels": [label["name"] for label in issue["labels"]["nodes"]],
                "metadata": {"github_issue_number": issue["number"]},
            })

        return items
```

**Webhooks (real-time sync):**
```python
@router.post("/webhooks/github")
async def github_webhook(request: Request, session: AsyncSession):
    """Handle GitHub webhook events."""
    event_type = request.headers.get("X-GitHub-Event")
    payload = await request.json()

    if event_type == "issues":
        action = payload["action"]  # opened, edited, closed
        issue = payload["issue"]

        # Update or create item
        external_id = f"github:{payload['repository']['full_name']}#{issue['number']}"
        item = await item_service.get_by_external_id(session, external_id)

        if action == "opened" and not item:
            await item_service.create(session, {
                "external_id": external_id,
                "title": issue["title"],
                "description": issue["body"],
            })
        elif action == "edited" and item:
            await item_service.update(session, item.id, {
                "title": issue["title"],
                "description": issue["body"],
            })
        elif action == "closed" and item:
            await item_service.update(session, item.id, {"status": "closed"})

    return {"status": "ok"}
```

### Jira Import (REST API)

```python
async def import_jira_issues(base_url: str, project_key: str, token: str):
    """Import Jira issues via REST API."""
    url = f"{base_url}/rest/api/3/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "jql": f"project = {project_key}",
        "maxResults": 100,
        "fields": "summary,description,status,priority,assignee,parent",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        data = response.json()
        issues = data["issues"]

        items = []
        for issue in issues:
            fields = issue["fields"]
            items.append({
                "external_id": f"jira:{issue['key']}",
                "title": fields["summary"],
                "description": fields.get("description", ""),
                "status": fields["status"]["name"].lower(),
                "priority": fields.get("priority", {}).get("name", "medium").lower(),
                "metadata": {
                    "jira_key": issue["key"],
                    "jira_type": fields["issuetype"]["name"],
                },
            })

        return items
```

### OpenAPI Import

```python
import yaml
from openapi_spec_validator import validate_spec

async def import_openapi_spec(file_path: str):
    """Parse OpenAPI spec, create requirements for each endpoint."""
    with open(file_path) as f:
        spec = yaml.safe_load(f)

    validate_spec(spec)  # Ensure valid OpenAPI 3.0/3.1

    items = []
    for path, path_item in spec["paths"].items():
        for method, operation in path_item.items():
            if method not in ["get", "post", "put", "delete", "patch"]:
                continue

            items.append({
                "external_id": f"openapi:{spec['info']['title']}:{method.upper()} {path}",
                "title": f"{method.upper()} {path}",
                "description": operation.get("summary", "") + "\n\n" + operation.get("description", ""),
                "item_type": "api_endpoint",
                "metadata": {
                    "http_method": method.upper(),
                    "path": path,
                    "operation_id": operation.get("operationId"),
                    "tags": operation.get("tags", []),
                },
            })

    return items
```

### Markdown Export

```python
async def export_to_markdown(session: AsyncSession, project_id: str) -> str:
    """Export project to markdown format."""
    items = await item_service.list_by_project(session, project_id)
    links = await link_service.list_by_project(session, project_id)

    md = f"# Project: {project.title}\n\n"

    # Requirements section
    requirements = [i for i in items if i.item_type == "requirement"]
    md += "## Requirements\n\n"
    for req in requirements:
        md += f"### {req.title} ({req.id})\n\n"
        md += f"{req.description}\n\n"

        # Linked test cases
        linked_tests = [l.target_item for l in links if l.source_item_id == req.id and l.link_type == "tests"]
        if linked_tests:
            md += "**Test Cases:**\n"
            for test in linked_tests:
                md += f"- [{test.title}](#{test.id})\n"
            md += "\n"

    # Test cases section
    test_cases = [i for i in items if i.item_type == "test_case"]
    md += "## Test Cases\n\n"
    for test in test_cases:
        md += f"### {test.title} ({test.id})\n\n"
        md += f"{test.description}\n\n"

    return md
```

### JSON Export (Full Backup)

```python
async def export_to_json(session: AsyncSession, project_id: str) -> dict:
    """Export project to JSON (full data dump)."""
    project = await project_service.get_by_id(session, project_id)
    items = await item_service.list_by_project(session, project_id)
    links = await link_service.list_by_project(session, project_id)

    return {
        "version": "1.0",
        "exported_at": datetime.utcnow().isoformat(),
        "project": {
            "id": str(project.id),
            "title": project.title,
            "description": project.description,
        },
        "items": [
            {
                "id": str(item.id),
                "item_type": item.item_type,
                "title": item.title,
                "description": item.description,
                "status": item.status,
                "metadata": item.metadata,
            }
            for item in items
        ],
        "links": [
            {
                "source_id": str(link.source_item_id),
                "target_id": str(link.target_item_id),
                "link_type": link.link_type,
            }
            for link in links
        ],
    }
```

## Alternatives Rejected

### Alternative 1: Direct Database Replication

- **Description:** Import by copying database rows directly
- **Pros:** Fast, simple
- **Cons:** No transformation, no field mapping, brittle (schema changes break import)
- **Why Rejected:** External systems have different schemas. Need transformation layer.

### Alternative 2: ETL Tools (Airbyte, Fivetran)

- **Description:** Use third-party ETL for import/export
- **Pros:** Pre-built connectors, scheduling, monitoring
- **Cons:** Expensive, vendor lock-in, overkill for traceability system
- **Why Rejected:** Custom import scripts simpler, cheaper, more flexible.

### Alternative 3: CSV-only Import

- **Description:** Only support CSV import (no API integrations)
- **Pros:** Simple, universal format
- **Cons:** No real-time sync, manual export from external systems, no link preservation
- **Why Rejected:** GitHub/Jira integrations are high-value features. CSV is fallback only.

### Alternative 4: Bidirectional Sync (Full)

- **Description:** Implement full bidirectional sync (TraceRTM ↔ GitHub/Jira)
- **Pros:** Changes in TraceRTM propagate to external systems
- **Cons:** Complex conflict resolution, high maintenance, risk of data loss
- **Why Rejected:** Bidirectional sync is Phase 2 feature. Unidirectional import sufficient for MVP.

## Consequences

### Positive

- **GitHub/Jira integration:** Import issues automatically, reduce manual data entry
- **OpenAPI parsing:** Auto-generate API requirements from specs
- **Markdown export:** Version control requirements in Git
- **JSON export:** Full backup for disaster recovery
- **Webhook support:** Real-time sync for GitHub, Linear

### Negative

- **API rate limits:** GitHub (5000 req/hour), Jira (varies by tier)
- **Maintenance:** APIs change, import scripts break
- **Duplicates:** Must handle duplicate detection (external_id matching)
- **Data loss risk:** Import bugs could overwrite data

### Neutral

- **Polling vs webhooks:** GitHub/Linear use webhooks, Jira uses polling (no webhooks in free tier)
- **Field mapping:** Custom mapping per external system (GitHub labels → TraceRTM tags)
- **Conflict resolution:** Last-write-wins for MVP, CRDT for Phase 2

## Implementation

### Affected Components

- `src/tracertm/services/github_import_service.py` - GitHub import
- `src/tracertm/services/jira_import_service.py` - Jira import
- `src/tracertm/services/import_service.py` - Generic import service
- `src/tracertm/services/export_service.py` - Export service
- `src/tracertm/api/handlers/webhooks.py` - Webhook handlers
- `src/tracertm/mcp/tools/import_export.py` - MCP tools for import/export

### Migration Strategy

**Phase 1: Import Framework (Week 1)**
- Implement generic import service
- Add `external_id` field to items table
- Duplicate detection logic

**Phase 2: GitHub Import (Week 2)**
- GitHub GraphQL client
- Webhook handler
- Field mapping (issues → requirements)

**Phase 3: Jira Import (Week 3)**
- Jira REST client
- Polling scheduler (every 5 min)
- Field mapping (issues → requirements)

**Phase 4: Export (Week 4)**
- Markdown export
- JSON export
- CSV export (basic)

### Rollout Plan

- **Phase 1:** GitHub import (one-time bulk)
- **Phase 2:** GitHub webhooks (real-time sync)
- **Phase 3:** Jira import (polling)
- **Phase 4:** Export features

### Success Criteria

- [ ] Import 1000+ GitHub issues in <5 min
- [ ] Preserve parent-child links (GitHub issue → PR)
- [ ] Detect duplicates (external_id matching)
- [ ] Webhook delivery <1s latency
- [ ] Export to markdown (valid syntax)
- [ ] JSON export (round-trip: export → import → no data loss)

## References

- [GitHub GraphQL API](https://docs.github.com/en/graphql)
- [Jira REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [OpenAPI Specification](https://spec.openapis.org/oas/v3.1.0)
- [ADR-0007: Database Architecture](ADR-0007-database-architecture.md)
- [src/tracertm/services/github_import_service.py](../../src/tracertm/services/github_import_service.py)

---

**Notes:**
- **External ID format:** `{system}:{identifier}` (e.g., `github:owner/repo#123`, `jira:PROJ-456`)
- **Duplicate detection:** Query by `external_id`, update if exists, create if not
- **Webhook security:** Verify GitHub signature (`X-Hub-Signature-256`)
- **Rate limits:** Batch imports in chunks (100 issues/request), respect rate limits
- **OpenAPI parsing:** Use `openapi-spec-validator` for validation, `pydantic` for parsing
