# Core API Reference

The Core API provides the fundamental functionality of the Pheno SDK.

## Overview

The Core API includes:

- Data processing functions
- Configuration management
- Error handling
- Logging utilities

## Functions

### get_registry_manager

Get the global registry manager instance.

**Returns:** `Any`

**File:** `src/pheno/core/unified_registry.py:318`

---

### get_tool_registry

Get the tool registry.

**Returns:** `Any`

**File:** `src/pheno/core/unified_registry.py:329`

---

### get_provider_registry

Get the provider registry.

**Returns:** `Any`

**File:** `src/pheno/core/unified_registry.py:336`

---

### get_adapter_registry

Get the adapter registry.

**Returns:** `Any`

**File:** `src/pheno/core/unified_registry.py:343`

---

### get_plugin_registry

Get the plugin registry.

**Returns:** `Any`

**File:** `src/pheno/core/unified_registry.py:350`

---

### get_resource_registry

Get the resource registry.

**Returns:** `Any`

**File:** `src/pheno/core/unified_registry.py:357`

---

### get_component_registry

Get the component registry.

**Returns:** `Any`

**File:** `src/pheno/core/unified_registry.py:364`

---

### __init__

Initialize the unified registry manager.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/unified_registry.py:74`

---

### _initialize_default_registries

Initialize default registries.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/unified_registry.py:86`

---

### create_registry

Create a new registry.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `registry_type` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/unified_registry.py:156`

---

### get_registry

Get a registry by name.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/unified_registry.py:191`

---

### list_registries

List all registry names.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/unified_registry.py:209`

---

### get_registry_config

Get configuration for a registry.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/unified_registry.py:216`

---

### register_item

Register an item in a specific registry.

**Parameters:**

- `self` (Any): No description
- `registry_name` (Any): No description
- `key` (Any): No description
- `item` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/unified_registry.py:225`

---

### get_item

Get an item from a registry.

**Parameters:**

- `self` (Any): No description
- `registry_name` (Any): No description
- `key` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/unified_registry.py:248`

---

### list_items

List items in a registry.

**Parameters:**

- `self` (Any): No description
- `registry_name` (Any): No description
- `prefix` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/unified_registry.py:255`

---

### unregister_item

Unregister an item from a registry.

**Parameters:**

- `self` (Any): No description
- `registry_name` (Any): No description
- `key` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/unified_registry.py:262`

---

### clear_registry

Clear all items from a registry.

**Parameters:**

- `self` (Any): No description
- `registry_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/unified_registry.py:269`

---

### auto_discover

Auto-discover items for a registry.

**Parameters:**

- `self` (Any): No description
- `registry_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/unified_registry.py:276`

---

### get_registry_summary

Get a summary of all registries.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/unified_registry.py:295`

---

### __init__

Initialize migrator for a target registry.

**Parameters:**

- `self` (Any): No description
- `target_registry` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/unified_registry.py:377`

---

### migrate_from_dict

Migrate items from a dictionary.

**Parameters:**

- `self` (Any): No description
- `items` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/unified_registry.py:387`

---

### migrate_from_old_registry

Migrate items from an old registry implementation.

**Parameters:**

- `self` (Any): No description
- `old_registry` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/unified_registry.py:400`

---

### _insert_path

Insert path into sys.path if it exists and isn't already present.

**Parameters:**

- `p` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/pathing.py:20`

---

### _find_upwards

Search upwards from start for any of the given directory names.

**Parameters:**

- `start` (Any): No description
- `names` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/pathing.py:40`

---

### ensure_project_src_on_path

Ensure the caller project's src directory is importable.

**Parameters:**

- `project_root` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/pathing.py:62`

---

### ensure_pheno_sdk_on_path

Ensure the pheno-sdk repository root and its src are importable.

**Parameters:**

- `hints` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/pathing.py:75`

---

### ensure_kinfra_on_path

Ensure KInfra library directory is importable if present.

**Parameters:**

- `hints` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/pathing.py:118`

---

### bootstrap

Perform standard path bootstrapping for repos that integrate Pheno-SDK.

**Parameters:**

- `project_root` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/pathing.py:156`

---

### to_dict

Convert to dictionary.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/core.py:58`

---

### to_dict

Convert to dictionary.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/core.py:95`

---

### to_dict

Convert to dictionary.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/core.py:127`

---

### from_dict

Create from dictionary.

**Parameters:**

- `cls` (Any): No description
- `data` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/core.py:144`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `project_name` (Any): No description
- `config` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/core.py:156`

---

### add_issue

Add a quality issue to the report.

**Parameters:**

- `self` (Any): No description
- `issue` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/core.py:166`

---

### add_issues

Add multiple quality issues to the report.

**Parameters:**

- `self` (Any): No description
- `issues` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/core.py:172`

---

### add_tool_report

Add a tool-specific report.

**Parameters:**

- `self` (Any): No description
- `tool_name` (Any): No description
- `report` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/core.py:178`

---

### finalize

Finalize the report and calculate metrics.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/core.py:184`

---

### _calculate_quality_score

Calculate overall quality score (0-100)

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/core.py:222`

---

### get_issues_by_severity

Get issues filtered by severity.

**Parameters:**

- `self` (Any): No description
- `severity` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/core.py:244`

---

### get_issues_by_tool

Get issues filtered by tool.

**Parameters:**

- `self` (Any): No description
- `tool` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/core.py:250`

---

### get_issues_by_type

Get issues filtered by type.

**Parameters:**

- `self` (Any): No description
- `issue_type` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/core.py:256`

---

### get_issues_by_file

Get issues filtered by file.

**Parameters:**

- `self` (Any): No description
- `file_path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/core.py:262`

---

### to_dict

Convert report to dictionary.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/core.py:268`

---

### to_json

Convert report to JSON string.

**Parameters:**

- `self` (Any): No description
- `indent` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/core.py:283`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `config` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/core.py:295`

---

### analyze_file

Analyze a single file and return quality issues.

**Parameters:**

- `self` (Any): No description
- `file_path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/core.py:301`

---

### analyze_directory

Analyze a directory and return quality issues.

**Parameters:**

- `self` (Any): No description
- `directory_path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/core.py:308`

---

### get_issues

Get all detected issues.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/core.py:314`

---

### clear_issues

Clear all detected issues.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/core.py:320`

---

### get_metrics

Get analysis metrics.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/core.py:326`

---

### config_manager

Retrieve the process-wide configuration manager singleton.

**Returns:** `Any`

**File:** `src/pheno/config/core.py:373`

---

### parse_dotenv

Parse .env file into dictionary.

**Parameters:**

- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/config/core.py:382`

---

### load_env_cascade

Load environment variables with cascading priority.

**Parameters:**

- `root_dirs` (Any): No description
- `env_files` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/config/core.py:412`

---

### from_env

Load configuration from environment variables.

**Parameters:**

- `cls` (Any): No description
- `prefix` (Any): No description
- `_return_dict` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/config/core.py:63`

---

### from_file

Load configuration from file (JSON, YAML, or TOML).

**Parameters:**

- `cls` (Any): No description
- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/config/core.py:90`

---

### load

Load configuration with hierarchical merging.

**Parameters:**

- `cls` (Any): No description
- `env_prefix` (Any): No description
- `config_file` (Any): No description
- `defaults` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/config/core.py:133`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/config/core.py:259`

---

### load_from_dict

Overwrite the registry with values from ``data``.

**Parameters:**

- `self` (Any): No description
- `data` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/config/core.py:263`

---

### load_from_env

Populate the registry from environment variables honouring ``prefix``.

**Parameters:**

- `self` (Any): No description
- `prefix` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/config/core.py:276`

---

### get

Get configuration value using dot notation.

**Parameters:**

- `self` (Any): No description
- `key` (Any): No description
- `default` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/config/core.py:295`

---

### set

Set configuration value using dot notation.

**Parameters:**

- `self` (Any): No description
- `key` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/config/core.py:319`

---

### freeze

Prevent further mutations to the registry.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/config/core.py:344`

---

### unfreeze

Re-enable mutations following a :meth:`freeze` call.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/config/core.py:352`

---

### to_dict

Produce a shallow copy of the current configuration state.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/config/core.py:360`

---

### to_dict

Convert to dictionary.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cicd/core.py:78`

---

### from_dict

Create from dictionary.

**Parameters:**

- `cls` (Any): No description
- `data` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cicd/core.py:101`

---

### to_dict

Convert to dictionary.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cicd/core.py:139`

---

### add_file

Add a file to the pipeline.

**Parameters:**

- `self` (Any): No description
- `file_path` (Any): No description
- `content` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cicd/core.py:168`

---

### get_file

Get file content.

**Parameters:**

- `self` (Any): No description
- `file_path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cicd/core.py:174`

---

### list_files

List all files in the pipeline.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cicd/core.py:180`

---

### to_dict

Convert to dictionary.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cicd/core.py:186`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `config` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cicd/core.py:205`

---

### generate_pipeline

Generate a complete CI/CD pipeline.

**Parameters:**

- `self` (Any): No description
- `project_path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cicd/core.py:211`

---

### generate_workflow

Generate a specific workflow file.

**Parameters:**

- `self` (Any): No description
- `stage` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cicd/core.py:218`

---

### generate_dockerfile

