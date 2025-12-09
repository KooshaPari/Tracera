"""
Comprehensive tests for PluginService.

Coverage target: 100%
Tests all methods including:
- register_plugin, unregister_plugin
- get_plugin, list_plugins
- enable_plugin, disable_plugin
- update_plugin_config
- register_hook, unregister_hook, execute_hook
- get_plugin_stats
- validate_plugin
- Plugin and PluginType classes

Covers:
- Success and failure scenarios
- Edge cases and validation
- Error handling and state management
- Hook execution with multiple callbacks
"""

import pytest
from tracertm.services.plugin_service import PluginService, Plugin, PluginType


class TestPluginServiceInit:
    """Test PluginService initialization."""

    def test_init_creates_empty_plugin_dict(self):
        """Test that initialization creates empty plugin dictionary."""
        service = PluginService()
        assert service.plugins == {}
        assert isinstance(service.plugins, dict)

    def test_init_creates_empty_hooks_dict(self):
        """Test that initialization creates empty hooks dictionary."""
        service = PluginService()
        assert service.hooks == {}
        assert isinstance(service.hooks, dict)


class TestRegisterPlugin:
    """Test register_plugin method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return PluginService()

    def test_register_basic_plugin(self, service):
        """Test registering a basic plugin with required fields."""
        plugin = service.register_plugin(
            name="test_plugin",
            version="1.0.0",
            plugin_type=PluginType.VIEW,
            description="Test plugin",
            author="Test Author",
        )

        assert plugin.name == "test_plugin"
        assert plugin.version == "1.0.0"
        assert plugin.plugin_type == PluginType.VIEW
        assert plugin.description == "Test plugin"
        assert plugin.author == "Test Author"
        assert plugin.enabled is True
        assert plugin.config == {}

    def test_register_plugin_with_config(self, service):
        """Test registering plugin with configuration."""
        config = {"setting1": "value1", "setting2": 42, "nested": {"key": "val"}}

        plugin = service.register_plugin(
            name="configured_plugin",
            version="1.0.0",
            plugin_type=PluginType.CUSTOM,
            description="Test",
            author="Author",
            config=config,
        )

        assert plugin.config == config
        assert plugin.config["setting2"] == 42

    def test_register_plugin_with_empty_config(self, service):
        """Test registering plugin with empty config dict."""
        plugin = service.register_plugin(
            name="empty_config",
            version="1.0.0",
            plugin_type=PluginType.VIEW,
            description="Test",
            author="Author",
            config={},
        )

        assert plugin.config == {}

    def test_register_plugin_with_none_config(self, service):
        """Test registering plugin with None config defaults to empty dict."""
        plugin = service.register_plugin(
            name="none_config",
            version="1.0.0",
            plugin_type=PluginType.VIEW,
            description="Test",
            author="Author",
            config=None,
        )

        assert plugin.config == {}

    def test_register_multiple_plugins_different_names(self, service):
        """Test registering multiple plugins with different names."""
        service.register_plugin("plugin1", "1.0.0", PluginType.VIEW, "Desc1", "Author1")
        service.register_plugin("plugin2", "1.0.0", PluginType.LINK_TYPE, "Desc2", "Author2")
        service.register_plugin("plugin3", "1.0.0", PluginType.EXPORT_FORMAT, "Desc3", "Author3")

        assert len(service.list_plugins()) == 3

    def test_register_overwrites_existing_plugin(self, service):
        """Test registering same plugin name overwrites previous."""
        service.register_plugin("plugin", "1.0.0", PluginType.VIEW, "Old", "Author")
        plugin = service.register_plugin("plugin", "2.0.0", PluginType.CUSTOM, "New", "New Author")

        assert plugin.version == "2.0.0"
        assert plugin.description == "New"
        assert plugin.plugin_type == PluginType.CUSTOM
        assert plugin.author == "New Author"
        assert len(service.list_plugins()) == 1

    def test_register_plugin_stored_in_dict(self, service):
        """Test that registered plugin is stored in plugins dict."""
        service.register_plugin("test", "1.0.0", PluginType.VIEW, "Desc", "Author")

        assert "test" in service.plugins
        assert service.plugins["test"].name == "test"

    def test_register_all_plugin_types(self, service):
        """Test registering plugins of all types."""
        for plugin_type in [PluginType.VIEW, PluginType.LINK_TYPE, PluginType.EXPORT_FORMAT,
                           PluginType.QUERY_FILTER, PluginType.CUSTOM]:
            name = f"plugin_{plugin_type.value}"
            service.register_plugin(name, "1.0.0", plugin_type, "Desc", "Author")
            assert service.plugins[name].plugin_type == plugin_type


class TestUnregisterPlugin:
    """Test unregister_plugin method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        service = PluginService()
        service.register_plugin("plugin1", "1.0.0", PluginType.VIEW, "Desc", "Author")
        service.register_plugin("plugin2", "1.0.0", PluginType.VIEW, "Desc", "Author")
        return service

    def test_unregister_existing_plugin(self, service):
        """Test unregistering an existing plugin."""
        result = service.unregister_plugin("plugin1")

        assert result is True
        assert service.get_plugin("plugin1") is None
        assert "plugin1" not in service.plugins

    def test_unregister_nonexistent_plugin(self, service):
        """Test unregistering plugin that doesn't exist."""
        result = service.unregister_plugin("nonexistent")

        assert result is False

    def test_unregister_leaves_other_plugins(self, service):
        """Test that unregistering one plugin doesn't affect others."""
        service.unregister_plugin("plugin1")

        assert service.get_plugin("plugin2") is not None

    def test_unregister_empty_service(self):
        """Test unregistering from empty service."""
        service = PluginService()
        result = service.unregister_plugin("nonexistent")

        assert result is False

    def test_unregister_all_plugins(self, service):
        """Test unregistering all plugins."""
        service.unregister_plugin("plugin1")
        service.unregister_plugin("plugin2")

        assert len(service.list_plugins()) == 0


