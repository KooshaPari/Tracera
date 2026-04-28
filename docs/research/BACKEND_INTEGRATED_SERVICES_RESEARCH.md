# Backend-Integrated Services Research
## API-Only Architecture Patterns

**Research Date:** 2025-11-20
**Philosophy:** Use external services for API/data only. Build all UIs in-house.

---

## Core Principle

> **External services = Data providers. Our backend = Orchestrator. Our frontend = Single unified UX.**

---

## 1. Headless Architecture Patterns

### Pattern: API-First, UI-Second

```
Traditional (External UIs):
User → Figma App → Figma Data
User → Slack App → Slack Messages
User → Linear App → Linear Tasks

Our Approach (Unified UI):
User → Our Frontend → Our Backend → External APIs (Figma, Slack, Linear)
                                   ↓
                            Our Database (cache/mirror)
```

### Benefits

| Benefit | Description |
|---------|-------------|
| **Unified UX** | Single interface for all interactions |
| **Custom Workflows** | Build exact flows we need |
| **Data Control** | Single source of truth in our DB |
| **Reduced Licenses** | Potentially fewer seats needed |
| **Offline Support** | Our backend caches data locally |

---

## 2. MCP Server Ecosystem Analysis

### Database MCP Servers

| Server | Stars | Language | Use Case |
|--------|-------|----------|----------|
| `supabase-community/supabase-mcp` | 668 | TypeScript | Full Supabase access |
| `stuzero/pg_mcp` | 169 | Python | PostgreSQL operations |
| Official `postgres` | - | TypeScript | Read-only PostgreSQL |
| Official `sqlite` | - | TypeScript | SQLite with BI |

**Composition Strategy:**
```python
# Use Supabase MCP for primary database operations
# Use pg_mcp for advanced PostgreSQL queries
# Compose both in our backend

db_layer = FastMCP("db-layer")
await db_layer.import_server("supabase", "npx @supabase-community/supabase-mcp")
await db_layer.import_server("pg", "npx @stuzero/pg_mcp")
```

### Design Tool MCP Servers

| Server | Stars | Language | Capabilities |
|--------|-------|----------|--------------|
| `sonnylazuardi/cursor-talk-to-figma-mcp` | 4,259 | TypeScript | AI design manipulation |
| `nicholaslee119/figma-mcp` | 1,291 | TypeScript | Read Figma, generate code |
| `mheers/mcp-webdesign` | 33 | TypeScript | Web design generation |

**Pattern: Design Without Designer UI**
```python
# Backend generates design via MCP
@tool()
async def generate_requirement_mockup(req: Requirement):
    """Generate design mockup from requirement, no Figma UI."""
    design = await figma_mcp.call_tool("create_design_from_prompt", {
        "prompt": f"Design for: {req.title}\n\n{req.description}",
        "template": "web-app",
        "components": "material-design-3"
    })

    # Export images for our frontend preview
    images = await figma_mcp.call_tool("export_images", {
        "file_id": design["file_id"],
        "format": "png"
    })

    # Store in our S3
    urls = await upload_to_s3(images, f"designs/{req.id}/")

    # Save metadata in our DB
    await db.designs.insert({
        "requirement_id": req.id,
        "figma_file_id": design["file_id"],
        "preview_urls": urls,
        "generated_at": datetime.utcnow()
    })

    return urls[0]  # Return URL for our frontend
```

### Project Management MCP Servers

| Server | Stars | Capabilities |
|--------|-------|--------------|
| `hmk/linear-mcp-server` | 38 | Linear task CRUD |
| `QuantGeekDev/mcp-server-jira` | 14 | Jira issue management |
| `tuki0918/mcp-server-github-project` | 2 | GitHub Projects V2 |