Generate Dockerfile.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cicd/core.py:225`

---

### generate_docker_compose

Generate docker-compose.yml.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cicd/core.py:232`

---

### generate_makefile

Generate Makefile.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cicd/core.py:239`

---

### register_template

Register a template.

**Parameters:**

- `self` (Any): No description
- `template` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cicd/core.py:245`

---

### get_template

Get a template by name.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cicd/core.py:251`

---

### list_templates

List available templates.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cicd/core.py:257`

---

### validate_config

Validate configuration and return errors.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cicd/core.py:263`

---

### generate_all

Generate complete CI/CD pipeline.

**Parameters:**

- `self` (Any): No description
- `project_path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cicd/core.py:280`

---

### _should_generate_stage

Determine if a stage should be generated.

**Parameters:**

- `self` (Any): No description
- `stage` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cicd/core.py:307`

---

### get_generated_pipelines

Get all generated pipelines.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cicd/core.py:314`

---

### clear_generated_pipelines

Clear generated pipelines.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cicd/core.py:320`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `level` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:24`

---

### debug

Log a debug message.

**Parameters:**

- `self` (Any): No description
- `message` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:30`

---

### info

Log an info message.

**Parameters:**

- `self` (Any): No description
- `message` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:36`

---

### warning

Log a warning message.

**Parameters:**

- `self` (Any): No description
- `message` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:42`

---

### error

Log an error message.

**Parameters:**

- `self` (Any): No description
- `message` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:48`

---

### critical

Log a critical message.

**Parameters:**

- `self` (Any): No description
- `message` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:54`

---

### log

Log a message at the specified level.

**Parameters:**

- `self` (Any): No description
- `level` (Any): No description
- `message` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:60`

---

### bind

Bind context to this logger.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:66`

---

### set_level

Set the logging level.

**Parameters:**

- `self` (Any): No description
- `level` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:72`

---

### add_handler

Add a log handler.

**Parameters:**

- `self` (Any): No description
- `handler` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:78`

---

### remove_handler

Remove a log handler.

**Parameters:**

- `self` (Any): No description
- `handler` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:84`

---

### is_enabled_for

Check if logging is enabled for the given level.

**Parameters:**

- `self` (Any): No description
- `level` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:89`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `level` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:101`

---

### emit

Emit a log record.

**Parameters:**

- `self` (Any): No description
- `record` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:106`

---

### flush

Flush any buffered records.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:114`

---

### close

Close the handler.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:120`

---

### should_emit

Check if the record should be emitted.

**Parameters:**

- `self` (Any): No description
- `record` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:125`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `config` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:137`

---

### format

Format a log record.

**Parameters:**

- `self` (Any): No description
- `record` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:142`

---

### format_exception

Format exception information.

**Parameters:**

- `self` (Any): No description
- `exc_info` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:153`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `config` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:169`

---

### start

Start monitoring.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:175`

---

### stop

Stop monitoring.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:181`

---

### get_metrics

Get current metrics.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:187`

---

### is_healthy

Check if the monitored system is healthy.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:195`

---

### is_running

Check if monitor is running.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:203`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `config` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:215`

---

### increment

Increment a counter metric.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:220`

---

### set

Set a gauge metric.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:230`

---

### observe

Observe a histogram/summary metric.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:240`

---

### get_metrics

Get all collected metrics.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:250`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `config` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:263`

---

### check_health

Perform a health check.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:268`

---

### is_healthy

Check if the system is healthy.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/interfaces.py:276`

---

### __str__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/types.py:24`

---

### from_string

Create LogLevel from string.

**Parameters:**

- `cls` (Any): No description
- `level` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/types.py:28`

---

### to_dict

Convert to dictionary for serialization.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/types.py:55`

---

### merge

Merge with another context.

**Parameters:**

- `self` (Any): No description
- `other` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/types.py:90`

---

### to_dict

Convert to dictionary.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/types.py:104`

---

### __post_init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/types.py:136`

---

### __post_init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/types.py:152`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `message` (Any): No description
- `error_code` (Any): No description
- `details` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/types.py:163`

---

### get_logger

Get or create a logger.

**Parameters:**

- `name` (Any): No description
- `level` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/logger.py:163`

---

### configure_logging

Configure global logging.

**Parameters:**

- `config` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/logger.py:178`

---

### shutdown_logging

Shutdown all loggers and handlers.

**Returns:** `Any`

**File:** `src/pheno/logging/core/logger.py:188`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `level` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/logger.py:21`

---

### debug

Log a debug message.

**Parameters:**

- `self` (Any): No description
- `message` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/logger.py:27`

---

### info

Log an info message.

**Parameters:**

- `self` (Any): No description
- `message` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/logger.py:33`

---

### warning

Log a warning message.

**Parameters:**

- `self` (Any): No description
- `message` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/logger.py:39`

---

### error

Log an error message.

**Parameters:**

- `self` (Any): No description
- `message` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/logger.py:45`

---

### critical

Log a critical message.

**Parameters:**

- `self` (Any): No description
- `message` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/logger.py:51`

---

### log

Log a message at the specified level.

**Parameters:**

- `self` (Any): No description
- `level` (Any): No description
- `message` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/logger.py:57`

---

### bind

Bind context to this logger.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/logger.py:81`

---

### set_level

Set the logging level.

**Parameters:**

- `self` (Any): No description
- `level` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/logger.py:99`

---

### add_handler

Add a log handler.

**Parameters:**

- `self` (Any): No description
- `handler` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/logger.py:105`

---

### remove_handler

Remove a log handler.

**Parameters:**

- `self` (Any): No description
- `handler` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/logger.py:112`

---

### _create_record

Create a log record.

**Parameters:**

- `self` (Any): No description
- `level` (Any): No description
- `message` (Any): No description
- `context` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/logging/core/logger.py:119`

---

### __post_init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/events/core/event_bus.py:24`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/events/core/event_bus.py:48`

---

### on

Decorator to register event handler.

**Parameters:**

- `self` (Any): No description
- `event_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/events/core/event_bus.py:52`

---

### subscribe

Subscribe to events.

**Parameters:**

- `self` (Any): No description
- `event_name` (Any): No description
- `handler` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/events/core/event_bus.py:70`

---

### unsubscribe

Unsubscribe from events.

**Parameters:**

- `self` (Any): No description
- `event_name` (Any): No description
- `handler` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/events/core/event_bus.py:84`

---

### _matches_pattern

Check if event name matches wildcard pattern.

**Parameters:**

- `self` (Any): No description
- `event_name` (Any): No description
- `pattern` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/events/core/event_bus.py:149`

---

### clear

Clear all handlers.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/events/core/event_bus.py:168`

---

### get_handlers

Get handlers for event name.

**Parameters:**

- `self` (Any): No description
- `event_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/events/core/event_bus.py:175`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/events/core/event_bus.py:204`

---

### on

Decorator to register event handler.

**Parameters:**

- `self` (Any): No description
- `event_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/events/core/event_bus.py:207`

---

### subscribe

Subscribe to events.

**Parameters:**

- `self` (Any): No description
- `event_name` (Any): No description
- `handler` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/events/core/event_bus.py:222`

---

### unsubscribe

Unsubscribe from events.

**Parameters:**

- `self` (Any): No description
- `event_name` (Any): No description
- `handler` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/events/core/event_bus.py:233`

---

### publish

Publish event to all subscribers synchronously.

**Parameters:**

- `self` (Any): No description
- `event_name` (Any): No description
- `data` (Any): No description
- `source` (Any): No description
- `correlation_id` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/events/core/event_bus.py:245`

---

### clear

Clear all handlers.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/events/core/event_bus.py:281`

---

### get_handlers

Get handlers for event name.

**Parameters:**

- `self` (Any): No description
- `event_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/events/core/event_bus.py:287`

---

### decorator



**Parameters:**

- `handler` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/events/core/event_bus.py:59`

---

### decorator



**Parameters:**

- `handler` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/events/core/event_bus.py:214`

---

### to_dict

Convert to dictionary.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/events/core/event_store.py:28`

---

### from_dict

Create from dictionary.

**Parameters:**

- `cls` (Any): No description
- `data` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/events/core/event_store.py:35`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `storage_path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/events/core/event_store.py:69`

---

### _load_from_disk

Load events from disk.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/events/core/event_store.py:77`

---

### _get_stream_file

Get file path for aggregate stream.

**Parameters:**

- `self` (Any): No description
- `aggregate_id` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/events/core/event_store.py:91`

---

### __init__

Initialize workflow engine.

**Parameters:**

- `self` (Any): No description
- `orchestrator` (Any): No description
- `persistence` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/workflow/core/engine.py:20`

---

### list_active_workflows

List all active workflows.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/workflow/core/engine.py:164`

---

### workflow

Decorator to mark a class as a workflow.

**Parameters:**

- `cls` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/workflow/core/workflow.py:175`

---

### step

Decorator to mark a method as a workflow step.

**Parameters:**

- `name` (Any): No description
- `inputs` (Any): No description
- `outputs` (Any): No description
- `retry_count` (Any): No description
- `timeout` (Any): No description
- `compensate` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/workflow/core/workflow.py:185`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/workflow/core/workflow.py:88`

---

### _discover_steps

Discover workflow steps from methods.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/workflow/core/workflow.py:96`