class TestGetPlugin:
    """Test get_plugin method."""

    @pytest.fixture
    def service(self):
        """Create service instance with plugins."""
        service = PluginService()
        service.register_plugin("existing", "1.0.0", PluginType.VIEW, "Desc", "Author")
        return service

    def test_get_existing_plugin(self, service):
        """Test getting an existing plugin."""
        plugin = service.get_plugin("existing")

        assert plugin is not None
        assert plugin.name == "existing"

    def test_get_nonexistent_plugin(self, service):
        """Test getting plugin that doesn't exist."""
        plugin = service.get_plugin("nonexistent")

        assert plugin is None

    def test_get_plugin_returns_correct_type(self, service):
        """Test that get_plugin returns Plugin instance."""
        plugin = service.get_plugin("existing")

        assert isinstance(plugin, Plugin)

    def test_get_plugin_from_empty_service(self):
        """Test getting plugin from empty service."""
        service = PluginService()
        plugin = service.get_plugin("any")

        assert plugin is None

    def test_get_plugin_case_sensitive(self, service):
        """Test that plugin names are case-sensitive."""
        plugin = service.get_plugin("EXISTING")

        assert plugin is None


class TestListPlugins:
    """Test list_plugins method."""

    @pytest.fixture
    def service(self):
        """Create service instance with sample plugins."""
        service = PluginService()
        service.register_plugin("view1", "1.0.0", PluginType.VIEW, "D", "A")
        service.register_plugin("view2", "1.0.0", PluginType.VIEW, "D", "A")
        service.register_plugin("link1", "1.0.0", PluginType.LINK_TYPE, "D", "A")
        service.register_plugin("export1", "1.0.0", PluginType.EXPORT_FORMAT, "D", "A")
        service.register_plugin("custom1", "1.0.0", PluginType.CUSTOM, "D", "A")
        return service

    def test_list_all_plugins(self, service):
        """Test listing all plugins without filter."""
        plugins = service.list_plugins()

        assert len(plugins) == 5

    def test_list_plugins_by_type_view(self, service):
        """Test listing only VIEW plugins."""
        plugins = service.list_plugins(plugin_type=PluginType.VIEW)

        assert len(plugins) == 2
        assert all(p.plugin_type == PluginType.VIEW for p in plugins)

    def test_list_plugins_by_type_link(self, service):
        """Test listing only LINK_TYPE plugins."""
        plugins = service.list_plugins(plugin_type=PluginType.LINK_TYPE)

        assert len(plugins) == 1
        assert plugins[0].plugin_type == PluginType.LINK_TYPE

    def test_list_plugins_by_type_no_matches(self, service):
        """Test listing plugins of type with no matches."""
        plugins = service.list_plugins(plugin_type=PluginType.QUERY_FILTER)

        assert len(plugins) == 0

    def test_list_plugins_empty_service(self):
        """Test listing plugins when none exist."""
        service = PluginService()
        plugins = service.list_plugins()

        assert len(plugins) == 0
        assert plugins == []

    def test_list_plugins_returns_list_type(self, service):
        """Test that list_plugins returns a list."""
        plugins = service.list_plugins()

        assert isinstance(plugins, list)


