"""
Sentry configuration for phenoSDK

Traces to: FR-PHENOSDK-SENTRY-001

Error tracking for Phenotype SDK with credential broker system
"""

import os
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration


def init_sentry():
    """Initialize Sentry with phenoSDK-specific configuration."""
    dsn = os.environ.get("SENTRY_DSN")
    
    if not dsn:
        return None
    
    environment = os.environ.get("SENTRY_ENVIRONMENT", "development")
    release = os.environ.get("PHENOSDK_VERSION", "dev")
    
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release,
        
        integrations=[
            FlaskIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        
        # Performance monitoring
        traces_sample_rate=0.1,
        
        # Attach stack traces
        attach_stacktrace=True,
        
        # Before send to filter sensitive credential data
        before_send=filter_sensitive_data,
        
        # Ignore certain errors
        ignore_errors=[
            "ConnectionResetError",
            "BrokenPipeError",
        ],
    )
    
    return sentry_sdk


def filter_sensitive_data(event, hint):
    """Filter out sensitive credential broker data from events."""
    if event.get("extra"):
        # Remove credential data
        for key in list(event["extra"].keys()):
            if any(sensitive in key.lower() for sensitive in ["password", "token", "secret", "key", "credential"]):
                event["extra"][key] = "[REDACTED]"
    
    # Sanitize request data
    if event.get("request", {}).get("data"):
        data = event["request"]["data"]
        if isinstance(data, dict):
            for key in list(data.keys()):
                if any(sensitive in key.lower() for sensitive in ["password", "token", "secret", "key"]):
                    data[key] = "[REDACTED]"
    
    return event


def capture_sdk_error(error: Exception, context: dict = None):
    """Capture SDK error with context."""
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                # Don't log sensitive values
                if any(sensitive in key.lower() for sensitive in ["password", "token", "secret"]):
                    value = "[REDACTED]"
                scope.set_extra(key, value)
        
        sentry_sdk.capture_exception(error)


def set_user_context(user_id: str, org_id: str = None):
    """Set user context for error tracking."""
    sentry_sdk.set_user({
        "id": user_id,
        "organization": org_id,
    })