---

### decorator



**Parameters:**

- `func` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/workflow/core/workflow.py:197`

---

### __init__

Initialize the hybrid orchestrator.

**Parameters:**

- `self` (Any): No description
- `config` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/workflow/orchestration/core/orchestrator.py:33`

---

### _update_metrics

Update orchestrator performance metrics.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/workflow/orchestration/core/orchestrator.py:327`

---

### get_metrics

Get current orchestrator metrics.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/workflow/orchestration/core/orchestrator.py:343`

---

### __init__

Initialize the agent task manager.

**Parameters:**

- `self` (Any): No description
- `redis_client` (Any): No description
- `agent_manager` (Any): No description
- `max_concurrent_tasks` (Any): No description
- `queue_max_size` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/workflow/orchestration/agents/task_manager/core.py:42`

---

### get_stats

Get manager statistics.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/workflow/orchestration/agents/task_manager/core.py:394`

---

### container



**Returns:** `Any`

**File:** `src/pheno/testing/fixtures/core.py:21`

---

### clean_container



**Returns:** `Any`

**File:** `src/pheno/testing/fixtures/core.py:26`

---

### user_repository



**Returns:** `Any`

**File:** `src/pheno/testing/fixtures/core.py:31`

---

### deployment_repository



**Returns:** `Any`

**File:** `src/pheno/testing/fixtures/core.py:36`

---

### service_repository



**Returns:** `Any`

**File:** `src/pheno/testing/fixtures/core.py:41`

---

### configuration_repository



**Returns:** `Any`

**File:** `src/pheno/testing/fixtures/core.py:46`

---

### event_publisher



**Returns:** `Any`

**File:** `src/pheno/testing/fixtures/core.py:51`

---

### create_user_use_case



**Parameters:**

- `user_repository` (Any): No description
- `event_publisher` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/testing/fixtures/core.py:56`

---

### update_user_use_case



**Parameters:**

- `user_repository` (Any): No description
- `event_publisher` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/testing/fixtures/core.py:63`

---

### get_user_use_case



**Parameters:**

- `user_repository` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/testing/fixtures/core.py:70`

---

### list_users_use_case



**Parameters:**

- `user_repository` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/testing/fixtures/core.py:77`

---

### deactivate_user_use_case



**Parameters:**

- `user_repository` (Any): No description
- `event_publisher` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/testing/fixtures/core.py:84`

---

### cli_adapter



**Parameters:**

- `user_repository` (Any): No description
- `deployment_repository` (Any): No description
- `service_repository` (Any): No description
- `configuration_repository` (Any): No description
- `event_publisher` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/testing/fixtures/core.py:91`

---

### user_commands



**Parameters:**

- `cli_adapter` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/testing/fixtures/core.py:110`

---

### deployment_commands



**Parameters:**

- `cli_adapter` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/testing/fixtures/core.py:117`

---

### service_commands



**Parameters:**

- `cli_adapter` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/testing/fixtures/core.py:124`

---

### configuration_commands



**Parameters:**

- `cli_adapter` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/testing/fixtures/core.py:131`

---

### sample_user_data



**Returns:** `Any`

**File:** `src/pheno/testing/fixtures/core.py:138`

---

### sample_deployment_data



**Returns:** `Any`

**File:** `src/pheno/testing/fixtures/core.py:143`

---

### sample_service_data



**Returns:** `Any`

**File:** `src/pheno/testing/fixtures/core.py:148`

---

### sample_configuration_data



**Returns:** `Any`

**File:** `src/pheno/testing/fixtures/core.py:153`

---

### pytest_configure



**Parameters:**

- `config` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/testing/fixtures/core.py:197`

---

### pytest_collection_modifyitems



**Parameters:**

- `config` (Any): No description
- `items` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/testing/fixtures/core.py:203`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `provider` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/storage/core/client.py:31`

---

### __init__

Initialize monitoring manager.

**Parameters:**

- `self` (Any): No description
- `config` (Any): No description
- `providers` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/observability/monitoring/core.py:90`

---

### _setup_logging

Setup logging configuration.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/observability/monitoring/core.py:114`

---

### add_provider

Add a monitoring provider.

**Parameters:**

- `self` (Any): No description
- `provider` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/observability/monitoring/core.py:292`

---

### remove_provider

Remove a monitoring provider.

**Parameters:**

- `self` (Any): No description
- `provider` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/observability/monitoring/core.py:299`

---

### get_metrics

Get current metrics.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/observability/monitoring/core.py:307`

---

### get_events

Get current events.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/observability/monitoring/core.py:313`

---

### clear_events

Clear events buffer.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/observability/monitoring/core.py:319`

---

### create_default_contexts

Create default context configurations.

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/config.py:177`

---

### load_config

Load configuration from file or create default.

**Parameters:**

- `config_path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/config.py:230`

---

### save_config

Save configuration to file.

**Parameters:**

- `config` (Any): No description
- `config_path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/config.py:267`

---

### get_project_config

Load project-specific configuration if it exists.

**Parameters:**

- `project_path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/config.py:285`

---

### save_project_config

Save project-specific configuration.

**Parameters:**

- `config` (Any): No description
- `project_path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/config.py:301`

---

### expand_workspace_path

Expand user paths in workspace configuration.

**Parameters:**

- `cls` (Any): No description
- `v` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/config.py:95`

---

### get_context

Get a specific context configuration.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/config.py:114`

---

### add_context

Add or update a context configuration.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `config` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/config.py:120`

---

### list_contexts

List all available context names.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/config.py:126`

---

### expand_paths

Expand user paths in configuration.

**Parameters:**

- `cls` (Any): No description
- `v` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/config.py:158`

---

### get_version

Get the current version of pheno-cli.

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/version.py:8`

---

### __init__

Initialize the context detector.

**Parameters:**

- `self` (Any): No description
- `config` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/context_detector.py:17`

---

### detect_from_entry_point

Detect context from command name (atoms, zen, byteport).

**Parameters:**

- `self` (Any): No description
- `argv0` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/context_detector.py:23`

---

### detect_from_project

Detect context from project files and patterns.

**Parameters:**

- `self` (Any): No description
- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/context_detector.py:45`

---

### detect_from_environment

Detect context from environment variables.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/context_detector.py:90`

---

### detect_from_config

Detect context from configuration files.

**Parameters:**

- `self` (Any): No description
- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/context_detector.py:112`

---

### detect_context

Main detection logic with fallbacks.

**Parameters:**

- `self` (Any): No description
- `path` (Any): No description
- `argv0` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/context_detector.py:163`

---

### _matches_pattern

Simple pattern matching with * wildcard support.

**Parameters:**

- `self` (Any): No description
- `text` (Any): No description
- `pattern` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/context_detector.py:193`

---

### __init__

Initialize the context.

**Parameters:**

- `self` (Any): No description
- `verbose` (Any): No description
- `debug` (Any): No description
- `config_path` (Any): No description
- `workspace` (Any): No description
- `context` (Any): No description
- `argv0` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/context.py:17`

---

### workspace

Get the current workspace directory.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/context.py:67`

---

### workspace

Set the workspace directory.

**Parameters:**

- `self` (Any): No description
- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/context.py:74`

---

### templates_dir

Get the templates directory.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/context.py:81`

---

### context_templates_dir

Get the context-specific templates directory.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/context.py:99`

---

### shared_templates_dir

Get the shared templates directory.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/context.py:107`

---

### get_current_project_path

Get the current project path if we're inside one.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/context.py:114`

---

### is_pheno_project

Check if a path is a pheno project.

**Parameters:**

- `self` (Any): No description
- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/context.py:128`

---

### _has_pheno_markers

Check for common pheno project markers.

**Parameters:**

- `self` (Any): No description
- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/context.py:134`

---

### switch_context

Switch to a different context.

**Parameters:**

- `self` (Any): No description
- `context_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/context.py:170`

---

### get_available_contexts

Get all available contexts with descriptions.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/context.py:190`

---

### get_context_info

Get information about the current context.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/core/context.py:198`

---

### add_log

Add a log message to this stage.

**Parameters:**

- `self` (Any): No description
- `message` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/command_engine/core.py:47`

---

### set_error

Set an error for this stage.

**Parameters:**

- `self` (Any): No description
- `error` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/command_engine/core.py:53`

---

### start

Mark stage as started.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/command_engine/core.py:61`

---

### complete

Mark stage as completed.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/command_engine/core.py:69`

---

### duration

Get stage duration in seconds.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/command_engine/core.py:78`

---

### failed_stages

Get stages that failed.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/command_engine/core.py:102`

---

### all_logs

Get all logs from all stages.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/command_engine/core.py:109`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `working_directory` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/command_engine/core.py:126`

---

### add_callback

Add a progress callback.

**Parameters:**

- `self` (Any): No description
- `callback` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/command_engine/core.py:131`

---

### _trigger_callbacks

Trigger all registered callbacks.

**Parameters:**

- `self` (Any): No description
- `stage` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/command_engine/core.py:137`

---

### cancel_command

Cancel a running command.

**Parameters:**

- `self` (Any): No description
- `command_id` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/command_engine/core.py:370`

---

### get_running_commands

Get list of running command IDs.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/command_engine/core.py:381`

---

### cleanup

