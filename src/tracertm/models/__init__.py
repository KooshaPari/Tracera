"""
SQLAlchemy models for TraceRTM.
"""

from tracertm.models.agent import Agent
from tracertm.models.agent_event import AgentEvent
from tracertm.models.agent_lock import AgentLock
from tracertm.models.base import Base
from tracertm.models.event import Event
from tracertm.models.external_link import ExternalLink
from tracertm.models.graph_change import GraphChange
from tracertm.models.graph_snapshot import GraphSnapshot
from tracertm.models.graph_type import GraphType
from tracertm.models.graph import Graph
from tracertm.models.graph_node import GraphNode
from tracertm.models.item import Item
from tracertm.models.item_view import ItemView
from tracertm.models.link import Link
from tracertm.models.link_type import LinkType
from tracertm.models.node_kind import NodeKind
from tracertm.models.node_kind_rule import NodeKindRule
from tracertm.models.workflow_run import WorkflowRun
from tracertm.models.problem import Problem, ProblemActivity
from tracertm.models.process import Process, ProcessExecution
from tracertm.models.project import Project
from tracertm.models.account import Account
from tracertm.models.account_user import AccountUser
try:
    from tracertm.models.test_case import TestCase, TestCaseActivity
    from tracertm.models.test_suite import TestSuite, TestSuiteTestCase, TestSuiteActivity
    from tracertm.models.test_run import TestRun, TestResult, TestRunActivity
    from tracertm.models.test_coverage import TestCoverage, CoverageActivity
    from tracertm.models.webhook_integration import WebhookIntegration, WebhookLog
    from tracertm.models.integration import (
        IntegrationCredential,
        IntegrationMapping,
        IntegrationSyncQueue,
        IntegrationSyncLog,
        IntegrationConflict,
        IntegrationRateLimit,
    )
except Exception:  # Avoid hard import failures during migrations or partial setups
    TestCase = None  # type: ignore[assignment]
    TestCaseActivity = None  # type: ignore[assignment]
    TestSuite = None  # type: ignore[assignment]
    TestSuiteTestCase = None  # type: ignore[assignment]
    TestSuiteActivity = None  # type: ignore[assignment]
    TestRun = None  # type: ignore[assignment]
    TestResult = None  # type: ignore[assignment]
    TestRunActivity = None  # type: ignore[assignment]
    TestCoverage = None  # type: ignore[assignment]
    CoverageActivity = None  # type: ignore[assignment]
    WebhookIntegration = None  # type: ignore[assignment]
    WebhookLog = None  # type: ignore[assignment]
    IntegrationCredential = None  # type: ignore[assignment]
    IntegrationMapping = None  # type: ignore[assignment]
    IntegrationSyncQueue = None  # type: ignore[assignment]
    IntegrationSyncLog = None  # type: ignore[assignment]
    IntegrationConflict = None  # type: ignore[assignment]
    IntegrationRateLimit = None  # type: ignore[assignment]
from tracertm.models.view import View

try:
    from tracertm.models.execution import Execution, ExecutionArtifact
    from tracertm.models.codex_agent import CodexAgentInteraction
    from tracertm.models.execution_config import ExecutionEnvironmentConfig
except Exception:  # Avoid hard import failures during migrations or partial setups
    Execution = None  # type: ignore[assignment]
    ExecutionArtifact = None  # type: ignore[assignment]
    CodexAgentInteraction = None  # type: ignore[assignment]
    ExecutionEnvironmentConfig = None  # type: ignore[assignment]

try:
    from tracertm.models.github_app_installation import GitHubAppInstallation
    from tracertm.models.github_project import GitHubProject
    from tracertm.models.linear_app import LinearAppInstallation
except Exception:
    GitHubAppInstallation = None  # type: ignore[assignment]
    GitHubProject = None  # type: ignore[assignment]
    LinearAppInstallation = None  # type: ignore[assignment]

try:
    # Note: ADR, Contract, Feature, Scenario are now defined in specification.py
    # The old individual files (adr.py, contract.py, feature.py, scenario.py) are deprecated
    # and should NOT be imported to avoid SQLAlchemy duplicate class registration errors
    from tracertm.models.requirement_quality import RequirementQuality
except Exception:  # Avoid hard import failures during migrations or partial setups
    RequirementQuality = None  # type: ignore[assignment]

try:
    from tracertm.models.specification import (
        ADR,
        ADRStatus,
        Contract,
        ContractType,
        ContractStatus,
        Feature,
        FeatureStatus,
        Scenario,
        ScenarioStatus,
        StepDefinition,
        StepType,
    )
