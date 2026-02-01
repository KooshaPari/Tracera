# Figma-as-Code & MCP Composition Research

**Research Date:** 2025-11-20
**Focus:** Programmatic Figma generation, MCP tool composition, backend-integrated design workflows

---

## Executive Summary

**Key Finding:** Figma REST API supports **reading** design data extensively but has **limited write capabilities**. Programmatic design creation requires Figma Plugin API. However, the MCP ecosystem provides multiple Figma servers we can compose.

**MCP Ecosystem:**
- **4,259 stars:** `sonnylazuardi/cursor-talk-to-figma-mcp` - AI-powered Figma manipulation via plugin
- **1,291 stars:** `nicholaslee119/figma-mcp` - Figma API access for code generation
- **94 stars:** `nicholasgriffintn/mcp-figma` - MCP server for Figma API
- **33 stars:** `mheers/mcp-webdesign` - Web design with Figma, Lucide, SVG integration

**Recommendation:** Use existing Figma MCP servers via FastMCP composition rather than building from scratch.

---

## 1. Figma REST API Capabilities

### Read Operations (Extensive)

**Available:**
- Get file data, nodes, components, styles
- Export images (PNG, JPG, SVG, PDF)
- Get comments, version history
- Access team libraries, projects

**Endpoints:**
```
GET /v1/files/:file_key
GET /v1/files/:file_key/nodes
GET /v1/files/:file_key/components
GET /v1/images/:file_key
GET /v1/files/:file_key/comments
GET /v1/files/:file_key/versions
```

### Write Operations (Limited)

**Available:**
- Post comments
- Create/update webhooks

**NOT Available via REST API:**
- Create files programmatically
- Create/modify frames
- Add/remove components
- Update designs

**Limitation:** Figma REST API is **read-only** for design content. Writing requires Plugin API.

---

## 2. Figma Plugin API (Programmatic Creation)

### Plugin-Based Design Generation

```typescript
// Figma plugin for programmatic design creation
figma.createPage();
const frame = figma.createFrame();
frame.name = "REQ-123 Design";
frame.resize(1200, 800);

// Create from requirement data
function generateRequirementFrame(req: Requirement) {
  const frame = figma.createFrame();
  frame.name = `REQ-${req.id}`;

  // Add title
  const title = figma.createText();
  title.characters = req.title;
  title.fontSize = 24;
  frame.appendChild(title);

  // Add acceptance criteria as components
  req.acceptanceCriteria.forEach((ac, i) => {
    const component = createChecklistItem(ac);
    component.y = 100 + (i * 50);
    frame.appendChild(component);
  });

  return frame;
}
```

**Pattern: Headless Plugin Execution**
- Run Figma plugin via Puppeteer/Playwright
- Automate browser to execute plugin
- Extract results via plugin API

**Limitation:** Complex setup, requires Figma desktop app or browser automation.

---

## 3. Existing Figma MCP Servers

### High-Value MCP Servers

#### 1. cursor-talk-to-figma-mcp (4,259 stars)
**Repository:** https://github.com/sonnylazuardi/cursor-talk-to-figma-mcp

**Capabilities:**
- AI-powered design manipulation
- Natural language → Figma changes
- Component creation and modification
- Uses Figma Plugin API bridge

**Architecture:**
```
AI Agent → MCP Server → Figma Plugin (via WebSocket) → Figma Desktop
```

**Integration Pattern:**
```python
# Compose into our MCP server
from fastmcp import FastMCP

main = FastMCP("trace-rtm")

# Import Figma MCP server
await main.import_server(
    "figma",
    "npx cursor-talk-to-figma-mcp",
    prefix="figma"
)

# Now available as: figma_create_component, figma_modify_frame, etc.
```

#### 2. nicholaslee119/figma-mcp (1,291 stars)
**Repository:** https://github.com/nicholaslee119/figma-mcp