Clean up any running processes.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/command_engine/core.py:387`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `project_name` (Any): No description
- `config_dir` (Any): No description
- `enable_monitoring` (Any): No description
- `enable_auto_recovery` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/infrastructure/core/manager.py:26`

---

### _initialize_components

Initialize all infrastructure components.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/infrastructure/core/manager.py:62`

---

### _import_components

Import required infrastructure components.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/infrastructure/core/manager.py:74`

---

### _setup_allocators

Setup port and resource allocators.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/infrastructure/core/manager.py:90`

---

### _setup_monitoring_components

Setup monitoring components if enabled.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/infrastructure/core/manager.py:97`

---

### _setup_orchestrator

Setup service orchestrator.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/infrastructure/core/manager.py:105`

---

### _setup_signal_handlers



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/infrastructure/core/manager.py:116`

---

### register_service



**Parameters:**

- `self` (Any): No description
- `config` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/infrastructure/core/manager.py:127`

---

### register_resource



**Parameters:**

- `self` (Any): No description
- `config` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/infrastructure/core/manager.py:136`

---

### get_service_status



**Parameters:**

- `self` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/infrastructure/core/manager.py:190`

---

### get_resource_status



**Parameters:**

- `self` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/infrastructure/core/manager.py:193`

---

### get_status_snapshot



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/infrastructure/core/manager.py:196`

---

### signal_handler



**Parameters:**

- `signum` (Any): No description
- `frame` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/shared/infrastructure/core/manager.py:117`

---

### get_test_registry



**Returns:** `Any`

**File:** `src/pheno/mcp/qa/core/test_registry.py:84`

---

### mcp_test



**Returns:** `Any`

**File:** `src/pheno/mcp/qa/core/test_registry.py:88`

---

### require_auth



**Parameters:**

- `func` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/mcp/qa/core/test_registry.py:124`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/mcp/qa/core/test_registry.py:21`

---

### register



**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `func` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/mcp/qa/core/test_registry.py:24`

---

### get_tests



**Parameters:**

- `self` (Any): No description
- `category` (Any): No description
- `tags` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/mcp/qa/core/test_registry.py:46`

---

### get_by_priority



**Parameters:**

- `self` (Any): No description
- `category` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/mcp/qa/core/test_registry.py:62`

---

### clear



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/mcp/qa/core/test_registry.py:66`

---

### get_stats



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/mcp/qa/core/test_registry.py:69`

---

### decorator



**Parameters:**

- `func` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/mcp/qa/core/test_registry.py:96`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `cache_file` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/mcp/qa/core/cache.py:34`

---

### _environment_signature



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/mcp/qa/core/cache.py:39`

---

### _load



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/mcp/qa/core/cache.py:42`

---

### _persist



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/mcp/qa/core/cache.py:53`

---

### _hash



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/mcp/qa/core/cache.py:64`

---

### should_skip



**Parameters:**

- `self` (Any): No description
- `test_name` (Any): No description
- `tool_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/mcp/qa/core/cache.py:71`

---

### record



**Parameters:**

- `self` (Any): No description
- `test_name` (Any): No description
- `tool_name` (Any): No description
- `status` (Any): No description
- `duration` (Any): No description
- `error` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/mcp/qa/core/cache.py:76`

---

### clear



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/mcp/qa/core/cache.py:91`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `client_adapter` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/mcp/qa/core/base/test_runner.py:25`

---

### _select_tests



**Parameters:**

- `self` (Any): No description
- `categories` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/mcp/qa/core/base/test_runner.py:61`

---

### _summarise



**Parameters:**

- `self` (Any): No description
- `results` (Any): No description
- `duration` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/mcp/qa/core/base/test_runner.py:128`

---

### _get_metadata

Projects provide run-specific metadata for reporting.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/mcp/qa/core/base/test_runner.py:145`

---

### endpoint



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/mcp/qa/core/base/client_adapter.py:35`

---

### get_unified_registry

Get the global unified registry instance.

**Returns:** `Any`

**File:** `src/pheno/providers/registry/core.py:79`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/providers/registry/core.py:26`

---

### register_provider

Register a provider with configuration.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `provider_class` (Any): No description
- `config` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/providers/registry/core.py:30`

---

### get_provider_capabilities

Get provider capabilities.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/providers/registry/core.py:48`

---

### get_authorization_url

Get OAuth authorization URL.

**Parameters:**

- `self` (Any): No description
- `state` (Any): No description
- `scope` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/auth/unified_auth/auth/unified/core/interfaces.py:46`

---

### get_mfa_type

Get the MFA type this provider handles.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/auth/unified_auth/auth/unified/core/interfaces.py:75`

---

### hash_password

Hash a password securely.

**Parameters:**

- `self` (Any): No description
- `password` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/auth/unified_auth/auth/unified/core/interfaces.py:193`

---

### verify_password

Verify a password against its hash.

**Parameters:**

- `self` (Any): No description
- `password` (Any): No description
- `hashed` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/auth/unified_auth/auth/unified/core/interfaces.py:200`

---

### generate_token

Generate a JWT token.

**Parameters:**

- `self` (Any): No description
- `payload` (Any): No description
- `expires_in` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/auth/unified_auth/auth/unified/core/interfaces.py:207`

---

### validate_token

Validate and decode a JWT token.

**Parameters:**

- `self` (Any): No description
- `token` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/auth/unified_auth/auth/unified/core/interfaces.py:214`

---

### has_role

Check if user has a specific role.

**Parameters:**

- `self` (Any): No description
- `role` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/auth/unified_auth/auth/unified/core/types.py:65`

---

### has_permission

Check if user has a specific permission.

**Parameters:**

- `self` (Any): No description
- `permission` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/auth/unified_auth/auth/unified/core/types.py:71`

---

### has_mfa_type

Check if user has MFA of specific type enabled.

**Parameters:**

- `self` (Any): No description
- `mfa_type` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/auth/unified_auth/auth/unified/core/types.py:77`

---

### is_expired

Check if token is expired.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/auth/unified_auth/auth/unified/core/types.py:106`

---

### time_until_expiry

Get seconds until expiry.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/auth/unified_auth/auth/unified/core/types.py:114`

---

### is_expired

Check if session is expired.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/auth/unified_auth/auth/unified/core/types.py:146`

---

### extend

Extend session by specified minutes.

**Parameters:**

- `self` (Any): No description
- `minutes` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/auth/unified_auth/auth/unified/core/types.py:154`

---

### invalidate

Invalidate the session.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/auth/unified_auth/auth/unified/core/types.py:162`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `providers` (Any): No description
- `mfa_providers` (Any): No description
- `session_provider` (Any): No description
- `default_provider` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/auth/unified_auth/auth/unified/core/manager.py:32`

---

### register_provider

Register an authentication provider.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `provider` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/auth/unified_auth/auth/unified/core/manager.py:47`

---

### register_mfa_provider

Register an MFA provider.

**Parameters:**

- `self` (Any): No description
- `mfa_type` (Any): No description
- `provider` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/auth/unified_auth/auth/unified/core/manager.py:54`

---

### set_session_provider

Set the session provider.

**Parameters:**

- `self` (Any): No description
- `provider` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/auth/unified_auth/auth/unified/core/manager.py:61`

---

### get_oauth_provider

Get OAuth provider.

**Parameters:**

- `self` (Any): No description
- `provider_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/auth/unified_auth/auth/unified/core/manager.py:221`

---

### create_oauth_state

Create OAuth state for CSRF protection.

**Parameters:**

- `self` (Any): No description
- `state` (Any): No description
- `metadata` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/auth/unified_auth/auth/unified/core/manager.py:230`

---

### validate_oauth_state

Validate OAuth state.

**Parameters:**

- `self` (Any): No description
- `state` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/auth/unified_auth/auth/unified/core/manager.py:236`

---

### get_oauth_authorization_url

Get OAuth authorization URL.

**Parameters:**

- `self` (Any): No description
- `provider_name` (Any): No description
- `redirect_uri` (Any): No description
- `scope` (Any): No description
- `state` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/auth/unified_auth/auth/unified/core/manager.py:250`

---

### _read_dotenv_values

Read dotenv values from .env file.

**Returns:** `Any`

**File:** `src/pheno/core/utils/env.py:25`

---

### _compute_force_override

Compute if force override is enabled.

**Parameters:**

- `values` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/utils/env.py:35`

---

### reload_env

Reload .env values and recompute override semantics.

**Parameters:**

- `dotenv_mapping` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/utils/env.py:43`

---

### env_override_enabled

Return True when ZEN_MCP_FORCE_ENV_OVERRIDE is enabled via the .env file.

**Returns:** `Any`

**File:** `src/pheno/core/utils/env.py:71`

---

### get_env

Retrieve environment variables respecting ZEN_MCP_FORCE_ENV_OVERRIDE.

**Parameters:**

- `key` (Any): No description
- `default` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/utils/env.py:78`

---

### get_env_bool

Boolean helper that respects override semantics.

**Parameters:**

- `key` (Any): No description
- `default` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/utils/env.py:97`

---

### get_all_env

Expose the loaded .env mapping for diagnostics/logging.

**Returns:** `Any`

**File:** `src/pheno/core/utils/env.py:112`

---

### suppress_env_vars

Temporarily remove environment variables during the context.

**Returns:** `Any`

