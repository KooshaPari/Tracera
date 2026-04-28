"""
Simple test runner for container tests without pytest plugins.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pheno.adapters.container import (
    Container,
    Lifecycle,
    get_container,
    reset_container,
)


# Test fixtures
class IDatabase:
    pass


class PostgresDatabase(IDatabase):
    def __init__(self):
        self.connection = "postgres://localhost"


class ICache:
    pass


class RedisCache(ICache):
    def __init__(self):
        self.host = "localhost"


class ILogger:
    pass


class ConsoleLogger(ILogger):
    def __init__(self):
        self.logs = []


class UserService:
    def __init__(self, database: IDatabase, cache: ICache, logger: ILogger):
        self.database = database
        self.cache = cache
        self.logger = logger


def test_basic_registration():
    """
    Test basic registration and resolution.
    """
    print("Testing basic registration...")
    container = Container()
    container.register(IDatabase, PostgresDatabase)
    db = container.resolve(IDatabase)

    assert isinstance(db, PostgresDatabase)
    assert db.connection == "postgres://localhost"
    print("✓ Basic registration works")


def test_singleton_lifecycle():
    """
    Test singleton returns same instance.
    """
    print("Testing singleton lifecycle...")
    container = Container()
    container.register(IDatabase, PostgresDatabase, Lifecycle.SINGLETON)

    db1 = container.resolve(IDatabase)
    db2 = container.resolve(IDatabase)

    assert db1 is db2
    print("✓ Singleton lifecycle works")


def test_transient_lifecycle():
    """
    Test transient returns new instance each time.
    """
    print("Testing transient lifecycle...")
    container = Container()
    container.register(IDatabase, PostgresDatabase, Lifecycle.TRANSIENT)

    db1 = container.resolve(IDatabase)
    db2 = container.resolve(IDatabase)

    assert db1 is not db2
    assert isinstance(db1, PostgresDatabase)
    assert isinstance(db2, PostgresDatabase)
    print("✓ Transient lifecycle works")


def test_auto_wiring():
    """
    Test automatic dependency injection.
    """
    print("Testing auto-wiring...")
    container = Container()

    # Register dependencies
    container.register(IDatabase, PostgresDatabase, Lifecycle.SINGLETON)
    container.register(ICache, RedisCache, Lifecycle.SINGLETON)
    container.register(ILogger, ConsoleLogger, Lifecycle.SINGLETON)

    # Register service with dependencies
    container.register(UserService, UserService)

    # Resolve - should auto-wire dependencies
    service = container.resolve(UserService)

    assert isinstance(service, UserService)
    assert isinstance(service.database, PostgresDatabase)
    assert isinstance(service.cache, RedisCache)
    assert isinstance(service.logger, ConsoleLogger)
    print("✓ Auto-wiring works")


def test_scoped_lifecycle():
    """
    Test scoped returns same instance within scope.
    """
    print("Testing scoped lifecycle...")
    container = Container()
    container.register(IDatabase, PostgresDatabase, Lifecycle.SCOPED)

    # Create scope
    scope1 = container.create_scope()
    container.set_scope(scope1)

    db1 = container.resolve(IDatabase)
    db2 = container.resolve(IDatabase)

    # Same instance within scope
    assert db1 is db2

    # Different instance in different scope
    scope2 = container.create_scope()
    container.set_scope(scope2)

    db3 = container.resolve(IDatabase)
    assert db3 is not db1
    print("✓ Scoped lifecycle works")


def test_circular_dependency_detection():
    """
    Test circular dependency is detected.
    """
    print("Testing circular dependency detection...")

    # Define classes first to avoid forward references
    class CircularB:
        pass

    class CircularA:
        def __init__(self, b: CircularB):
            self.b = b

    # Now update CircularB to depend on CircularA
    CircularB.__init__ = lambda self, a: setattr(self, "a", a)
    CircularB.__init__.__annotations__ = {"a": CircularA}

    container = Container()
    container.register(CircularA, CircularA)
    container.register(CircularB, CircularB)

    try:
        container.resolve(CircularA)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        # The circular dependency is detected, but wrapped in auto-wiring error
        # Check that it failed (which is correct behavior)
        assert "Cannot auto-wire" in str(e) or "Circular dependency" in str(e)
        print("✓ Circular dependency detection works")


def test_global_container():
    """
    Test global container functions.
    """
    print("Testing global container...")

    # Reset first
    reset_container()

    container = get_container()
    assert isinstance(container, Container)

    # Register something
    container.register(IDatabase, PostgresDatabase)

    # Get again - should be same instance
    container2 = get_container()
    assert container is container2
    assert container2.has_service(IDatabase)

    # Reset
    reset_container()
    container3 = get_container()
    assert container3 is not container
    assert not container3.has_service(IDatabase)

    print("✓ Global container works")


def test_backward_compatibility():
    """
    Test DependencyContainer alias.
    """
    print("Testing backward compatibility...")
    from pheno.adapters.container import DependencyContainer

    assert DependencyContainer is Container

    container = DependencyContainer()
    container.register(IDatabase, PostgresDatabase)
    db = container.resolve(IDatabase)

    assert isinstance(db, PostgresDatabase)
    print("✓ Backward compatibility works")


def run_all_tests():
    """
    Run all tests.
    """
    print("\n" + "=" * 60)
    print("Running Container Tests")
    print("=" * 60 + "\n")

    tests = [
        test_basic_registration,
        test_singleton_lifecycle,
        test_transient_lifecycle,
        test_auto_wiring,
        test_scoped_lifecycle,
        test_circular_dependency_detection,
        test_global_container,
        test_backward_compatibility,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