**Capabilities:**
- Read Figma files for code generation
- Extract component metadata
- Design token extraction
- Screen/frame export

**Usage:**
```python
@tool()
async def extract_requirement_designs(figma_file_id: str):
    """Extract all designs tagged with requirement IDs."""
    file_data = await ctx.call_tool("figma_get_file", {"file_id": figma_file_id})

    # Find frames with [REQ-XXX] naming
    designs = []
    for node in file_data["document"]["children"]:
        if match := re.search(r'\[REQ-(\d+)\]', node["name"]):
            designs.append({
                "requirement_id": match.group(1),
                "figma_node_id": node["id"],
                "design_name": node["name"]
            })

    return designs
```

#### 3. mheers/mcp-webdesign (33 stars)
**Repository:** https://github.com/mheers/mcp-webdesign

**Capabilities:**
- Render web pages from prompts
- Figma integration for design reference
- SVG generation
- HTMX components

**Pattern: Design-to-Code Pipeline**
```
Requirement → AI generates HTML/CSS → Figma MCP imports → Design refinement
```

---

## 4. FastMCP Composition Patterns

### Pattern 1: `import_server` (Server Composition)

**Official Documentation:** https://gofastmcp.com/servers/composition

```python
from fastmcp import FastMCP

# Main orchestrator server
orchestrator = FastMCP("trace-rtm-unified")

# Import multiple specialized servers with prefixes
await orchestrator.import_server("figma", figma_mcp_server)
await orchestrator.import_server("github", github_mcp_server)
await orchestrator.import_server("linear", linear_mcp_server)
await orchestrator.import_server("db", supabase_mcp_server)

# Tools are namespaced:
# - figma_get_file
# - figma_create_component
# - github_create_issue
# - linear_create_task
# - db_query

# Create meta-tools that orchestrate across servers
@orchestrator.tool()
async def create_feature_with_design(
    ctx: Context,
    feature_name: str,
    requirements: list[str]
):
    """Orchestrate: requirement → design → code → task."""

    # 1. Create design in Figma
    design = await ctx.call_tool("figma_create_frame", {
        "name": feature_name,
        "requirements": requirements
    })

    # 2. Create GitHub branch
    branch = await ctx.call_tool("github_create_branch", {
        "name": f"feature/{feature_name.lower().replace(' ', '-')}"
    })

    # 3. Create Linear task
    task = await ctx.call_tool("linear_create_task", {
        "title": feature_name,
        "description": f"Design: {design['url']}\nBranch: {branch['url']}"
    })

    # 4. Store in our database
    await ctx.call_tool("db_insert", {
        "table": "features",
        "data": {
            "name": feature_name,
            "figma_url": design['url'],
            "github_branch": branch['name'],
            "linear_task_id": task['id']
        }
    })

    return {
        "feature_id": task['id'],
        "design_url": design['url'],
        "branch_url": branch['url'],
        "task_url": task['url']
    }
```

### Pattern 2: Server Proxies (Wrap External Servers)

**Official Documentation:** https://gofastmcp.com/servers/proxy

```python
from fastmcp import FastMCP
from fastmcp.server import MCPProxy

# Create proxy to external MCP server
figma_proxy = MCPProxy("npx @figma/mcp-server")

# Use in our server
main = FastMCP("trace")

@main.tool()
async def get_requirement_design(req_id: str):
    """Proxy to Figma MCP server."""
    # Calls external server's tool
    design = await figma_proxy.call_tool("get_design", {"req_id": req_id})

    # Store in our database
    await db.designs.insert({"req_id": req_id, "figma_data": design})

    return design
```

### Pattern 3: Resource Aggregation