**File:** `src/pheno/core/utils/env.py:120`

---

### get_restriction_service

Get the global restriction service instance.

**Returns:** `Any`

**File:** `src/pheno/core/utils/model_restrictions.py:154`

---

### __init__

Initialize the restriction service by loading from environment.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/utils/model_restrictions.py:53`

---

### _load_from_env

Load restrictions from environment variables.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/utils/model_restrictions.py:61`

---

### is_allowed

Check if a model is allowed for a given provider.

**Parameters:**

- `self` (Any): No description
- `provider_type` (Any): No description
- `model_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/utils/model_restrictions.py:94`

---

### filter_models

Filter a list of models to only those allowed for the provider.

**Parameters:**

- `self` (Any): No description
- `provider_type` (Any): No description
- `models` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/utils/model_restrictions.py:111`

---

### get_restricted_models

Get the set of restricted (allowed) models for a provider.

**Parameters:**

- `self` (Any): No description
- `provider_type` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/utils/model_restrictions.py:127`

---

### has_restrictions

Check if there are any restrictions for a provider.

**Parameters:**

- `self` (Any): No description
- `provider_type` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/utils/model_restrictions.py:138`

---

### get_env



**Parameters:**

- `key` (Any): No description
- `default` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/utils/__init__.py:13`

---

### get_env_bool



**Parameters:**

- `key` (Any): No description
- `default` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/utils/__init__.py:16`

---

### env_override_enabled



**Returns:** `Any`

**File:** `src/pheno/core/utils/__init__.py:21`

---

### reload_env



**Returns:** `Any`

**File:** `src/pheno/core/utils/__init__.py:24`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/provider.py:25`

---

### register_provider



**Parameters:**

- `self` (Any): No description
- `provider_type` (Any): No description
- `provider_class` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/provider.py:30`

---

### get_provider



**Parameters:**

- `self` (Any): No description
- `provider_type` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/provider.py:46`

---

### _create_provider_instance



**Parameters:**

- `self` (Any): No description
- `provider_class` (Any): No description
- `provider_type` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/provider.py:65`

---

### get_providers_by_priority



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/provider.py:68`

---

### clear_instances



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/provider.py:74`

---

### get_tool_registry



**Returns:** `Any`

**File:** `src/pheno/core/registry/globals.py:16`

---

### get_provider_registry



**Returns:** `Any`

**File:** `src/pheno/core/registry/globals.py:20`

---

### get_plugin_registry



**Returns:** `Any`

**File:** `src/pheno/core/registry/globals.py:24`

---

### register_tool



**Parameters:**

- `name` (Any): No description
- `tool` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/globals.py:28`

---

### get_tool



**Parameters:**

- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/globals.py:32`

---

### list_tools



**Parameters:**

- `prefix` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/globals.py:36`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/base.py:39`

---

### register



**Parameters:**

- `self` (Any): No description
- `key` (Any): No description
- `item` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/base.py:45`

---

### get



**Parameters:**

- `self` (Any): No description
- `key` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/base.py:66`

---

### get_with_metadata



**Parameters:**

- `self` (Any): No description
- `key` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/base.py:72`

---

### list



**Parameters:**

- `self` (Any): No description
- `prefix` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/base.py:78`

---

### unregister



**Parameters:**

- `self` (Any): No description
- `key` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/base.py:87`

---

### clear



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/base.py:95`

---

### load_entry_points



**Parameters:**

- `self` (Any): No description
- `group` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/base.py:100`

---

### __len__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/base.py:118`

---

### __contains__



**Parameters:**

- `self` (Any): No description
- `key` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/base.py:122`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/adapters/plugins.py:19`

---

### register



**Parameters:**

- `self` (Any): No description
- `adapter_type` (Any): No description
- `name` (Any): No description
- `plugin` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/adapters/plugins.py:22`

---

### get



**Parameters:**

- `self` (Any): No description
- `adapter_type` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/adapters/plugins.py:26`

---

### clear



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/adapters/plugins.py:30`

---

### get_adapter_registry



**Returns:** `Any`

**File:** `src/pheno/core/registry/adapters/registry.py:246`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/adapters/registry.py:27`

---

### register_adapter



**Parameters:**

- `self` (Any): No description
- `adapter_type` (Any): No description
- `name` (Any): No description
- `adapter_class` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/adapters/registry.py:37`

---

### register_plugin



**Parameters:**

- `self` (Any): No description
- `adapter_type` (Any): No description
- `name` (Any): No description
- `plugin` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/adapters/registry.py:81`

---

### get_adapter_class



**Parameters:**

- `self` (Any): No description
- `adapter_type` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/adapters/registry.py:84`

---

### create_adapter_instance



**Parameters:**

- `self` (Any): No description
- `adapter_type` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/adapters/registry.py:93`

---

### resolve_adapter



**Parameters:**

- `self` (Any): No description
- `adapter_type` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/adapters/registry.py:146`

---

### resolve_many



**Parameters:**

- `self` (Any): No description
- `adapter_type` (Any): No description
- `names` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/adapters/registry.py:149`

---

### list_adapters



**Parameters:**

- `self` (Any): No description
- `adapter_type` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/adapters/registry.py:152`

---

### get_adapter_types



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/adapters/registry.py:156`

---

### get_adapters_by_priority



**Parameters:**

- `self` (Any): No description
- `adapter_type` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/adapters/registry.py:160`

---

### register_callback



**Parameters:**

- `self` (Any): No description
- `key` (Any): No description
- `callback` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/adapters/registry.py:193`

---

### trigger_callbacks



**Parameters:**

- `self` (Any): No description
- `key` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/adapters/registry.py:196`

---

### autodiscover



**Parameters:**

- `self` (Any): No description
- `package` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/adapters/registry.py:208`

---

### get_metrics



**Parameters:**

- `self` (Any): No description
- `adapter_type` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/adapters/registry.py:232`

---

### _instance_key



**Parameters:**

- `self` (Any): No description
- `adapter_type` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/core/registry/adapters/registry.py:239`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `service_infra` (Any): No description
- `enable_fallback_layer` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/service_manager/manager/core.py:39`

---

### emit_stage



**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `text` (Any): No description
- `status` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/service_manager/manager/core.py:108`

---

### emit_status



**Parameters:**

- `self` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/service_manager/manager/core.py:119`

---

### emit_and_log



**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `text` (Any): No description
- `status` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/service_manager/manager/core.py:122`

---

### _publish_status



**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `payload` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/service_manager/manager/core.py:126`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `port` (Any): No description
- `templates_dir` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/fallback_site/server/core.py:33`

---

### attach_service_manager

Bind a service manager for restart/stop actions.

**Parameters:**

- `self` (Any): No description
- `manager` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/fallback_site/server/core.py:55`

---

### set_page

Update the current fallback page metadata.

**Parameters:**

- `self` (Any): No description
- `page_type` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/fallback_site/server/core.py:90`

---

### update_service_status

Persist service status details for display.

**Parameters:**

- `self` (Any): No description
- `service_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/fallback_site/server/core.py:105`

---

### remove_services_with_prefix

Remove tracked services that match a prefix.

**Parameters:**

- `self` (Any): No description
- `prefix` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/fallback_site/server/core.py:111`

---

### _register_routes

Configure aiohttp routes for public and admin endpoints.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/fallback_site/server/core.py:117`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `proxy_port` (Any): No description
- `fallback_port` (Any): No description
- `default_upstream_port` (Any): No description
- `fallback_server` (Any): No description
- `middleware` (Any): No description
- `templates_dir` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/proxy_gateway/server/core.py:31`

---

### app

Expose the aiohttp application for external customization.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/proxy_gateway/server/core.py:71`

---

### _configure_routes



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/proxy_gateway/server/core.py:77`

---

### add_upstream

Register an upstream service.

**Parameters:**

- `self` (Any): No description
- `path_prefix` (Any): No description
- `port` (Any): No description
- `host` (Any): No description
- `service_name` (Any): No description
- `tenant` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/proxy_gateway/server/core.py:84`

---

### remove_upstream



**Parameters:**

- `self` (Any): No description
- `path_prefix` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/proxy_gateway/server/core.py:106`

---

### set_service_starting



**Parameters:**

- `self` (Any): No description
- `service_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/proxy_gateway/server/core.py:112`

---

### set_service_running



**Parameters:**

- `self` (Any): No description
- `service_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/proxy_gateway/server/core.py:116`

---

### set_service_error



**Parameters:**

- `self` (Any): No description
- `service_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/proxy_gateway/server/core.py:120`

---

### enable_maintenance



**Parameters:**

- `self` (Any): No description
- `message` (Any): No description
- `estimated_duration` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/proxy_gateway/server/core.py:124`

---

### disable_maintenance



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/proxy_gateway/server/core.py:130`

---

### _register_health_check



**Parameters:**

- `self` (Any): No description
- `service_name` (Any): No description
- `upstream` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/proxy_gateway/server/core.py:172`

---

### _unregister_health_check



**Parameters:**

- `self` (Any): No description
- `service_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/proxy_gateway/server/core.py:181`

---

### __init__

Wrap the provided adapter with the high-level Database facade.

**Parameters:**

- `self` (Any): No description
- `adapter` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/database/core/engine.py:11`

---

### from_

Query table.

**Parameters:**

- `self` (Any): No description
- `table` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/database/core/engine.py:19`

