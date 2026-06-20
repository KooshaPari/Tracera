"""Integration tests for advanced services.

Consolidated from batch1, batch2, and batch3 test files.
Tests advanced analytics, traceability, agent coordination, agent performance,
webhooks, commit linking, documentation, event sourcing, external integrations,
GitHub import, impact analysis, traceability matrix, query optimization,
and security compliance services with real database interactions.

Total Tests: 100+ integration tests
Approach: Real database interactions, minimal mocking, comprehensive edge cases
Coverage Strategy: Happy paths, edge cases, error scenarios, concurrent operations
"""

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
    # Batch 2
    "TestAPIWebhooksServiceIntegration",
    # Batch 1
    "TestAdvancedAnalyticsServiceIntegration",
    "TestAdvancedTraceabilityEnhancementsServiceIntegration",
    "TestAdvancedTraceabilityServiceIntegration",
    "TestAgentCoordinationServiceIntegration",
    "TestAgentPerformanceServiceIntegration",
    "TestCommitLinkingServiceIntegration",
    "TestDocumentationServiceIntegration",
    "TestEventSourcingServiceIntegration",
    "TestExternalIntegrationServiceIntegration",
    # Batch 3
    "TestGitHubImportService",
    "TestImpactAnalysisService",
    "TestQueryOptimizationService",
    "TestSecurityComplianceService",
    "TestTraceabilityMatrixService",
]
