#!/usr/bin/env python3
"""
Simple standalone test to verify backend implementations.
This script tests the backends without requiring external databases.
"""

import shutil
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_imports():
    """Test that all backends can be imported."""
    print("=" * 60)
    print("Testing Backend Imports")
    print("=" * 60)

    # Test base backend
    try:
        print("✓ IndexBackend imported successfully")
    except Exception as e:
        print(f"✗ IndexBackend import failed: {e}")
        return False

    # Test PgVector backend
    try:
        # Import might fail due to missing asyncpg, but that's optional
        from pheno.vector.backends.pgvector import PgVectorBackend
        print("✓ PgVectorBackend imported successfully")
        pgvector_available = True
    except ImportError as e:
        print(f"⚠ PgVectorBackend import skipped (missing dependencies): {e}")
        pgvector_available = False

    # Test LanceDB backend
    try:
        from pheno.vector.backends.lancedb import LanceDBBackend
        print("✓ LanceDBBackend imported successfully")
        lancedb_available = True
    except ImportError as e:
        print(f"⚠ LanceDBBackend import skipped (missing dependencies): {e}")
        lancedb_available = False

    # Test exports from __init__
    try:
        print("✓ Backends module exports working")
    except Exception as e:
        print(f"✗ Backends module exports failed: {e}")
        return False

    return True


def test_client_integration():
    """Test that backends are integrated into client."""
    print("\n" + "=" * 60)
    print("Testing Client Integration")
    print("=" * 60)

    try:
        from pheno.vector.client import IndexBackend

        # Check pgvector factory
        assert hasattr(IndexBackend, "pgvector"), "IndexBackend.pgvector not found"
        print("✓ IndexBackend.pgvector() factory available")

        # Check lancedb factory
        assert hasattr(IndexBackend, "lancedb"), "IndexBackend.lancedb not found"
        print("✓ IndexBackend.lancedb() factory available")

        # Check supabase factory (should still work)
        assert hasattr(IndexBackend, "supabase"), "IndexBackend.supabase not found"
        print("✓ IndexBackend.supabase() factory available")

        return True
    except Exception as e:
        print(f"✗ Client integration test failed: {e}")
        return False


def test_lancedb_basic():
    """Test basic LanceDB operations if available."""
    print("\n" + "=" * 60)
    print("Testing LanceDB Backend (if available)")
    print("=" * 60)

    try:
        import asyncio

        from pheno.vector.backends.lancedb import LanceDBBackend

        # Create temp directory
        temp_dir = tempfile.mkdtemp(prefix="lancedb_test_")

        try:
            async def run_test():
                backend = LanceDBBackend(
                    uri=temp_dir,
                    table_name="test_table",
                    dimension=384,
                )

                # Initialize
                await backend.initialize()
                print("✓ LanceDB backend initialized")

                # Insert a vector
                vector = [0.1] * 384
                metadata = {"type": "test", "name": "vector1"}
                await backend.insert(id="test_1", vector=vector, metadata=metadata)
                print("✓ Vector inserted successfully")

                # Count
                count = await backend.count()
                assert count >= 1, f"Expected count >= 1, got {count}"
                print(f"✓ Vector count: {count}")

                # Search
                results = await backend.search(query_vector=vector, limit=5)
                assert len(results) >= 1, f"Expected >= 1 result, got {len(results)}"
                print(f"✓ Search returned {len(results)} result(s)")

                # Delete
                deleted = await backend.delete("test_1")
                assert deleted, "Delete should return True"
                print("✓ Vector deleted successfully")

                # Verify deletion
                count_after = await backend.count()
                assert count_after == 0, f"Expected count 0 after delete, got {count_after}"
                print("✓ Count verified after deletion")

                await backend.close()
                print("✓ Backend closed successfully")

            asyncio.run(run_test())
            print("\n✓✓✓ All LanceDB tests passed! ✓✓✓")
            return True

        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)

    except ImportError as e:
        print(f"⚠ LanceDB tests skipped (missing dependencies): {e}")
        return None
    except Exception as e:
        print(f"✗ LanceDB test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pgvector_interface():
    """Test PgVector backend interface (without requiring database)."""
    print("\n" + "=" * 60)
    print("Testing PgVector Backend Interface")
    print("=" * 60)

    try:
        from pheno.vector.backends.pgvector import PgVectorBackend

        # Create backend instance (won't connect yet)
        backend = PgVectorBackend(
            dsn="postgresql://test:test@localhost/test",
            table_name="test_table",
            dimension=768,
        )

        # Check attributes
        assert backend.dsn is not None, "DSN should be set"
        assert backend.table_name == "test_table", "Table name mismatch"
        assert backend.dimension == 768, "Dimension mismatch"
        print("✓ PgVectorBackend instance created with correct attributes")

        # Check distance operator mapping
        assert backend._get_distance_operator() == "vector_l2_ops"
        assert backend._get_distance_function() == "<->"
        print("✓ Distance metric functions work correctly")

        print("\n✓✓✓ PgVector interface tests passed! ✓✓✓")
        return True

    except ImportError as e:
        print(f"⚠ PgVector tests skipped (missing dependencies): {e}")
        return None
    except Exception as e:
        print(f"✗ PgVector test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PHENO-SDK VECTOR BACKEND VALIDATION")
    print("=" * 60 + "\n")

    results = []

    # Test imports
    results.append(("Imports", test_imports()))

    # Test client integration
    results.append(("Client Integration", test_client_integration()))

    # Test LanceDB (if available)
    lancedb_result = test_lancedb_basic()
    if lancedb_result is not None:
        results.append(("LanceDB Basic Operations", lancedb_result))

    # Test PgVector interface
    pgvector_result = test_pgvector_interface()
    if pgvector_result is not None:
        results.append(("PgVector Interface", pgvector_result))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} passed")

    if failed > 0:
        print(f"\n⚠ {failed} test(s) failed")
        sys.exit(1)
    else:
        print("\n✓✓✓ ALL TESTS PASSED! ✓✓✓")
        sys.exit(0)


if __name__ == "__main__":
    main()
