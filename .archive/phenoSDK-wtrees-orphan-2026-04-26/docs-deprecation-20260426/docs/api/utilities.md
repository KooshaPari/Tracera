# Utilities API Reference

The Utilities API provides helper functions and common utilities.

## Overview

The Utilities API includes:

- Data manipulation helpers
- Format conversion utilities
- Validation functions
- Common algorithms

## Functions

### generate_issue_id

Generate a unique issue ID.

**Parameters:**

- `issue_type` (Any): No description
- `file_path` (Any): No description
- `line` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/utils.py:21`

---

### generate_report_id

Generate a unique report ID.

**Parameters:**

- `project_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/utils.py:29`

---

### normalize_file_path

Normalize file path for consistent comparison.

**Parameters:**

- `file_path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/utils.py:37`

---

### matches_pattern

Check if file path matches any of the given patterns.

**Parameters:**

- `file_path` (Any): No description
- `patterns` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/utils.py:44`

---

### should_exclude_file

Check if file should be excluded based on patterns.

**Parameters:**

- `file_path` (Any): No description
- `exclude_patterns` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/utils.py:54`

---

### get_file_extension

Get file extension.

**Parameters:**

- `file_path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/utils.py:61`

---

### is_python_file

Check if file is a Python file.

**Parameters:**

- `file_path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/utils.py:68`

---

### is_source_file

Check if file is a source code file.

**Parameters:**

- `file_path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/utils.py:75`

---

### calculate_confidence_score

Calculate confidence score for an issue.

**Parameters:**

- `severity` (Any): No description
- `impact` (Any): No description
- `metadata` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/utils.py:83`

---

### categorize_issue

Categorize an issue based on type and tool.

**Parameters:**

- `issue_type` (Any): No description
- `tool` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/utils.py:121`

---

### generate_tags

Generate tags for an issue.

**Parameters:**

- `issue_type` (Any): No description
- `tool` (Any): No description
- `severity` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/utils.py:231`

---

### format_duration

Format duration in human-readable format.

**Parameters:**

- `seconds` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/utils.py:251`

---

### format_file_size

Format file size in human-readable format.

**Parameters:**

- `bytes_size` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/utils.py:265`

---

### calculate_quality_trend

Calculate quality trend.

**Parameters:**

- `current_score` (Any): No description
- `previous_score` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/utils.py:276`

---

### get_priority_score

Calculate priority score (1-10, higher is more important)

**Parameters:**

- `severity` (Any): No description
- `impact` (Any): No description
- `confidence` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/utils.py:288`

---

### group_issues_by_file

Group issues by file path.

**Parameters:**

- `issues` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/utils.py:314`

---

### group_issues_by_type

Group issues by type.

**Parameters:**

- `issues` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/utils.py:327`

---

### group_issues_by_severity

Group issues by severity.

**Parameters:**

- `issues` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/quality/utils.py:340`

---

### _b64_encode

Base64url encode.

**Parameters:**

- `data` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/security/jwt_utils.py:21`

---

### _b64_decode

Base64url decode.

**Parameters:**

- `data` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/security/jwt_utils.py:28`

---

### create_jwt

Create JWT token.

**Parameters:**

- `payload` (Any): No description
- `secret` (Any): No description
- `algorithm` (Any): No description
- `expires_in` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/security/jwt_utils.py:39`

---

### verify_jwt

Verify and decode JWT token.

**Parameters:**

- `token` (Any): No description
- `secret` (Any): No description
- `algorithms` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/security/jwt_utils.py:96`

---

### decode_jwt

Decode JWT token without verification.

**Parameters:**

- `token` (Any): No description
- `verify` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/security/jwt_utils.py:163`

---

### wait_for

Wait for a condition to become true (sync version).

**Parameters:**

- `condition` (Any): No description
- `timeout` (Any): No description
- `interval` (Any): No description
- `message` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/testing/utils.py:62`

---

### capture_logs

Capture log messages for testing.

**Parameters:**

- `logger_name` (Any): No description
- `level` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/testing/utils.py:105`

---

### temp_env

Temporarily set environment variables.

**Returns:** `Any`

**File:** `src/pheno/testing/utils.py:150`

---

### assert_dict_contains

Assert that actual dict contains all keys/values from expected dict.

**Parameters:**

- `actual` (Any): No description
- `expected` (Any): No description
- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/testing/utils.py:228`

---

### assert_list_contains

Assert that actual list contains all items from expected list.

**Parameters:**

- `actual` (Any): No description
- `expected` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/testing/utils.py:262`

---

### retry_on_exception

Decorator to retry function on exception.

**Parameters:**

- `max_attempts` (Any): No description
- `delay` (Any): No description
- `exceptions` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/testing/utils.py:284`

---

### __init__

Initialize with frozen time.

**Parameters:**

- `self` (Any): No description
- `frozen_time` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/testing/utils.py:198`

---

### __enter__

Enter context.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/testing/utils.py:209`

---

### __exit__

Exit context.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/testing/utils.py:217`

---

### decorator



**Parameters:**

