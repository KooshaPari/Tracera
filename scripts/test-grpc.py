#!/usr/bin/env python3
"""
Test script for TraceRTM gRPC integration.

This script tests the Python gRPC client connecting to the Go gRPC server.

Usage:
    python scripts/test-grpc.py
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tracertm.services.grpc_client import GoBackendClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_connection():
    """Test basic connection to gRPC server."""
    logger.info("Testing gRPC connection...")

    try:
        async with GoBackendClient() as client:
            logger.info("✅ Successfully connected to gRPC server")
            return True
    except Exception as e:
        logger.error(f"❌ Failed to connect: {e}")
        return False


async def test_analyze_impact():
    """Test impact analysis."""
    logger.info("Testing impact analysis...")

    try:
        async with GoBackendClient() as client:
            result = await client.analyze_impact(
                item_id="test-item-123",
                project_id="test-project-456",
                direction="both",
                max_depth=2
            )

            logger.info(f"✅ Impact analysis succeeded")
            logger.info(f"   Total impacted items: {result['total_count']}")
            logger.info(f"   Items by type: {result['items_by_type']}")
            logger.info(f"   Items by depth: {result['items_by_depth']}")
            logger.info(f"   Critical paths: {len(result['critical_paths'])}")

            return True
    except Exception as e:
        logger.error(f"❌ Impact analysis failed: {e}")
        return False


async def test_find_cycles():
    """Test cycle detection."""
    logger.info("Testing cycle detection...")

    try:
        async with GoBackendClient() as client:
            result = await client.find_cycles(
                project_id="test-project-456",
                max_cycle_length=10
            )

            logger.info(f"✅ Cycle detection succeeded")
            logger.info(f"   Has cycles: {result['has_cycles']}")
            logger.info(f"   Total cycles: {result['total_count']}")

            return True
    except Exception as e:
        logger.error(f"❌ Cycle detection failed: {e}")
        return False


async def test_calculate_path():
    """Test path calculation."""
    logger.info("Testing path calculation...")

    try:
        async with GoBackendClient() as client:
            result = await client.calculate_path(
                project_id="test-project-456",
                source_item_id="test-item-1",
                target_item_id="test-item-2"
            )

            logger.info(f"✅ Path calculation succeeded")
            logger.info(f"   Path exists: {result['path_exists']}")
            logger.info(f"   Path length: {result['path_length']}")

            return True
    except Exception as e:
        logger.error(f"❌ Path calculation failed: {e}")
        return False


async def main():
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
        logger.info(f"Running: {test_name}")
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
        logger.info(f"{status}: {test_name}")

    logger.info("")
    logger.info(f"Results: {passed}/{total} tests passed")

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