**Pattern: Sync Data, Skip External PM UI**
```python
# Bi-directional sync without opening Linear/Jira
class PMToolSync:
    async def sync_from_linear(self):
        """Pull Linear tasks into our database."""
        tasks = await linear_mcp.call_tool("list_tasks", {"project_id": project_id})

        for task in tasks:
            await db.requirements.upsert({
                "id": task["id"],
                "title": task["title"],
                "status": self.map_linear_status(task["state"]),
                "external_id": task["id"],
                "external_source": "linear",
                "synced_at": datetime.utcnow()
            })

    async def push_to_linear(self, req_id: str):
        """Create Linear task from our requirement."""
        req = await db.requirements.get(req_id)

        task = await linear_mcp.call_tool("create_task", {
            "title": req.title,
            "description": req.description,
            "labels": [req.priority]
        })

        # Link in our DB
        await db.requirements.update(req_id, {
            "external_id": task["id"],
            "external_source": "linear"
        })
```

### Notification MCP Servers (Webhook-Based, No Apps)

| Server | Type | Benefit |
|--------|------|---------|
| `thadius83/mcp-discord-webhook` | Webhook | No Discord app needed |
| `thadius83/mcp-server-slack-webhook` | Webhook | No Slack app needed |
| `thadius83/mcp-server-ntfy` | Push | Self-hosted notifications |

**Pattern: Backend-Rendered Notifications**
```python
# Our backend generates notification content
@tool()
async def notify_requirement_approved(req_id: str):
    """Send notification without external app UI."""
    req = await db.requirements.get(req_id)

    # Render notification in our backend
    message = f"""
✅ Requirement Approved

{req.title}
ID: {req.id}
Assigned: {req.assignee}
Next: Implementation

View: https://our-app.com/requirements/{req.id}
"""

    # Send via webhook (no Slack app UI)
    await slack_webhook_mcp.call_tool("send", {
        "channel": "#requirements",
        "text": message
    })

    # Also store in our notifications table
    await db.notifications.insert({
        "user_id": req.assignee,
        "type": "requirement_approved",
        "data": {"requirement_id": req.id},
        "read": False
    })

    # Push to our frontend via WebSocket
    await ws.send(req.assignee, {
        "type": "notification",
        "message": message
    })
```

---

## 3. FastMCP Composition Deep Dive

### Official Documentation Summary

**Source:** https://gofastmcp.com/servers/composition

**Key Methods:**
- `import_server(prefix, server)` - Compose servers with namespace
- `MCPProxy(server_command)` - Wrap external MCP server
- `lifespan` events - Startup/shutdown coordination

### Composition Example (Production-Ready)

```python
# main_server.py - Unified trace RTM MCP server
from fastmcp import FastMCP
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(server):
    """Manage server lifecycle."""
    # Startup: initialize all subsystems
    await db.connect()
    await redis.connect()
    await nats.connect()

    # Import external MCP servers
    await server.import_server("figma", "npx @nicholaslee119/figma-mcp")
    await server.import_server("github", "npx @modelcontextprotocol/server-github")
    await server.import_server("linear", "npx @hmk/linear-mcp-server")
    await server.import_server("supabase", "npx @supabase-community/supabase-mcp")
    await server.import_server("slack", "npx @thadius83/mcp-server-slack-webhook")

    yield

    # Shutdown: cleanup
    await db.disconnect()
    await redis.disconnect()
    await nats.disconnect()

main = FastMCP("trace-rtm-unified", lifespan=lifespan)

# Our custom orchestration tools
@main.tool()
async def create_requirement_full_workflow(ctx: Context, **req_data):
    """Complete workflow using composed servers."""
    # Database
    req = await ctx.call_tool("supabase_insert", {"table": "requirements", "data": req_data})

    # Design generation
    design = await ctx.call_tool("figma_create_design", {"spec": req_data})

    # GitHub issue
    issue = await ctx.call_tool("github_create_issue", {
        "repo": req_data["repo"],
        "title": req_data["title"]
    })

    # Linear task
    task = await ctx.call_tool("linear_create_task", {
        "title": req_data["title"],
        "description": f"GitHub: {issue['url']}\nDesign: {design['url']}"
    })

    # Notification
    await ctx.call_tool("slack_send", {
        "text": f"New requirement: {req_data['title']}"
    })

    return {
        "requirement_id": req["id"],
        "figma_url": design["url"],
        "github_issue": issue["number"],
        "linear_task": task["id"]
    }
```

### Tool Namespacing

```python
# With prefixes, tools are namespaced:
# figma_get_file
# figma_create_design
# github_create_issue
# github_create_pr
# linear_create_task
# linear_update_task
# supabase_insert
# supabase_query
# slack_send

# List all composed tools
@main.tool()
async def list_capabilities():
    return main.list_tools()
```