- `func` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/testing/utils.py:301`

---

### wrapper



**Returns:** `Any`

**File:** `src/pheno/testing/utils.py:302`

---

### truncate

Truncate text to maximum length.

**Parameters:**

- `text` (Any): No description
- `max_length` (Any): No description
- `suffix` (Any): No description
- `word_boundary` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/strings/text_utils.py:10`

---

### wrap_text

Wrap text to specified width.

**Parameters:**

- `text` (Any): No description
- `width` (Any): No description
- `indent` (Any): No description
- `subsequent_indent` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/strings/text_utils.py:48`

---

### pad_string

Pad string to specified length.

**Parameters:**

- `text` (Any): No description
- `length` (Any): No description
- `char` (Any): No description
- `align` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/strings/text_utils.py:76`

---

### remove_whitespace

Remove whitespace from text.

**Parameters:**

- `text` (Any): No description
- `keep` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/strings/text_utils.py:109`

---

### indent_text

Indent all lines in text.

**Parameters:**

- `text` (Any): No description
- `indent` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/strings/text_utils.py:130`

---

### decode_jwt

Decode JWT token and return claims.

**Parameters:**

- `token` (Any): No description
- `verify_signature` (Any): No description
- `secret` (Any): No description
- `algorithms` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:32`

---

### extract_user_from_jwt

Extract user information from JWT token.

**Parameters:**

- `token` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:82`

---

### is_token_expired

Check if JWT token is expired.

**Parameters:**

- `token` (Any): No description
- `buffer_seconds` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:109`

---

### is_expired

Check if access token is expired.

**Parameters:**

- `self` (Any): No description
- `buffer_seconds` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:165`

---

### to_dict

Convert to dictionary.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:173`

---

### from_dict

Create from dictionary.

**Parameters:**

- `cls` (Any): No description
- `data` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:187`

---

### __init__

Initialize token manager.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:221`

---

### set_tokens

Store tokens for a key.

**Parameters:**

- `self` (Any): No description
- `key` (Any): No description
- `tokens` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:227`

---

### get_tokens

Retrieve tokens for a key.

**Parameters:**

- `self` (Any): No description
- `key` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:237`

---

### remove_tokens

Remove tokens for a key.

**Parameters:**

- `self` (Any): No description
- `key` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:248`

---

### clear

Clear all stored tokens.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:258`

---

### save_to_file

Save tokens to JSON file.

**Parameters:**

- `self` (Any): No description
- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:265`

---

### from_file

Load tokens from JSON file.

**Parameters:**

- `cls` (Any): No description
- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:282`

---

### __init__

Initialize credential store.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:334`

---

### set

Store a credential.

**Parameters:**

- `self` (Any): No description
- `key` (Any): No description
- `value` (Any): No description
- `sensitive` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:341`

---

### get

Retrieve a credential.

**Parameters:**

- `self` (Any): No description
- `key` (Any): No description
- `default` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:356`

---

### has

Check if credential exists.

**Parameters:**

- `self` (Any): No description
- `key` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:368`

---

### remove

Remove a credential.

**Parameters:**

- `self` (Any): No description
- `key` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:374`

---

### clear

Clear all credentials.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:383`

---

### save_to_file

Save credentials to JSON file.

**Parameters:**

- `self` (Any): No description
- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:391`

---

### from_file

Load credentials from JSON file.

**Parameters:**

- `cls` (Any): No description
- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:415`

---

### __init__

Initialize session manager.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:468`

---

### create_session

Create a new session.

**Parameters:**

- `self` (Any): No description
- `session_id` (Any): No description
- `tokens` (Any): No description
- `credentials` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:475`

---

### get_tokens

Get tokens for session.

**Parameters:**

- `self` (Any): No description
- `session_id` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:498`

---

### get_credential

Get credential for session.

**Parameters:**

- `self` (Any): No description
- `session_id` (Any): No description
- `key` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:504`

---

### end_session

End a session and clean up.

**Parameters:**

- `self` (Any): No description
- `session_id` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:513`

---

### clear_all

Clear all sessions.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/auth.py:522`

---

### configure_logging

Configure logging for the application.

**Parameters:**

- `level` (Any): No description
- `format_string` (Any): No description
- `date_format` (Any): No description
- `log_file` (Any): No description
- `quiet_libraries` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/logging.py:24`

---

### get_logger

Get a logger instance with consistent configuration.

**Parameters:**

- `name` (Any): No description
- `level` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/logging.py:79`

---

### quiet_library_loggers

Suppress logging from noisy libraries.

**Parameters:**

- `libraries` (Any): No description
- `level` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/logging.py:105`

---

### set_verbose_mode

Enable or disable verbose logging (DEBUG level).

**Parameters:**

- `enabled` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/logging.py:116`

---

### create_file_handler

Create a file handler for logging.

**Parameters:**

- `log_file` (Any): No description
- `level` (Any): No description
- `format_string` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/logging.py:126`

---

### add_file_logging

Add file logging to the root logger.

**Parameters:**

