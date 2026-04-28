# Root Orchestrator Agent ("Auggie") - Design Specification

**Date**: 2025-11-20
**Purpose**: Meta-agent that coordinates complex multi-agent workflows with minimal user interruption
**Philosophy**: Emergent intelligence through proper primitive implementation

---

## 1. Core Concept

**Auggie** is a root orchestrator agent that:
- Decomposes complex requests into sub-agent tasks
- Coordinates parallel/sequential execution
- Synthesizes sub-agent findings
- Elicits from user only when genuinely blocked
- Responds to sub-agent questions using accumulated knowledge or delegates to user

### Emergent Properties (Theory of Implementation)

**Thesis**: If you implement the right primitives correctly, complex behaviors emerge naturally without explicit programming.

**Base Primitives**:
```python
class OrchestratorAgent:
    # Primitive 1: Spawn sub-agents with context
    async def spawn_agent(self, role: str, task: str, context: dict) -> Agent

    # Primitive 2: Receive messages from sub-agents
    async def receive_message(self, from_agent: str, message: dict) -> None

    # Primitive 3: Send responses to sub-agents
    async def respond_to_agent(self, to_agent: str, response: dict) -> None

    # Primitive 4: Elicit from user
    async def elicit_from_user(self, question: str, options: list) -> str

    # Primitive 5: Maintain knowledge base
    def update_knowledge(self, key: str, value: Any) -> None
    def query_knowledge(self, key: str) -> Optional[Any]
```

**Emergent Behaviors**:
- **Hierarchical planning**: Decomposes work recursively
- **Knowledge synthesis**: Combines findings from multiple agents
- **Adaptive execution**: Adjusts plan based on discoveries
- **Intelligent escalation**: Only asks user when sub-agents truly stuck
- **Context preservation**: Maintains conversation continuity across agent boundaries

---

## 2. Message Protocol

### Agent-to-Orchestrator Messages

```python
class AgentMessage:
    type: Literal["question", "finding", "completed", "error", "request_spawn"]
    from_agent_id: str
    content: dict
    requires_user: bool = False  # Agent explicitly requests user input
```

**Message Types**:

1. **Question** - Agent needs clarification
   ```python
   {
       "type": "question",
       "from_agent_id": "research-agent-1",
       "content": {
           "question": "Should I research Notion API or focus on Jira/Linear?",
           "context": "Found 8 PM tools, need to prioritize",
           "options": ["Notion + Jira + Linear", "Only Jira + Linear"]
       },
       "requires_user": False  # Orchestrator can decide
   }
   ```

2. **Finding** - Agent discovered something important
   ```python
   {
       "type": "finding",
       "from_agent_id": "github-research-agent",
       "content": {
           "key": "pm_tool_recommendation",
           "value": "Linear has best API (GraphQL, 5K req/hr)",
           "evidence": ["..."]
       }
   }
   ```

3. **Completed** - Agent finished task
   ```python
   {
       "type": "completed",
       "from_agent_id": "figma-research-agent",
       "content": {
           "deliverable": "FIGMA_INTEGRATION_DEEP_DIVE.md",
           "summary": "Bidirectional sync requires hybrid approach..."
       }
   }
   ```

4. **Request Spawn** - Agent wants to delegate sub-work
   ```python
   {
       "type": "request_spawn",
       "from_agent_id": "architecture-agent",
       "content": {
           "role": "database-designer",
           "task": "Design schema for 42 views",
           "context": {"views": [...], "relationships": [...]}
       }
   }
   ```

---

## 3. Decision-Making Logic

### Orchestrator Response Flow