```python
@orchestrator.resource("project://{project_id}/overview")
async def project_overview(project_id: str):
    """Aggregate data from multiple MCP servers."""

    # Parallel fetch from all sources
    design, code, tasks, traces = await asyncio.gather(
        ctx.call_tool("figma_get_project_designs", {"project_id": project_id}),
        ctx.call_tool("github_get_repo_stats", {"project_id": project_id}),
        ctx.call_tool("linear_get_project_tasks", {"project_id": project_id}),
        ctx.call_tool("db_query", {"query": f"SELECT * FROM traces WHERE project_id='{project_id}'"})
    )

    return {
        "project_id": project_id,
        "design_coverage": len(design["frames"]),
        "code_stats": code,
        "active_tasks": len([t for t in tasks if t["state"] != "done"]),
        "trace_count": len(traces)
    }
```

---

## 5. Backend-Integrated Design Workflow

### Architecture: No Figma UI Needed

```
Requirements (Our Backend)
         ↓
   Design Generation (AI + Figma Plugin MCP)
         ↓
   Design Storage (Our Database + S3)
         ↓
   Design Preview (Our Frontend - embedded Figma viewer)
         ↓
   Code Generation (AI from design data)
         ↓
   Implementation (Our workflow)
```

### Implementation

```python
# Backend service: requirement → design
class RequirementDesignService:
    def __init__(self, figma_mcp: MCPClient, db: Database):
        self.figma = figma_mcp
        self.db = db

    async def generate_design_from_requirement(self, req_id: str):
        """Generate Figma design from requirement without opening Figma UI."""

        # 1. Get requirement data
        req = await self.db.requirements.get(req_id)

        # 2. Generate design via MCP (uses Figma Plugin API)
        design_spec = self._requirement_to_design_spec(req)
        design = await self.figma.call_tool("generate_design", design_spec)

        # 3. Export as images for preview (no Figma UI needed)
        images = await self.figma.call_tool("export_images", {
            "file_id": design["file_id"],
            "format": "png",
            "scale": 2
        })

        # 4. Store in our database
        await self.db.designs.insert({
            "requirement_id": req_id,
            "figma_file_id": design["file_id"],
            "figma_node_id": design["node_id"],
            "preview_urls": images,
            "created_at": datetime.utcnow()
        })

        # 5. Return data for our frontend
        return {
            "design_id": design["file_id"],
            "preview_url": images[0],  # First exported image
            "edit_url": f"https://figma.com/file/{design['file_id']}"  # Optional: for manual edits
        }

    def _requirement_to_design_spec(self, req: Requirement) -> dict:
        """Convert requirement to design generation prompt."""
        return {
            "prompt": f"""Create a design frame for requirement: {req.title}

Description: {req.description}

Acceptance Criteria:
{chr(10).join(f'- {ac}' for ac in req.acceptance_criteria)}

Style: Material Design 3.0
Components: Use existing component library
Layout: Responsive web (mobile + desktop)""",
            "style": "material-design",
            "template": "web-app"
        }
```

### Frontend Integration (Embedded Figma Viewer)

```typescript
// React component: render Figma design without opening Figma app
import { FigmaEmbed } from '@figma/embed-kit'

function RequirementDesignPreview({ designId }: { designId: string }) {
  return (
    <FigmaEmbed
      fileId={designId}
      nodeId="node-id"
      embedHost="https://our-backend.com"
      allowFullscreen={false}
      // Read-only viewer, no Figma account needed
    />
  )
}
```

---

## 6. MCP Server Composition Examples

### Example 1: Unified Trace MCP Server

