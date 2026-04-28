#!/usr/bin/env python3
"""
Integration Example: MCP Tool Decorators + Multi-Agent Orchestration

This example demonstrates how to combine MCP tool decorators (framework-agnostic
tool registration) with multi-agent orchestration to build a sophisticated
multi-agent system with reusable tools.

Use Case:
---------
A research assistant system with multiple specialized agents that:
1. Share a common tool registry using MCP decorators
2. Coordinate work using multi-agent orchestration
3. Execute complex research tasks collaboratively
4. Track performance and quality metrics

Benefits:
---------
- Reusable tools across multiple agents and frameworks
- Type-safe tool registration with validation
- Efficient agent coordination and handoffs
- Comprehensive observability

Author: Pheno SDK Team
License: MIT
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# Multi-agent orchestration
from pheno.mcp.agents.orchestration import (
    Agent,
    AgentCapability,
    MultiAgentOrchestrator,
    OrchestratorConfig,
    Task,
    TaskPriority,
    TaskStatus,
)

# MCP tool decorators
from pheno.mcp.tools.decorators import (
    ToolFramework,
    batch_register_tools,
    convert_to_framework,
    tool,
)

# Metrics
from pheno.observability.metrics.advanced import get_metrics_collector

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# Shared Tool Registry (MCP Tools)
# ============================================================================


class ToolRegistry:
    """
    Centralized tool registry for all agents.
    """

    def __init__(self):
        self.tools = {}
        self.call_count = {}

    def register(self, name: str, func: Any):
        """
        Register a tool.
        """
        self.tools[name] = func
        self.call_count[name] = 0

    def get_tool(self, name: str) -> Optional[Any]:
        """
        Get a registered tool.
        """
        return self.tools.get(name)

    def call(self, name: str, **kwargs) -> Any:
        """
        Call a tool by name.
        """
        tool_func = self.tools.get(name)
        if not tool_func:
            raise ValueError(f"Tool '{name}' not found")

        self.call_count[name] += 1
        return tool_func(**kwargs)


# Global registry
registry = ToolRegistry()


# ============================================================================
# Define Reusable Tools with MCP Decorators
# ============================================================================


@tool(
    name="web_search",
    description="Search the web for information",
    framework=ToolFramework.CUSTOM,
)
async def web_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Search the web for information.

    Args:
        query: Search query
        max_results: Maximum number of results to return

    Returns:
        List of search results with title and URL
    """
    logger.info(f"Searching web: {query}")
    await asyncio.sleep(0.1)  # Simulate API call

    # Mock results
    results = [
        {
            "title": f"Result {i+1} for {query}",
            "url": f"https://example.com/result{i+1}",
            "snippet": f"This is a snippet for result {i+1}...",
        }
        for i in range(min(max_results, 3))
    ]

    registry.register("web_search", web_search)
    return results


@tool(
    name="read_document",
    description="Read and extract content from a document URL",
    framework=ToolFramework.CUSTOM,
)
async def read_document(url: str) -> str:
    """Read a document from a URL.

    Args:
        url: Document URL

    Returns:
        Document content
    """
    logger.info(f"Reading document: {url}")
    await asyncio.sleep(0.1)  # Simulate fetch

    content = f"""
    Document from {url}:

    This is mock content from the document. In a real implementation,
    this would fetch and parse the actual document.

    Key points:
    - Point 1: Important information
    - Point 2: More details
    - Point 3: Additional context
    """

    registry.register("read_document", read_document)
    return content


@tool(
    name="summarize_text",
    description="Summarize a long text into key points",
    framework=ToolFramework.CUSTOM,
)
async def summarize_text(text: str, max_length: int = 200) -> str:
    """Summarize text to key points.

    Args:
        text: Text to summarize
        max_length: Maximum length of summary

    Returns:
        Summarized text
    """
    logger.info(f"Summarizing text ({len(text)} chars)")
    await asyncio.sleep(0.05)  # Simulate processing

    # Mock summary (in reality, use LLM)
    summary = f"Summary: {text[:max_length]}..."

    registry.register("summarize_text", summarize_text)
    return summary