---

### invalidate_dependents

Invalidate all computed properties that depend on a given property.

**Parameters:**

- `property_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_bindings.py:149`

---

### reactive_property

Decorator for creating reactive properties.

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_bindings.py:167`

---

### computed_property

Decorator for creating computed properties.

**Parameters:**

- `func` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_bindings.py:181`

---

### create_reactive_proxy

Create a reactive proxy for an object with specified properties.

**Parameters:**

- `obj` (Any): No description
- `properties` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_bindings.py:200`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `func` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_bindings.py:43`

---

### __get__



**Parameters:**

- `self` (Any): No description
- `obj` (Any): No description
- `objtype` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_bindings.py:50`

---

### invalidate

Invalidate cached value for an object.

**Parameters:**

- `self` (Any): No description
- `obj` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_bindings.py:64`

---

### clear_cache

Clear all cached values.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_bindings.py:71`

---

### get_dependencies

Get detected dependencies for an object.

**Parameters:**

- `self` (Any): No description
- `obj` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_bindings.py:78`

---

### _track_dependency

Track a dependency during computation.

**Parameters:**

- `self` (Any): No description
- `dependency_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_bindings.py:84`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_bindings.py:103`

---

### start_tracking

Start tracking dependencies for a computation.

**Parameters:**

- `self` (Any): No description
- `computed_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_bindings.py:107`

---

### end_tracking

End tracking and store dependencies.

**Parameters:**

- `self` (Any): No description
- `computed_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_bindings.py:113`

---

### track_dependency

Track access to a reactive property.

**Parameters:**

- `self` (Any): No description
- `property_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_bindings.py:120`

---

### get_dependencies

Get tracked dependencies for a computation.

**Parameters:**

- `self` (Any): No description
- `computed_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_bindings.py:126`

---

### clear_dependencies

Clear dependencies for a computation.

**Parameters:**

- `self` (Any): No description
- `computed_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_bindings.py:132`

---

### get_all_dependencies

Get all tracked dependencies.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_bindings.py:138`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `target` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_bindings.py:213`

---

### __getattr__



**Parameters:**

- `self` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_bindings.py:216`

---

### __setattr__



**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_bindings.py:226`

---

### load_config

Convenience helper returning a configured :class:`ConfigManager`.

**Parameters:**

- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_manager.py:340`

---

### create_example_config

Generate an example configuration YAML file.

**Parameters:**

- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_manager.py:350`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_manager.py:32`

---

### _register_default_migrations

Seed the migration registry with built-in upgrades.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_manager.py:50`

---

### load_defaults

Populate defaults from :class:`ConfigSchema`.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_manager.py:66`

---

### load_config

Load configuration from ``path`` and optionally override the profile.

**Parameters:**

- `self` (Any): No description
- `path` (Any): No description
- `profile` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_manager.py:76`

---

### load_user_config

Merge a user-level configuration file.

**Parameters:**

- `self` (Any): No description
- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_manager.py:104`

---

### load_project_config

Alias for :meth:`load_config` for API parity.

**Parameters:**

- `self` (Any): No description
- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_manager.py:120`

---

### _merge_configs

Rebuild the merged configuration snapshot honoring precedence.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_manager.py:127`

---

### _deep_merge



**Parameters:**

- `self` (Any): No description
- `base` (Any): No description
- `override` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_manager.py:139`

---

### get

Return the value for ``key`` using dot notation.

**Parameters:**

- `self` (Any): No description
- `key` (Any): No description
- `default` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_manager.py:146`

---

### set

Store ``value`` at ``key`` (runtime override).

**Parameters:**

- `self` (Any): No description
- `key` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_manager.py:160`

---

### get_all

Return a deep copy of the merged configuration.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_manager.py:174`

---

### save

Persist the merged configuration to disk.

**Parameters:**

- `self` (Any): No description
- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_manager.py:182`

---

### validate

Validate the merged configuration against the schema.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_manager.py:199`

---

### switch_profile

Switch to ``profile`` and apply predefined overrides.

**Parameters:**

- `self` (Any): No description
- `profile` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_manager.py:213`

---

### enable_hot_reload

Start watching the active config file for changes.

**Parameters:**

- `self` (Any): No description
- `callback` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_manager.py:231`

---

### disable_hot_reload

Stop the file watcher if it is running.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_manager.py:251`

---

### _on_file_changed



**Parameters:**

- `self` (Any): No description
- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_manager.py:262`

---

### export_schema

Write the JSON schema for the configuration to ``path``.

**Parameters:**

- `self` (Any): No description
- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_manager.py:277`

---

### export_example

Write an example YAML configuration to ``path``.

**Parameters:**

- `self` (Any): No description
- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_manager.py:287`

---

### __del__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_manager.py:336`

---

### migrate_1_0_to_1_1



**Parameters:**

- `payload` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_manager.py:55`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `callback` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_file_watcher.py:19`

---

### on_modified



**Parameters:**

- `self` (Any): No description
- `event` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_file_watcher.py:25`

---

### validate_name



**Parameters:**

- `cls` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_schemas.py:26`

---

### validate_backend



**Parameters:**

- `cls` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_schemas.py:45`

---

### validate_level



**Parameters:**

- `cls` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_schemas.py:65`

---

### validate_secret_key



**Parameters:**

- `cls` (Any): No description
- `value` (Any): No description
- `values` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_schemas.py:87`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_migration.py:19`

---

### register

Register a migration function.

**Parameters:**

- `self` (Any): No description
- `from_version` (Any): No description
- `to_version` (Any): No description
- `migration` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_migration.py:22`

---

### migrate

Apply a chain of migrations to reach ``to_version``.

**Parameters:**

- `self` (Any): No description
- `payload` (Any): No description
- `from_version` (Any): No description
- `to_version` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_migration.py:35`

---

### _find_path

Return the shortest migration path via breadth-first search.

**Parameters:**

- `self` (Any): No description
- `start` (Any): No description
- `target` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_migration.py:62`

---

### get_version_history

Return a sorted list of all known schema versions.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_migration.py:85`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `persistence_file` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:55`

---

### _initialize_state_containers

Initialize all state storage containers.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:61`

---

### _initialize_locks_and_transactions

Initialize thread safety and transaction state.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:71`

---

### _load_persisted_state

Load persisted state from file if available.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:78`

---

### get_state

Get state value using dot notation.

**Parameters:**

- `self` (Any): No description
- `path` (Any): No description
- `default` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:91`

---

### set_state

Set state value using dot notation.

**Parameters:**

- `self` (Any): No description
- `path` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:103`

---

### subscribe

Subscribe to state changes matching a pattern.

**Parameters:**

- `self` (Any): No description
- `pattern` (Any): No description
- `callback` (Any): No description
- `priority` (Any): No description
- `weak` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:119`

---

### unsubscribe

Unsubscribe from state changes.

**Parameters:**

- `self` (Any): No description
- `pattern` (Any): No description
- `callback_or_id` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:136`

---

### transaction

Context manager for atomic state updates.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:147`

---

### undo

Undo the last state change.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:158`

---

### redo

Redo the last undone state change.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:172`

---

### get_history

Get the history of state changes.

**Parameters:**

- `self` (Any): No description
- `limit` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:186`

---

### persist_state

Persist current state to file.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:200`

---

### get_all_state

Get a copy of the entire state.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:217`

---

### clear_state

Clear all state and history.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:223`

---

### _get_nested_value

Get value from nested dictionary using dot notation.

**Parameters:**

- `self` (Any): No description
- `data` (Any): No description
- `path` (Any): No description
- `default` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:233`

---

### _set_nested_value

Set value in nested dictionary using dot notation.

**Parameters:**

- `self` (Any): No description
- `data` (Any): No description
- `path` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:247`

---

### _delete_nested_value

Delete value from nested dictionary using dot notation.

**Parameters:**

- `self` (Any): No description
- `data` (Any): No description
- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:261`

---

### _apply_change

Apply a state change and notify observers.

**Parameters:**

- `self` (Any): No description
- `change` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:276`

---

### _notify_observers

Notify observers of state change.

**Parameters:**

- `self` (Any): No description
- `change` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:284`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `store` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:305`

---

### __enter__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:309`

---

### __exit__



**Parameters:**

- `self` (Any): No description
- `exc_type` (Any): No description
- `exc_val` (Any): No description
- `exc_tb` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:314`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:344`

---

### _discover_reactive_properties

Discover reactive properties on the widget.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:348`

---

### _on_property_changed

Handle reactive property changes.

**Parameters:**

- `self` (Any): No description
- `old_value` (Any): No description
- `new_value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:360`

---

### refresh

Refresh the widget display.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:367`

---

### enable_auto_refresh

Enable or disable automatic refresh on property changes.

**Parameters:**

- `self` (Any): No description
- `enabled` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:375`

---

### get_reactive_properties

Get list of reactive property names.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/textual_integrations.py:381`

---

### __str__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/config_profiles.py:18`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `descriptor` (Any): No description
- `obj` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_primitives.py:23`

---

### value

Get the current value.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_primitives.py:30`

---

### set

Set the value with validation and notification.

**Parameters:**

