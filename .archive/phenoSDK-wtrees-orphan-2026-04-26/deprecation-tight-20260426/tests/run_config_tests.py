"""
Simple test runner for config tests.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pheno.config import (
    AppConfig,
    ConfigManager,
    DatabaseConfig,
    RedisConfig,
    config_manager,
    load_env_cascade,
    parse_dotenv,
)


def test_config_from_env():
    """
    Test loading config from environment variables.
    """
    print("Testing config from environment...")

    # Set environment variables
    os.environ["APP_NAME"] = "test-app"
    os.environ["APP_DEBUG"] = "true"
    os.environ["APP_LOG_LEVEL"] = "DEBUG"

    try:
        config = AppConfig.from_env(prefix="APP_")

        assert config.name == "test-app"
        assert config.log_level == "DEBUG"
        print("✓ Config from environment works")
    finally:
        # Cleanup
        del os.environ["APP_NAME"]
        del os.environ["APP_DEBUG"]
        del os.environ["APP_LOG_LEVEL"]


def test_config_from_file():
    """
    Test loading config from YAML file.
    """
    print("Testing config from file...")

    # Create temporary YAML file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(
            """
name: file-app
debug: true
log_level: INFO
environment: production
""",
        )
        temp_file = f.name

    try:
        config = AppConfig.from_file(temp_file)

        assert config.name == "file-app"
        assert config.debug == True
        assert config.log_level == "INFO"
        assert config.environment == "production"
        print("✓ Config from file works")
    finally:
        os.unlink(temp_file)


def test_config_hierarchical_loading():
    """
    Test hierarchical config loading (env > file > defaults).
    """
    print("Testing hierarchical loading...")

    # Create temporary YAML file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(
            """
name: file-app
debug: false
log_level: INFO
""",
        )
        temp_file = f.name

    # Set environment variable (should override file)
    os.environ["APP_DEBUG"] = "true"

    try:
        config = AppConfig.load(
            env_prefix="APP_", config_file=temp_file, defaults={"environment": "development"},
        )

        # From env (highest priority)
        assert config.debug == True

        # From file
        assert config.name == "file-app"
        assert config.log_level == "INFO"

        # From defaults
        assert config.environment == "development"

        print("✓ Hierarchical loading works")
    finally:
        del os.environ["APP_DEBUG"]
        os.unlink(temp_file)


def test_database_config():
    """
    Test DatabaseConfig.
    """
    print("Testing DatabaseConfig...")

    config = DatabaseConfig(
        host="db.example.com", port=5433, name="mydb", user="admin", password="secret",
    )

    assert config.host == "db.example.com"
    assert config.port == 5433
    assert config.name == "mydb"
    assert config.user == "admin"
    assert config.password == "secret"

    print("✓ DatabaseConfig works")


def test_redis_config():
    """
    Test RedisConfig.
    """
    print("Testing RedisConfig...")

    config = RedisConfig(host="redis.example.com", port=6380, db=1, password="secret")

    assert config.host == "redis.example.com"
    assert config.port == 6380
    assert config.db == 1
    assert config.password == "secret"

    print("✓ RedisConfig works")


def test_config_manager_dot_notation():
    """
    Test ConfigManager with dot notation.
    """
    print("Testing ConfigManager dot notation...")

    manager = ConfigManager()
    manager.load_from_dict(
        {
            "app": {"name": "test-app", "debug": True},
            "database": {"host": "localhost", "port": 5432},
        },
    )

    # Get with dot notation
    assert manager.get("app.name") == "test-app"
    assert manager.get("app.debug") == True
    assert manager.get("database.host") == "localhost"
    assert manager.get("database.port") == 5432

    # Get with default
    assert manager.get("app.missing", "default") == "default"

    print("✓ ConfigManager dot notation works")


def test_config_manager_set():
    """
    Test ConfigManager set method.
    """
    print("Testing ConfigManager set...")

    manager = ConfigManager()
    manager.load_from_dict({"app": {}})

    # Set values
    manager.set("app.debug", True)
    manager.set("app.log_level", "DEBUG")

    assert manager.get("app.debug") == True
    assert manager.get("app.log_level") == "DEBUG"

    print("✓ ConfigManager set works")


def test_config_manager_freeze():
    """
    Test ConfigManager freeze/unfreeze.
    """
    print("Testing ConfigManager freeze...")

    manager = ConfigManager()
    manager.load_from_dict({"app": {"debug": False}})

    # Freeze
    manager.freeze()

    # Try to modify (should raise)
    try:
        manager.set("app.debug", True)
        assert False, "Should have raised RuntimeError"
    except RuntimeError as e:
        assert "frozen" in str(e).lower()

    # Unfreeze
    manager.unfreeze()
    manager.set("app.debug", True)
    assert manager.get("app.debug") == True

    print("✓ ConfigManager freeze works")


def test_parse_dotenv():
    """
    Test parsing .env files.
    """
    print("Testing parse_dotenv...")

    # Create temporary .env file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write(
            """
# Comment
APP_NAME=test-app
APP_DEBUG=true
APP_LOG_LEVEL="INFO"

# Another comment
DATABASE_HOST=localhost
""",
        )
        temp_file = f.name

    try:
        env_vars = parse_dotenv(temp_file)

        assert env_vars["APP_NAME"] == "test-app"
        assert env_vars["APP_DEBUG"] == "true"
        assert env_vars["APP_LOG_LEVEL"] == "INFO"
        assert env_vars["DATABASE_HOST"] == "localhost"

        print("✓ parse_dotenv works")
    finally:
        os.unlink(temp_file)


def test_load_env_cascade():
    """
    Test cascading .env file loading.
    """
    print("Testing load_env_cascade...")

    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create .env file
        env_file = temp_path / ".env"
        env_file.write_text(
            """
APP_NAME=base-app
APP_DEBUG=false
""",
        )

        # Create .env.local file (should override)
        env_local = temp_path / ".env.local"
        env_local.write_text(
            """
APP_DEBUG=true
APP_LOG_LEVEL=DEBUG
""",
        )

        # Load with cascade
        env_vars = load_env_cascade(root_dirs=[temp_path])

        # From .env
        assert env_vars["APP_NAME"] == "base-app"

        # From .env.local (overrides .env)
        assert env_vars["APP_DEBUG"] == "true"
        assert env_vars["APP_LOG_LEVEL"] == "DEBUG"

        print("✓ load_env_cascade works")


def test_global_config_manager():
    """
    Test global config manager.
    """
    print("Testing global config manager...")

    manager = config_manager()
    assert isinstance(manager, ConfigManager)

    # Should be singleton
    manager2 = config_manager()
    assert manager is manager2

    print("✓ Global config manager works")


def run_all_tests():
    """
    Run all tests.
    """
    print("\n" + "=" * 60)
    print("Running Config Tests")
    print("=" * 60 + "\n")

    tests = [
        test_config_from_env,
        test_config_from_file,
        test_config_hierarchical_loading,
        test_database_config,
        test_redis_config,
        test_config_manager_dot_notation,
        test_config_manager_set,
        test_config_manager_freeze,
        test_parse_dotenv,
        test_load_env_cascade,
        test_global_config_manager,
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
