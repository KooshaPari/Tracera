"""
Analytics integration for phenoSDK

Traces to: FR-PHENOSDK-ANALYTICS-001

Product analytics for PhenoSDK with credential broker system
"""

import os
from typing import Dict, Any, Optional
from python.analytics import init_analytics, track, identify, EventType

ANALYTICS_ENDPOINT = os.environ.get("PHENOTYPE_ANALYTICS_ENDPOINT", "https://analytics.phenotype.dev/v1/events")
ANALYTICS_KEY = os.environ.get("PHENOTYPE_ANALYTICS_KEY", "")


def init_phenosdk_analytics():
    """Initialize analytics for phenoSDK"""
    if not ANALYTICS_KEY:
        return
    
    init_analytics({
        "endpoint": ANALYTICS_ENDPOINT,
        "api_key": ANALYTICS_KEY,
        "environment": os.environ.get("PHENOTYPE_ENV", "development"),
        "version": os.environ.get("PHENOSDK_VERSION", "dev"),
        "debug": os.environ.get("PHENOTYPE_ENV") == "development",
    })


def track_credential_issued(credential_type: str, user_id: str, tenant_id: Optional[str] = None):
    """Track credential issuance"""
    track(EventType.FEATURE_USED, {
        "feature": "credential_broker",
        "action": "credential_issued",
        "credential_type": credential_type,
        "user_id": user_id,
        "tenant_id": tenant_id,
    })


def track_credential_revoked(credential_id: str, user_id: str, reason: str):
    """Track credential revocation"""
    track(EventType.FEATURE_USED, {
        "feature": "credential_broker",
        "action": "credential_revoked",
        "credential_id": credential_id,
        "user_id": user_id,
        "reason": reason,
    })


def track_sdk_initialized(tenant_id: str, version: str):
    """Track SDK initialization"""
    track(EventType.FEATURE_USED, {
        "feature": "sdk",
        "action": "initialized",
        "tenant_id": tenant_id,
        "version": version,
    })


def track_api_call(endpoint: str, method: str, duration_ms: float, status_code: int):
    """Track API call performance"""
    event_type = EventType.API_CALL if status_code < 400 else EventType.ERROR_OCCURRED
    track(event_type, {
        "endpoint": endpoint,
        "method": method,
        "duration_ms": duration_ms,
        "status_code": status_code,
    })


def identify_tenant_user(user_id: str, tenant_id: str, email: Optional[str] = None):
    """Identify a tenant user"""
    identify(user_id, {
        "tenant_id": tenant_id,
        "email": email,
        "user_type": "tenant",
    })


def track_workflow_execution(workflow_name: str, status: str, duration_ms: float, metadata: Optional[Dict[str, Any]] = None):
    """Track workflow execution"""
    metadata = metadata or {}
    
    event_type_map = {
        "started": EventType.WORKFLOW_STARTED,
        "completed": EventType.WORKFLOW_COMPLETED,
        "failed": EventType.WORKFLOW_FAILED,
    }
    
    event_type = event_type_map.get(status, EventType.CUSTOM)
    if event_type == EventType.CUSTOM:
        event_type = f"workflow.{status}"
    
    track(event_type, {
        "workflow": workflow_name,
        "status": status,
        "duration_ms": duration_ms,
        **metadata,
    })
