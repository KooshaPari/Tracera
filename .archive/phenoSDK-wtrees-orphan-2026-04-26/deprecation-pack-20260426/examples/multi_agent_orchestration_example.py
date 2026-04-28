"""Multi-Agent Orchestration Examples.

This module demonstrates practical usage of pheno-sdk's multi-agent orchestration
framework with different workflow patterns and frameworks.

Examples:
1. Sequential Workflow - Research and Writing Pipeline
2. Parallel Workflow - Multi-Source Data Collection
3. Hierarchical Workflow - Project Management
4. Conditional Workflow - Adaptive Content Processing

Run individual examples:
    python examples/multi_agent_orchestration_example.py --example sequential
    python examples/multi_agent_orchestration_example.py --example parallel
    python examples/multi_agent_orchestration_example.py --example hierarchical
    python examples/multi_agent_orchestration_example.py --example conditional
    python examples/multi_agent_orchestration_example.py --example all
"""

import asyncio
import logging
from typing import Any

from pheno.mcp.agents.orchestration import (
    AgentPoolConfig,
    DependencyConfig,
    FrameworkConfig,
    Orchestrator,
    WorkflowConfig,
    WorkflowPattern,
)
from pheno.mcp.ports import TaskConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def sequential_workflow_example():
    """
    Example 1: Sequential Workflow - Research and Writing Pipeline.

    Demonstrates a simple sequential workflow where a researcher gathers
    information and a writer creates content based on the research.
    """
    logger.info("=== Sequential Workflow Example ===")

    # Create orchestrator with CrewAI
    orchestrator = Orchestrator(
        framework="crewai",
        framework_config=FrameworkConfig(framework="crewai", verbose=True, max_iterations=5),
        pool_config=AgentPoolConfig(max_agents=5, max_concurrent_tasks=2),
    )

    try:
        # Create agents
        logger.info("Creating agents...")

        researcher_id = await orchestrator.create_agent(
            name="senior_researcher",
            role="Senior Research Analyst",
            goal="Discover and analyze the latest AI trends",
            backstory="You're a senior research analyst with 10 years of experience "
            "in artificial intelligence and machine learning.",
        )

        writer_id = await orchestrator.create_agent(
            name="tech_writer",
            role="Technical Content Writer",
            goal="Create engaging and informative technical content",
            backstory="You're a skilled technical writer who excels at making "
            "complex topics accessible to a broad audience.",
        )

        # Define tasks
        logger.info("Defining workflow tasks...")

        tasks = [
            TaskConfig(
                description="Research the latest developments in multi-agent AI systems. "
                "Focus on practical applications and emerging frameworks.",
                agent="senior_researcher",
                expected_output="Comprehensive research summary with key findings",
            ),
            TaskConfig(
                description="Based on the research, write a 500-word blog post about "
                "multi-agent AI systems. Make it engaging and accessible.",
                agent="tech_writer",
                expected_output="Well-structured blog post ready for publication",
                dependencies=[],  # Will be set automatically in sequential mode
            ),
        ]

        # Create workflow
        workflow_id = orchestrator.create_workflow(pattern=WorkflowPattern.SEQUENTIAL, tasks=tasks)

        logger.info(f"Workflow created: {workflow_id}")

        # Execute workflow
        logger.info("Executing workflow...")
        result = await orchestrator.execute_workflow(workflow_id)

        # Display results
        logger.info(f"\n{'='*60}")
        logger.info("Workflow Results:")
        logger.info(f"Status: {result.status}")
        logger.info(f"Duration: {result.total_duration_ms:.2f}ms")
        logger.info(
            f"Completed Tasks: {len([r for r in result.task_results.values() if r.success])}"
        )

        for task_id, task_result in result.task_results.items():
            logger.info(f"\nTask {task_id}:")
            logger.info(f"  Status: {task_result.status}")
            logger.info(
                f"  Duration: {task_result.duration_ms:.2f}ms"
                if task_result.duration_ms
                else "  Duration: N/A"
            )
            if task_result.output:
                logger.info(f"  Output Preview: {str(task_result.output)[:200]}...")

        # Get pool statistics
        stats = await orchestrator.get_pool_stats()
        logger.info(f"\nAgent Pool Stats:")
        logger.info(f"  Total Agents: {stats['total_agents']}")
        logger.info(f"  Completed Tasks: {stats['total_tasks_completed']}")

        logger.info(f"{'='*60}\n")

        return result

    finally:
        await orchestrator.shutdown()