- `self` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_primitives.py:36`

---

### _debounced_notify

Notify observers with debouncing.

**Parameters:**

- `self` (Any): No description
- `old_value` (Any): No description
- `new_value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_primitives.py:64`

---

### subscribe

Subscribe to changes in this property.

**Parameters:**

- `self` (Any): No description
- `callback` (Any): No description
- `priority` (Any): No description
- `weak` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_primitives.py:77`

---

### unsubscribe

Unsubscribe from changes in this property.

**Parameters:**

- `self` (Any): No description
- `callback_or_id` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_primitives.py:83`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `default` (Any): No description
- `validator` (Any): No description
- `debounce` (Any): No description
- `layout` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_primitives.py:116`

---

### __set_name__



**Parameters:**

- `self` (Any): No description
- `owner` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_primitives.py:131`

---

### __get__



**Parameters:**

- `self` (Any): No description
- `obj` (Any): No description
- `objtype` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_primitives.py:135`

---

### __set__



**Parameters:**

- `self` (Any): No description
- `obj` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_primitives.py:144`

---

### get_change_history

Get the history of changes for this property.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_primitives.py:151`

---

### clear_history

Clear the change history.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/reactive_primitives.py:157`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/observer/observer_pattern.py:39`

---

### subscribe

Subscribe to notifications.

**Parameters:**

- `self` (Any): No description
- `callback` (Any): No description
- `priority` (Any): No description
- `weak` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/observer/observer_pattern.py:45`

---

### unsubscribe

Unsubscribe from notifications.

**Parameters:**

- `self` (Any): No description
- `callback_or_id` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/observer/observer_pattern.py:79`

---

### notify_sync

Synchronous notification (blocks until all observers called).

**Parameters:**

- `self` (Any): No description
- `old_value` (Any): No description
- `new_value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/observer/observer_pattern.py:135`

---

### _cleanup_dead_ref

Clean up dead weak reference.

**Parameters:**

- `self` (Any): No description
- `sub_id` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/observer/observer_pattern.py:166`

---

### clear

Remove all observers.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/observer/observer_pattern.py:176`

---

### observer_count

Get number of active observers.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/observer/observer_pattern.py:184`

---

### invert

Create an inverted change for undo operations.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/state/state_management.py:23`

---

### commit

Mark transaction as committed.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/state/state_management.py:47`

---

### rollback

Get inverted changes for rollback.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/state/state_management.py:54`

---

### on_create

Invoked once after a component mounts and completes initialization.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/mixins.py:21`

---

### on_destroy

Executed during teardown just before the component is unmounted.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/mixins.py:26`

---

### on_show

Called when the component transitions from hidden to visible.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/mixins.py:31`

---

### on_hide

Called when the component transitions from visible to hidden.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/mixins.py:36`

---

### on_focus

Trigger fired when the component gains input focus.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/mixins.py:41`

---

### on_blur

Trigger fired when the component loses input focus.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/mixins.py:46`

---

### on_resize

React to layout recalculations that change the component's size.

**Parameters:**

- `self` (Any): No description
- `size` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/mixins.py:51`

---

### on_move

Respond to positional changes in the layout.

**Parameters:**

- `self` (Any): No description
- `offset` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/mixins.py:56`

---

### handle_click

Process pointer click interactions.

**Parameters:**

- `self` (Any): No description
- `event` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/mixins.py:67`

---

### handle_key

Process keyboard events such as key presses and releases.

**Parameters:**

- `self` (Any): No description
- `event` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/mixins.py:72`

---

### handle_mouse

Process low-level mouse events (move, wheel, etc.).

**Parameters:**

- `self` (Any): No description
- `event` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/mixins.py:77`

---

### handle_focus

Respond to focus events dispatched by the UI framework.

**Parameters:**

- `self` (Any): No description
- `event` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/mixins.py:82`

---

### handle_blur

Respond to blur events dispatched by the UI framework.

**Parameters:**

- `self` (Any): No description
- `event` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/mixins.py:87`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/mixins.py:98`

---

### subscribe_to_state

Register a callback that runs whenever a state key changes.

**Parameters:**

- `self` (Any): No description
- `callback` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/mixins.py:102`

---

### unsubscribe_from_state

Remove a previously registered state change callback.

**Parameters:**

- `self` (Any): No description
- `callback` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/mixins.py:108`

---

### set_state

Update a single state key and notify subscribers of the change.

**Parameters:**

- `self` (Any): No description
- `key` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/mixins.py:115`

---

### update_state

Apply multiple state mutations and emit notifications per key.

**Parameters:**

- `self` (Any): No description
- `data` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/mixins.py:128`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/mixins.py:141`

---

### register_plugin

Register or replace a plugin implementation.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `plugin` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/mixins.py:145`

---

### unregister_plugin

Remove a plugin from the component.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/mixins.py:151`

---

### get_plugin

Retrieve a plugin instance by name.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/mixins.py:158`

---

### has_plugin

Determine whether a plugin has been registered.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/mixins.py:164`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/textual.py:17`

---

### compose



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/textual.py:21`

---

### on_mount



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/textual.py:24`

---

### on_unmount



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/textual.py:27`

---

### refresh



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/textual.py:30`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/textual.py:39`

---

### compose



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/textual.py:43`

---

### compose



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/textual.py:53`

---

### compose



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/textual.py:61`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/events.py:15`

---

### __call__



**Parameters:**

- `self` (Any): No description
- `event` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/events.py:23`

---

### reactive



**Parameters:**

- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/environment.py:21`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/composite.py:19`

---

### compose



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/composite.py:26`

---

### on_mount



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/composite.py:29`

---

### on_unmount



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/composite.py:33`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/composite.py:45`

---

### compose



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/composite.py:52`

---

### on_mount



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/composite.py:55`

---

### on_unmount



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/composite.py:59`

---

### create_component

Instantiate a component while forwarding constructor kwargs.

**Parameters:**

- `component_class` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/helpers.py:13`

---

### mount_component

Convenience helper that calls :meth:`BaseComponent.mount`.

**Parameters:**

- `component` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/helpers.py:20`

---

### unmount_component

Convenience helper that calls :meth:`BaseComponent.unmount`.

**Parameters:**

- `component` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/helpers.py:27`

---

### component_lifecycle

Context manager that mounts a component for the duration of the block.

**Parameters:**

- `component` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/helpers.py:35`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/base.py:27`

---

### compose

Produce the widget tree rendered by the component.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/base.py:36`

---

### mount

Transition the component into the mounted state and invoke hooks.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/base.py:42`

---

### unmount

Gracefully tear down the component and trigger unmount hooks.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/base.py:58`

---

### on_mount

Lifecycle hook invoked after the component has been mounted.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/base.py:74`

---

### on_unmount

Lifecycle hook triggered before the component is removed.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/base.py:79`

---

### add_child

Attach a child component to this component.

**Parameters:**

- `self` (Any): No description
- `child` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/base.py:84`

---

### remove_child

Remove a previously attached child component.

**Parameters:**

- `self` (Any): No description
- `child` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/base.py:92`

---

### emit_event

Dispatch an event to all registered handlers for ``event_type``.

**Parameters:**

- `self` (Any): No description
- `event_type` (Any): No description
- `event` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/base.py:100`

---

### add_event_handler

Register an event handler for a specific event category.

**Parameters:**

- `self` (Any): No description
- `event_type` (Any): No description
- `handler` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/base.py:111`

---

### remove_event_handler

Unregister a previously registered event handler.

**Parameters:**

- `self` (Any): No description
- `event_type` (Any): No description
- `handler` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/base.py:117`

---

### get_state

Convenience proxy to :class:`ComponentStateStore.get`.

**Parameters:**

- `self` (Any): No description
- `key` (Any): No description
- `default` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/base.py:126`

---

### set_state

Proxy to :class:`ComponentStateStore.set` for ergonomic overrides.

**Parameters:**

- `self` (Any): No description
- `key` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/base.py:132`

---

### update_state

Merge multiple state values at once.

**Parameters:**

- `self` (Any): No description
- `data` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/base.py:138`

---

### get

Fetch a stored value, returning ``default`` when missing.

**Parameters:**

- `self` (Any): No description
- `key` (Any): No description
- `default` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/state.py:21`

---

### set

Persist a value and bump the version counter.

**Parameters:**

- `self` (Any): No description
- `key` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/state.py:27`

---

### update

Merge multiple values into the state.

**Parameters:**

- `self` (Any): No description
- `data` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/state.py:34`

---

### clear

Reset stored values and increment the version.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/components/state.py:41`

---

### to_dict



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/theme.py:28`

---

### from_dict



**Parameters:**

- `cls` (Any): No description
- `data` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/theme.py:39`

---

### from_base_color

Generate a complete palette from a base color.

**Parameters:**

- `cls` (Any): No description
- `base_color` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/palette.py:33`

---

### get_color

Get color by name, falling back to the primary color.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/palette.py:71`

---

### to_dict

Convert palette to dictionary of hex strings.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/palette.py:77`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/engine.py:18`

---

### add_theme

Add a theme to the engine.

**Parameters:**

- `self` (Any): No description
- `theme` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/engine.py:24`

---

### set_theme

Set the current theme.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/engine.py:30`

---

### add_rule

Add a style rule.

**Parameters:**

- `self` (Any): No description
- `selector` (Any): No description
- `properties` (Any): No description
- `source_order` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/engine.py:39`