- `log_file` (Any): No description
- `level` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/logging.py:151`

---

### log_exception

Log an exception with consistent formatting.

**Parameters:**

- `logger` (Any): No description
- `message` (Any): No description
- `exc_info` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/logging.py:162`

---

### debug

Log debug message.

**Parameters:**

- `message` (Any): No description
- `logger_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/logging.py:247`

---

### info

Log info message.

**Parameters:**

- `message` (Any): No description
- `logger_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/logging.py:254`

---

### warning

Log warning message.

**Parameters:**

- `message` (Any): No description
- `logger_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/logging.py:261`

---

### error

Log error message.

**Parameters:**

- `message` (Any): No description
- `logger_name` (Any): No description
- `exc_info` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/logging.py:268`

---

### critical

Log critical message.

**Parameters:**

- `message` (Any): No description
- `logger_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/logging.py:275`

---

### __init__

Initialize context manager.

**Parameters:**

- `self` (Any): No description
- `logger_name` (Any): No description
- `level` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/logging.py:183`

---

### __enter__

Enter context - set temporary level.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/logging.py:194`

---

### __exit__

Exit context - restore original level.

**Parameters:**

- `self` (Any): No description
- `exc_type` (Any): No description
- `exc_val` (Any): No description
- `exc_tb` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/logging.py:199`

---

### __init__

Initialize context manager.

**Parameters:**

- `self` (Any): No description
- `logger_names` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/logging.py:213`

---

### __enter__

Enter context - suppress logging.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/logging.py:222`

---

### __exit__

Exit context - restore logging.

**Parameters:**

- `self` (Any): No description
- `exc_type` (Any): No description
- `exc_val` (Any): No description
- `exc_tb` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/logging.py:235`

---

### get_env

Retrieve an environment variable with optional casting and validation.

**Parameters:**

- `key` (Any): No description
- `default` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/config.py:34`

---

### get_env_config

Return a mapping of environment variables filtered by ``prefix``.

**Parameters:**

- `prefix` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/config.py:64`

---

### load_env_file

Parse a ``.env`` file and optionally apply the values to ``os.environ``.

**Parameters:**

- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/config.py:76`

---

### load_yaml

Load structured configuration from YAML, relying on :class:`Config`.

**Parameters:**

- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/config.py:90`

---

### save_yaml

Persist a mapping to disk as YAML.

**Parameters:**

- `data` (Any): No description
- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/config.py:102`

---

### get_config

Return auxiliary configuration hints expected by legacy consumers.

**Returns:** `Any`

**File:** `src/pheno/dev/utils/config.py:241`

---

### from_dict

Construct a configuration instance from a plain mapping.

**Parameters:**

- `cls` (Any): No description
- `data` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/config.py:126`

---

### to_dict

Convert the configuration dataclass into a serialisable mapping.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/config.py:135`

---

### from_yaml

Create a configuration instance from a YAML file.

**Parameters:**

- `cls` (Any): No description
- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/config.py:159`

---

### to_yaml

Write the configuration to a YAML file.

**Parameters:**

- `self` (Any): No description
- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/config.py:166`

---

### validate

Hook for subclasses that require custom validation logic.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/config.py:173`

---

### load

Return merged environment values without mutating ``os.environ``.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/config.py:218`

---

### apply

Load values and apply them to the current process environment.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/config.py:227`

---

### __init__

Initialize reporter.

**Parameters:**

- `self` (Any): No description
- `collector` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metrics_reporter.py:28`

---

### format_text

Format metrics as plain text.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metrics_reporter.py:36`

---

### format_json

Format metrics as JSON-serializable dict.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metrics_reporter.py:75`

---

### log_metrics

Log metrics using logger.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metrics_reporter.py:83`

---

### to_dict

Convert to dictionary.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metric_types.py:30`

---

### __init__

Initialize counter.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `initial` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metric_types.py:52`

---

### increment

Increment counter.

**Parameters:**

- `self` (Any): No description
- `amount` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metric_types.py:62`

---

### decrement

Decrement counter.

**Parameters:**

- `self` (Any): No description
- `amount` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metric_types.py:68`

---

### reset

Reset counter to zero.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metric_types.py:74`

---

### value

Get current value.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metric_types.py:81`

---

### __init__

Initialize gauge.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `initial` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metric_types.py:98`

---

### set

Set gauge value.

**Parameters:**

- `self` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metric_types.py:108`

---

### increment

Increment gauge.

**Parameters:**

- `self` (Any): No description
- `amount` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metric_types.py:114`

---

### decrement

Decrement gauge.

**Parameters:**

- `self` (Any): No description
- `amount` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metric_types.py:120`

---

### value

Get current value.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metric_types.py:127`

---

### __init__

Initialize histogram.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metric_types.py:144`

---

### observe

Record an observation.

**Parameters:**

- `self` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metric_types.py:153`

---

### reset

Clear all observations.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metric_types.py:159`

---

### count

Number of observations.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metric_types.py:166`

---

### statistics

Calculate statistics.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metric_types.py:172`

---

### __init__

Initialize metrics collector.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metrics_collector.py:42`

