"""Repository layer for TraceRTM."""

from tracertm.repositories.account_repository import AccountRepository
from tracertm.repositories.agent_repository import AgentRepository
from tracertm.repositories.blockchain_repository import (
    BaselineRepository,
    SpecEmbeddingRepository,
    VersionBlockRepository,
)
from tracertm.repositories.event_repository import EventRepository
from tracertm.repositories.execution_repository import (
    ExecutionArtifactRepository,
    ExecutionEnvironmentConfigRepository,
    ExecutionRepository,
)
from tracertm.repositories.github_app_repository import GitHubAppInstallationRepository
from tracertm.repositories.github_project_repository import GitHubProjectRepository
from tracertm.repositories.integration_repository import (
    IntegrationConflictRepository,
    IntegrationCredentialRepository,
    IntegrationMappingRepository,
    IntegrationRateLimitRepository,
    IntegrationSyncLogRepository,
    IntegrationSyncQueueRepository,
)
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.item_spec_repository import (
    DefectSpecRepository,
    EpicSpecRepository,
    ItemSpecBatchRepository,
    RequirementSpecRepository,
    TaskSpecRepository,
    TestSpecRepository,
    UserStorySpecRepository,
)
from tracertm.repositories.linear_app_repository import LinearAppInstallationRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.problem_repository import ProblemRepository
from tracertm.repositories.process_repository import ProcessRepository
from tracertm.repositories.project_repository import ProjectRepository
from tracertm.repositories.specification_repository import (
    ADRRepository,
    ContractRepository,
    FeatureRepository,
    ScenarioRepository,
)
from tracertm.repositories.test_case_repository import TestCaseRepository
from tracertm.repositories.test_coverage_repository import TestCoverageRepository
from tracertm.repositories.test_run_repository import TestRunRepository
from tracertm.repositories.test_suite_repository import TestSuiteRepository
from tracertm.repositories.webhook_repository import WebhookRepository

__all__ = [
    "ADRRepository",
    "AccountRepository",
    "AgentRepository",
    "BaselineRepository",
    "ContractRepository",
    "DefectSpecRepository",
    "EpicSpecRepository",
    "EventRepository",
    "ExecutionArtifactRepository",
    "ExecutionEnvironmentConfigRepository",
    "ExecutionRepository",
    "FeatureRepository",
    "GitHubAppInstallationRepository",
    "GitHubProjectRepository",
    "IntegrationConflictRepository",
    "IntegrationCredentialRepository",
    "IntegrationMappingRepository",
    "IntegrationRateLimitRepository",
    "IntegrationSyncLogRepository",
    "IntegrationSyncQueueRepository",
    "ItemRepository",
    "ItemSpecBatchRepository",
    "LinearAppInstallationRepository",
    "LinkRepository",
    "ProblemRepository",
    "ProcessRepository",
    "ProjectRepository",
    # Item Specification Repositories
    "RequirementSpecRepository",
    "ScenarioRepository",
    "SpecEmbeddingRepository",
    "TaskSpecRepository",
    "TestCaseRepository",
    "TestCoverageRepository",
    "TestRunRepository",
    "TestSpecRepository",
    "TestSuiteRepository",
    "UserStorySpecRepository",
    # Blockchain/ML Repositories
    "VersionBlockRepository",
    "WebhookRepository",
]
