"""Service layer for TraceRTM."""

from tracertm.services.bulk_service import BulkOperationService, BulkPreview
from tracertm.services.event_service import EventService
from tracertm.services.item_service import ItemService
from tracertm.services.spec_analytics_service_v2 import SpecAnalyticsServiceV2

__all__ = [
    "BulkOperationService",
    "BulkPreview",
    "EventService",
    "ItemService",
    "SpecAnalyticsServiceV2",
]

# Create singleton instance for use across the application
spec_analytics_service = SpecAnalyticsServiceV2()
