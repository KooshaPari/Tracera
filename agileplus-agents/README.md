# agileplus-agents

Agent orchestration and autonomous task execution framework for AgilePlus, enabling AI-driven work automation and decision-making within spec-driven development workflows.

## Overview

agileplus-agents is a Python + Rust framework for building autonomous agents that operate within AgilePlus spec-driven development contexts. Agents can understand specs, decompose work into tasks, execute implementations, validate against requirements, and handle feedback loops. The framework provides prompt templates, tool integrations, memory management, and multi-agent coordination for complex project orchestration.

## Technology Stack

- **Agent Runtime**: Python (FastMCP + LangChain) with Claude API integration
- **Tool Integration**: MCP servers for Rust binaries, external APIs
- **Knowledge Base**: Vector embeddings (FAISS) for spec and FR search
- **Execution**: Async orchestration with Tokio bridges for Rust tool calls
- **Observability**: Structured logging, trace correlation with Tracera
- **Storage**: SQLite for memory, chat history, task state

## Key Features

- **Spec Understanding**: Parse and understand AgilePlus specs with FR traceability
- **Multi-Agent Delegation**: Dispatch specialized subagents (researcher, planner, implementer)
- **Tool Integration**: Call Rust binaries, APIs, and MCP servers from agent context
- **Memory Management**: Persistent memory with vector search for context retrieval
- **Feedback Loops**: Handle spec clarification, requirement validation, and refinement
- **Parallel Execution**: Coordinate multiple agents working on independent tasks
- **Observability**: Full trace logging, token usage tracking, decision audit trail
- **Prompt Engineering**: Curated templates for spec analysis, planning, and code review

## Quick Start

```bash
# Clone the repository
git clone https://github.com/KooshaPari/agileplus-agents.git
cd agileplus-agents

# Review governance
cat CLAUDE.md

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install Rust tools (optional, for tool bindings)
cd rust && cargo build --release && cd ..

# Run tests
pytest tests/ -v

# Launch an agent for a spec
python3 -m agileplus_agents run --spec-id SPEC-001 --agent planner
```

## Project Structure

```
agileplus-agents/
  README.md
  CLAUDE.md
  pyproject.toml                 # Python package config
  Cargo.toml                     # Rust tool bindings
  requirements.txt               # Python dependencies
  src/
    agileplus_agents/
      __init__.py
      agent.py                   # Base agent class
      orchestrator.py            # Multi-agent coordination
      spec_parser.py             # Spec understanding + FR extraction
      memory.py                  # Persistent memory + vector search
      tools/
        mcp_bridge.py            # MCP server integration
        rust_tools.py            # Rust binary tool wrapper
        agilep CLAUDE API.py      # AgilePlus API client
      templates/
        researcher.prompt        # Spec research template
        planner.prompt           # Work decomposition template
        implementer.prompt       # Code generation template
      models/
        __init__.py              # SQLAlchemy ORM for memory
  rust/
    Cargo.toml                   # Rust workspace
    crates/
      agileplus-agent-tools/     # FFI for Python agents
  tests/
    test_spec_parser.py
    test_agent_execution.py
    test_memory.py
    integration/
      test_end_to_end.py
  examples/
    simple_spec_workflow.py      # Basic agent workflow example
    multi_agent_orchestration.py # Parallel agent execution
```

## Related Phenotype Projects

- **[AgilePlus](../AgilePlus/)** — Spec-driven development platform; primary consumer of agents
- **[phenotype-skills](../phenotype-skills/)** — Agent skill registry; agents call skills as tools
- **[PhenoLang](../PhenoLang/)** — Workflow DSL; agents generate PhenoLang code
- **[cheap-llm-mcp](../cheap-llm-mcp/)** — Cost-optimized LLM routing for agent reasoning

## Governance & Contributing

- **CLAUDE.md** — Python + Rust mixed-language conventions
- **Agent Design Guide**: [docs/agent-design/](docs/agent-design/)
- **Prompt Templates**: [src/agileplus_agents/templates/](src/agileplus_agents/templates/)
- **Functional Requirements**: [docs/FUNCTIONAL_REQUIREMENTS.md](docs/FUNCTIONAL_REQUIREMENTS.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

All agent implementations must have corresponding FRs and test coverage. See AGENTS.md for testing requirements.