async def parallel_workflow_example():
    """
    Example 2: Parallel Workflow - Multi-Source Data Collection.

    Demonstrates parallel execution where multiple agents collect data
    from different sources simultaneously, then a consolidator merges results.
    """
    logger.info("=== Parallel Workflow Example ===")

    orchestrator = Orchestrator(
        framework="crewai",
        pool_config=AgentPoolConfig(
            max_agents=10, max_concurrent_tasks=5  # Allow parallel execution
        ),
    )

    try:
        # Create specialized data collectors
        logger.info("Creating data collector agents...")

        news_collector = await orchestrator.create_agent(
            name="news_collector",
            role="News Data Collector",
            goal="Gather recent news articles about AI",
            backstory="Expert at finding relevant news sources",
        )

        academic_collector = await orchestrator.create_agent(
            name="academic_collector",
            role="Academic Paper Collector",
            goal="Find relevant academic papers on AI",
            backstory="Experienced at navigating academic databases",
        )

        social_collector = await orchestrator.create_agent(
            name="social_collector",
            role="Social Media Analyst",
            goal="Analyze AI discussions on social media",
            backstory="Expert at social media trend analysis",
        )

        consolidator = await orchestrator.create_agent(
            name="data_consolidator",
            role="Data Integration Specialist",
            goal="Merge and synthesize data from multiple sources",
            backstory="Skilled at data integration and analysis",
        )

        # Define tasks with dependencies
        logger.info("Defining parallel tasks...")

        tasks = [
            TaskConfig(
                description="Collect latest AI news from major tech publications",
                agent="news_collector",
                expected_output="List of relevant news articles",
                metadata={"task_id": "news_collection"},
            ),
            TaskConfig(
                description="Find recent academic papers on multi-agent systems",
                agent="academic_collector",
                expected_output="List of academic papers with summaries",
                metadata={"task_id": "academic_collection"},
            ),
            TaskConfig(
                description="Analyze AI discussions and sentiment on social media",
                agent="social_collector",
                expected_output="Social media trend analysis",
                metadata={"task_id": "social_collection"},
            ),
            TaskConfig(
                description="Consolidate all collected data into a comprehensive report",
                agent="data_consolidator",
                expected_output="Integrated analysis report",
                metadata={"task_id": "consolidation"},
            ),
        ]

        # Define dependencies - consolidator depends on all collectors
        dependencies = [
            DependencyConfig(
                task_id="consolidation",
                depends_on=["news_collection", "academic_collection", "social_collection"],
            )
        ]

        # Create parallel workflow
        workflow_id = orchestrator.create_workflow(
            pattern=WorkflowPattern.PARALLEL, tasks=tasks, dependencies=dependencies
        )

        logger.info("Executing parallel workflow...")
        result = await orchestrator.execute_workflow(workflow_id)

        # Display results
        logger.info(f"\n{'='*60}")
        logger.info("Parallel Workflow Results:")
        logger.info(f"Status: {result.status}")
        logger.info(f"Total Duration: {result.total_duration_ms:.2f}ms")
        logger.info(
            f"Success Rate: {sum(1 for r in result.task_results.values() if r.success)}/{len(result.task_results)}"
        )

        logger.info(f"{'='*60}\n")

        return result

    finally:
        await orchestrator.shutdown()