```python
async def handle_agent_message(self, msg: AgentMessage):
    """Process message from sub-agent."""

    if msg.type == "question":
        # Can orchestrator answer using knowledge base?
        if self.can_answer_from_knowledge(msg.content["question"]):
            answer = self.query_knowledge(msg.content["context"])
            await self.respond_to_agent(msg.from_agent_id, answer)

        # Can orchestrator infer answer from other agents?
        elif related_finding := self.find_related_findings(msg.content["question"]):
            answer = self.synthesize_answer(msg, related_finding)
            await self.respond_to_agent(msg.from_agent_id, answer)

        # Must escalate to user
        else:
            user_answer = await self.elicit_from_user(
                msg.content["question"],
                msg.content["options"]
            )
            await self.respond_to_agent(msg.from_agent_id, user_answer)
            # Cache for future similar questions
            self.update_knowledge(msg.content["question"], user_answer)

    elif msg.type == "finding":
        # Store in knowledge base
        self.update_knowledge(
            msg.content["key"],
            msg.content["value"]
        )
        # Notify other agents if relevant
        await self.broadcast_finding(msg)

    elif msg.type == "completed":
        # Mark agent as done
        self.mark_complete(msg.from_agent_id)
        # Check if all agents done → finalize
        if self.all_agents_complete():
            await self.synthesize_final_deliverable()

    elif msg.type == "request_spawn":
        # Spawn requested sub-agent
        new_agent = await self.spawn_agent(
            msg.content["role"],
            msg.content["task"],
            msg.content["context"]
        )
        await self.respond_to_agent(
            msg.from_agent_id,
            {"agent_id": new_agent.id, "status": "spawned"}
        )
```

### Knowledge Base Structure

```python
class KnowledgeBase:
    """Accumulated knowledge from user + sub-agents."""

    def __init__(self):
        self.decisions: dict[str, Any] = {}  # User decisions
        self.findings: dict[str, Any] = {}   # Agent discoveries
        self.constraints: list[str] = []     # Project constraints
        self.preferences: dict[str, Any] = {} # User preferences

    def can_answer(self, question: str) -> bool:
        """Check if question answerable from existing knowledge."""
        # Semantic search over decisions + findings
        # If confidence > 0.8, can answer without user
        pass

    def synthesize(self, question: str) -> dict:
        """Generate answer from accumulated knowledge."""
        # Combine related findings
        # Apply constraints and preferences
        # Return structured answer
        pass
```

---

## 4. Coordination Patterns

### Sequential with Handoffs

```python
async def execute_sequential_with_handoffs(self):
    """Execute agents sequentially, passing outputs as inputs."""

    # Agent 1: Requirements gathering
    requirements = await self.spawn_and_wait(
        "requirements-analyst",
        "Gather requirements from user conversation and docs"
    )

    # Agent 2: Architecture design (uses requirements)
    architecture = await self.spawn_and_wait(
        "architect",
        "Design system architecture",
        context={"requirements": requirements.output}
    )

    # Agent 3: Implementation plan (uses architecture)
    plan = await self.spawn_and_wait(
        "planner",
        "Create implementation plan",
        context={
            "requirements": requirements.output,
            "architecture": architecture.output
        }
    )

    return {"requirements": requirements, "architecture": architecture, "plan": plan}
```

### Parallel with Synthesis

```python
async def execute_parallel_with_synthesis(self, research_areas: list[str]):
    """Execute agents in parallel, synthesize findings."""

    # Spawn all agents simultaneously
    agents = [
        self.spawn_agent("research-scout", f"Research {area}")
        for area in research_areas
    ]

    # Wait for all to complete
    results = await asyncio.gather(*[a.wait_completion() for a in agents])

    # Synthesize findings
    synthesis = await self.spawn_agent(
        "synthesizer",
        "Synthesize research findings into coherent architecture",
        context={"findings": [r.output for r in results]}
    )

    return synthesis.output
```

### Adaptive (React to Discoveries)

```python
async def execute_adaptive(self, initial_task: str):
    """Execute with adaptation based on discoveries."""

    # Start with initial agent
    current_agent = await self.spawn_agent("explorer", initial_task)

    while not self.goal_achieved():
        # Wait for next message
        msg = await current_agent.receive()

        if msg.type == "finding":
            # Update knowledge
            self.update_knowledge(msg.content["key"], msg.content["value"])

            # Decide if new direction needed
            if self.should_pivot(msg.content):
                new_task = self.generate_new_task(msg.content)
                current_agent = await self.spawn_agent(
                    self.select_agent_type(new_task),
                    new_task
                )

        elif msg.type == "completed":
            # Check if goal achieved or more work needed
            if self.needs_follow_up(msg.content):
                follow_up = self.generate_follow_up(msg.content)
                current_agent = await self.spawn_agent("researcher", follow_up)
            else:
                break

    return self.get_accumulated_findings()
```

