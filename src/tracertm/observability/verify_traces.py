"""Verification script to test OpenTelemetry instrumentation and trace generation.

This script:
1. Initializes OpenTelemetry with OTLP exporter
2. Creates sample spans to verify instrumentation
3. Checks connectivity to OTLP endpoint
4. Validates trace export functionality
"""

import asyncio
import importlib.util
import logging
import os
import sys
from typing import Any

from opentelemetry import trace

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
    results: dict[str, Any] = {
        "initialized": False,
        "tracer_available": False,
        "test_spans_created": False,
        "errors": [],
    }

    try:
        # Import and initialize tracing
        from tracertm.observability import get_tracer, init_tracing

        logger.info("Initializing OpenTelemetry tracing...")

        # Initialize with environment variables or defaults
        service_name = os.getenv("SERVICE_NAME", "tracertm-verification")
        otlp_endpoint = os.getenv(
            "PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT",
            "127.0.0.1:4317",
        )
        environment = os.getenv("TRACING_ENVIRONMENT", "development")

        logger.info("Configuration:")
        logger.info("  Service: %s", service_name)
        logger.info("  Endpoint: %s", otlp_endpoint)
        logger.info("  Environment: %s", environment)

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
                msg = "Test error for verification"
                raise ValueError(msg)
        except ValueError as e:
            logger.info("Created error span with exception: %s", e)

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
        logger.exception("❌ Import error")
    except RuntimeError as e:
        results["errors"].append(f"Runtime error: {e}")
        logger.exception("❌ Runtime error")
    except Exception as e:
        results["errors"].append(f"Unexpected error: {e}")
        logger.exception("❌ Unexpected error")

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
        "redis_compatible_cache": False,
    }

    for name, pkg in [
        ("fastapi", "opentelemetry.instrumentation.fastapi"),
        ("sqlalchemy", "opentelemetry.instrumentation.sqlalchemy"),
        ("httpx", "opentelemetry.instrumentation.httpx"),
        ("requests", "opentelemetry.instrumentation.requests"),
        ("redis_compatible_cache", "opentelemetry.instrumentation.redis"),
    ]:
        spec = importlib.util.find_spec(pkg)
        packages[name] = spec is not None
        if spec is not None:
            logger.info("✅ %s instrumentation available", name.title())
        else:
            logger.warning("⚠️  %s instrumentation not available", name.title())

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
    logger.info("")
    logger.info("=" * 80)
    logger.info("VERIFICATION SUMMARY")
    logger.info("=" * 80)

    logger.info("Tracing Initialized: %s", results["initialized"])
    logger.info("Tracer Available: %s", results["tracer_available"])
    logger.info("Test Spans Created: %s", results["test_spans_created"])

    logger.info("\nInstrumentation Packages:")
    for package, available in packages.items():
        status = "✅" if available else "⚠️ "
        logger.info("  %s %s", status, package)

    if results["errors"]:
        logger.error("\nErrors encountered:")
        for error in results["errors"]:
            logger.error("  ❌ %s", error)
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