```python
# server.py - Compose all integrations
from fastmcp import FastMCP
from fastmcp.client import Client

main = FastMCP("trace-rtm-unified")

# Import external MCP servers
external_servers = {
    "figma": "npx @nicholaslee119/figma-mcp",
    "github": "npx @modelcontextprotocol/server-github",
    "linear": "npx @hmk/linear-mcp-server",
    "supabase": "npx @supabase-community/supabase-mcp",
    "slack": "npx @thadius83/mcp-server-slack-webhook"
}

for prefix, command in external_servers.items():
    await main.import_server(prefix, command)

# Add our custom orchestration tools
@main.tool()
async def create_requirement_with_design(
    ctx: Context,
    title: str,
    description: str,
    project_id: str,
    generate_design: bool = True
):
    """
    Create requirement with optional design generation.
    Orchestrates: DB insert → Figma generation → Linear task → Slack notification
    """
    # 1. Store in our PostgreSQL via Supabase MCP
    req = await ctx.call_tool("supabase_insert", {
        "table": "requirements",
        "data": {
            "title": title,
            "description": description,
            "project_id": project_id,
            "status": "draft"
        }
    })
    req_id = req["id"]

    # 2. Generate design in Figma (optional)
    design_url = None
    if generate_design:
        design = await ctx.call_tool("figma_create_design_from_text", {
            "text": f"{title}\n\n{description}",
            "template": "requirement-spec"
        })
        design_url = design["url"]

        # Link design to requirement
        await ctx.call_tool("supabase_update", {
            "table": "requirements",
            "id": req_id,
            "data": {"figma_design_url": design_url}
        })

    # 3. Create Linear task
    task = await ctx.call_tool("linear_create_task", {
        "title": f"Implement: {title}",
        "description": f"Requirement: {req_id}\nDesign: {design_url or 'TBD'}",
        "project_id": project_id
    })

    # 4. Send Slack notification (webhook, no Slack app)
    await ctx.call_tool("slack_send_webhook", {
        "channel": "#requirements",
        "text": f"✨ New requirement created: {title}",
        "attachments": [{
            "title": title,
            "text": description[:200],
            "fields": [
                {"title": "Requirement ID", "value": req_id},
                {"title": "Linear Task", "value": task["url"]},
                {"title": "Design", "value": design_url or "Not generated"}
            ]
        }]
    })

    return {
        "requirement_id": req_id,
        "design_url": design_url,
        "linear_task_url": task["url"],
        "status": "created"
    }
```

### Example 2: Database MCP Composition

```python
# Compose multiple database MCP servers
db_orchestrator = FastMCP("db-orchestrator")

await db_orchestrator.import_server("pg", "npx @stuzero/pg_mcp")  # PostgreSQL
await db_orchestrator.import_server("supabase", "npx @supabase-community/supabase-mcp")

@db_orchestrator.tool()
async def cross_database_query(ctx: Context, query_type: str):
    """Query across multiple databases."""
    if query_type == "analytics":
        # Use PostgreSQL for complex joins
        return await ctx.call_tool("pg_query", {
            "sql": "SELECT ... FROM requirements JOIN traces ..."
        })
    elif query_type == "realtime":
        # Use Supabase for real-time subscriptions
        return await ctx.call_tool("supabase_subscribe", {
            "table": "requirements",
            "event": "INSERT"
        })
```

### Example 3: Notification Aggregation

```python
# Unified notification MCP (no external apps)
notifications = FastMCP("notifications")

await notifications.import_server("slack", "npx @thadius83/mcp-server-slack-webhook")
await notifications.import_server("discord", "npx @thadius83/mcp-discord-webhook")
await notifications.import_server("ntfy", "npx @thadius83/mcp-server-ntfy")

@notifications.tool()
async def notify_all_channels(ctx: Context, message: str, priority: str = "normal"):
    """Send notification to all configured channels."""
    results = await asyncio.gather(
        ctx.call_tool("slack_send", {"text": message}),
        ctx.call_tool("discord_send", {"content": message}),
        ctx.call_tool("ntfy_send", {"message": message, "priority": priority}),
        return_exceptions=True
    )

    return {
        "sent": sum(1 for r in results if not isinstance(r, Exception)),
        "failed": sum(1 for r in results if isinstance(r, Exception))
    }
```

---

## 7. Backend-Only Integration Philosophy

### Core Principles