---

### increment

Increment a counter.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `amount` (Any): No description
- `tags` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metrics_collector.py:51`

---

### decrement

Decrement a counter.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `amount` (Any): No description
- `tags` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metrics_collector.py:64`

---

### set_gauge

Set a gauge value.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `value` (Any): No description
- `tags` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metrics_collector.py:77`

---

### observe

Record a histogram observation.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `value` (Any): No description
- `tags` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metrics_collector.py:90`

---

### timer

Context manager for timing operations.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `tags` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metrics_collector.py:104`

---

### get_metrics

Get all collected metrics.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metrics_collector.py:122`

---

### reset

Reset all metrics.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metrics_collector.py:136`

---

### _make_key

Create metric key from name and tags.

**Parameters:**

- `name` (Any): No description
- `tags` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metrics_collector.py:146`

---

### __init__

Initialize aggregator.

**Parameters:**

- `self` (Any): No description
- `window_seconds` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metrics_collector.py:171`

---

### record

Record a metric value.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description
- `value` (Any): No description
- `tags` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metrics_collector.py:180`

---

### aggregate

Aggregate metrics for a name.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metrics_collector.py:194`

---

### _clean_old_metrics

Remove metrics outside time window.

**Parameters:**

- `self` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/metrics_collector.py:224`

---

### add_streaming_routes

Add streaming routes to a FastAPI/Starlette application.

**Parameters:**

- `app` (Any): No description
- `manager` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/streaming.py:115`

---

### should_bypass_auth

Check if a path should bypass authentication.

**Parameters:**

- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/middleware.py:29`

---

### get_nextjs_authkit_config

Get Next.js AuthKit middleware configuration with KInfra paths excluded.

**Returns:** `Any`

**File:** `src/pheno/dev/utils/middleware.py:47`

---

### get_nextjs_matcher_pattern

Get Next.js middleware matcher pattern excluding KInfra routes.

**Returns:** `Any`

**File:** `src/pheno/dev/utils/middleware.py:71`

---

### get_express_middleware

Get Express.js middleware function that bypasses auth for KInfra routes.

**Returns:** `Any`

**File:** `src/pheno/dev/utils/middleware.py:83`

---

### get_django_exempt_urls

Get Django URL patterns to exempt from authentication.

**Returns:** `Any`

**File:** `src/pheno/dev/utils/middleware.py:106`

---

### print_integration_guide

Print integration guide for a specific framework.

**Parameters:**

- `framework` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/middleware.py:223`

---

### kinfra_auth_bypass

Express middleware to bypass auth for KInfra routes.

**Parameters:**

- `req` (Any): No description
- `res` (Any): No description
- `next` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/middleware.py:93`

---

### __post_init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/task_queue.py:24`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `max_workers` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/task_queue.py:41`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `max_calls` (Any): No description
- `time_window` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/semaphores.py:19`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/semaphores.py:56`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/event_bus.py:34`

---

### on

Register event handler decorator.

**Parameters:**

- `self` (Any): No description
- `event_name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/event_bus.py:37`

---

### off

Remove event handler.

**Parameters:**

- `self` (Any): No description
- `event_name` (Any): No description
- `handler` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/event_bus.py:50`

---

### decorator



**Parameters:**

- `handler` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/event_bus.py:42`

---

### to_dict

Convert to dictionary.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/event_store.py:28`

---

### from_dict

Create from dictionary.

**Parameters:**

- `cls` (Any): No description
- `data` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/event_store.py:35`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/event_store.py:76`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `storage_path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/event_store.py:119`

---

### _get_stream_file

Get file path for aggregate stream.

**Parameters:**

- `self` (Any): No description
- `aggregate_id` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/event_store.py:123`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `backend` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/event_store.py:228`

---

### should_retry

Check if should retry delivery.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/webhook_manager.py:53`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `secret` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/webhook_manager.py:69`

---

### sign

Generate HMAC signature for payload.

**Parameters:**

- `self` (Any): No description
- `payload` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/webhook_manager.py:72`

---

### verify

Verify HMAC signature.

**Parameters:**

- `payload` (Any): No description
- `signature` (Any): No description
- `secret` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/webhook_manager.py:80`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `max_attempts` (Any): No description
- `initial_delay` (Any): No description
- `multiplier` (Any): No description
- `max_delay` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/webhook_manager.py:94`

---

### next_retry_time

Calculate next retry time using exponential backoff.

**Parameters:**

- `self` (Any): No description
- `attempt` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/webhook_manager.py:106`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `secret` (Any): No description
- `retry_policy` (Any): No description
- `timeout` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/webhook_manager.py:147`

---

### on_success

Register success callback.

**Parameters:**

- `self` (Any): No description
- `callback` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/webhook_manager.py:184`

---

### on_failure

Register failure callback.

**Parameters:**

- `self` (Any): No description
- `callback` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/webhook_manager.py:191`

---

### get_delivery

Get delivery record by ID.

**Parameters:**

- `self` (Any): No description
- `delivery_id` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/webhook_manager.py:308`

