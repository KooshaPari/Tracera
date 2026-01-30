"""
Pytest configuration for repository tests.

Provides async session fixtures with proper SQLite async support.
"""

import asyncio
import os
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Import models to register them with SQLAlchemy
from tracertm.models.base import Base
from tracertm.models.agent import Agent
from tracertm.models.agent_event import AgentEvent
from tracertm.models.agent_lock import AgentLock
from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
# Additional models required for Link repository tests
from tracertm.models.graph import Graph
from tracertm.models.view import View
from tracertm.models.item_view import ItemView
# Additional models for other repositories
from tracertm.models.workflow_run import WorkflowRun
from tracertm.models.requirement_quality import RequirementQuality
# Test-related models
from tracertm.models.test_run import TestRun, TestResult, TestRunActivity
from tracertm.models.test_case import TestCase, TestCaseActivity
from tracertm.models.test_suite import TestSuite, TestSuiteTestCase, TestSuiteActivity
# Problem model
from tracertm.models.problem import Problem, ProblemActivity
# Process model
from tracertm.models.process import Process, ProcessExecution
# Test coverage model
from tracertm.models.test_coverage import TestCoverage, CoverageActivity


@pytest_asyncio.fixture(scope="function")
async def async_session_factory():
    """
    Create an async session factory for tests.

    Returns a factory function that creates new async sessions for each test.
    Manages the database lifecycle including schema creation and cleanup.
    """
    # Determine database URL
    db_url = os.getenv("TEST_DATABASE_URL")

    temp_path = None
    if db_url is None:
        # Create a temporary file-based database
        temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        temp_path = temp_db.name
        temp_db.close()
        db_url = f"sqlite+aiosqlite:///{temp_path}"

    # Create engine
    engine = create_async_engine(
        db_url,
        echo=False,
        future=True,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        future=True,
    )

    yield async_session

    # Cleanup
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()
    finally:
        # Clean up temp file if it was created
        if temp_path:
            try:
                Path(temp_path).unlink()
            except Exception:
                pass


@pytest_asyncio.fixture(scope="function")
async def db_session(async_session_factory):
    """
    Create an async database session for a test.

    Provides a fresh session for each test with automatic rollback
    and cleanup.
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def project_with_graph(db_session: AsyncSession):
    """
    Create a project with a default graph for link tests.

    This fixture provides a project that has all the required entities
    for creating links (project + default graph).
    """
    from tracertm.repositories.project_repository import ProjectRepository

    # Create project
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test project for link tests")

    # Create a default graph for the project
    graph = Graph(
        id=str(uuid4()),
        project_id=project.id,
        name="default",
        graph_type="default",
        description="Default graph for testing",
    )
    db_session.add(graph)
    await db_session.flush()
    await db_session.refresh(graph)

    return {"project": project, "graph": graph}


@pytest_asyncio.fixture(scope="function")
async def default_graph(db_session: AsyncSession, project_with_graph):
    """
    Get the default graph from a project_with_graph fixture.
    """
    return project_with_graph["graph"]


async def create_default_graph_for_project(session: AsyncSession, project_id: str) -> Graph:
    """
    Helper function to create a default graph for a project.

    This should be called after creating a project to enable link creation.
    """
    graph = Graph(
        id=str(uuid4()),
        project_id=project_id,
        name="default",
        graph_type="default",
        description="Default graph for testing",
    )
    session.add(graph)
    await session.flush()
    await session.refresh(graph)
    return graph


@pytest_asyncio.fixture(scope="function", autouse=False)
async def link_test_setup(db_session: AsyncSession):
    """
    Fixture that patches ProjectRepository.create to automatically create a default graph.

    Use this fixture in link tests to ensure graphs are created automatically.
    """
    from tracertm.repositories.project_repository import ProjectRepository

    original_create = ProjectRepository.create

    async def create_with_graph(self, **kwargs):
        project = await original_create(self, **kwargs)
        await create_default_graph_for_project(self.session, project.id)
        return project

    ProjectRepository.create = create_with_graph
    yield
    ProjectRepository.create = original_create
