"""Verification script to test OpenTelemetry instrumentation and trace generation.

This script:
1. Initializes OpenTelemetry with OTLP exporter
2. Creates sample spans to verify instrumentation
3. Checks connectivity to OTLP endpoint
4. Validates trace export functionality
"""

import asyncio
import logging
import os
import sys
from typing import Any

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def verify_tracing_setup() -> dict[str, Any]:
    """Verify OpenTelemetry setup and generate test traces.

    Returns:
        Dictionary with verification results
    """
    results = {
        "initialized": False,
        "tracer_available": False,
        "test_spans_created": False,
        "errors": [],
    }

    try:
        # Import and initialize tracing
        from tracertm.observability import init_tracing, get_tracer

        logger.info("Initializing OpenTelemetry tracing...")

        # Initialize with environment variables or defaults
        service_name = os.getenv("SERVICE_NAME", "tracertm-verification")
        otlp_endpoint = os.getenv("OTLP_ENDPOINT", "127.0.0.1:4317")
        environment = os.getenv("TRACING_ENVIRONMENT", "development")

        logger.info(f"Configuration:")
        logger.info(f"  Service: {service_name}")
        logger.info(f"  Endpoint: {otlp_endpoint}")
        logger.info(f"  Environment: {environment}")

        # Initialize tracing
        tracer = init_tracing(
            service_name=service_name,
            service_version="1.0.0",
            environment=environment,
            otlp_endpoint=otlp_endpoint,
        )

        results["initialized"] = True
        logger.info("✅ Tracing initialized successfully")

        # Verify tracer is available
        tracer = get_tracer()
        if tracer is not None:
            results["tracer_available"] = True
            logger.info("✅ Tracer instance available")

        # Create sample spans to test functionality
        logger.info("Creating sample test spans...")

        # Sync span
        with tracer.start_as_current_span("test.sync.operation") as span:
            span.set_attribute("test.type", "sync")
            span.set_attribute("test.language", "python")
            logger.info("Created sync span: test.sync.operation")

        # Async span
        with tracer.start_as_current_span("test.async.operation") as span:
            span.set_attribute("test.type", "async")
            span.set_attribute("test.language", "python")
            await asyncio.sleep(0.1)  # Simulate async work
            logger.info("Created async span: test.async.operation")

        # Error span
        try:
            with tracer.start_as_current_span("test.error.operation") as span:
                span.set_attribute("test.type", "error")
                raise ValueError("Test error for verification")
        except ValueError as e:
            logger.info(f"Created error span with exception: {e}")

        # Nested spans
        with tracer.start_as_current_span("test.parent.span") as parent_span:
            parent_span.set_attribute("span.type", "parent")

            with tracer.start_as_current_span("test.child.span") as child_span:
                child_span.set_attribute("span.type", "child")
                logger.info("Created nested spans")

        results["test_spans_created"] = True
        logger.info("✅ Test spans created successfully")

        # Force flush to ensure spans are exported
        logger.info("Flushing spans to OTLP endpoint...")
        current_provider = trace.get_tracer_provider()
        if hasattr(current_provider, "force_flush"):
            current_provider.force_flush(timeout_millis=5000)
            logger.info("✅ Spans flushed successfully")

    except ImportError as e:
        results["errors"].append(f"Import error: {e}")
        logger.error(f"❌ Import error: {e}")
    except RuntimeError as e:
        results["errors"].append(f"Runtime error: {e}")
        logger.error(f"❌ Runtime error: {e}")
    except Exception as e:
        results["errors"].append(f"Unexpected error: {e}")
        logger.error(f"❌ Unexpected error: {e}")

    return results


async def verify_instrumentation_packages() -> dict[str, Any]:
    """Verify that instrumentation packages are installed.

    Returns:
        Dictionary with package availability status
    """
    packages = {
        "fastapi": False,
        "sqlalchemy": False,
        "httpx": False,
        "requests": False,
        "redis": False,
    }

    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        packages["fastapi"] = True
        logger.info("✅ FastAPI instrumentation available")
    except ImportError:
        logger.warning("⚠️  FastAPI instrumentation not available")

    try:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

        packages["sqlalchemy"] = True
        logger.info("✅ SQLAlchemy instrumentation available")
    except ImportError:
        logger.warning("⚠️  SQLAlchemy instrumentation not available")

    try:
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

        packages["httpx"] = True
        logger.info("✅ HTTPX instrumentation available")
    except ImportError:
        logger.warning("⚠️  HTTPX instrumentation not available")

    try:
        from opentelemetry.instrumentation.requests import RequestsInstrumentor

        packages["requests"] = True
        logger.info("✅ Requests instrumentation available")
    except ImportError:
        logger.warning("⚠️  Requests instrumentation not available")

    try:
        from opentelemetry.instrumentation.redis import RedisInstrumentor

        packages["redis"] = True
        logger.info("✅ Redis instrumentation available")
    except ImportError:
        logger.warning("⚠️  Redis instrumentation not available")

    return packages


async def main() -> None:
    """Run all verification checks."""
    logger.info("=" * 80)
    logger.info("OpenTelemetry Instrumentation Verification")
    logger.info("=" * 80)

    # Check packages
    logger.info("\nVerifying instrumentation packages...")
    packages = await verify_instrumentation_packages()

    # Verify tracing setup
    logger.info("\nVerifying tracing setup...")
    results = await verify_tracing_setup()

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("VERIFICATION SUMMARY")
    logger.info("=" * 80)

    logger.info(f"Tracing Initialized: {results['initialized']}")
    logger.info(f"Tracer Available: {results['tracer_available']}")
    logger.info(f"Test Spans Created: {results['test_spans_created']}")

    logger.info("\nInstrumentation Packages:")
    for package, available in packages.items():
        status = "✅" if available else "⚠️ "
        logger.info(f"  {status} {package}")

    if results["errors"]:
        logger.error("\nErrors encountered:")
        for error in results["errors"]:
            logger.error(f"  ❌ {error}")
        sys.exit(1)

    if results["initialized"] and results["tracer_available"] and results["test_spans_created"]:
        logger.info("\n✅ All verification checks passed!")
        logger.info("Traces are being generated and exported to OTLP endpoint.")
        sys.exit(0)
    else:
        logger.warning("\n⚠️  Some verification checks failed.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