---

### resolve

Resolve styles for an element using cascade.

**Parameters:**

- `self` (Any): No description
- `element` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/engine.py:52`

---

### _matches_selector

Check if selector matches element and context.

**Parameters:**

- `self` (Any): No description
- `selector` (Any): No description
- `element` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/engine.py:88`

---

### _apply_theme_colors

Apply theme colors to properties.

**Parameters:**

- `self` (Any): No description
- `properties` (Any): No description
- `theme` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/engine.py:104`

---

### clear_cache

Clear the style cache.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/engine.py:119`

---

### export_theme

Export theme as dictionary.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/engine.py:125`

---

### import_theme

Import theme from dictionary.

**Parameters:**

- `self` (Any): No description
- `data` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/engine.py:133`

---

### apply_high_contrast



**Parameters:**

- `theme` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/accessibility.py:33`

---

### apply_colorblind_support



**Parameters:**

- `theme` (Any): No description
- `colorblind_type` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/accessibility.py:41`

---

### apply_reduced_motion



**Parameters:**

- `theme` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/accessibility.py:71`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `inline` (Any): No description
- `ids` (Any): No description
- `classes` (Any): No description
- `elements` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/cascade.py:16`

---

### __lt__

Compare specificities.

**Parameters:**

- `self` (Any): No description
- `other` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/cascade.py:22`

---

### __eq__

Check if specificities are equal.

**Parameters:**

- `self` (Any): No description
- `other` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/cascade.py:33`

---

### from_selector

Calculate specificity from CSS selector.

**Parameters:**

- `cls` (Any): No description
- `selector` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/cascade.py:45`

---

### __post_init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/cascade.py:70`

---

### prevent_default

Mark the event as having its default action prevented.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/models.py:31`

---

### stop_propagation

Stop further propagation after current handlers.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/models.py:38`

---

### stop_immediate_propagation

Alias for stop_propagation to match DOM semantics.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/models.py:44`

---

### to_dict

Serialize the event to a dictionary.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/models.py:50`

---

### from_dict

Deserialize an event from a dictionary.

**Parameters:**

- `cls` (Any): No description
- `payload` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/models.py:68`

---

### detect_format



**Parameters:**

- `text` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/formatters.py:20`

---

### format_json



**Parameters:**

- `text` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/formatters.py:33`

---

### format_exception



**Parameters:**

- `text` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/formatters.py:49`

---

### format_structured



**Parameters:**

- `text` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/formatters.py:66`

---

### highlight_urls



**Parameters:**

- `text` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/formatters.py:83`

---

### format_rich



**Parameters:**

- `self` (Any): No description
- `show_timestamp` (Any): No description
- `show_level` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/models.py:29`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `callback` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/handlers.py:16`

---

### emit



**Parameters:**

- `self` (Any): No description
- `record` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/handlers.py:20`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `original_stream` (Any): No description
- `callback` (Any): No description
- `source` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/writers.py:14`

---

### write



**Parameters:**

- `self` (Any): No description
- `text` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/writers.py:23`

---

### flush



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/writers.py:37`

---

### capture_output



**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/manager.py:191`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/manager.py:24`

---

### _append_line



**Parameters:**

- `self` (Any): No description
- `line` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/manager.py:52`

---

### _on_line_captured



**Parameters:**

- `self` (Any): No description
- `text` (Any): No description
- `source` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/manager.py:58`

---

### _on_log_captured



**Parameters:**

- `self` (Any): No description
- `line` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/manager.py:62`

---

### start



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/manager.py:65`

---

### stop



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/manager.py:89`

---

### __enter__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/manager.py:108`

---

### __exit__



**Parameters:**

- `self` (Any): No description
- `exc_type` (Any): No description
- `exc_val` (Any): No description
- `exc_tb` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/manager.py:112`

---

### get_lines



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/manager.py:115`

---

### get_text



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/manager.py:133`

---

### clear



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/manager.py:144`

---

### export



**Parameters:**

- `self` (Any): No description
- `filepath` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/stream_capture/manager.py:148`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `event_bus` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/propagation/propagation.py:19`

---

### set_propagation_path

Set the ordered path for propagation (target last).

**Parameters:**

- `self` (Any): No description
- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/propagation/propagation.py:26`

---

### propagate_event

Dispatch an event through capture, target, and bubble phases.

**Parameters:**

- `self` (Any): No description
- `event` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/propagation/propagation.py:35`

---

### __call__

Handle a dispatched event.

**Parameters:**

- `self` (Any): No description
- `event` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/handlers/handlers.py:19`

---

### __lt__



**Parameters:**

- `self` (Any): No description
- `other` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/handlers/handlers.py:49`

---

### __gt__



**Parameters:**

- `self` (Any): No description
- `other` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/handlers/handlers.py:52`

---

### __eq__



**Parameters:**

- `self` (Any): No description
- `other` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/handlers/handlers.py:55`

---

### is_async

Return True when the wrapped handler is coroutine based.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/handlers/handlers.py:63`

---

### get_global_event_bus

Return a process-wide event bus instance.

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/event_bus/global_bus.py:19`

---

### get_global_propagation

Return a global propagation helper bound to the global bus.

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/event_bus/global_bus.py:29`

---

### emit_event

Emit an event synchronously through the global bus.

**Parameters:**

- `event_type` (Any): No description
- `data` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/event_bus/global_bus.py:39`

---

### register_handler

Register a handler on the global bus.

**Parameters:**

- `event_type` (Any): No description
- `handler` (Any): No description
- `priority` (Any): No description
- `once` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/event_bus/global_bus.py:55`

---

### unregister_handler

Remove a handler from the global bus.

**Parameters:**

- `event_type` (Any): No description
- `handler` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/event_bus/global_bus.py:64`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/event_bus/bus.py:23`

---

### register_handler

Register a handler for a specific event type.

**Parameters:**

- `self` (Any): No description
- `event_type` (Any): No description
- `handler` (Any): No description
- `priority` (Any): No description
- `once` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/event_bus/bus.py:32`

---

### unregister_handler

Remove a handler previously registered.

**Parameters:**

- `self` (Any): No description
- `event_type` (Any): No description
- `handler` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/event_bus/bus.py:47`

---

### clear_handlers

Clear handlers for a given type or all handlers.

**Parameters:**

- `self` (Any): No description
- `event_type` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/event_bus/bus.py:58`

---

### get_handlers

Return a copy of handlers for the provided event.

**Parameters:**

- `self` (Any): No description
- `event_type` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/event_bus/bus.py:68`

---

### emit

Emit an event synchronously.

**Parameters:**

- `self` (Any): No description
- `event` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/event_bus/bus.py:78`

---

### get_event_history

Return recent events, optionally filtered by type.

**Parameters:**

- `self` (Any): No description
- `event_type` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/event_bus/bus.py:149`

---

### clear_event_history

Clear recorded history.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/event_bus/bus.py:158`

---

### get_stats

Return diagnostic information about the bus.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/event_bus/bus.py:165`

---

### _add_to_history



**Parameters:**

- `self` (Any): No description
- `event` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/events/event_bus/bus.py:180`

---

### from_hex

Create RGB color from hex string.

**Parameters:**

- `cls` (Any): No description
- `hex_color` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/color_utils/rgb_color.py:22`

---

### to_hex

Convert to hex string.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/color_utils/rgb_color.py:35`

---

### to_hsl

Convert to HSL (hue, saturation, lightness).

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/color_utils/rgb_color.py:41`

---

### from_hsl

Create RGB color from HSL values.

**Parameters:**

- `cls` (Any): No description
- `h` (Any): No description
- `s` (Any): No description
- `l` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/color_utils/rgb_color.py:49`

---

### luminance

Calculate relative luminance according to WCAG.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/color_utils/rgb_color.py:56`

---

### contrast_ratio

Calculate WCAG contrast ratio between two colors.

**Parameters:**

- `self` (Any): No description
- `other` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/color_utils/rgb_color.py:75`

---

### meets_wcag

Check if color meets WCAG contrast requirements.

**Parameters:**

- `self` (Any): No description
- `background` (Any): No description
- `level` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/color_utils/rgb_color.py:92`

---

### lighten

Lighten color by amount (0-1).

**Parameters:**

- `self` (Any): No description
- `amount` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/color_utils/rgb_color.py:105`

---

### darken

Darken color by amount (0-1).

**Parameters:**

- `self` (Any): No description
- `amount` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/color_utils/rgb_color.py:113`

---

### saturate

Increase saturation by amount (0-1).

**Parameters:**

- `self` (Any): No description
- `amount` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/color_utils/rgb_color.py:121`

---

### desaturate

Decrease saturation by amount (0-1).

**Parameters:**

- `self` (Any): No description
- `amount` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/color_utils/rgb_color.py:129`

---

### rotate_hue

Rotate hue by degrees.

**Parameters:**

- `self` (Any): No description
- `degrees` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/color_utils/rgb_color.py:137`

---

### blend

Blend with another color.

**Parameters:**

- `self` (Any): No description
- `other` (Any): No description
- `amount` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/color_utils/rgb_color.py:145`

---

### _channel_luminance



**Parameters:**

- `channel` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/core/theming/color_utils/rgb_color.py:63`

---