---

### get_pending

Get all pending deliveries.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/webhook_manager.py:314`

---

### get_failed

Get all failed deliveries.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/webhook_manager.py:324`

---

### get_stats

Get delivery statistics.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/webhook_manager.py:330`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `secret` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/webhook_manager.py:370`

---

### verify

Verify webhook signature.

**Parameters:**

- `self` (Any): No description
- `payload` (Any): No description
- `signature` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/async_utils/webhook_manager.py:373`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/query_filter.py:15`

---

### eq



**Parameters:**

- `self` (Any): No description
- `field` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/query_filter.py:18`

---

### neq



**Parameters:**

- `self` (Any): No description
- `field` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/query_filter.py:22`

---

### gt



**Parameters:**

- `self` (Any): No description
- `field` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/query_filter.py:26`

---

### gte



**Parameters:**

- `self` (Any): No description
- `field` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/query_filter.py:30`

---

### lt



**Parameters:**

- `self` (Any): No description
- `field` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/query_filter.py:34`

---

### lte



**Parameters:**

- `self` (Any): No description
- `field` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/query_filter.py:38`

---

### like



**Parameters:**

- `self` (Any): No description
- `field` (Any): No description
- `pattern` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/query_filter.py:42`

---

### ilike



**Parameters:**

- `self` (Any): No description
- `field` (Any): No description
- `pattern` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/query_filter.py:46`

---

### in_



**Parameters:**

- `self` (Any): No description
- `field` (Any): No description
- `values` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/query_filter.py:50`

---

### is_null



**Parameters:**

- `self` (Any): No description
- `field` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/query_filter.py:54`

---

### to_dict



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/query_filter.py:58`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `ttl` (Any): No description
- `max_size` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/cache.py:18`

---

### get



**Parameters:**

- `self` (Any): No description
- `key` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/cache.py:23`

---

### set



**Parameters:**

- `self` (Any): No description
- `key` (Any): No description
- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/cache.py:33`

---

### invalidate



**Parameters:**

- `self` (Any): No description
- `pattern` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/cache.py:40`

---

### clear



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/cache.py:48`

---

### make_key



**Parameters:**

- `operation` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/cache.py:52`

---

### has_fields

Check if the response has all required fields.

**Parameters:**

- `response` (Any): No description
- `required_fields` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/validators.py:16`

---

### has_any_fields

Check if the response has any of the specified fields.

**Parameters:**

- `response` (Any): No description
- `fields` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/validators.py:25`

---

### validate_pagination

Validate pagination structure.

**Parameters:**

- `response` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/validators.py:34`

---

### validate_list_response

Validate list response structure.

**Parameters:**

- `response` (Any): No description
- `data_key` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/validators.py:42`

---

### validate_success_response

Validate standard success response.

**Parameters:**

- `result` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/validators.py:56`

---

### extract_id

Extract an identifier field from common response shapes.

**Parameters:**

- `response` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/validators.py:63`

---

### is_uuid

Check if value is a valid UUID string.

**Parameters:**

- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/validators.py:82`

---

### is_iso_timestamp

Check if value is an ISO 8601 timestamp.

**Parameters:**

- `value` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/validators.py:92`

---

### is_in_range

Check if value is within a numeric range.

**Parameters:**

- `value` (Any): No description
- `min_val` (Any): No description
- `max_val` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/validators.py:105`

---

### is_valid_slug

Check if value matches a slug pattern.

**Parameters:**

- `value` (Any): No description
- `pattern` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/validators.py:124`

---

### timestamp

Generate timestamp string for unique identifiers.

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/data_generation.py:17`

---

### unique_id

Generate unique identifier with optional prefix.

**Parameters:**

- `prefix` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/data_generation.py:24`

---

### uuid

Generate a random UUID string.

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/data_generation.py:32`

---

### slug_from_uuid

Generate a slug-safe unique identifier.

**Parameters:**

- `prefix` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/data_generation.py:39`

---

### organization_data

Generate organization test data with valid slug.

**Parameters:**

- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/data_generation.py:52`

---

### project_data

Generate project test data.

**Parameters:**

- `name` (Any): No description
- `organization_id` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/data_generation.py:65`

---

### document_data

Generate document test data.

**Parameters:**

- `name` (Any): No description
- `project_id` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/data_generation.py:83`

---

### requirement_data

Generate requirement test data.

**Parameters:**

- `name` (Any): No description
- `document_id` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/data_generation.py:102`

---

### test_data

Generate test case data.

**Parameters:**

- `title` (Any): No description
- `project_id` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/data_generation.py:121`

---

### batch_data

Generate batch test data for a given entity type.

**Parameters:**

- `entity_type` (Any): No description
- `count` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/data_generation.py:140`

---

### timeout_wrapper

Decorator adding a timeout to async test functions.

**Parameters:**

- `timeout_seconds` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/timeout.py:59`

---

### detect_slow_tests

Return tests whose recorded durations exceed the threshold.

**Parameters:**

