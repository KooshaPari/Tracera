"""SQLAlchemy model exports and optional imports. Not part of public API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tracertm.models.account import Account
from tracertm.models.account_user import AccountUser
from tracertm.models.agent import Agent
from tracertm.models.agent_event import AgentEvent
from tracertm.models.agent_lock import AgentLock
from tracertm.models.agent_session import AgentSession
from tracertm.models.base import Base
from tracertm.models.event import Event
from tracertm.models.external_link import ExternalLink
from tracertm.models.graph import Graph
from tracertm.models.graph_change import GraphChange
from tracertm.models.graph_node import GraphNode
from tracertm.models.graph_snapshot import GraphSnapshot
from tracertm.models.graph_type import GraphType
from tracertm.models.item import Item
from tracertm.models.item_view import ItemView
from tracertm.models.link import Link
from tracertm.models.link_type import LinkType
from tracertm.models.node_kind import NodeKind
from tracertm.models.node_kind_rule import NodeKindRule
from tracertm.models.problem import Problem, ProblemActivity
from tracertm.models.process import Process, ProcessExecution
from tracertm.models.project import Project
from tracertm.models.user import User
from tracertm.models.workflow_run import WorkflowRun
from tracertm.models.workflow_schedule import WorkflowSchedule

if TYPE_CHECKING:
    from tracertm.models.integration import (
        IntegrationConflict,
        IntegrationCredential,
        IntegrationMapping,
        IntegrationRateLimit,
        IntegrationSyncLog,
        IntegrationSyncQueue,
    )
    from tracertm.models.test_case import TestCase, TestCaseActivity
    from tracertm.models.test_coverage import CoverageActivity, TestCoverage
    from tracertm.models.test_run import TestResult, TestRun, TestRunActivity
    from tracertm.models.test_suite import (
        TestSuite,
        TestSuiteActivity,
        TestSuiteTestCase,
    )
    from tracertm.models.webhook_integration import WebhookIntegration, WebhookLog
else:
    try:
        from tracertm.models.integration import (
            IntegrationConflict,
            IntegrationCredential,
            IntegrationMapping,
            IntegrationRateLimit,
            IntegrationSyncLog,
            IntegrationSyncQueue,
        )
        from tracertm.models.test_case import TestCase, TestCaseActivity
        from tracertm.models.test_coverage import CoverageActivity, TestCoverage
        from tracertm.models.test_run import TestResult, TestRun, TestRunActivity
        from tracertm.models.test_suite import TestSuite, TestSuiteActivity, TestSuiteTestCase
        from tracertm.models.webhook_integration import WebhookIntegration, WebhookLog
    except ImportError:  # Avoid hard import failures during migrations or partial setups
        TestCase = None  # type: ignore[assignment,misc]
        TestCaseActivity = None  # type: ignore[assignment,misc]
        TestSuite = None  # type: ignore[assignment,misc]
        TestSuiteTestCase = None  # type: ignore[assignment,misc]
        TestSuiteActivity = None  # type: ignore[assignment,misc]
        TestRun = None  # type: ignore[assignment,misc]
        TestResult = None  # type: ignore[assignment,misc]
        TestRunActivity = None  # type: ignore[assignment,misc]
        TestCoverage = None  # type: ignore[assignment,misc]
        CoverageActivity = None  # type: ignore[assignment,misc]
        WebhookIntegration = None  # type: ignore[assignment,misc]
        WebhookLog = None  # type: ignore[assignment,misc]
        IntegrationCredential = None  # type: ignore[assignment,misc]
        IntegrationMapping = None  # type: ignore[assignment,misc]
        IntegrationSyncQueue = None  # type: ignore[assignment,misc]
        IntegrationSyncLog = None  # type: ignore[assignment,misc]
        IntegrationConflict = None  # type: ignore[assignment,misc]
        IntegrationRateLimit = None  # type: ignore[assignment,misc]

from tracertm.models.view import View

if TYPE_CHECKING:
    from tracertm.models.blockchain import (
        Baseline,
        BaselineItem,
        MerkleProofCache,
        SpecEmbedding,
        VersionBlock,
        VersionChainIndex,
    )
    from tracertm.models.codex_agent import CodexAgentInteraction
    from tracertm.models.execution import Execution, ExecutionArtifact
    from tracertm.models.execution_config import ExecutionEnvironmentConfig
    from tracertm.models.github_app_installation import GitHubAppInstallation
    from tracertm.models.github_project import GitHubProject
    from tracertm.models.item_spec import (
        ConstraintType,
        DefectSpec,
        EpicSpec,
        RequirementSpec,
        RequirementType,
        RiskLevel,
        TaskSpec,
        TestSpec,
        TestType,
        UserStorySpec,
        VerificationStatus,
    )
    from tracertm.models.linear_app import LinearAppInstallation
    from tracertm.models.requirement_quality import RequirementQuality
    from tracertm.models.specification import (
        ADR,
        ADRStatus,
        Contract,
        ContractStatus,
        ContractType,
        Feature,
        FeatureStatus,
        Scenario,
        ScenarioStatus,
        StepDefinition,
        StepType,
    )
else:
    try:
        from tracertm.models.codex_agent import CodexAgentInteraction
        from tracertm.models.execution import Execution, ExecutionArtifact
        from tracertm.models.execution_config import ExecutionEnvironmentConfig
    except ImportError:  # Avoid hard import failures during migrations or partial setups
        Execution = None  # type: ignore[assignment,misc]
        ExecutionArtifact = None  # type: ignore[assignment,misc]
        CodexAgentInteraction = None  # type: ignore[assignment,misc]
        ExecutionEnvironmentConfig = None  # type: ignore[assignment,misc]

    try:
        from tracertm.models.github_app_installation import GitHubAppInstallation
        from tracertm.models.github_project import GitHubProject
        from tracertm.models.linear_app import LinearAppInstallation
    except ImportError:
        GitHubAppInstallation = None  # type: ignore[assignment,misc]
        GitHubProject = None  # type: ignore[assignment,misc]
        LinearAppInstallation = None  # type: ignore[assignment,misc]

    try:
        from tracertm.models.requirement_quality import RequirementQuality
    except ImportError:  # Avoid hard import failures during migrations or partial setups
        RequirementQuality = None  # type: ignore[assignment,misc]

    try:
        from tracertm.models.specification import (
            ADR,
            ADRStatus,
            Contract,
            ContractStatus,
            ContractType,
            Feature,
            FeatureStatus,
            Scenario,
            ScenarioStatus,
            StepDefinition,
            StepType,
        )
    except ImportError:  # Avoid hard import failures during migrations or partial setups
        ADR = None  # type: ignore[assignment,misc]
        ADRStatus = None  # type: ignore[assignment,misc]
        Contract = None  # type: ignore[assignment,misc]
        ContractType = None  # type: ignore[assignment,misc]
        ContractStatus = None  # type: ignore[assignment,misc]
        Feature = None  # type: ignore[assignment,misc]
        FeatureStatus = None  # type: ignore[assignment,misc]
        Scenario = None  # type: ignore[assignment,misc]
        ScenarioStatus = None  # type: ignore[assignment,misc]
        StepDefinition = None  # type: ignore[assignment,misc]
        StepType = None  # type: ignore[assignment,misc]

    try:
        from tracertm.models.item_spec import (
            ConstraintType,
            DefectSpec,
            EpicSpec,
            RequirementSpec,
            RequirementType,
            RiskLevel,
            TaskSpec,
            TestSpec,
            TestType,
            UserStorySpec,
            VerificationStatus,
        )
    except ImportError:  # Avoid hard import failures during migrations or partial setups
        RequirementSpec = None  # type: ignore[assignment,misc]
        TestSpec = None  # type: ignore[assignment,misc]
        EpicSpec = None  # type: ignore[assignment,misc]
        UserStorySpec = None  # type: ignore[assignment,misc]
        TaskSpec = None  # type: ignore[assignment,misc]
        DefectSpec = None  # type: ignore[assignment,misc]
        RequirementType = None  # type: ignore[assignment,misc]
        ConstraintType = None  # type: ignore[assignment,misc]
        RiskLevel = None  # type: ignore[assignment,misc]
        VerificationStatus = None  # type: ignore[assignment,misc]
        TestType = None  # type: ignore[assignment,misc]

    try:
        from tracertm.models.blockchain import (
            Baseline,
            BaselineItem,
            MerkleProofCache,
            SpecEmbedding,
            VersionBlock,
            VersionChainIndex,
        )
    except ImportError:  # Avoid hard import failures during migrations or partial setups
        VersionBlock = None  # type: ignore[assignment,misc]
        VersionChainIndex = None  # type: ignore[assignment,misc]
        Baseline = None  # type: ignore[assignment,misc]
        BaselineItem = None  # type: ignore[assignment,misc]
        MerkleProofCache = None  # type: ignore[assignment,misc]
        SpecEmbedding = None  # type: ignore[assignment,misc]

__all__ = [
    "ADR",
    "ADRStatus",
    "Account",
    "AccountUser",
    "Agent",
    "AgentEvent",
    "AgentLock",
    "AgentSession",
    "Base",
    "Baseline",
    "BaselineItem",
    "CodexAgentInteraction",
    "ConstraintType",
    "Contract",
    "ContractStatus",
    "ContractType",
    "CoverageActivity",
    "DefectSpec",
    "EpicSpec",
    "Event",
    "Execution",
    "ExecutionArtifact",
    "ExecutionEnvironmentConfig",
    "ExternalLink",
    "Feature",
    "FeatureStatus",
    "GitHubAppInstallation",
    "GitHubProject",
    "Graph",
    "GraphChange",
    "GraphNode",
    "GraphSnapshot",
    "GraphType",
    "IntegrationConflict",
    "IntegrationCredential",
    "IntegrationMapping",
    "IntegrationRateLimit",
    "IntegrationSyncLog",
    "IntegrationSyncQueue",
    "Item",
    "ItemView",
    "LinearAppInstallation",
    "Link",
    "LinkType",
    "MerkleProofCache",
    "NodeKind",
    "NodeKindRule",
    "Problem",
    "ProblemActivity",
    "Process",
    "ProcessExecution",
    "Project",
    "RequirementQuality",
    "RequirementSpec",
    "RequirementType",
    "RiskLevel",
    "Scenario",
    "ScenarioStatus",
    "SpecEmbedding",
    "StepDefinition",
    "StepType",
    "TaskSpec",
    "TestCase",
    "TestCaseActivity",
    "TestCoverage",
    "TestResult",
    "TestRun",
    "TestRunActivity",
    "TestSpec",
    "TestSuite",
    "TestSuiteActivity",
    "TestSuiteTestCase",
    "TestType",
    "User",
    "UserStorySpec",
    "VerificationStatus",
    "VersionBlock",
    "VersionChainIndex",
    "View",
    "WebhookIntegration",
    "WebhookLog",
    "WorkflowRun",
    "WorkflowSchedule",
]