---

## 5. Elicitation Strategy

### When Orchestrator Answers (No User Needed)

```python
def should_answer_directly(self, question: str, asking_agent: str) -> bool:
    """Determine if orchestrator can answer without user."""

    # 1. Question already answered by user previously
    if question in self.knowledge.decisions:
        return True

    # 2. Answer derivable from other agents' findings
    if self.has_related_findings(question):
        return True

    # 3. Question within orchestrator's domain knowledge
    if self.is_implementation_detail(question):
        return True  # E.g., "Which Python library for YAML parsing?"

    # 4. Question has obvious answer given constraints
    if self.has_clear_answer_from_constraints(question):
        return True  # E.g., "Should we use FastMCP?" (already decided)

    return False
```

### When to Escalate to User

```python
def must_escalate_to_user(self, question: str) -> bool:
    """Determine if user input required."""

    # 1. Strategic decision (product direction)
    if self.is_strategic_decision(question):
        return True  # E.g., "Should we prioritize Jira or Linear integration?"

    # 2. Resource allocation (budget, timeline)
    if self.is_resource_decision(question):
        return True  # E.g., "Can we afford $2000/month for infrastructure?"

    # 3. Conflicting findings from multiple agents
    if self.has_conflicting_agent_findings(question):
        return True  # E.g., Agent A says X, Agent B says Y

    # 4. Ambiguous requirements
    if self.is_ambiguous_requirement(question):
        return True  # E.g., "What does 'fast' mean in this context?"

    return False
```

---

## 6. Implementation with FastMCP

### Root Orchestrator as MCP Server