- `results` (Any): No description
- `threshold_ms` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/timeout.py:43`

---

### decorator



**Parameters:**

- `func` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/timeout.py:64`

---

### is_connection_error

Check if an error message indicates a connection failure.

**Parameters:**

- `error` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/retry.py:54`

---

### immediate

No wait.

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/retry.py:14`

---

### linear

Linear backoff: delay × attempt.

**Parameters:**

- `attempt` (Any): No description
- `base_delay` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/retry.py:21`

---

### exponential

Exponential backoff capped at max_delay.

**Parameters:**

- `attempt` (Any): No description
- `base_delay` (Any): No description
- `max_delay` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/retry.py:26`

---

### fibonacci

Fibonacci backoff sequence.

**Parameters:**

- `attempt` (Any): No description
- `base_delay` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/retry.py:38`

---

### fib



**Parameters:**

- `n` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/retry.py:43`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/performance.py:14`

---

### start

Start tracking.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/performance.py:18`

---

### record

Record a test execution.

**Parameters:**

- `self` (Any): No description
- `test_name` (Any): No description
- `duration_ms` (Any): No description
- `success` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/performance.py:24`

---

### get_stats

Return simple aggregates about tracked tests.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/helpers/performance.py:37`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `supabase_client` (Any): No description
- `cache_ttl` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/adapters/supabase.py:22`

---

### _get_client



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/adapters/supabase.py:26`

---

### _apply_filters



**Parameters:**

- `self` (Any): No description
- `query` (Any): No description
- `filters` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/adapters/supabase.py:39`

---

### _build_cache_key



**Parameters:**

- `self` (Any): No description
- `table` (Any): No description
- `select` (Any): No description
- `filters` (Any): No description
- `order_by` (Any): No description
- `limit` (Any): No description
- `offset` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/adapters/supabase.py:89`

---

### _apply_ordering



**Parameters:**

- `self` (Any): No description
- `query` (Any): No description
- `order_by` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/adapters/supabase.py:125`

---

### _apply_pagination



**Parameters:**

- `self` (Any): No description
- `query` (Any): No description
- `limit` (Any): No description
- `offset` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/adapters/supabase.py:133`

---

### __init__



**Parameters:**

- `self` (Any): No description
- `cache_ttl` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/adapters/base.py:22`

---

### set_access_token



**Parameters:**

- `self` (Any): No description
- `token` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/dev/utils/database/adapters/base.py:26`

---

### setup_logging

Setup logging for the CLI.

**Parameters:**

- `verbose` (Any): No description
- `debug` (Any): No description
- `log_file` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/utils/logging.py:14`

---

### get_logger

Get a logger instance.

**Parameters:**

- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/utils/logging.py:70`

---

### init_git_repo

Initialize a git repository in the project directory.

**Parameters:**

- `project_dir` (Any): No description
- `initial_commit` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/utils/git.py:13`

---

### is_git_repo

Check if path is a git repository.

**Parameters:**

- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/utils/git.py:87`

---

### get_git_root

Get the root of the git repository.

**Parameters:**

- `path` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/utils/git.py:98`

---

### get_user_config_dir

Get user configuration directory.

**Returns:** `Any`

**File:** `src/pheno/cli/app/utils/paths.py:9`

---

### get_user_data_dir

Get user data directory.

**Returns:** `Any`

**File:** `src/pheno/cli/app/utils/paths.py:21`

---

### get_user_cache_dir

Get user cache directory.

**Returns:** `Any`

**File:** `src/pheno/cli/app/utils/paths.py:33`

---

### handle_exception

Handle and display exceptions in a user-friendly way.

**Parameters:**

- `error` (Any): No description
- `debug` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/utils/exceptions.py:44`

---

### __init__

Initialize the error.

**Parameters:**

- `self` (Any): No description
- `message` (Any): No description
- `hint` (Any): No description
- `exit_code` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/utils/exceptions.py:16`

---

### load_setup_project_module

Dynamically load the setup_project.py module.

**Parameters:**

- `templates_dir` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/utils/project.py:9`

---

### __init__

Initialize with templates directory.

**Parameters:**

- `self` (Any): No description
- `templates_dir` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/utils/project.py:34`

---

### setup_full_project

Setup complete standardized CI/CD for a project.

**Parameters:**

- `self` (Any): No description
- `project_name` (Any): No description
- `project_dir` (Any): No description
- `project_version` (Any): No description
- `project_description` (Any): No description
- `keywords` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/utils/project.py:47`

---

### copy_template

Copy a template file to target location.

**Parameters:**

- `self` (Any): No description
- `template_path` (Any): No description
- `target_path` (Any): No description
- `replace_placeholders` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/utils/project.py:66`

---

### set_replacements

Set template replacement variables.

**Parameters:**

- `self` (Any): No description
- `project_name` (Any): No description
- `project_version` (Any): No description
- `project_description` (Any): No description
- `keywords` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/cli/app/utils/project.py:74`

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

### age_seconds

Process age in seconds.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/process_monitoring.py:64`

---

### is_active

Whether process appears to be active.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/process_monitoring.py:71`

---