1. **External services = API/data only, not UIs**
   - Use Figma API, not Figma desktop app (except for manual design)
   - Use Slack webhooks, not Slack app UI
   - Use GitHub API, not GitHub web UI
   - Use Linear API, not Linear app

2. **All user interactions in OUR frontend**
   - Unified React/Next.js UI for everything
   - Embedded viewers (Figma embed, code previews)
   - In-app notifications (no external app needed)

3. **MCP servers = backend integration layer**
   - Compose existing MCP servers for external APIs
   - Build custom MCP tools for orchestration
   - FastMCP as unified agent interface

4. **Webhooks → our backend → our frontend**
   - External events flow through our backend
   - Store in our database
   - Push to our frontend via WebSocket
   - No reliance on external notification UIs

### Architecture

```
┌─────────────────────────────────────────────────────┐
│              OUR UNIFIED FRONTEND                    │
│  ┌────────────────────────────────────────────────┐ │
│  │ Requirements View │ Design Preview │ Tasks    │ │
│  │ (our UI)         │ (Figma embed)  │ (our UI) │ │
│  └────────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────┘
                     │ WebSocket + REST
┌────────────────────▼────────────────────────────────┐
│           OUR BACKEND (FastMCP Orchestrator)        │
│  ┌─────────────────────────────────────────────┐   │
│  │  Composed MCP Servers                       │   │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐       │   │
│  │  │Figma │ │GitHub│ │Linear│ │Supa  │  ...  │   │
│  │  │ MCP  │ │ MCP  │ │ MCP  │ │ MCP  │       │   │
│  │  └──────┘ └──────┘ └──────┘ └──────┘       │   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────┐   │
│  │  Webhook Receivers (event ingestion)       │   │
│  │  /webhooks/figma  /webhooks/github  ...    │   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────┐   │
│  │  PostgreSQL (single source of truth)        │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────┘
                      │ API calls only (no UIs)
┌─────────────────────▼───────────────────────────────┐
│  External APIs (Figma, GitHub, Linear, Supabase)   │
│  (we use their data, not their UIs)                 │
└─────────────────────────────────────────────────────┘
```

---

## 8. Specific Integration Recommendations

### Figma Integration
- **Use:** Existing MCP servers (cursor-talk-to-figma-mcp for creation)
- **Compose:** Into our FastMCP orchestrator
- **UI:** Embedded Figma viewer in our frontend
- **Storage:** Design metadata in PostgreSQL, images in S3

### GitHub Integration
- **Use:** Official GitHub MCP server
- **Compose:** With our requirement tracking
- **UI:** Build our own PR/issue views
- **Webhook:** Receive events, store in our DB, show in our UI

### Linear/Jira Integration
- **Use:** Existing MCP servers
- **Compose:** Bi-directional sync (their tasks ↔ our requirements)
- **UI:** Show tasks in our unified dashboard
- **Webhook:** Sync updates without opening Linear

### Supabase Integration
- **Use:** Official Supabase MCP server
- **Compose:** As our database layer for MCP tools
- **UI:** Build custom admin panels (skip Supabase dashboard except emergencies)
- **Real-time:** Use Supabase subscriptions for live updates

### Slack/Discord Integration
- **Use:** Webhook-only MCP servers (thadius83/mcp-server-slack-webhook)
- **Compose:** Notification aggregator
- **UI:** Show notifications in our app (optional Slack for team chat)
- **Webhook:** Receive mentions, store in our DB

---

## 9. Implementation Roadmap

### Week 1: MCP Composition Foundation
```bash
# Install existing MCP servers
npm install -g @nicholaslee119/figma-mcp
npm install -g @modelcontextprotocol/server-github
npm install -g @hmk/linear-mcp-server
npm install -g @supabase-community/supabase-mcp

# Create orchestrator
# server.py
from fastmcp import FastMCP
main = FastMCP("trace-rtm")

# Import servers (as shown above)
await main.import_server("figma", ...)
await main.import_server("github", ...)
# etc.
```