class TestEnableDisablePlugin:
    """Test enable_plugin and disable_plugin methods."""

    @pytest.fixture
    def service(self):
        """Create service instance with plugin."""
        service = PluginService()
        service.register_plugin("plugin", "1.0.0", PluginType.VIEW, "Desc", "Author")
        return service

    def test_disable_plugin_success(self, service):
        """Test disabling an enabled plugin."""
        result = service.disable_plugin("plugin")

        assert result is True
        plugin = service.get_plugin("plugin")
        assert plugin.enabled is False

    def test_enable_plugin_success(self, service):
        """Test enabling a disabled plugin."""
        service.disable_plugin("plugin")

        result = service.enable_plugin("plugin")

        assert result is True
        plugin = service.get_plugin("plugin")
        assert plugin.enabled is True

    def test_disable_nonexistent_plugin(self, service):
        """Test disabling plugin that doesn't exist."""
        result = service.disable_plugin("nonexistent")

        assert result is False

    def test_enable_nonexistent_plugin(self, service):
        """Test enabling plugin that doesn't exist."""
        result = service.enable_plugin("nonexistent")

        assert result is False

    def test_disable_already_disabled_plugin(self, service):
        """Test disabling plugin that's already disabled."""
        service.disable_plugin("plugin")
        result = service.disable_plugin("plugin")

        assert result is True
        assert service.get_plugin("plugin").enabled is False

    def test_enable_already_enabled_plugin(self, service):
        """Test enabling plugin that's already enabled."""
        result = service.enable_plugin("plugin")

        assert result is True
        assert service.get_plugin("plugin").enabled is True

    def test_toggle_plugin_state_multiple_times(self, service):
        """Test toggling plugin state multiple times."""
        service.disable_plugin("plugin")
        assert service.get_plugin("plugin").enabled is False

        service.enable_plugin("plugin")
        assert service.get_plugin("plugin").enabled is True

        service.disable_plugin("plugin")
        assert service.get_plugin("plugin").enabled is False