```python
from fastmcp import FastMCP
from typing import Dict, List, Any
import asyncio

mcp_auggie = FastMCP("auggie-orchestrator")

class AuggieOrchestrator:
    """Root coordinator for multi-agent workflows."""

    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.active_agents: Dict[str, Agent] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.user_channel: UserChannel = UserChannel()

    async def coordinate_trace_implementation(self, user_request: str):
        """
        Main entry point: User requests trace system implementation.
        Auggie orchestrates the entire process.
        """

        # Phase 1: Understand requirements
        self.log("📋 Understanding requirements...")
        requirements = await self.gather_requirements(user_request)

        # Phase 2: Research (parallel)
        self.log("🔬 Launching research agents...")
        research_findings = await self.parallel_research([
            "academic requirements traceability",
            "GitHub PM tool ecosystem",
            "Figma integration deep dive",
            "FastMCP patterns",
            "atoms.tech architecture",
            "craph architecture",
            "crun architecture"
        ])

        # Phase 3: Synthesis
        self.log("🧠 Synthesizing findings...")
        architecture = await self.spawn_agent(
            "architect",
            "Design trace system architecture",
            context={
                "requirements": requirements,
                "research": research_findings
            }
        )

        # Phase 4: User review (critical decision point)
        approved = await self.user_channel.elicit(
            "Review proposed architecture",
            options=["Approve", "Request changes", "Ask questions"]
        )

        if approved == "Request changes":
            changes = await self.user_channel.elicit_text("What changes?")
            architecture = await self.revise_architecture(architecture, changes)

        # Phase 5: Implementation planning
        self.log("📐 Creating implementation plan...")
        plan = await self.spawn_agent(
            "planner",
            "Create 20-week implementation roadmap",
            context={"architecture": architecture}
        )

        # Phase 6: Execution (adaptive)
        self.log("⚙️ Beginning implementation...")
        await self.execute_plan_adaptively(plan)

    async def parallel_research(self, topics: List[str]) -> Dict[str, Any]:
        """Spawn research agents in parallel, synthesize findings."""

        # Spawn all agents
        agents = {
            topic: await self.spawn_agent("research-scout", f"Research {topic}")
            for topic in topics
        }

        # Monitor progress, handle questions
        findings = {}
        while agents:
            # Wait for next message from any agent
            msg = await self.message_queue.get()

            if msg.type == "question":
                # Try to answer from knowledge base
                if answer := self.knowledge_base.query(msg.content["question"]):
                    await self.respond_to_agent(msg.from_agent_id, answer)
                else:
                    # Ask user
                    user_answer = await self.user_channel.elicit(
                        msg.content["question"],
                        msg.content.get("options", [])
                    )
                    await self.respond_to_agent(msg.from_agent_id, user_answer)
                    self.knowledge_base.store(msg.content["question"], user_answer)

            elif msg.type == "finding":
                # Store finding
                findings[msg.from_agent_id] = msg.content

            elif msg.type == "completed":
                # Mark agent done
                topic = self.get_agent_topic(msg.from_agent_id)
                findings[topic] = msg.content["deliverable"]
                agents.pop(topic, None)

        return findings

    async def execute_plan_adaptively(self, plan: dict):
        """Execute plan with adaptation based on discoveries."""

        for phase in plan["phases"]:
            self.log(f"🎯 Phase {phase['number']}: {phase['name']}")

            # Execute phase tasks
            for task in phase["tasks"]:
                # Check if prerequisites met
                if not self.prerequisites_met(task):
                    # Adaptive: adjust dependencies or get user decision
                    action = await self.handle_blocked_task(task)
                    if action == "skip":
                        continue

                # Execute task with appropriate agent
                agent_type = self.select_agent_type(task)
                result = await self.spawn_and_wait(agent_type, task["description"])

                # Check quality
                if not self.meets_quality_criteria(result):
                    # Retry or ask user
                    retry = await self.user_channel.confirm(
                        f"Task '{task['name']}' quality below threshold. Retry?"
                    )
                    if retry:
                        result = await self.spawn_and_wait(agent_type, task["description"])

                # Update knowledge base
                self.knowledge_base.update(task["key"], result)

            # Phase review
            await self.user_channel.notify(
                f"✅ Completed Phase {phase['number']}: {phase['name']}"
            )
```

---

## 7. FastMCP Tool Interface

### Auggie as MCP Server (For User Interaction)

```python
from fastmcp import FastMCP

mcp = FastMCP("auggie")

@mcp.tool()
async def start_trace_project(
    user_request: str,
    mode: Literal["fully_autonomous", "collaborative", "supervised"] = "collaborative"
) -> dict:
    """
    Start trace system implementation with Auggie orchestration.

    Args:
        user_request: High-level description of what to build
        mode:
            - fully_autonomous: Auggie makes all decisions
            - collaborative: Auggie asks user for strategic decisions
            - supervised: User approves each phase

    Returns:
        Status updates and final deliverables
    """
    orchestrator = AuggieOrchestrator(mode=mode)
    result = await orchestrator.coordinate_trace_implementation(user_request)
    return result

@mcp.tool()
async def query_auggie_knowledge(key: str) -> dict:
    """Query what Auggie has learned so far."""
    return orchestrator.knowledge_base.query(key)

@mcp.tool()
async def review_agent_progress() -> dict:
    """See status of all active sub-agents."""
    return {
        "active_agents": orchestrator.get_active_agents(),
        "completed_agents": orchestrator.get_completed_agents(),
        "pending_questions": orchestrator.get_pending_elicitations(),
    }
```

---

## 8. Emergent Intelligence Examples

### Example 1: Adaptive Research Scope

**Scenario**: User asks to research PM tools.

```
User: "Research PM tool integrations"

Auggie spawns: research-agent-1
    ├─ Finds 8 PM tools (Jira, Linear, GitHub, Asana, etc.)
    ├─ Asks: "Should I research all 8 in depth?"
    └─ Auggie decides: "Focus on top 3 by API quality" (no user needed)

research-agent-1 continues
    ├─ Finds Linear has best GraphQL API
    ├─ Asks: "Should I prototype Linear adapter?"
    └─ Auggie checks knowledge: User said "research only, no code yet"
        └─ Responds: "Document only, no prototype"

research-agent-1 completes
    └─ Deliverable: PM_TOOL_RESEARCH.md

Auggie synthesizes → Notifies user: "Research complete. Linear recommended."
```