@tool(
    name="extract_entities",
    description="Extract named entities from text",
    framework=ToolFramework.CUSTOM,
)
async def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extract named entities from text.

    Args:
        text: Text to analyze

    Returns:
        Dictionary of entity types and their values
    """
    logger.info(f"Extracting entities from text")
    await asyncio.sleep(0.05)  # Simulate NLP processing

    # Mock entities
    entities = {
        "persons": ["John Doe", "Jane Smith"],
        "organizations": ["Acme Corp", "Tech Inc"],
        "locations": ["New York", "San Francisco"],
        "dates": ["2024-01-15", "next week"],
    }

    registry.register("extract_entities", extract_entities)
    return entities


@tool(
    name="generate_report",
    description="Generate a formatted report from data",
    framework=ToolFramework.CUSTOM,
)
async def generate_report(
    title: str,
    sections: List[Dict[str, str]],
    format: str = "markdown",
) -> str:
    """Generate a formatted report.

    Args:
        title: Report title
        sections: List of sections with 'heading' and 'content'
        format: Output format (markdown, html, text)

    Returns:
        Formatted report
    """
    logger.info(f"Generating report: {title}")
    await asyncio.sleep(0.05)  # Simulate formatting

    if format == "markdown":
        report = f"# {title}\n\n"
        for section in sections:
            report += f"## {section['heading']}\n\n{section['content']}\n\n"
    else:
        report = f"{title}\n\n" + "\n\n".join(f"{s['heading']}\n{s['content']}" for s in sections)

    registry.register("generate_report", generate_report)
    return report


# ============================================================================
# Specialized Agents
# ============================================================================


class ResearchAgent(Agent):
    """
    Agent specialized in research tasks.
    """

    def __init__(self, agent_id: str, registry: ToolRegistry):
        super().__init__(
            agent_id=agent_id,
            capabilities=[
                AgentCapability.RESEARCH,
                AgentCapability.ANALYSIS,
            ],
            max_concurrent_tasks=2,
        )
        self.registry = registry

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute a research task.
        """
        logger.info(f"Agent {self.agent_id} executing task: {task.task_id}")

        # Use web search tool
        query = task.metadata.get("query", "")
        results = await self.registry.call("web_search", query=query, max_results=3)

        # Read top documents
        documents = []
        for result in results[:2]:
            doc = await self.registry.call("read_document", url=result["url"])
            documents.append(doc)

        return {
            "search_results": results,
            "documents": documents,
            "agent": self.agent_id,
        }


class AnalysisAgent(Agent):
    """
    Agent specialized in analysis tasks.
    """

    def __init__(self, agent_id: str, registry: ToolRegistry):
        super().__init__(
            agent_id=agent_id,
            capabilities=[
                AgentCapability.ANALYSIS,
                AgentCapability.REASONING,
            ],
            max_concurrent_tasks=3,
        )
        self.registry = registry

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute an analysis task.
        """
        logger.info(f"Agent {self.agent_id} executing task: {task.task_id}")

        # Get documents from previous task
        documents = task.metadata.get("documents", [])

        # Summarize each document
        summaries = []
        for doc in documents:
            summary = await self.registry.call("summarize_text", text=doc, max_length=150)
            summaries.append(summary)

        # Extract entities
        all_entities = []
        for doc in documents:
            entities = await self.registry.call("extract_entities", text=doc)
            all_entities.append(entities)

        return {
            "summaries": summaries,
            "entities": all_entities,
            "agent": self.agent_id,
        }


class ReportingAgent(Agent):
    """
    Agent specialized in report generation.
    """

    def __init__(self, agent_id: str, registry: ToolRegistry):
        super().__init__(
            agent_id=agent_id,
            capabilities=[
                AgentCapability.SUMMARIZATION,
            ],
            max_concurrent_tasks=1,
        )
        self.registry = registry

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute a reporting task.
        """
        logger.info(f"Agent {self.agent_id} executing task: {task.task_id}")

        # Get analysis results
        summaries = task.metadata.get("summaries", [])
        entities = task.metadata.get("entities", [])

        # Generate report sections
        sections = [
            {
                "heading": "Executive Summary",
                "content": "\n".join(summaries),
            },
            {
                "heading": "Key Entities",
                "content": str(entities),
            },
            {
                "heading": "Conclusion",
                "content": "This research provides comprehensive insights.",
            },
        ]

        # Generate report
        report = await self.registry.call(
            "generate_report",
            title=task.metadata.get("title", "Research Report"),
            sections=sections,
            format="markdown",
        )

        return {
            "report": report,
            "agent": self.agent_id,
        }


# ============================================================================
# Research System with Multi-Agent Orchestration
# ============================================================================