class TestUpdatePluginConfig:
    """Test update_plugin_config method."""

    @pytest.fixture
    def service(self):
        """Create service instance with configured plugin."""
        service = PluginService()
        service.register_plugin(
            "plugin",
            "1.0.0",
            PluginType.VIEW,
            "Desc",
            "Author",
            config={"key1": "value1", "key2": "value2"},
        )
        return service

    def test_update_config_adds_new_keys(self, service):
        """Test updating config adds new keys."""
        new_config = {"key3": "value3", "key4": "value4"}

        result = service.update_plugin_config("plugin", new_config)

        assert result is not None
        plugin = service.get_plugin("plugin")
        assert plugin.config["key3"] == "value3"
        assert plugin.config["key4"] == "value4"

    def test_update_config_merges_with_existing(self, service):
        """Test that update merges with existing config."""
        new_config = {"key1": "new_value", "key3": "value3"}

        service.update_plugin_config("plugin", new_config)

        plugin = service.get_plugin("plugin")
        assert plugin.config["key1"] == "new_value"
        assert plugin.config["key2"] == "value2"
        assert plugin.config["key3"] == "value3"

    def test_update_config_nonexistent_plugin(self, service):
        """Test updating config of nonexistent plugin."""
        result = service.update_plugin_config("nonexistent", {"key": "value"})

        assert result is None

    def test_update_config_empty_dict(self, service):
        """Test updating with empty config dict."""
        result = service.update_plugin_config("plugin", {})

        assert result is not None
        plugin = service.get_plugin("plugin")
        # Original config should remain
        assert "key1" in plugin.config

    def test_update_config_returns_plugin(self, service):
        """Test that update returns the updated plugin."""
        result = service.update_plugin_config("plugin", {"new": "value"})

        assert isinstance(result, Plugin)
        assert result.name == "plugin"

    def test_update_config_with_nested_dict(self, service):
        """Test updating config with nested dictionary."""
        nested_config = {"nested": {"level1": {"level2": "value"}}}

        service.update_plugin_config("plugin", nested_config)

        plugin = service.get_plugin("plugin")
        assert plugin.config["nested"]["level1"]["level2"] == "value"


class TestHookRegistration:
    """Test register_hook and unregister_hook methods."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return PluginService()

    def test_register_single_hook(self, service):
        """Test registering a single hook."""
        def test_hook():
            return "executed"

        service.register_hook("test_event", test_hook)

        assert "test_event" in service.hooks
        assert len(service.hooks["test_event"]) == 1
        assert test_hook in service.hooks["test_event"]

    def test_register_multiple_hooks_same_event(self, service):
        """Test registering multiple hooks for same event."""
        def hook1():
            pass

        def hook2():
            pass

        def hook3():
            pass

        service.register_hook("event", hook1)
        service.register_hook("event", hook2)
        service.register_hook("event", hook3)

        assert len(service.hooks["event"]) == 3

    def test_register_hooks_different_events(self, service):
        """Test registering hooks for different events."""
        def hook1():
            pass

        def hook2():
            pass

        service.register_hook("event1", hook1)
        service.register_hook("event2", hook2)

        assert "event1" in service.hooks
        assert "event2" in service.hooks
        assert len(service.hooks["event1"]) == 1
        assert len(service.hooks["event2"]) == 1

    def test_unregister_hook_success(self, service):
        """Test successfully unregistering a hook."""
        def hook():
            pass

        service.register_hook("event", hook)
        result = service.unregister_hook("event", hook)

        assert result is True
        assert hook not in service.hooks.get("event", [])

    def test_unregister_hook_not_registered(self, service):
        """Test unregistering hook that wasn't registered."""
        def hook():
            pass

        result = service.unregister_hook("event", hook)

        assert result is False

    def test_unregister_hook_wrong_event(self, service):
        """Test unregistering hook from wrong event."""
        def hook():
            pass

        service.register_hook("event1", hook)
        result = service.unregister_hook("event2", hook)

        assert result is False

    def test_unregister_one_of_multiple_hooks(self, service):
        """Test unregistering one hook when multiple exist."""
        def hook1():
            pass

        def hook2():
            pass

        service.register_hook("event", hook1)
        service.register_hook("event", hook2)

        service.unregister_hook("event", hook1)

        assert hook1 not in service.hooks["event"]
        assert hook2 in service.hooks["event"]
        assert len(service.hooks["event"]) == 1


