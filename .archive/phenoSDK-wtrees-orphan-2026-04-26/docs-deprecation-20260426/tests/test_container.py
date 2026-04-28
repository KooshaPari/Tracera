"""Tests for the consolidated DI container.

Tests all features:
- Auto-wiring via type hints
- Lifecycle management (singleton, transient, scoped)
- Circular dependency detection
- Constructor injection
- Named services and aliases
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest

from pheno.adapters.container import (
    Container,
    Lifecycle,
    get_container,
    reset_container,
    set_container,
)


# Test fixtures - simple service classes
class IDatabase:
    """
    Database interface.
    """



class PostgresDatabase(IDatabase):
    """
    Postgres implementation.
    """

    def __init__(self):
        self.connection = "postgres://localhost"


class ICache:
    """
    Cache interface.
    """



class RedisCache(ICache):
    """
    Redis implementation.
    """

    def __init__(self):
        self.host = "localhost"


class ILogger:
    """
    Logger interface.
    """



class ConsoleLogger(ILogger):
    """
    Console logger implementation.
    """

    def __init__(self):
        self.logs = []


class UserService:
    """
    Service with dependencies.
    """

    def __init__(self, database: IDatabase, cache: ICache, logger: ILogger):
        self.database = database
        self.cache = cache
        self.logger = logger


class CircularA:
    """
    For testing circular dependency detection.
    """

    def __init__(self, b: "CircularB"):
        self.b = b


class CircularB:
    """
    For testing circular dependency detection.
    """

    def __init__(self, a: CircularA):
        self.a = a


class ScopedService:
    """
    Service for testing scoped lifecycle.
    """

    instance_count = 0

    def __init__(self):
        ScopedService.instance_count += 1
        self.id = ScopedService.instance_count


@pytest.fixture
def container():
    """
    Fresh container for each test.
    """
    return Container()


@pytest.fixture(autouse=True)
def reset_global_container():
    """
    Reset global container after each test.
    """
    yield
    reset_container()


class TestBasicRegistration:
    """
    Test basic service registration and resolution.
    """

    def test_register_and_resolve(self, container):
        """
        Test basic registration and resolution.
        """
        container.register(IDatabase, PostgresDatabase)
        db = container.resolve(IDatabase)

        assert isinstance(db, PostgresDatabase)
        assert db.connection == "postgres://localhost"

    def test_register_with_factory(self, container):
        """
        Test registration with factory function.
        """
        container.register(ICache, lambda c: RedisCache())
        cache = container.resolve(ICache)

        assert isinstance(cache, RedisCache)

    def test_register_singleton_instance(self, container):
        """
        Test registering pre-created singleton.
        """
        db = PostgresDatabase()
        container.register_singleton(IDatabase, db)

        resolved = container.resolve(IDatabase)
        assert resolved is db

    def test_has_service(self, container):
        """
        Test checking if service is registered.
        """
        assert not container.has_service(IDatabase)

        container.register(IDatabase, PostgresDatabase)
        assert container.has_service(IDatabase)

    def test_list_services(self, container):
        """
        Test listing registered services.
        """
        container.register(IDatabase, PostgresDatabase)
        container.register(ICache, RedisCache)

        services = container.list_services()
        assert "IDatabase" in services
        assert "ICache" in services


class TestLifecycleManagement:
    """
    Test lifecycle strategies.
    """

    def test_singleton_lifecycle(self, container):
        """
        Test singleton returns same instance.
        """
        container.register(IDatabase, PostgresDatabase, Lifecycle.SINGLETON)

        db1 = container.resolve(IDatabase)
        db2 = container.resolve(IDatabase)

        assert db1 is db2

    def test_transient_lifecycle(self, container):
        """
        Test transient returns new instance each time.
        """
        container.register(IDatabase, PostgresDatabase, Lifecycle.TRANSIENT)

        db1 = container.resolve(IDatabase)
        db2 = container.resolve(IDatabase)

        assert db1 is not db2
        assert isinstance(db1, PostgresDatabase)
        assert isinstance(db2, PostgresDatabase)

    def test_scoped_lifecycle(self, container):
        """
        Test scoped returns same instance within scope.
        """
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

    def test_scoped_without_scope_raises(self, container):
        """
        Test scoped service without scope raises error.
        """
        container.register(IDatabase, PostgresDatabase, Lifecycle.SCOPED)

        with pytest.raises(ValueError, match="Scoped service requires a scope"):
            container.resolve(IDatabase)


class TestAutoWiring:
    """
    Test automatic dependency injection.
    """

    def test_auto_wire_dependencies(self, container):
        """
        Test auto-wiring constructor dependencies.
        """
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

    def test_auto_wire_with_missing_dependency_raises(self, container):
        """
        Test auto-wiring with missing dependency raises error.
        """
        # Register only some dependencies
        container.register(IDatabase, PostgresDatabase)

        # Try to register service with missing dependencies
        container.register(UserService, UserService)

        with pytest.raises(ValueError, match="Cannot auto-wire parameter"):
            container.resolve(UserService)


class TestCircularDependencyDetection:
    """
    Test circular dependency detection.
    """

    def test_circular_dependency_detected(self, container):
        """
        Test circular dependency is detected and raises error.
        """
        container.register(CircularA, CircularA)
        container.register(CircularB, CircularB)

        with pytest.raises(ValueError, match="Circular dependency detected"):
            container.resolve(CircularA)


class TestGlobalContainer:
    """
    Test global container functions.
    """

    def test_get_global_container(self):
        """
        Test getting global container.
        """
        container = get_container()
        assert isinstance(container, Container)

    def test_set_global_container(self):
        """
        Test setting global container.
        """
        custom_container = Container()
        custom_container.register(IDatabase, PostgresDatabase)

        set_container(custom_container)

        container = get_container()
        assert container is custom_container
        assert container.has_service(IDatabase)

    def test_reset_global_container(self):
        """
        Test resetting global container.
        """
        container = get_container()
        container.register(IDatabase, PostgresDatabase)

        reset_container()

        new_container = get_container()
        assert new_container is not container
        assert not new_container.has_service(IDatabase)


class TestClearContainer:
    """
    Test clearing container state.
    """

    def test_clear_removes_all_services(self, container):
        """
        Test clear removes all registered services.
        """
        container.register(IDatabase, PostgresDatabase)
        container.register(ICache, RedisCache)

        assert container.has_service(IDatabase)
        assert container.has_service(ICache)

        container.clear()

        assert not container.has_service(IDatabase)
        assert not container.has_service(ICache)
        assert len(container.list_services()) == 0


class TestBackwardCompatibility:
    """
    Test backward compatibility.
    """

    def test_dependency_container_alias(self):
        """
        Test DependencyContainer is alias for Container.
        """
        from pheno.adapters.container import DependencyContainer

        assert DependencyContainer is Container

        # Should work the same way
        container = DependencyContainer()
        container.register(IDatabase, PostgresDatabase)
        db = container.resolve(IDatabase)

        assert isinstance(db, PostgresDatabase)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