class ResearchSystem:
    """Multi-agent research system.

    This system demonstrates:
    - Tool sharing across agents using MCP decorators
    - Agent coordination with orchestrator
    - Complex multi-step workflows
    - Metrics tracking
    """

    def __init__(self):
        self.registry = registry
        self.metrics = get_metrics_collector()

        # Create agents
        self.research_agent = ResearchAgent("researcher-1", self.registry)
        self.analysis_agent = AnalysisAgent("analyzer-1", self.registry)
        self.reporting_agent = ReportingAgent("reporter-1", self.registry)

        # Create orchestrator
        self.orchestrator = MultiAgentOrchestrator(
            config=OrchestratorConfig(
                max_concurrent_tasks=5,
                task_timeout_seconds=30,
                enable_load_balancing=True,
            ),
            logger=logger,
        )

        # Register agents
        self.orchestrator.register_agent(self.research_agent)
        self.orchestrator.register_agent(self.analysis_agent)
        self.orchestrator.register_agent(self.reporting_agent)

    async def conduct_research(
        self,
        query: str,
        report_title: str = "Research Report",
    ) -> Dict[str, Any]:
        """Conduct research using multi-agent system.

        Args:
            query: Research query
            report_title: Title for final report

        Returns:
            Research results and report
        """
        logger.info(f"Starting research: {query}")

        # Step 1: Create research task
        research_task = Task(
            task_id="research-1",
            description=f"Research: {query}",
            required_capabilities=[AgentCapability.RESEARCH],
            priority=TaskPriority.HIGH,
            metadata={"query": query},
        )

        # Submit and wait for research
        start_time = asyncio.get_event_loop().time()
        research_result = await self.orchestrator.submit_task(research_task)
        research_time = (asyncio.get_event_loop().time() - start_time) * 1000

        # Step 2: Create analysis task
        analysis_task = Task(
            task_id="analysis-1",
            description=f"Analyze research results",
            required_capabilities=[AgentCapability.ANALYSIS],
            priority=TaskPriority.MEDIUM,
            metadata={
                "documents": research_result.get("documents", []),
                "search_results": research_result.get("search_results", []),
            },
            depends_on=["research-1"],
        )

        # Submit and wait for analysis
        start_time = asyncio.get_event_loop().time()
        analysis_result = await self.orchestrator.submit_task(analysis_task)
        analysis_time = (asyncio.get_event_loop().time() - start_time) * 1000

        # Step 3: Create reporting task
        reporting_task = Task(
            task_id="reporting-1",
            description=f"Generate research report",
            required_capabilities=[AgentCapability.SUMMARIZATION],
            priority=TaskPriority.LOW,
            metadata={
                "title": report_title,
                "summaries": analysis_result.get("summaries", []),
                "entities": analysis_result.get("entities", []),
            },
            depends_on=["analysis-1"],
        )

        # Submit and wait for report
        start_time = asyncio.get_event_loop().time()
        reporting_result = await self.orchestrator.submit_task(reporting_task)
        reporting_time = (asyncio.get_event_loop().time() - start_time) * 1000

        # Record metrics
        total_time = research_time + analysis_time + reporting_time
        self.metrics.record_performance(latency_ms=total_time, success=True)

        # Get orchestrator stats
        stats = self.orchestrator.get_statistics()

        return {
            "research": research_result,
            "analysis": analysis_result,
            "report": reporting_result.get("report", ""),
            "timing": {
                "research_ms": research_time,
                "analysis_ms": analysis_time,
                "reporting_ms": reporting_time,
                "total_ms": total_time,
            },
            "orchestrator_stats": stats,
            "tool_usage": self.registry.call_count,
        }


# ============================================================================
# Example Usage
# ============================================================================


async def main():
    """
    Run the integration example.
    """

    # Create research system
    system = ResearchSystem()

    # Example 1: Simple research query
    print("\n" + "=" * 80)
    print("Example 1: Multi-Agent Research")
    print("=" * 80)

    result = await system.conduct_research(
        query="What is quantum computing and its applications?",
        report_title="Quantum Computing Research Report",
    )

    print(f"\nResearch completed in {result['timing']['total_ms']:.2f}ms")
    print(f"\nTiming Breakdown:")
    print(f"  Research: {result['timing']['research_ms']:.2f}ms")
    print(f"  Analysis: {result['timing']['analysis_ms']:.2f}ms")
    print(f"  Reporting: {result['timing']['reporting_ms']:.2f}ms")

    print(f"\nTool Usage:")
    for tool_name, count in result["tool_usage"].items():
        print(f"  {tool_name}: {count} calls")

    print(f"\nOrchestrator Statistics:")
    stats = result["orchestrator_stats"]
    print(f"  Total tasks: {stats.get('total_tasks', 0)}")
    print(f"  Completed tasks: {stats.get('completed_tasks', 0)}")
    print(f"  Failed tasks: {stats.get('failed_tasks', 0)}")
    print(f"  Average task time: {stats.get('avg_task_time_ms', 0):.2f}ms")

    print(f"\nGenerated Report (first 500 chars):")
    print(result["report"][:500])
    print("...")

    print("\n" + "=" * 80)
    print("Integration example complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