class TestHookExecution:
    """Test execute_hook method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return PluginService()

    def test_execute_single_hook(self, service):
        """Test executing single registered hook."""
        results = []

        def hook(data):
            results.append(data)

        service.register_hook("process", hook)
        service.execute_hook("process", "test_data")

        assert len(results) == 1
        assert results[0] == "test_data"

    def test_execute_multiple_hooks(self, service):
        """Test executing multiple hooks for same event."""
        results = []

        def hook1(data):
            results.append(f"hook1_{data}")

        def hook2(data):
            results.append(f"hook2_{data}")

        service.register_hook("event", hook1)
        service.register_hook("event", hook2)
        service.execute_hook("event", "data")

        assert len(results) == 2
        assert "hook1_data" in results
        assert "hook2_data" in results

    def test_execute_hook_with_return_values(self, service):
        """Test that execute_hook returns list of results."""
        def hook1():
            return "result1"

        def hook2():
            return "result2"

        service.register_hook("event", hook1)
        service.register_hook("event", hook2)
        results = service.execute_hook("event")

        assert len(results) == 2
        assert "result1" in results
        assert "result2" in results

    def test_execute_nonexistent_hook(self, service):
        """Test executing hook that doesn't exist."""
        results = service.execute_hook("nonexistent", "data")

        assert results == []

    def test_execute_hook_with_exception(self, service):
        """Test that hook exceptions are caught and returned."""
        def failing_hook():
            raise ValueError("Hook failed")

        service.register_hook("event", failing_hook)
        results = service.execute_hook("event")

        assert len(results) == 1
        assert "error" in results[0]

    def test_execute_hook_partial_failure(self, service):
        """Test executing hooks when some fail."""
        def success_hook():
            return "success"

        def failing_hook():
            raise Exception("Fail")

        service.register_hook("event", success_hook)
        service.register_hook("event", failing_hook)
        results = service.execute_hook("event")

        assert len(results) == 2
        assert "success" in results

    def test_execute_hook_with_multiple_arguments(self, service):
        """Test executing hook with multiple arguments."""
        result = []

        def hook(a, b, c):
            result.append((a, b, c))

        service.register_hook("event", hook)
        service.execute_hook("event", 1, 2, 3)

        assert result[0] == (1, 2, 3)

    def test_execute_hook_with_keyword_arguments(self, service):
        """Test executing hook with keyword arguments."""
        result = []

        def hook(name, value):
            result.append({"name": name, "value": value})

        service.register_hook("event", hook)
        service.execute_hook("event", name="test", value=42)

        assert result[0] == {"name": "test", "value": 42}


class TestGetPluginStats:
    """Test get_plugin_stats method."""

    @pytest.fixture
    def service(self):
        """Create service instance with sample data."""
        service = PluginService()
        service.register_plugin("plugin1", "1.0.0", PluginType.VIEW, "D", "A")
        service.register_plugin("plugin2", "1.0.0", PluginType.VIEW, "D", "A")
        service.register_plugin("plugin3", "1.0.0", PluginType.LINK_TYPE, "D", "A")
        service.disable_plugin("plugin2")

        def hook():
            pass

        service.register_hook("event1", hook)
        service.register_hook("event2", hook)
        return service

    def test_stats_total_plugins(self, service):
        """Test stats returns correct total plugins count."""
        stats = service.get_plugin_stats()

        assert stats["total_plugins"] == 3

    def test_stats_enabled_disabled_count(self, service):
        """Test stats returns correct enabled/disabled counts."""
        stats = service.get_plugin_stats()

        assert stats["enabled"] == 2
        assert stats["disabled"] == 1

    def test_stats_by_type(self, service):
        """Test stats returns counts by plugin type."""
        stats = service.get_plugin_stats()

        assert "by_type" in stats
        assert stats["by_type"]["view"] == 2
        assert stats["by_type"]["link_type"] == 1

    def test_stats_total_hooks(self, service):
        """Test stats returns total hooks count."""
        stats = service.get_plugin_stats()

        assert stats["total_hooks"] == 2

    def test_stats_empty_service(self):
        """Test stats for empty service."""
        service = PluginService()
        stats = service.get_plugin_stats()

        assert stats["total_plugins"] == 0
        assert stats["enabled"] == 0
        assert stats["disabled"] == 0
        assert stats["total_hooks"] == 0

    def test_stats_all_disabled(self):
        """Test stats when all plugins are disabled."""
        service = PluginService()
        service.register_plugin("p1", "1.0.0", PluginType.VIEW, "D", "A")
        service.register_plugin("p2", "1.0.0", PluginType.VIEW, "D", "A")
        service.disable_plugin("p1")
        service.disable_plugin("p2")

        stats = service.get_plugin_stats()

        assert stats["enabled"] == 0
        assert stats["disabled"] == 2


