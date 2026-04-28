#!/usr/bin/env python3
"""Test script for TraceRTM gRPC integration.

This script tests the Python gRPC client connecting to the Go gRPC server.

Usage:
    python scripts/python/test_grpc.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tracertm.services.grpc_client import GoBackendClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def test_connection() -> bool | None:
    """Test basic connection to gRPC server."""
    logger.info("Testing gRPC connection...")

    try:
        async with GoBackendClient() as _client:
            logger.info("✅ Successfully connected to gRPC server")
            return True
    except Exception as e:
        logger.exception("❌ Failed to connect: %s", e)
        return False


async def test_analyze_impact() -> bool | None:
    """Test impact analysis."""
    logger.info("Testing impact analysis...")

    try:
        async with GoBackendClient() as client:
            result = await client.analyze_impact(
                item_id="test-item-123",
                project_id="test-project-456",
                direction="both",
                max_depth=2,
            )

            logger.info("✅ Impact analysis succeeded")
            logger.info("   Total impacted items: %s", result["total_count"])
            logger.info("   Items by type: %s", result["items_by_type"])
            logger.info("   Items by depth: %s", result["items_by_depth"])
            logger.info(f"   Critical paths: {len(result['critical_paths'])}")

            return True
    except Exception as e:
        logger.exception("❌ Impact analysis failed: %s", e)
        return False


async def test_find_cycles() -> bool | None:
    """Test cycle detection."""
    logger.info("Testing cycle detection...")

    try:
        async with GoBackendClient() as client:
            result = await client.find_cycles(project_id="test-project-456", max_cycle_length=10)

            logger.info("✅ Cycle detection succeeded")
            logger.info("   Has cycles: %s", result["has_cycles"])
            logger.info("   Total cycles: %s", result["total_count"])

            return True
    except Exception as e:
        logger.exception("❌ Cycle detection failed: %s", e)
        return False


async def test_calculate_path() -> bool | None:
    """Test path calculation."""
    logger.info("Testing path calculation...")

    try:
        async with GoBackendClient() as client:
            result = await client.calculate_path(
                project_id="test-project-456",
                source_item_id="test-item-1",
                target_item_id="test-item-2",
            )

            logger.info("✅ Path calculation succeeded")
            logger.info("   Path exists: %s", result["path_exists"])
            logger.info("   Path length: %s", result["path_length"])

            return True
    except Exception as e:
        logger.exception("❌ Path calculation failed: %s", e)
        return False


async def main() -> None:
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("TraceRTM gRPC Integration Test Suite")
    logger.info("=" * 60)

    tests = [
        ("Connection Test", test_connection),
        ("Impact Analysis", test_analyze_impact),
        ("Cycle Detection", test_find_cycles),
        ("Path Calculation", test_calculate_path),
    ]

    results = []

    for test_name, test_func in tests:
        logger.info("")
        logger.info("Running: %s", test_name)
        logger.info("-" * 60)

        result = await test_func()
        results.append((test_name, result))

    # Print summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info("%s: %s", status, test_name)

    logger.info("")
    logger.info("Results: %s/%s tests passed", passed, total)

    if passed == total:
        logger.info("🎉 All tests passed!")
        sys.exit(0)
    else:
        logger.error("⚠️  Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        sys.exit(1)
