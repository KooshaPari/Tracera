"""
Project-specific quality analysis configuration for pheno-sdk.
"""

from .config import create_custom_config

# Project-specific configuration
PROJECT_CONFIG = create_custom_config(
    "pheno-sdk",
    enabled_tools=[
        "pattern_detector",
        "architectural_validator",
        "performance_detector",
        "security_scanner",
        "code_smell_detector",
        "integration_gates",
        "atlas_health",
    ],
    thresholds={
        "max_violations": 50,
        "max_warnings": 100,
        "max_errors": 10,
        "quality_score_threshold": 80.0,
        "max_loop_iterations": 1000,
        "max_nested_loops": 3,
        "max_function_calls": 50,
        "max_memory_usage_mb": 100,
        "max_response_time_ms": 1000,
        "max_database_queries": 10,
        "max_file_operations": 5,
        "max_network_calls": 3,
        "long_method_lines": 50,
        "long_method_complexity": 15,
        "large_class_methods": 20,
        "large_class_lines": 500,
        "long_parameter_list": 5,
        "duplicate_code_lines": 10,
        "dead_code_unused_days": 30,
        "magic_number_count": 5,
        "deep_nesting": 4,
        "long_chain_calls": 5,
        "too_many_returns": 3,
        "cyclomatic_complexity": 10,
    },
    filters={
        "severity": ["high", "critical"],
        "impact": ["High", "Critical"],
        "file_patterns": ["*.py"],
        "exclude_patterns": ["__pycache__", "*.pyc", ".git", "node_modules"],
    },
    output_format="json",
    output_path="reports",
    parallel_analysis=True,
    max_workers=4,
    timeout_seconds=300,
)

# Tool-specific configurations
TOOL_CONFIGS = {
    "pattern_detector": {
        "enabled_patterns": [
            "god_object",
            "feature_envy",
            "data_clump",
            "shotgun_surgery",
            "divergent_change",
            "parallel_inheritance",
            "lazy_class",
            "inappropriate_intimacy",
            "message_chain",
            "middle_man",
        ],
        "thresholds": {
            "god_object_methods": 15,
            "feature_envy_ratio": 2.0,
            "data_clump_params": 3,
        },
    },
    "architectural_validator": {
        "enabled_patterns": [
            "hexagonal_architecture",
            "clean_architecture",
            "solid_principles",
            "layered_architecture",
            "domain_driven_design",
        ],
    },
    "performance_detector": {
        "enabled_patterns": [
            "n_plus_one_query",
            "memory_leak",
            "blocking_calls",
            "inefficient_loops",
            "excessive_io",
        ],
        "thresholds": {
            "max_loop_iterations": 1000,
            "max_nested_loops": 3,
            "max_memory_usage_mb": 100,
        },
    },
    "security_scanner": {
        "enabled_patterns": [
            "sql_injection",
            "xss_vulnerability",
            "insecure_deserialization",
            "authentication_bypass",
            "authorization_flaw",
        ],
    },
    "code_smell_detector": {
        "enabled_patterns": [
            "long_method",
            "large_class",
            "duplicate_code",
            "dead_code",
            "magic_number",
            "deep_nesting",
            "high_complexity",
        ],
        "thresholds": {
            "long_method_lines": 50,
            "large_class_methods": 20,
            "cyclomatic_complexity": 10,
        },
    },
    "integration_gates": {
        "enabled_gates": [
            "api_contracts",
            "data_flow_validation",
            "error_handling",
            "logging_validation",
            "security_validation",
        ],
    },
}