### __init__

Initialize process monitor.

**Parameters:**

- `self` (Any): No description
- `max_processes` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/process_monitoring.py:92`

---

### start_monitoring

Start monitoring a process.

**Parameters:**

- `self` (Any): No description
- `pid` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/process_monitoring.py:114`

---

### stop_monitoring

Stop monitoring a process and return final metrics.

**Parameters:**

- `self` (Any): No description
- `pid` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/process_monitoring.py:149`

---

### update_all_metrics

Update metrics for all monitored processes.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/process_monitoring.py:171`

---

### get_process_metrics

Get metrics for a specific process.

**Parameters:**

- `self` (Any): No description
- `pid` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/process_monitoring.py:179`

---

### get_all_metrics

Get metrics for all monitored processes.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/process_monitoring.py:185`

---

### get_active_processes

Get list of currently active process IDs.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/process_monitoring.py:191`

---

### get_process_history

Get metrics history.

**Parameters:**

- `self` (Any): No description
- `pid` (Any): No description
- `event_type` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/process_monitoring.py:197`

---

### add_metrics_callback

Add callback for metrics events.

**Parameters:**

- `self` (Any): No description
- `callback` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/process_monitoring.py:221`

---

### set_alert_thresholds

Set alert thresholds for resource usage.

**Parameters:**

- `self` (Any): No description
- `cpu_percent` (Any): No description
- `memory_mb` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/process_monitoring.py:229`

---

### _update_process_metrics

Update metrics for a process.

**Parameters:**

- `self` (Any): No description
- `metrics` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/process_monitoring.py:240`

---

### _check_alerts

Check if metrics exceed alert thresholds.

**Parameters:**

- `self` (Any): No description
- `metrics` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/process_monitoring.py:286`

---

### _add_to_history

Add event to history.

**Parameters:**

- `self` (Any): No description
- `metrics` (Any): No description
- `event_type` (Any): No description
- `message` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/process_monitoring.py:321`

---

### export_metrics

Export monitoring data in various formats.

**Parameters:**

- `self` (Any): No description
- `format` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/process_monitoring.py:345`

---

### cleanup_stale_processes

Remove processes that are no longer running.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/process_monitoring.py:419`

---

### terminate_process

Safely terminate a process with graceful shutdown attempt.

**Parameters:**

- `pid` (Any): No description
- `timeout` (Any): No description
- `force_kill` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/process_lifecycle.py:21`

---

### cleanup_orphaned_processes

Terminate orphaned processes matching a pattern.

**Parameters:**

- `grace_period` (Any): No description
- `force_kill` (Any): No description
- `exclude_pids` (Any): No description
- `process_name_pattern` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/process_lifecycle.py:74`

---

### _build_trace_config

Return an aiohttp TraceConfig if the OTel instrumentation is available.

**Returns:** `Any`

**File:** `src/pheno/infra/utils/aiohttp_otel.py:14`

---

### apply_aiohttp_otel_kwargs

Merge OTel trace config into aiohttp.ClientSession kwargs if possible.

**Parameters:**

- `kwargs` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/aiohttp_otel.py:30`

---

### dns_safe_slug

Create a DNS-safe slug from a service name.

**Parameters:**

- `value` (Any): No description
- `default` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/dns.py:14`

---

### validate_dns_label

Validate if a string is a valid DNS label according to RFC 1123.

**Parameters:**

- `label` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/dns.py:73`

---

### create_subdomain

Create a full subdomain from service name and base domain.

**Parameters:**

- `service_name` (Any): No description
- `domain` (Any): No description
- `max_levels` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/dns.py:106`

---

### extract_service_name_from_hostname

Extract service name from a hostname by taking the first label.

**Parameters:**

- `hostname` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/dns.py:139`

---

### check_tcp_health

Check if a TCP port is accepting connections (synchronous).

**Parameters:**

- `host` (Any): No description
- `port` (Any): No description
- `timeout` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/health.py:18`

---

### check_http_health

Check HTTP endpoint health (synchronous).

**Parameters:**

- `url` (Any): No description
- `timeout` (Any): No description
- `expected_status` (Any): No description
- `method` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/health.py:46`

---

### check_tunnel_health

Check both local service and tunnel reachability.

**Parameters:**

- `hostname` (Any): No description
- `port` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/health.py:155`

---

### _load_pydevkit_httpx_hooks

Best-effort import of pydevkit's HTTPX OTel hooks.

**Returns:** `Any`

**File:** `src/pheno/infra/utils/httpx_otel.py:15`

---

### apply_httpx_otel_event_hooks

Merge pydevkit's HTTPX OTel event hooks (if present) into client kwargs.

**Parameters:**

- `kwargs` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/httpx_otel.py:55`

---

### _resolve_lsof

Resolve path to lsof binary.

**Returns:** `Any`

**File:** `src/pheno/infra/utils/platform_shims.py:26`

---

### is_port_free

Check if a port is free by attempting to bind to it.

**Parameters:**