async def hierarchical_workflow_example():
    """
    Example 3: Hierarchical Workflow - Project Management.

    Demonstrates hierarchical execution where a project manager delegates
    tasks to specialized worker agents.
    """
    logger.info("=== Hierarchical Workflow Example ===")

    orchestrator = Orchestrator(
        framework="crewai",
        framework_config=FrameworkConfig(
            framework="crewai", allow_delegation=True, verbose=True  # Enable delegation
        ),
        pool_config=AgentPoolConfig(max_agents=10),
    )

    try:
        # Create manager and worker agents
        logger.info("Creating project team...")

        manager = await orchestrator.create_agent(
            name="project_manager",
            role="AI Project Manager",
            goal="Plan and coordinate the development of an AI application",
            backstory="Experienced project manager with deep technical knowledge",
        )

        architect = await orchestrator.create_agent(
            name="system_architect",
            role="System Architect",
            goal="Design system architecture and data models",
            backstory="Senior architect with expertise in AI systems",
        )

        backend_dev = await orchestrator.create_agent(
            name="backend_developer",
            role="Backend Developer",
            goal="Implement backend services and APIs",
            backstory="Expert Python developer specializing in AI backends",
        )

        frontend_dev = await orchestrator.create_agent(
            name="frontend_developer",
            role="Frontend Developer",
            goal="Build user interfaces and frontend components",
            backstory="Skilled frontend developer with UX expertise",
        )

        qa_engineer = await orchestrator.create_agent(
            name="qa_engineer",
            role="QA Engineer",
            goal="Ensure quality through testing and validation",
            backstory="Detail-oriented QA engineer with automation expertise",
        )

        # Define hierarchical tasks
        logger.info("Defining project tasks...")

        tasks = [
            TaskConfig(
                description="Create a comprehensive project plan for building an "
                "AI-powered document analysis system. Break down into "
                "components and assign to appropriate team members.",
                agent="project_manager",
                expected_output="Detailed project plan with task assignments",
            ),
            TaskConfig(
                description="Design the system architecture including data models, "
                "API structure, and component interactions.",
                agent="system_architect",
                expected_output="Architecture diagrams and technical specifications",
            ),
            TaskConfig(
                description="Implement the backend API for document processing and analysis.",
                agent="backend_developer",
                expected_output="API implementation plan and code structure",
            ),
            TaskConfig(
                description="Design and implement the user interface for document upload "
                "and results visualization.",
                agent="frontend_developer",
                expected_output="UI/UX design and component specifications",
            ),
            TaskConfig(
                description="Create test plan and implement automated tests for all components.",
                agent="qa_engineer",
                expected_output="Test plan and test automation strategy",
            ),
        ]

        # Create hierarchical workflow
        workflow_id = orchestrator.create_workflow(
            pattern=WorkflowPattern.HIERARCHICAL, tasks=tasks
        )

        logger.info("Executing hierarchical workflow...")
        result = await orchestrator.execute_workflow(workflow_id)

        # Display results
        logger.info(f"\n{'='*60}")
        logger.info("Hierarchical Workflow Results:")
        logger.info(f"Status: {result.status}")
        logger.info(f"Project completed in: {result.total_duration_ms:.2f}ms")

        logger.info("\nTask Breakdown:")
        for task_id, task_result in result.task_results.items():
            logger.info(f"\n  {task_id}:")
            logger.info(f"    Agent: {task_result.agent_id}")
            logger.info(f"    Status: {task_result.status}")
            logger.info(
                f"    Duration: {task_result.duration_ms:.2f}ms"
                if task_result.duration_ms
                else "    Duration: N/A"
            )

        logger.info(f"{'='*60}\n")

        return result

    finally:
        await orchestrator.shutdown()


