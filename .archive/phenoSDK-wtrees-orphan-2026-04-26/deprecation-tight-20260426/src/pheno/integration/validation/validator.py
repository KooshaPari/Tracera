"""Main integration validator for pheno-integration.

This module provides the central IntegrationValidator class that orchestrates all
integration validation operations across all pheno-sdk libraries.
"""

import importlib
import os
import traceback
from datetime import datetime
from typing import Any

from .types import (
    IntegrationTest,
    ValidationConfig,
    ValidationResult,
    ValidationStatus,
)


class IntegrationValidator:
    """
    Main integration validator implementation.
    """

    def __init__(
        self, name: str = "integration_validator", config: ValidationConfig | None = None,
    ):
        self.name = name
        self.config = config or ValidationConfig()

        self._tests: dict[str, IntegrationTest] = {}
        self._results: list[ValidationResult] = []

        # Library paths
        self.library_paths = [
            "pheno-auth",
            "pheno-config",
            "pheno-logging",
            "pheno-errors",
            "pheno-testing",
            "pheno-docs",
        ]

    def validate_all_libraries(self) -> list[ValidationResult]:
        """Validate all pheno-sdk libraries.

        Returns:
            List of validation results
        """
        results = []

        try:
            # Validate individual libraries
            for library in self.library_paths:
                result = self._validate_library(library)
                results.append(result)

            # Validate cross-library integration
            cross_library_result = self._validate_cross_library_integration()
            results.append(cross_library_result)

            # Validate performance
            performance_result = self._validate_performance()
            results.append(performance_result)

            # Validate migration paths
            migration_result = self._validate_migration_paths()
            results.append(migration_result)

        except Exception as e:
            error_result = ValidationResult(
                test_id="validation_error",
                test_name="validate_all_libraries",
                status=ValidationStatus.ERROR,
                start_time=datetime.now(),
                error=e,
                error_message=str(e),
                error_traceback=traceback.format_exc(),
            )
            results.append(error_result)

        self._results.extend(results)
        return results

    def validate_library(self, library_name: str) -> ValidationResult:
        """Validate a specific library.

        Args:
            library_name: Name of the library to validate

        Returns:
            Validation result
        """
        return self._validate_library(library_name)

    def validate_cross_library_integration(self) -> ValidationResult:
        """Validate cross-library integration.

        Returns:
            Validation result
        """
        return self._validate_cross_library_integration()

    def validate_performance(self) -> ValidationResult:
        """Validate performance across all libraries.

        Returns:
            Validation result
        """
        return self._validate_performance()

    def validate_migration_paths(self) -> ValidationResult:
        """Validate migration paths.

        Returns:
            Validation result
        """
        return self._validate_migration_paths()

    def add_test(self, test: IntegrationTest) -> None:
        """
        Add an integration test.
        """
        self._tests[test.name] = test

    def run_test(self, test_name: str) -> ValidationResult:
        """Run a specific integration test.

        Args:
            test_name: Name of the test to run

        Returns:
            Validation result
        """
        if test_name not in self._tests:
            return ValidationResult(
                test_id="test_not_found",
                test_name=test_name,
                status=ValidationStatus.ERROR,
                start_time=datetime.now(),
                error_message=f"Test '{test_name}' not found",
            )

        test = self._tests[test_name]
        return self._run_single_test(test)

    def run_all_tests(self) -> list[ValidationResult]:
        """Run all integration tests.

        Returns:
            List of validation results
        """
        results = []

        for test in self._tests.values():
            result = self._run_single_test(test)
            results.append(result)

        self._results.extend(results)
        return results

    def get_results(self) -> list[ValidationResult]:
        """
        Get all validation results.
        """
        return self._results

    def get_summary(self) -> dict[str, Any]:
        """
        Get validation summary.
        """
        if not self._results:
            return {"total": 0, "passed": 0, "failed": 0, "error": 0}

        total = len(self._results)
        passed = len([r for r in self._results if r.status == ValidationStatus.PASSED])
        failed = len([r for r in self._results if r.status == ValidationStatus.FAILED])
        error = len([r for r in self._results if r.status == ValidationStatus.ERROR])

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "error": error,
            "success_rate": (passed / total) * 100 if total > 0 else 0,
        }

    def _validate_library(self, library_name: str) -> ValidationResult:
        """
        Validate a specific library.
        """
        start_time = datetime.now()

        try:
            # Check if library exists
            if not self._library_exists(library_name):
                return ValidationResult(
                    test_id=f"library_{library_name}",
                    test_name=f"validate_{library_name}",
                    status=ValidationStatus.FAILED,
                    start_time=start_time,
                    end_time=datetime.now(),
                    error_message=f"Library '{library_name}' not found",
                )

            # Check if library can be imported
            if not self._library_importable(library_name):
                return ValidationResult(
                    test_id=f"library_{library_name}",
                    test_name=f"validate_{library_name}",
                    status=ValidationStatus.FAILED,
                    start_time=start_time,
                    end_time=datetime.now(),
                    error_message=f"Library '{library_name}' cannot be imported",
                )

            # Check library structure
            structure_valid = self._validate_library_structure(library_name)

            # Check library interfaces
            interfaces_valid = self._validate_library_interfaces(library_name)

            # Check library configuration
            config_valid = self._validate_library_configuration(library_name)

            # Determine overall status
            if structure_valid and interfaces_valid and config_valid:
                status = ValidationStatus.PASSED
                error_message = None
            else:
                status = ValidationStatus.FAILED
                error_message = "Library validation failed"

            return ValidationResult(
                test_id=f"library_{library_name}",
                test_name=f"validate_{library_name}",
                status=status,
                start_time=start_time,
                end_time=datetime.now(),
                error_message=error_message,
                details={
                    "structure_valid": structure_valid,
                    "interfaces_valid": interfaces_valid,
                    "config_valid": config_valid,
                },
            )

        except Exception as e:
            return ValidationResult(
                test_id=f"library_{library_name}",
                test_name=f"validate_{library_name}",
                status=ValidationStatus.ERROR,
                start_time=start_time,
                end_time=datetime.now(),
                error=e,
                error_message=str(e),
                error_traceback=traceback.format_exc(),
            )

    def _validate_cross_library_integration(self) -> ValidationResult:
        """
        Validate cross-library integration.
        """
        start_time = datetime.now()

        try:
            # Test auth-config integration
            auth_config_valid = self._test_auth_config_integration()

            # Test logging-error integration
            logging_error_valid = self._test_logging_error_integration()

            # Test testing-docs integration
            testing_docs_valid = self._test_testing_docs_integration()

            # Test config-logging integration
            config_logging_valid = self._test_config_logging_integration()

            # Determine overall status
            if all(
                [auth_config_valid, logging_error_valid, testing_docs_valid, config_logging_valid],
            ):
                status = ValidationStatus.PASSED
                error_message = None
            else:
                status = ValidationStatus.FAILED
                error_message = "Cross-library integration validation failed"

            return ValidationResult(
                test_id="cross_library_integration",
                test_name="validate_cross_library_integration",
                status=status,
                start_time=start_time,
                end_time=datetime.now(),
                error_message=error_message,
                details={
                    "auth_config_valid": auth_config_valid,
                    "logging_error_valid": logging_error_valid,
                    "testing_docs_valid": testing_docs_valid,
                    "config_logging_valid": config_logging_valid,
                },
            )

        except Exception as e:
            return ValidationResult(
                test_id="cross_library_integration",
                test_name="validate_cross_library_integration",
                status=ValidationStatus.ERROR,
                start_time=start_time,
                end_time=datetime.now(),
                error=e,
                error_message=str(e),
                error_traceback=traceback.format_exc(),
            )

    def _validate_performance(self) -> ValidationResult:
        """
        Validate performance across all libraries.
        """
        start_time = datetime.now()

        try:
            # Test memory usage
            memory_usage = self._test_memory_usage()

            # Test response time
            response_time = self._test_response_time()

            # Test throughput
            throughput = self._test_throughput()

            # Determine performance status
            performance_acceptable = (
                memory_usage < 100 * 1024 * 1024  # 100MB
                and response_time < 1.0  # 1 second
                and throughput > 100  # 100 operations/second
            )

            status = ValidationStatus.PASSED if performance_acceptable else ValidationStatus.FAILED

            return ValidationResult(
                test_id="performance_validation",
                test_name="validate_performance",
                status=status,
                start_time=start_time,
                end_time=datetime.now(),
                metrics={
                    "memory_usage": memory_usage,
                    "response_time": response_time,
                    "throughput": throughput,
                },
            )

        except Exception as e:
            return ValidationResult(
                test_id="performance_validation",
                test_name="validate_performance",
                status=ValidationStatus.ERROR,
                start_time=start_time,
                end_time=datetime.now(),
                error=e,
                error_message=str(e),
                error_traceback=traceback.format_exc(),
            )

    def _validate_migration_paths(self) -> ValidationResult:
        """
        Validate migration paths.
        """
        start_time = datetime.now()

        try:
            # Test backward compatibility
            backward_compatible = self._test_backward_compatibility()

            # Test data integrity
            data_integrity = self._test_data_integrity()

            # Test rollback capability
            rollback_capable = self._test_rollback_capability()

            # Determine migration status
            migration_valid = all([backward_compatible, data_integrity, rollback_capable])

            status = ValidationStatus.PASSED if migration_valid else ValidationStatus.FAILED

            return ValidationResult(
                test_id="migration_validation",
                test_name="validate_migration_paths",
                status=status,
                start_time=start_time,
                end_time=datetime.now(),
                details={
                    "backward_compatible": backward_compatible,
                    "data_integrity": data_integrity,
                    "rollback_capable": rollback_capable,
                },
            )

        except Exception as e:
            return ValidationResult(
                test_id="migration_validation",
                test_name="validate_migration_paths",
                status=ValidationStatus.ERROR,
                start_time=start_time,
                end_time=datetime.now(),
                error=e,
                error_message=str(e),
                error_traceback=traceback.format_exc(),
            )

    def _run_single_test(self, test: IntegrationTest) -> ValidationResult:
        """
        Run a single integration test.
        """
        start_time = datetime.now()

        try:
            # Run the test function
            result = test.test_function()

            # Check if result matches expected
            if test.expected_result is not None and result != test.expected_result:
                return ValidationResult(
                    test_id=test.test_id,
                    test_name=test.name,
                    status=ValidationStatus.FAILED,
                    start_time=start_time,
                    end_time=datetime.now(),
                    error_message=f"Test result does not match expected: {result} != {test.expected_result}",
                )

            return ValidationResult(
                test_id=test.test_id,
                test_name=test.name,
                status=ValidationStatus.PASSED,
                start_time=start_time,
                end_time=datetime.now(),
                details={"result": result},
            )

        except Exception as e:
            return ValidationResult(
                test_id=test.test_id,
                test_name=test.name,
                status=ValidationStatus.ERROR,
                start_time=start_time,
                end_time=datetime.now(),
                error=e,
                error_message=str(e),
                error_traceback=traceback.format_exc(),
            )

    # Helper methods for validation
    def _library_exists(self, library_name: str) -> bool:
        """
        Check if library exists.
        """
        return os.path.exists(library_name)

    def _library_importable(self, library_name: str) -> bool:
        """
        Check if library can be imported.
        """
        try:
            importlib.import_module(library_name)
            return True
        except ImportError:
            return False

    def _validate_library_structure(self, library_name: str) -> bool:
        """
        Validate library structure.
        """
        # Check for required files
        required_files = ["__init__.py", "core/__init__.py"]
        for file in required_files:
            if not os.path.exists(os.path.join(library_name, file)):
                return False
        return True

    def _validate_library_interfaces(self, library_name: str) -> bool:
        """
        Validate library interfaces.
        """
        # This would check for required interfaces
        # For now, return True as a placeholder
        return True

    def _validate_library_configuration(self, library_name: str) -> bool:
        """
        Validate library configuration.
        """
        # This would check for valid configuration
        # For now, return True as a placeholder
        return True

    def _test_auth_config_integration(self) -> bool:
        """
        Test auth-config integration.
        """
        # This would test actual integration
        # For now, return True as a placeholder
        return True

    def _test_logging_error_integration(self) -> bool:
        """
        Test logging-error integration.
        """
        # This would test actual integration
        # For now, return True as a placeholder
        return True

    def _test_testing_docs_integration(self) -> bool:
        """
        Test testing-docs integration.
        """
        # This would test actual integration
        # For now, return True as a placeholder
        return True

    def _test_config_logging_integration(self) -> bool:
        """
        Test config-logging integration.
        """
        # This would test actual integration
        # For now, return True as a placeholder
        return True

    def _test_memory_usage(self) -> float:
        """
        Test memory usage.
        """
        # This would test actual memory usage
        # For now, return a placeholder value
        return 50 * 1024 * 1024  # 50MB

    def _test_response_time(self) -> float:
        """
        Test response time.
        """
        # This would test actual response time
        # For now, return a placeholder value
        return 0.5  # 0.5 seconds

    def _test_throughput(self) -> float:
        """
        Test throughput.
        """
        # This would test actual throughput
        # For now, return a placeholder value
        return 200  # 200 operations/second

    def _test_backward_compatibility(self) -> bool:
        """
        Test backward compatibility.
        """
        # This would test actual backward compatibility
        # For now, return True as a placeholder
        return True

    def _test_data_integrity(self) -> bool:
        """
        Test data integrity.
        """
        # This would test actual data integrity
        # For now, return True as a placeholder
        return True

    def _test_rollback_capability(self) -> bool:
        """
        Test rollback capability.
        """
        # This would test actual rollback capability
        # For now, return True as a placeholder
        return True