---

## 4. Service Integration Matrix

### External Service Usage Strategy

| Service | Use Their | Build Our | Integration Method |
|---------|-----------|-----------|-------------------|
| **Figma** | API, data, exports | Design viewer, design list UI | MCP composition |
| **GitHub** | API, git data, webhooks | PR viewer, issue tracker UI | Official GitHub MCP |
| **Linear/Jira** | API, task data, webhooks | Task board UI, sprint planning | MCP composition |
| **Supabase** | PostgreSQL, auth API | Admin panels, dashboards | Official Supabase MCP |
| **Slack** | Webhook delivery | In-app notifications, chat | Webhook MCP only |
| **Elasticsearch** | Search API | Search UI, filters | Direct client |
| **S3/MinIO** | Storage API | File browser, uploader | AWS SDK |
| **Temporal** | Workflow engine | Workflow dashboards | Temporal SDK |

### Minimal External UI Usage

**Only use external UIs for:**
1. **Supabase Dashboard** - Occasional database admin, monitoring
2. **Grafana** - Operational dashboards (optional: can build in our UI)
3. **Figma Desktop** - Manual design editing by designers (not developers)

**Everything else:** API-only, our frontend.

---

## 5. Webhook Aggregation Service

### Architecture

```python
# webhooks/aggregator.py - Central webhook receiver
from fastapi import FastAPI, Request
import hmac

app = FastAPI()

@app.post("/webhooks/{service}")
async def universal_webhook(service: str, request: Request):
    """Universal webhook receiver for all external services."""

    # Verify signature (service-specific)
    await verify_webhook_signature(service, request)

    payload = await request.json()

    # Store event (audit trail + replay capability)
    event_id = await db.webhook_events.insert({
        "service": service,
        "payload": payload,
        "received_at": datetime.utcnow(),
        "processed": False
    })

    # Route to appropriate handler
    handler = WEBHOOK_HANDLERS.get(service)
    if handler:
        await handler(payload, event_id)

    # Broadcast to our frontend (WebSocket)
    await ws_manager.broadcast_event(service, payload)

    # Trigger MCP actions if needed
    await trigger_mcp_actions(service, payload)

    return {"status": "received", "event_id": event_id}

async def verify_webhook_signature(service: str, request: Request):
    """Verify webhook is authentic."""
    secrets = {
        "github": os.getenv("GITHUB_WEBHOOK_SECRET"),
        "linear": os.getenv("LINEAR_WEBHOOK_SECRET"),
        "figma": os.getenv("FIGMA_WEBHOOK_SECRET"),
    }

    signature = request.headers.get("X-Hub-Signature-256")  # GitHub format
    body = await request.body()

    expected = hmac.new(
        secrets[service].encode(),
        body,
        'sha256'
    ).hexdigest()

    if not hmac.compare_digest(signature, f"sha256={expected}"):
        raise HTTPException(status_code=401, detail="Invalid signature")

# Service-specific handlers
async def handle_github_webhook(payload: dict, event_id: str):
    """Process GitHub webhook event."""
    event_type = payload.get("action")

    if event_type == "opened" and "pull_request" in payload:
        # PR opened: trigger requirement link detection
        pr = payload["pull_request"]
        req_ids = extract_requirement_ids(pr["body"])

        for req_id in req_ids:
            await db.requirement_links.insert({
                "requirement_id": req_id,
                "github_pr_number": pr["number"],
                "github_pr_url": pr["html_url"]
            })

async def handle_linear_webhook(payload: dict, event_id: str):
    """Process Linear webhook event."""
    if payload["type"] == "Issue" and payload["action"] == "update":
        # Sync Linear task update to our requirements
        linear_id = payload["data"]["id"]
        new_status = payload["data"]["state"]["name"]

        req = await db.requirements.find_one({"external_id": linear_id})
        if req:
            await db.requirements.update(req["id"], {
                "status": map_linear_status(new_status),
                "synced_at": datetime.utcnow()
            })
```

---

## 6. Self-Contained Notification System

### Pattern: No External App UIs