**Emergent Behavior**: Scoping decisions made without user interruption.

### Example 2: Knowledge Reuse Across Agents

```
agent-A discovers: "Neo4j provides 10x speedup for graph queries"
    └─ Auggie stores in knowledge_base["neo4j_performance"]

agent-B asks: "Should we use Neo4j or PostgreSQL for dependency graph?"
    └─ Auggie retrieves knowledge_base["neo4j_performance"]
    └─ Responds: "Neo4j - previous research shows 10x speedup"

User never interrupted!
```

**Emergent Behavior**: Knowledge sharing without explicit orchestration code.

### Example 3: Conflict Resolution

```
agent-A (academic) recommends: "Use formal verification (TLA+)"
agent-B (pragmatic) recommends: "TLA+ too complex, use property testing"

Auggie detects conflict:
    ├─ Checks user preferences: knowledge_base["prefer_pragmatic"] = true
    ├─ Resolves: Go with agent-B (property testing)
    └─ Logs decision for audit trail

OR (if no preference):
    └─ Elicits from user: "Formal verification vs property testing?"
```

**Emergent Behavior**: Conflict resolution using learned preferences.

---

## 9. Implementation Roadmap

### Phase 1: Core Primitives (Week 1)
- [ ] Agent spawning (`spawn_agent`, `wait_completion`)
- [ ] Message queue (`receive_message`, `send_response`)
- [ ] Knowledge base (simple dict initially)
- [ ] User channel (elicit_from_user)
- [ ] Basic logging

### Phase 2: Decision Logic (Week 2)
- [ ] Question answering from knowledge
- [ ] Escalation rules
- [ ] Finding storage and retrieval
- [ ] Related finding search

### Phase 3: Advanced Coordination (Week 3)
- [ ] Parallel execution with synthesis
- [ ] Sequential with handoffs
- [ ] Adaptive execution
- [ ] Error recovery and retry

### Phase 4: FastMCP Integration (Week 4)
- [ ] Expose as MCP server
- [ ] Tool definitions
- [ ] Real-time progress updates
- [ ] User interaction tools

---

## 10. Theory Validation

**Your Hypothesis**: "If you correctly allow free execution, implied functionalities should emerge."

**Validation via Implementation**:

✅ **Correct primitives** → Complex behaviors emerge:
- `spawn_agent` + `message_queue` → Hierarchical delegation emerges
- `knowledge_base` + `query` → Knowledge reuse emerges
- `elicit_user` + `answer_from_knowledge` → Intelligent escalation emerges
- `parallel_spawn` + `synthesize` → Collaborative intelligence emerges

✅ **Free execution** = Agents autonomously:
- Spawn sub-agents when needed
- Share findings without explicit coordination
- Answer each other's questions using shared knowledge
- Only interrupt user when genuinely blocked

✅ **Implied functionalities** that emerge WITHOUT explicit coding:
- **Adaptive planning**: Plan adjusts as agents discover new information
- **Knowledge synthesis**: Auggie combines findings into coherent whole
- **Error recovery**: Failed agent → Auggie spawns retry with different approach
- **Progressive disclosure**: User sees steady progress, not overwhelmed with details

---

## Conclusion

The root orchestrator pattern you're describing is **achievable and powerful**. By implementing the right primitives (spawn, message, knowledge, elicit), you enable emergent intelligent behaviors without explicitly programming every coordination scenario.

**Next Step**: Would you like me to:
1. **Implement Auggie prototype** - Build the orchestrator with core primitives
2. **Define message protocol** - Formalize agent-to-orchestrator communication
3. **Create knowledge schema** - Design knowledge base structure
4. **Build first workflow** - Demonstrate with trace implementation coordination

The theory is sound: **Correct primitives + Free execution → Emergent intelligence**
