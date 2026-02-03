"""
Integration tests for advanced services.

Consolidated from batch1, batch2, and batch3 test files.
Tests advanced analytics, traceability, agent coordination, agent performance,
webhooks, commit linking, documentation, event sourcing, external integrations,
GitHub import, impact analysis, traceability matrix, query optimization,
and security compliance services with real database interactions.

Total Tests: 100+ integration tests
Approach: Real database interactions, minimal mocking, comprehensive edge cases
Coverage Strategy: Happy paths, edge cases, error scenarios, concurrent operations
"""

from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.agent import Agent
from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
from tracertm.repositories.agent_repository import AgentRepository
from tracertm.repositories.event_repository import EventRepository
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.services.advanced_analytics_service import AdvancedAnalyticsService
from tracertm.services.advanced_traceability_enhancements_service import (
    AdvancedTraceabilityEnhancementsService,
)
from tracertm.services.advanced_traceability_service import (
    AdvancedTraceabilityService,
)
from tracertm.services.agent_coordination_service import (
    AgentConflict,
    AgentCoordinationService,
)
from tracertm.services.agent_performance_service import AgentPerformanceService

# Re-export all test classes from batch files
# This consolidates the tests without duplication
from .test_advanced_services_batch1 import (
    TestAdvancedAnalyticsServiceIntegration,
    TestAdvancedTraceabilityEnhancementsServiceIntegration,
    TestAdvancedTraceabilityServiceIntegration,
    TestAgentCoordinationServiceIntegration,
    TestAgentPerformanceServiceIntegration,
)
from .test_advanced_services_batch2 import (
    TestAPIWebhooksServiceIntegration,
    TestCommitLinkingServiceIntegration,
    TestDocumentationServiceIntegration,
    TestEventSourcingServiceIntegration,
    TestExternalIntegrationServiceIntegration,
)
from .test_advanced_services_batch3 import (
    TestGitHubImportService,
    TestImpactAnalysisService,
    TestQueryOptimizationService,
    TestSecurityComplianceService,
    TestTraceabilityMatrixService,
)

# All test classes are now available in this consolidated module
__all__ = [
    # Batch 1
    "TestAdvancedAnalyticsServiceIntegration",
    "TestAdvancedTraceabilityServiceIntegration",
    "TestAdvancedTraceabilityEnhancementsServiceIntegration",
    "TestAgentCoordinationServiceIntegration",
    "TestAgentPerformanceServiceIntegration",
    # Batch 2
    "TestAPIWebhooksServiceIntegration",
    "TestCommitLinkingServiceIntegration",
    "TestDocumentationServiceIntegration",
    "TestEventSourcingServiceIntegration",
    "TestExternalIntegrationServiceIntegration",
    # Batch 3
    "TestGitHubImportService",
    "TestImpactAnalysisService",
    "TestTraceabilityMatrixService",
    "TestQueryOptimizationService",
    "TestSecurityComplianceService",
]
