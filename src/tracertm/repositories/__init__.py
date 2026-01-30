"""Repository layer for TraceRTM."""

from tracertm.repositories.agent_repository import AgentRepository
from tracertm.repositories.event_repository import EventRepository
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.problem_repository import ProblemRepository
from tracertm.repositories.process_repository import ProcessRepository
from tracertm.repositories.project_repository import ProjectRepository
from tracertm.repositories.test_case_repository import TestCaseRepository
from tracertm.repositories.test_suite_repository import TestSuiteRepository
from tracertm.repositories.test_run_repository import TestRunRepository
from tracertm.repositories.test_coverage_repository import TestCoverageRepository
from tracertm.repositories.webhook_repository import WebhookRepository
from tracertm.repositories.integration_repository import (
    IntegrationCredentialRepository,
    IntegrationMappingRepository,
    IntegrationSyncQueueRepository,
    IntegrationSyncLogRepository,
    IntegrationConflictRepository,
    IntegrationRateLimitRepository,
)
from tracertm.repositories.execution_repository import (
    ExecutionRepository,
    ExecutionArtifactRepository,
    ExecutionEnvironmentConfigRepository,
)
from tracertm.repositories.account_repository import AccountRepository
from tracertm.repositories.github_app_repository import GitHubAppInstallationRepository
from tracertm.repositories.github_project_repository import GitHubProjectRepository
from tracertm.repositories.linear_app_repository import LinearAppInstallationRepository
from tracertm.repositories.specification_repository import (
    ADRRepository,
    ContractRepository,
    FeatureRepository,
    ScenarioRepository,
)
from tracertm.repositories.item_spec_repository import (
    RequirementSpecRepository,
    TestSpecRepository,
    EpicSpecRepository,
    UserStorySpecRepository,
    TaskSpecRepository,
    DefectSpecRepository,
    ItemSpecBatchRepository,
)
from tracertm.repositories.blockchain_repository import (
    VersionBlockRepository,
    BaselineRepository,
    SpecEmbeddingRepository,
)

__all__ = [
    "AgentRepository",
    "EventRepository",
    "ItemRepository",
    "LinkRepository",
    "ProblemRepository",
    "ProcessRepository",
    "ProjectRepository",
    "TestCaseRepository",
    "TestSuiteRepository",
    "TestRunRepository",
    "TestCoverageRepository",
    "WebhookRepository",
    "IntegrationCredentialRepository",
    "IntegrationMappingRepository",
    "IntegrationSyncQueueRepository",
    "IntegrationSyncLogRepository",
    "IntegrationConflictRepository",
    "IntegrationRateLimitRepository",
    "ExecutionRepository",
    "ExecutionArtifactRepository",
    "ExecutionEnvironmentConfigRepository",
    "AccountRepository",
    "GitHubAppInstallationRepository",
    "GitHubProjectRepository",
    "LinearAppInstallationRepository",
    "ADRRepository",
    "ContractRepository",
    "FeatureRepository",
    "ScenarioRepository",
    # Item Specification Repositories
    "RequirementSpecRepository",
    "TestSpecRepository",
    "EpicSpecRepository",
    "UserStorySpecRepository",
    "TaskSpecRepository",
    "DefectSpecRepository",
    "ItemSpecBatchRepository",
    # Blockchain/ML Repositories
    "VersionBlockRepository",
    "BaselineRepository",
    "SpecEmbeddingRepository",
]