### Week 2: Backend Integration Layer
```python
# Build webhook receiver service
# webhooks/service.py
@app.post("/webhooks/figma")
async def figma_webhook(payload: dict):
    # Store event
    await db.events.insert({"source": "figma", "data": payload})

    # Push to frontend via WebSocket
    await ws_manager.broadcast(payload)

    # Trigger MCP actions if needed
    if payload["event_type"] == "FILE_COMMENT":
        await handle_figma_comment(payload)

@app.post("/webhooks/linear")
async def linear_webhook(payload: dict):
    # Similar pattern: store → broadcast → trigger actions
    pass
```

### Week 3: Frontend Integration
```typescript
// Unified dashboard with embedded viewers
function Dashboard() {
  return (
    <div className="grid grid-cols-3">
      <RequirementsPanel />  {/* Our UI */}
      <FigmaDesignPreview /> {/* Embedded Figma */}
      <TasksPanel />         {/* Our UI showing Linear/Jira data */}
    </div>
  )
}

// WebSocket for real-time updates
useEffect(() => {
  const ws = new WebSocket('ws://backend/events')
  ws.onmessage = (msg) => {
    const event = JSON.parse(msg.data)
    // Update our state, no external app needed
    dispatch({ type: 'EXTERNAL_UPDATE', payload: event })
  }
}, [])
```

### Week 4: Testing & Optimization
- Test MCP server composition
- Measure orchestration latency
- Optimize webhook processing
- Load test unified frontend

---

## 10. Advantages of This Approach

### vs. Using External Apps

| Aspect | External Apps | Our Approach |
|--------|---------------|--------------|
| **UX** | Fragmented (Figma app, Slack app, Linear app) | Unified single UI |
| **Context Switching** | High (3-5 apps) | Zero (everything in one place) |
| **Customization** | Limited to app features | Unlimited (our code) |
| **Workflows** | Manual cross-app | Automated orchestration |
| **Data Control** | Siloed in each service | Unified in our DB |
| **Offline** | Depends on each app | Our offline-first design |

### Business Value

- **Developer Velocity:** No context switching = faster workflows
- **Customization:** Build exact workflows we need
- **Integration:** Deep connections impossible in external apps
- **Data Ownership:** Single source of truth in our system
- **Cost:** Potentially lower (fewer licenses if we replace UIs)

---

## 11. Open Questions

1. **Figma Plugin Distribution:** How to distribute our custom Figma plugin for design generation?
   - Option A: Private plugin (team only)
   - Option B: Public plugin (community)
   - Option C: Embedded in MCP server (automated execution)

2. **MCP Server Hosting:** Where to run external MCP servers?
   - Option A: Local (npx on developer machines)
   - Option B: Docker containers (centralized)
   - Option C: Serverless functions (AWS Lambda)

3. **WebSocket Scaling:** How to handle 1000 concurrent agents with real-time updates?
   - Consider: Redis pub/sub for horizontal scaling
   - Consider: NATS JetStream for event persistence

4. **Design Storage:** Store full Figma files or just references?
   - Option A: References only (lightweight)
   - Option B: Periodic snapshots (audit trail)
   - Option C: Full mirror (independence from Figma)

---

## Conclusion

**Figma-as-Code:** Feasible via MCP composition with existing servers (cursor-talk-to-figma-mcp for creation, nicholaslee119/figma-mcp for reading).

**Backend Integration:** Build unified MCP orchestrator composing 10+ external MCP servers. All user interactions in our frontend, external services provide data/APIs only.

**Next Steps:**
1. Test composing 2-3 MCP servers (Figma + GitHub + Supabase)
2. Build proof-of-concept unified orchestrator
3. Implement webhook aggregation service
4. Create unified frontend with embedded viewers

**Key Insight:** FastMCP's composition features enable building a **meta-MCP server** that orchestrates dozens of external services while maintaining a single, unified interface for agents and users.