async def conditional_workflow_example():
    """
    Example 4: Conditional Workflow - Adaptive Content Processing.

    Demonstrates conditional execution where tasks run based on
    runtime conditions and previous task results.
    """
    logger.info("=== Conditional Workflow Example ===")

    orchestrator = Orchestrator(framework="crewai", pool_config=AgentPoolConfig(max_agents=8))

    try:
        # Create content processing agents
        logger.info("Creating content processing agents...")

        content_analyzer = await orchestrator.create_agent(
            name="content_analyzer",
            role="Content Analyzer",
            goal="Analyze content type and characteristics",
            backstory="Expert at content classification and analysis",
        )

        text_processor = await orchestrator.create_agent(
            name="text_processor",
            role="Text Processing Specialist",
            goal="Process and enhance text content",
            backstory="Skilled at text processing and NLP",
        )

        sentiment_analyzer = await orchestrator.create_agent(
            name="sentiment_analyzer",
            role="Sentiment Analysis Expert",
            goal="Analyze sentiment and emotional tone",
            backstory="Expert at sentiment analysis and emotion detection",
        )

        summarizer = await orchestrator.create_agent(
            name="summarizer",
            role="Content Summarizer",
            goal="Create concise summaries of content",
            backstory="Skilled at extracting key information",
        )

        # Define conditional tasks
        logger.info("Defining conditional workflow...")

        tasks = [
            TaskConfig(
                description="Analyze the input content to determine its type, length, "
                "and characteristics. Classify as: news, article, social post, etc.",
                agent="content_analyzer",
                expected_output="Content analysis with metadata",
                metadata={"task_id": "analysis"},
            ),
            TaskConfig(
                description="Process and clean the text content. Remove noise and format properly.",
                agent="text_processor",
                expected_output="Cleaned and formatted text",
                metadata={"task_id": "text_processing"},
            ),
            TaskConfig(
                description="Perform sentiment analysis on the content. "
                "Determine overall tone and emotional content.",
                agent="sentiment_analyzer",
                expected_output="Sentiment analysis report",
                metadata={"task_id": "sentiment_analysis"},
            ),
            TaskConfig(
                description="Create a concise summary of the main points.",
                agent="summarizer",
                expected_output="Content summary",
                metadata={"task_id": "summarization"},
            ),
        ]

        # Define conditional dependencies
        def should_analyze_sentiment(ctx: dict[str, Any]) -> bool:
            """
            Only analyze sentiment for longer content.
            """
            # In real implementation, check content length from context
            # For demo, always return True
            return True

        def should_summarize(ctx: dict[str, Any]) -> bool:
            """
            Only summarize if content is long enough.
            """
            # In real implementation, check content length
            return True

        dependencies = [
            DependencyConfig(task_id="text_processing", depends_on=["analysis"]),
            DependencyConfig(
                task_id="sentiment_analysis",
                depends_on=["text_processing"],
                condition=should_analyze_sentiment,
            ),
            DependencyConfig(
                task_id="summarization", depends_on=["text_processing"], condition=should_summarize
            ),
        ]

        # Create conditional workflow
        workflow_id = orchestrator.create_workflow(
            pattern=WorkflowPattern.CONDITIONAL, tasks=tasks, dependencies=dependencies
        )

        logger.info("Executing conditional workflow...")
        result = await orchestrator.execute_workflow(
            workflow_id, inputs={"content": "Sample AI article about multi-agent systems..."}
        )

        # Display results
        logger.info(f"\n{'='*60}")
        logger.info("Conditional Workflow Results:")
        logger.info(f"Status: {result.status}")
        logger.info(f"Executed Tasks: {len(result.task_results)}")

        logger.info("\nExecution Flow:")
        for task_id, task_result in result.task_results.items():
            status_icon = (
                "✓" if task_result.success else "✗" if task_result.status.value == "failed" else "○"
            )
            logger.info(f"  {status_icon} {task_id}: {task_result.status.value}")

        logger.info(f"{'='*60}\n")

        return result

    finally:
        await orchestrator.shutdown()


async def main():
    """
    Run all examples.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Multi-Agent Orchestration Examples")
    parser.add_argument(
        "--example",
        choices=["sequential", "parallel", "hierarchical", "conditional", "all"],
        default="all",
        help="Which example to run",
    )
    args = parser.parse_args()

    examples = {
        "sequential": sequential_workflow_example,
        "parallel": parallel_workflow_example,
        "hierarchical": hierarchical_workflow_example,
        "conditional": conditional_workflow_example,
    }

    try:
        if args.example == "all":
            logger.info("Running all examples...\n")
            for name, example_func in examples.items():
                logger.info(f"\n{'#'*60}")
                logger.info(f"# Running: {name.upper()}")
                logger.info(f"{'#'*60}\n")
                await example_func()
                await asyncio.sleep(1)  # Brief pause between examples
        else:
            await examples[args.example]()

        logger.info("\n✅ All examples completed successfully!")

    except Exception as e:
        logger.error(f"❌ Error running examples: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