class TestValidatePlugin:
    """Test validate_plugin method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return PluginService()

    def test_validate_valid_plugin(self, service):
        """Test validating a valid plugin."""
        plugin = Plugin(
            name="valid",
            version="1.0.0",
            plugin_type=PluginType.VIEW,
            description="Valid plugin",
            author="Author",
        )

        errors = service.validate_plugin(plugin)

        assert errors == []

    def test_validate_missing_name(self, service):
        """Test validation catches missing name."""
        plugin = Plugin(
            name="",
            version="1.0.0",
            plugin_type=PluginType.VIEW,
            description="Valid",
            author="Author",
        )

        errors = service.validate_plugin(plugin)

        assert len(errors) > 0
        assert any("name" in err.lower() for err in errors)

    def test_validate_missing_version(self, service):
        """Test validation catches missing version."""
        plugin = Plugin(
            name="test",
            version="",
            plugin_type=PluginType.VIEW,
            description="Valid",
            author="Author",
        )

        errors = service.validate_plugin(plugin)

        assert len(errors) > 0
        assert any("version" in err.lower() for err in errors)

    def test_validate_missing_author(self, service):
        """Test validation catches missing author."""
        plugin = Plugin(
            name="test",
            version="1.0.0",
            plugin_type=PluginType.VIEW,
            description="Valid",
            author="",
        )

        errors = service.validate_plugin(plugin)

        assert len(errors) > 0
        assert any("author" in err.lower() for err in errors)

    def test_validate_missing_description(self, service):
        """Test validation catches missing description."""
        plugin = Plugin(
            name="test",
            version="1.0.0",
            plugin_type=PluginType.VIEW,
            description="",
            author="Author",
        )

        errors = service.validate_plugin(plugin)

        assert len(errors) > 0
        assert any("description" in err.lower() for err in errors)

    def test_validate_multiple_errors(self, service):
        """Test validation catches multiple errors."""
        plugin = Plugin(
            name="",
            version="",
            plugin_type=PluginType.VIEW,
            description="",
            author="",
        )

        errors = service.validate_plugin(plugin)

        assert len(errors) == 4  # All four required fields missing


class TestPluginType:
    """Test PluginType enum."""

    def test_all_plugin_types_defined(self):
        """Test that all plugin types are defined."""
        assert PluginType.VIEW == "view"
        assert PluginType.LINK_TYPE == "link_type"
        assert PluginType.EXPORT_FORMAT == "export_format"
        assert PluginType.QUERY_FILTER == "query_filter"
        assert PluginType.CUSTOM == "custom"

    def test_plugin_type_str_values(self):
        """Test that plugin types are strings."""
        for plugin_type in PluginType:
            assert isinstance(plugin_type.value, str)

    def test_plugin_type_uniqueness(self):
        """Test that all plugin type values are unique."""
        values = [pt.value for pt in PluginType]
        assert len(values) == len(set(values))


class TestPluginDataclass:
    """Test Plugin dataclass."""

    def test_create_minimal_plugin(self):
        """Test creating Plugin with required fields only."""
        plugin = Plugin(
            name="test",
            version="1.0.0",
            plugin_type=PluginType.VIEW,
            description="Test plugin",
            author="Author",
        )

        assert plugin.name == "test"
        assert plugin.version == "1.0.0"
        assert plugin.plugin_type == PluginType.VIEW
        assert plugin.description == "Test plugin"
        assert plugin.author == "Author"
        assert plugin.enabled is True
        assert plugin.config == {}

    def test_create_plugin_with_all_fields(self):
        """Test creating Plugin with all fields."""
        config = {"option": "value"}
        plugin = Plugin(
            name="test",
            version="1.0.0",
            plugin_type=PluginType.VIEW,
            description="Test",
            author="Author",
            enabled=False,
            config=config,
        )

        assert plugin.enabled is False
        assert plugin.config == config

    def test_plugin_defaults(self):
        """Test Plugin default values."""
        plugin = Plugin(
            name="test",
            version="1.0.0",
            plugin_type=PluginType.VIEW,
            description="Test",
            author="Author",
        )

        assert plugin.enabled is True
        assert plugin.config == {}

    def test_plugin_with_complex_config(self):
        """Test Plugin with complex nested config."""
        config = {
            "nested": {
                "level1": {
                    "level2": ["item1", "item2"],
                }
            },
            "list": [1, 2, 3],
        }

        plugin = Plugin(
            name="test",
            version="1.0.0",
            plugin_type=PluginType.VIEW,
            description="Test",
            author="Author",
            config=config,
        )

        assert plugin.config["nested"]["level1"]["level2"] == ["item1", "item2"]
        assert plugin.config["list"] == [1, 2, 3]


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return PluginService()

    def test_register_plugin_with_special_characters_in_name(self, service):
        """Test registering plugin with special characters in name."""
        plugin = service.register_plugin(
            name="plugin-with-dashes_and_underscores.123",
            version="1.0.0",
            plugin_type=PluginType.VIEW,
            description="Test",
            author="Author",
        )

        assert plugin.name == "plugin-with-dashes_and_underscores.123"

    def test_register_plugin_with_very_long_description(self, service):
        """Test plugin with very long description."""
        long_desc = "A" * 10000
        plugin = service.register_plugin(
            "test", "1.0.0", PluginType.VIEW, long_desc, "Author"
        )

        assert len(plugin.description) == 10000

    def test_register_plugin_with_unicode_name(self, service):
        """Test plugin with unicode characters in name."""
        plugin = service.register_plugin(
            "測試插件", "1.0.0", PluginType.VIEW, "Test", "Author"
        )

        assert plugin.name == "測試插件"

    def test_execute_hook_empty_event_name(self, service):
        """Test executing hook with empty event name."""
        results = service.execute_hook("")

        assert results == []

    def test_update_config_with_very_large_dict(self, service):
        """Test updating config with very large dictionary."""
        service.register_plugin("test", "1.0.0", PluginType.VIEW, "Test", "Author")

        large_config = {f"key_{i}": f"value_{i}" for i in range(1000)}
        result = service.update_plugin_config("test", large_config)

        assert result is not None
        assert len(service.get_plugin("test").config) >= 1000

    def test_multiple_services_independent(self):
        """Test that multiple service instances are independent."""
        service1 = PluginService()
        service2 = PluginService()

        service1.register_plugin("plugin1", "1.0.0", PluginType.VIEW, "Test", "Author")

        assert len(service1.list_plugins()) == 1
        assert len(service2.list_plugins()) == 0

    def test_hook_execution_order_preserved(self, service):
        """Test that hooks execute in registration order."""
        results = []

        def hook1():
            results.append(1)

        def hook2():
            results.append(2)

        def hook3():
            results.append(3)

        service.register_hook("event", hook1)
        service.register_hook("event", hook2)
        service.register_hook("event", hook3)
        service.execute_hook("event")

        assert results == [1, 2, 3]

    def test_plugin_config_mutation_after_registration(self, service):
        """Test that modifying config after registration affects stored plugin."""
        config = {"key": "value"}
        plugin = service.register_plugin("test", "1.0.0", PluginType.VIEW, "Test", "Author", config=config)

        # Modify config through service
        service.update_plugin_config("test", {"new_key": "new_value"})

        # Original plugin object should reflect changes
        stored_plugin = service.get_plugin("test")
        assert "new_key" in stored_plugin.config