except Exception:  # Avoid hard import failures during migrations or partial setups
    ADR = None  # type: ignore[assignment]
    ADRStatus = None  # type: ignore[assignment]
    Contract = None  # type: ignore[assignment]
    ContractType = None  # type: ignore[assignment]
    ContractStatus = None  # type: ignore[assignment]
    Feature = None  # type: ignore[assignment]
    FeatureStatus = None  # type: ignore[assignment]
    Scenario = None  # type: ignore[assignment]
    ScenarioStatus = None  # type: ignore[assignment]
    StepDefinition = None  # type: ignore[assignment]
    StepType = None  # type: ignore[assignment]

try:
    from tracertm.models.item_spec import (
        RequirementSpec,
        TestSpec,
        EpicSpec,
        UserStorySpec,
        TaskSpec,
        DefectSpec,
        RequirementType,
        ConstraintType,
        RiskLevel,
        VerificationStatus,
        TestType,
    )
except Exception:  # Avoid hard import failures during migrations or partial setups
    RequirementSpec = None  # type: ignore[assignment]
    TestSpec = None  # type: ignore[assignment]
    EpicSpec = None  # type: ignore[assignment]
    UserStorySpec = None  # type: ignore[assignment]
    TaskSpec = None  # type: ignore[assignment]
    DefectSpec = None  # type: ignore[assignment]
    RequirementType = None  # type: ignore[assignment]
    ConstraintType = None  # type: ignore[assignment]
    RiskLevel = None  # type: ignore[assignment]
    VerificationStatus = None  # type: ignore[assignment]
    TestType = None  # type: ignore[assignment]

try:
    from tracertm.models.blockchain import (
        VersionBlock,
        VersionChainIndex,
        Baseline,
        BaselineItem,
        MerkleProofCache,
        SpecEmbedding,
    )
except Exception:  # Avoid hard import failures during migrations or partial setups
    VersionBlock = None  # type: ignore[assignment]
    VersionChainIndex = None  # type: ignore[assignment]
    Baseline = None  # type: ignore[assignment]
    BaselineItem = None  # type: ignore[assignment]
    MerkleProofCache = None  # type: ignore[assignment]
    SpecEmbedding = None  # type: ignore[assignment]

__all__ = [
    "Agent",
    "AgentEvent",
    "AgentLock",
    "Base",
    "Event",
    "ExternalLink",
    "GraphChange",
    "GraphSnapshot",
    "GraphType",
    "Graph",
    "GraphNode",
    "Item",
    "ItemView",
    "Link",
    "LinkType",
    "NodeKind",
    "NodeKindRule",
    "WorkflowRun",
    "Problem",
    "ProblemActivity",
    "Process",
    "ProcessExecution",
    "Project",
    "Account",
    "AccountUser",
    "TestCase",
    "TestCaseActivity",
    "TestSuite",
    "TestSuiteTestCase",
    "TestSuiteActivity",
    "TestRun",
    "TestResult",
    "TestRunActivity",
    "TestCoverage",
    "CoverageActivity",
    "WebhookIntegration",
    "WebhookLog",
    "IntegrationCredential",
    "IntegrationMapping",
    "IntegrationSyncQueue",
    "IntegrationSyncLog",
    "IntegrationConflict",
    "IntegrationRateLimit",
    "View",
    "Execution",
    "ExecutionArtifact",
    "CodexAgentInteraction",
    "ExecutionEnvironmentConfig",
    # Specification Engine Models
    "ADR",
    "ADRStatus",
    "Contract",
    "ContractType",
    "ContractStatus",
    "Feature",
    "FeatureStatus",
    "Scenario",
    "ScenarioStatus",
    "StepDefinition",
    "StepType",
    "RequirementQuality",
    "GitHubAppInstallation",
    "GitHubProject",
    "LinearAppInstallation",
    # Item Specification Models
    "RequirementSpec",
    "TestSpec",
    "EpicSpec",
    "UserStorySpec",
    "TaskSpec",
    "DefectSpec",
    # Item Specification Enums
    "RequirementType",
    "ConstraintType",
    "RiskLevel",
    "VerificationStatus",
    "TestType",
    # Blockchain/ML Models
    "VersionBlock",
    "VersionChainIndex",
    "Baseline",
    "BaselineItem",
    "MerkleProofCache",
    "SpecEmbedding",
]