- `port` (Any): No description
- `host` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/platform_shims.py:53`

---

### get_port_occupant

Get information about process occupying a port.

**Parameters:**

- `port` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/platform_shims.py:78`

---

### kill_processes_on_port

Kill all processes listening on a specific port.

**Parameters:**

- `port` (Any): No description
- `timeout` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/platform_shims.py:169`

---

### _kill_via_lsof

Kill processes using lsof (fallback for permission issues).

**Parameters:**

- `port` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/platform_shims.py:231`

---

### _is_likely_our_cmd

Best-effort detection that a process belongs to our dev stack.

**Parameters:**

- `cmdline` (Any): No description
- `name` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/platform_shims.py:260`

---

### free_port_if_likely_ours

If the given port is occupied by a same-project process, terminate it.

**Parameters:**

- `port` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/platform_shims.py:298`

---

### get_project_id

Return a stable project identifier.

**Parameters:**

- `default` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/identity.py:15`

---

### stable_offset

Compute a small, deterministic offset for the given project id.

**Parameters:**

- `project_id` (Any): No description
- `modulo` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/identity.py:35`

---

### base_ports_from_env

Read base fallback/proxy ports from env if provided, else defaults.

**Parameters:**

- `default_fallback` (Any): No description
- `default_proxy` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/identity.py:44`

---

### _sanitize



**Parameters:**

- `text` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/infra/utils/identity.py:53`

---

### get_env

Get environment variable with optional default.

**Parameters:**

- `key` (Any): No description
- `default` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/clink/utils/env.py:10`

---

### draw_box

Draw a box with optional title.

**Parameters:**

- `width` (Any): No description
- `height` (Any): No description
- `title` (Any): No description
- `style` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/box_drawing.py:86`

---

### draw_border

Draw a border around content.

**Parameters:**

- `content` (Any): No description
- `style` (Any): No description
- `title` (Any): No description
- `padding` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/box_drawing.py:131`

---

### get_charset

Get box drawing character set.

**Parameters:**

- `style` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/box_drawing.py:73`

---

### hex_to_rgb

Convert hex color to RGB tuple.

**Parameters:**

- `hex_color` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/colors.py:92`

---

### rgb_to_hex

Convert RGB to hex color.

**Parameters:**

- `r` (Any): No description
- `g` (Any): No description
- `b` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/colors.py:99`

---

### darken

Darken a color.

**Parameters:**

- `hex_color` (Any): No description
- `factor` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/colors.py:106`

---

### lighten

Lighten a color.

**Parameters:**

- `hex_color` (Any): No description
- `factor` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/colors.py:113`

---

### hex_to_rgb

Convert hex color to RGB tuple.

**Parameters:**

- `hex_color` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/colors.py:13`

---

### rgb_to_hex

Convert RGB to hex color.

**Parameters:**

- `r` (Any): No description
- `g` (Any): No description
- `b` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/colors.py:25`

---

### darken

Darken a color by factor (0-1).

**Parameters:**

- `hex_color` (Any): No description
- `factor` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/colors.py:32`

---

### lighten

Lighten a color by factor (0-1).

**Parameters:**

- `hex_color` (Any): No description
- `factor` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/colors.py:45`

---

### is_light

Determine if color is light or dark.

**Parameters:**

- `hex_color` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/colors.py:58`

---

### contrast_color

Get contrasting color (black or white).

**Parameters:**

- `hex_color` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/colors.py:70`

---

### blend

Blend two colors together.

**Parameters:**

- `color1` (Any): No description
- `color2` (Any): No description
- `factor` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/colors.py:77`

---

### get_shortcuts

Get global shortcuts instance.

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/keyboard.py:140`

---

### register_shortcut

Register a global shortcut.

**Parameters:**

- `key` (Any): No description
- `description` (Any): No description
- `action` (Any): No description
- `category` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/keyboard.py:147`

---

### get_shortcut

Get global shortcut.

**Parameters:**

- `key` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/keyboard.py:156`

---

### __init__



**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/keyboard.py:32`

---

### register

Register a keyboard shortcut.

**Parameters:**

- `self` (Any): No description
- `key` (Any): No description
- `description` (Any): No description
- `action` (Any): No description
- `category` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/keyboard.py:36`

---

### unregister

Unregister a shortcut.

**Parameters:**

- `self` (Any): No description
- `key` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/keyboard.py:58`

---

### get_shortcut

Get shortcut by key.

**Parameters:**

- `self` (Any): No description
- `key` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/keyboard.py:78`

---

### execute

Execute shortcut action.

**Parameters:**

- `self` (Any): No description
- `key` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/keyboard.py:84`

---

### get_category

Get all shortcuts in a category.

**Parameters:**

- `self` (Any): No description
- `category` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/keyboard.py:100`

---

### get_all_categories

Get list of all categories.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/keyboard.py:106`

---

### get_help_text

Generate help text for all shortcuts.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/keyboard.py:112`

---

### clear

Clear all shortcuts.

**Parameters:**

- `self` (Any): No description

**Returns:** `Any`

**File:** `src/pheno/ui/tui/utils/keyboard.py:128`

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