```python
# notifications/service.py - Our notification system
class NotificationService:
    """Backend notification orchestrator."""

    async def notify(
        self,
        user_id: str,
        notification_type: str,
        data: dict,
        channels: list[str] = ["in-app"]
    ):
        """Send notification via multiple channels."""

        # 1. Store in our database (primary notification store)
        notification = await db.notifications.insert({
            "user_id": user_id,
            "type": notification_type,
            "data": data,
            "read": False,
            "created_at": datetime.utcnow()
        })

        # 2. Push to our frontend (WebSocket)
        if "in-app" in channels:
            await ws_manager.send_to_user(user_id, {
                "type": "notification",
                "id": notification["id"],
                "message": self.format_message(notification_type, data)
            })

        # 3. Optional: Send to external channels (API-only, no apps)
        if "slack" in channels:
            await slack_webhook.post(
                SLACK_WEBHOOK_URL,
                json={"text": self.format_message(notification_type, data)}
            )

        if "email" in channels:
            await email_service.send(
                to=user["email"],
                subject=f"Notification: {notification_type}",
                body=self.format_message(notification_type, data)
            )

        # 4. Push notification (self-hosted ntfy.sh)
        if "push" in channels:
            await ntfy_mcp.call_tool("send", {
                "topic": user_id,
                "message": self.format_message(notification_type, data),
                "priority": "default"
            })

        return notification["id"]
```

### User Preference System

```python
# Users configure notification preferences in OUR app
class NotificationPreferences(BaseModel):
    in_app: bool = True
    email: bool = True
    slack: bool = False  # Optional, webhook-based
    push: bool = False   # Self-hosted ntfy.sh

# Check preferences before sending
async def notify_user(user_id: str, notification: Notification):
    prefs = await db.notification_preferences.get(user_id)

    channels = []
    if prefs.in_app:
        channels.append("in-app")
    if prefs.email:
        channels.append("email")
    if prefs.slack:
        channels.append("slack")
    if prefs.push:
        channels.append("push")

    await notification_service.notify(user_id, notification.type, notification.data, channels)
```

---

## 7. Implementation Recommendations

### Phase 1: Core Backend Services
```python
# Build foundational services in our backend
services/
├── design_service.py        # Figma integration (API-only)
├── code_service.py          # GitHub integration (API-only)
├── task_service.py          # Linear/Jira integration (API-only)
├── notification_service.py  # Unified notifications (our system)
└── webhook_service.py       # Event aggregation
```

### Phase 2: MCP Orchestrator
```python
# Compose external MCP servers
from fastmcp import FastMCP

orchestrator = FastMCP("trace-rtm")

# Import all external MCP servers
await orchestrator.import_server("figma", figma_mcp)
await orchestrator.import_server("github", github_mcp)
await orchestrator.import_server("linear", linear_mcp)
await orchestrator.import_server("db", supabase_mcp)

# Add orchestration tools that use multiple servers
@orchestrator.tool()
async def requirement_to_implementation(req_id: str):
    """Complete workflow: requirement → design → code → task."""
    # Use composed tools...
```

### Phase 3: Unified Frontend
```typescript
// Single React/Next.js app with embedded viewers
function UnifiedDashboard() {
  return (
    <Layout>
      <Sidebar>
        {/* Our navigation */}
      </Sidebar>

      <MainContent>
        <RequirementsView />    {/* Our UI */}
        <DesignPreview />       {/* Figma embed */}
        <CodePreview />         {/* Monaco editor */}
        <TaskBoard />           {/* Our UI, Linear data */}
      </MainContent>

      <Notifications>
        {/* Our notification center, data from all sources */}
      </Notifications>
    </Layout>
  )
}
```

---

## Conclusion

**Backend-Integrated Architecture:**
- Compose 10+ external MCP servers in our FastMCP orchestrator
- Build all user-facing UIs in our frontend
- Use external services for API/data only
- Webhook aggregation for event-driven sync
- Self-contained notification system

**Next Steps:**
1. Inventory existing MCP servers in atoms-mcp-prod/zen-mcp-server
2. Build proof-of-concept composition (Figma + GitHub + Supabase)
3. Implement webhook aggregation service
4. Create unified frontend mockups
