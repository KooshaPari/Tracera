"""Pytest configuration for repository tests.

Provides async session fixtures with proper SQLite async support.
"""

import asyncio
import logging
import os
import tempfile
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Account models
from tracertm.models.account import Account
from tracertm.models.account_user import AccountUser
from tracertm.models.agent import Agent
from tracertm.models.agent_event import AgentEvent
from tracertm.models.agent_lock import AgentLock

# Import models to register them with SQLAlchemy
from tracertm.models.base import Base

# Blockchain models
from tracertm.models.blockchain import (
    Baseline,
    BaselineItem,
    MerkleProofCache,
    SpecEmbedding,
    VersionBlock,
    VersionChainIndex,
)
from tracertm.models.event import Event

# Execution models
from tracertm.models.execution import Execution, ExecutionArtifact
from tracertm.models.execution_config import ExecutionEnvironmentConfig

# GitHub App Installation model
from tracertm.models.github_app_installation import GitHubAppInstallation

# GitHub Project model
from tracertm.models.github_project import GitHubProject

# Additional models required for Link repository tests
from tracertm.models.graph import Graph

# Integration models
from tracertm.models.integration import (
    IntegrationConflict,
    IntegrationCredential,
    IntegrationMapping,
    IntegrationRateLimit,
    IntegrationSyncLog,
    IntegrationSyncQueue,
)
from tracertm.models.item import Item

# Item Specification models (enhanced spec types)
from tracertm.models.item_spec import (
    DefectSpec,
    EpicSpec,
    RequirementSpec,
    TaskSpec,
    TestSpec,
    UserStorySpec,
)
from tracertm.models.item_view import ItemView

# Linear App model
from tracertm.models.linear_app import LinearAppInstallation
from tracertm.models.link import Link

# Problem model
from tracertm.models.problem import Problem, ProblemActivity

# Process model
from tracertm.models.process import Process, ProcessExecution
from tracertm.models.project import Project
from tracertm.models.requirement_quality import RequirementQuality

# Specification models
from tracertm.models.specification import ADR, Contract, Feature, Scenario
from tracertm.models.test_case import TestCase, TestCaseActivity

# Test coverage model
from tracertm.models.test_coverage import CoverageActivity, TestCoverage

# Test-related models
from tracertm.models.test_run import TestResult, TestRun, TestRunActivity
from tracertm.models.test_suite import TestSuite, TestSuiteActivity, TestSuiteTestCase
from tracertm.models.view import View

# Webhook models
from tracertm.models.webhook_integration import WebhookIntegration, WebhookLog

# Additional models for other repositories
from tracertm.models.workflow_run import WorkflowRun


@pytest_asyncio.fixture(scope="function")
async def async_session_factory() -> None:
    """Create an async session factory for tests.

    Returns a factory function that creates new async sessions for each test.
    Manages the database lifecycle including schema creation and cleanup.
    """
    # Determine database URL
    db_url = os.getenv("TEST_DATABASE_URL")

    temp_path = None
    if db_url is None:
        # Create a temporary file-based database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            temp_path = temp_db.name
        db_url = f"sqlite+aiosqlite:///{temp_path}"

    # Create engine
    engine = create_async_engine(
        db_url,
        echo=False,
        future=True,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)

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
        # Clean up temp file if it was created (run in thread to avoid ASYNC240)
        if temp_path:
            try:
                await asyncio.to_thread(Path(temp_path).unlink)
            except Exception as e:
                logging.getLogger(__name__).debug("Cleanup temp path %s: %s", temp_path, e)


@pytest_asyncio.fixture(scope="function")
async def db_session(async_session_factory: Any) -> None:
    """Create an async database session for a test.

    Provides a fresh session for each test with automatic rollback
    and cleanup.
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def project_with_graph(db_session: AsyncSession) -> None:
    """Create a project with a default graph for link tests.

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
async def default_graph(db_session: AsyncSession, _project_with_graph: Any) -> None:
    """Get the default graph from a project_with_graph fixture."""
    await asyncio.sleep(0)
    return project_with_graph["graph"]


async def create_default_graph_for_project(session: AsyncSession, project_id: str) -> Graph:
    """Helper function to create a default graph for a project.

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
async def link_test_setup(_db_session: AsyncSession) -> None:
    """Fixture that patches ProjectRepository.create to automatically create a default graph.

    Use this fixture in link tests to ensure graphs are created automatically.
    """
    await asyncio.sleep(0)
    from tracertm.repositories.project_repository import ProjectRepository

    original_create = ProjectRepository.create

    async def create_with_graph(self, **kwargs: Any) -> None:
        project = await original_create(self, **kwargs)
        await create_default_graph_for_project(self.session, str(project.id))
        return project

    ProjectRepository.create = create_with_graph
    yield
    ProjectRepository.create = original_create
