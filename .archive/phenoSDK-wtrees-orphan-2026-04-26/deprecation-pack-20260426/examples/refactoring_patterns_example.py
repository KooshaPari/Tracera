"""Refactoring Patterns Example.

This example demonstrates the usage of hexagonal refactoring patterns
for analyzing, extracting, and validating Python code architecture.

Run this example:
    python examples/refactoring_patterns_example.py
"""

import asyncio
import logging
from pathlib import Path
from typing import List

from pheno.patterns.refactoring import (
    AnalysisResult,
    ClassExtractor,
    CodeAnalyzer,
    ConcernExtractor,
    LayerExtractor,
    PatternExtractor,
    analyze_complexity,
    detect_large_files,
    detect_violations,
    validate_dependencies,
    validate_layers,
    validate_port_adapter,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Sample code for testing
SAMPLE_CODE = '''
"""Sample module for refactoring demonstration."""

from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class User:
    """User entity."""

    def __init__(self, user_id: str, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email

    def validate_email(self) -> bool:
        """Validate email format."""
        return '@' in self.email and '.' in self.email


class UserService:
    """Service for user operations."""

    def __init__(self):
        self.users: List[User] = []

    def create_user(self, name: str, email: str) -> User:
        """Create a new user."""
        user_id = self._generate_id()
        user = User(user_id, name, email)

        if not user.validate_email():
            raise ValueError("Invalid email")

        self.users.append(user)
        logger.info(f"Created user: {user_id}")

        return user

    def _generate_id(self) -> str:
        """Generate user ID."""
        return f"user_{len(self.users) + 1}"

    def find_user(self, user_id: str) -> Optional[User]:
        """Find user by ID."""
        for user in self.users:
            if user.user_id == user_id:
                return user
        return None

    def validate_credentials(self, email: str, password: str) -> bool:
        """Validate user credentials."""
        # This is authentication logic - should be in separate concern
        for user in self.users:
            if user.email == email:
                # Simplified authentication
                return True
        return False


class UserRepository:
    """Repository for user persistence."""

    def save(self, user: User) -> None:
        """Save user to database."""
        # Database logic
        logger.info(f"Saving user {user.user_id} to database")

    def find_by_id(self, user_id: str) -> Optional[User]:
        """Find user by ID."""
        # Database query
        return None


class UserFactory:
    """Factory for creating users."""

    @staticmethod
    def create_admin(name: str, email: str) -> User:
        """Create admin user."""
        return User(f"admin_{name}", name, email)

    @staticmethod
    def create_regular(name: str, email: str) -> User:
        """Create regular user."""
        return User(f"user_{name}", name, email)
'''


async def example_1_basic_analysis():
    """Example 1: Analyze a file for metrics and violations."""
    print("\n" + "=" * 80)
    print("Example 1: Basic Code Analysis")
    print("=" * 80 + "\n")

    # Create temporary test file
    test_file = Path("/tmp/sample.py")
    test_file.write_text(SAMPLE_CODE)

    try:
        # Create analyzer
        analyzer = CodeAnalyzer(
            size_threshold=200,  # Lower threshold for demo
            complexity_threshold=5,
            cognitive_threshold=10,
        )

        # Analyze file
        result = await analyzer.analyze_file(test_file)

        # Display metrics
        print("Code Metrics:")
        print(f"  Lines of Code: {result.metrics.lines_of_code}")
        print(f"  Cyclomatic Complexity: {result.metrics.cyclomatic_complexity}")
        print(f"  Cognitive Complexity: {result.metrics.cognitive_complexity}")
        print(f"  Classes: {result.metrics.class_count}")
        print(f"  Functions: {result.metrics.function_count}")
        print(f"  Imports: {result.metrics.import_count}")
        print(f"  Needs Refactoring: {result.metrics.needs_refactoring}")

        # Display violations
        if result.violations:
            print(f"\nViolations ({len(result.violations)}):")
            for violation in result.violations:
                print(f"  [{violation.severity.upper()}] {violation.violation_type}")
                print(f"    Line {violation.line_number}: {violation.message}")

        # Display suggestions
        if result.refactoring_suggestions:
            print("\nRefactoring Suggestions:")
            for suggestion in result.refactoring_suggestions:
                print(f"  • {suggestion}")

        print(f"\nPriority: {result.priority.upper()}")
        print(f"Severity Score: {result.severity_score}")

    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


async def example_2_complexity_analysis():
    """Example 2: Analyze complexity of a file."""
    print("\n" + "=" * 80)
    print("Example 2: Complexity Analysis")
    print("=" * 80 + "\n")

    test_file = Path("/tmp/sample.py")
    test_file.write_text(SAMPLE_CODE)

    try:
        # Analyze complexity
        complexity = await analyze_complexity(test_file)

        print("File Complexity:")
        print(f"  File: {complexity['file']}")
        print(f"  Cyclomatic Complexity: {complexity['cyclomatic_complexity']}")
        print(f"  Cognitive Complexity: {complexity['cognitive_complexity']}")

        print("\nFunction Complexities:")
        for func, comp in complexity["function_complexities"].items():
            print(f"  {func}: {comp}")

    finally:
        if test_file.exists():
            test_file.unlink()


async def example_3_class_extraction():
    """Example 3: Extract a class to separate file."""
    print("\n" + "=" * 80)
    print("Example 3: Class Extraction")
    print("=" * 80 + "\n")

    test_file = Path("/tmp/sample.py")
    test_file.write_text(SAMPLE_CODE)

    try:
        # Create extractor
        extractor = ClassExtractor()

        # Extract User class
        result = await extractor.extract_class(
            source_file=test_file, class_name="User", target_file=Path("/tmp/user.py")
        )

        if result.success:
            print("✓ Extraction successful!")
            print(f"  Source: {result.source_file}")
            print(f"  Target: {result.target_file}")
            print(f"  Dependencies: {len(result.dependencies)}")

            print("\nExtracted Code Preview:")
            print(result.extracted_code[:300] + "...")

            print("\nDependencies:")
            for dep in result.dependencies:
                print(f"  {dep}")
        else:
            print(f"✗ Extraction failed: {result.error}")

    finally:
        if test_file.exists():
            test_file.unlink()
        if Path("/tmp/user.py").exists():
            Path("/tmp/user.py").unlink()


async def example_4_concern_extraction():
    """Example 4: Extract code by functional concern."""
    print("\n" + "=" * 80)
    print("Example 4: Concern Extraction")
    print("=" * 80 + "\n")

    test_file = Path("/tmp/sample.py")
    test_file.write_text(SAMPLE_CODE)

    try:
        # Create extractor
        extractor = ConcernExtractor()

        # Extract authentication concern
        result = await extractor.extract_concern(
            source_file=test_file, concern="authentication", target_dir=Path("/tmp")
        )

        if result.success:
            print("✓ Concern extraction successful!")
            print(f"  Source: {result.source_file}")
            print(f"  Target: {result.target_file}")
            print(f"  Concern: authentication")

            print("\nExtracted Code Preview:")
            print(result.extracted_code[:300] + "...")
        else:
            print(f"✗ Extraction failed: {result.error}")

    finally:
        if test_file.exists():
            test_file.unlink()
        if Path("/tmp/authentication.py").exists():
            Path("/tmp/authentication.py").unlink()


async def example_5_pattern_extraction():
    """Example 5: Extract design pattern."""
    print("\n" + "=" * 80)
    print("Example 5: Pattern Extraction")
    print("=" * 80 + "\n")

    test_file = Path("/tmp/sample.py")
    test_file.write_text(SAMPLE_CODE)

    try:
        # Create extractor
        extractor = PatternExtractor()

        # Extract factory pattern
        result = await extractor.extract_pattern(
            source_file=test_file, pattern_type="factory", target_dir=Path("/tmp")
        )

        if result.success:
            print("✓ Pattern extraction successful!")
            print(f"  Source: {result.source_file}")
            print(f"  Target: {result.target_file}")
            print(f"  Pattern: factory")

            print("\nExtracted Code Preview:")
            print(result.extracted_code[:300] + "...")
        else:
            print(f"✗ Extraction failed: {result.error}")

    finally:
        if test_file.exists():
            test_file.unlink()
        if Path("/tmp/factory.py").exists():
            Path("/tmp/factory.py").unlink()


async def example_6_layer_extraction():
    """Example 6: Extract by architectural layer."""
    print("\n" + "=" * 80)
    print("Example 6: Layer Extraction")
    print("=" * 80 + "\n")

    test_file = Path("/tmp/sample.py")
    test_file.write_text(SAMPLE_CODE)

    try:
        # Create extractor
        extractor = LayerExtractor()

        # Extract domain layer (entities)
        result = await extractor.extract_layer(
            source_file=test_file, layer="domain", target_dir=Path("/tmp/domain")
        )

        if result.success:
            print("✓ Layer extraction successful!")
            print(f"  Source: {result.source_file}")
            print(f"  Target: {result.target_file}")
            print(f"  Layer: domain")

            print("\nExtracted Code Preview:")
            print(result.extracted_code[:300] + "...")
        else:
            print(f"✗ Extraction failed: {result.error}")

    finally:
        if test_file.exists():
            test_file.unlink()
        # Cleanup domain directory
        import shutil

        if Path("/tmp/domain").exists():
            shutil.rmtree("/tmp/domain")


async def example_7_port_adapter_validation():
    """Example 7: Validate port/adapter pattern."""
    print("\n" + "=" * 80)
    print("Example 7: Port/Adapter Validation")
    print("=" * 80 + "\n")

    # Sample port interface
    port_code = '''
from typing import Protocol
from typing import Optional

class User:
    """User entity."""
    def __init__(self, user_id: str, name: str):
        self.user_id = user_id
        self.name = name

class UserRepository(Protocol):
    """Port for user repository."""

    async def save(self, user: User) -> None:
        """Save a user."""
        ...

    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Find user by ID."""
        ...
'''

    # Sample adapter implementation
    adapter_code = '''
from typing import Optional

class User:
    """User entity."""
    def __init__(self, user_id: str, name: str):
        self.user_id = user_id
        self.name = name

class SqlUserRepository:
    """SQL adapter for user repository."""

    async def save(self, user: User) -> None:
        """Save user to database."""
        # Database implementation
        pass

    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Find user by ID."""
        # Database query
        return None
'''

    port_file = Path("/tmp/user_repository_port.py")
    adapter_file = Path("/tmp/sql_user_repository.py")

    port_file.write_text(port_code)
    adapter_file.write_text(adapter_code)

    try:
        # Validate port
        print("Validating Port Interface...")
        port_result = await validate_port_adapter(port_file, is_port=True)

        if port_result.is_valid:
            print("✓ Port interface is valid")
        else:
            print(f"✗ Port validation failed ({port_result.error_count} errors)")
            for issue in port_result.issues:
                print(f"  {issue}")

        # Validate adapter
        print("\nValidating Adapter Implementation...")
        adapter_result = await validate_port_adapter(adapter_file, is_port=False)

        if adapter_result.is_valid:
            print("✓ Adapter implementation is valid")
        else:
            print(f"✗ Adapter validation failed ({adapter_result.error_count} errors)")
            for issue in adapter_result.issues:
                print(f"  {issue}")

    finally:
        if port_file.exists():
            port_file.unlink()
        if adapter_file.exists():
            adapter_file.unlink()


async def example_8_layer_validation():
    """Example 8: Validate layer separation."""
    print("\n" + "=" * 80)
    print("Example 8: Layer Validation")
    print("=" * 80 + "\n")

    # Sample application layer code
    app_code = '''
"""Application service."""

from typing import Optional

# Correct: Application can depend on domain
class User:
    """Domain entity."""
    pass

# Correct: Application service
class UserService:
    """Application service for user operations."""

    def create_user(self, name: str) -> User:
        """Create a new user."""
        user = User()
        return user
'''

    test_file = Path("/tmp/application/service.py")
    test_file.parent.mkdir(exist_ok=True)
    test_file.write_text(app_code)

    try:
        # Validate layers
        result = await validate_layers(test_file)

        print(f"Layer Validation Result:")
        print(f"  File: {result.file_path}")
        print(f"  Valid: {result.is_valid}")
        print(f"  Errors: {result.error_count}")
        print(f"  Warnings: {result.warning_count}")

        if result.issues:
            print("\nIssues:")
            for issue in result.issues:
                print(f"  [{issue.severity.upper()}] {issue.rule_name}")
                print(f"    Line {issue.line_number}: {issue.message}")

    finally:
        if test_file.exists():
            test_file.unlink()
        if test_file.parent.exists():
            test_file.parent.rmdir()


async def example_9_dependency_validation():
    """Example 9: Validate dependency rules."""
    print("\n" + "=" * 80)
    print("Example 9: Dependency Validation")
    print("=" * 80 + "\n")

    # Sample code with dependencies
    dep_code = '''
"""Sample module with dependencies."""

import logging
from typing import List
from pathlib import Path

logger = logging.getLogger(__name__)

class Service:
    """Service class."""

    def __init__(self):
        self.items: List[str] = []

    def process(self) -> None:
        """Process items."""
        logger.info("Processing")
'''

    test_file = Path("/tmp/service.py")
    test_file.write_text(dep_code)

    try:
        # Validate dependencies
        result = await validate_dependencies(test_file)

        print(f"Dependency Validation Result:")
        print(f"  File: {result.file_path}")
        print(f"  Valid: {result.is_valid}")
        print(f"  Errors: {result.error_count}")
        print(f"  Warnings: {result.warning_count}")

        if result.issues:
            print("\nIssues:")
            for issue in result.issues:
                print(f"  [{issue.severity.upper()}] {issue.rule_name}")
                print(f"    {issue.message}")

    finally:
        if test_file.exists():
            test_file.unlink()


async def example_10_batch_analysis():
    """Example 10: Batch analysis of multiple files."""
    print("\n" + "=" * 80)
    print("Example 10: Batch Analysis")
    print("=" * 80 + "\n")

    # Create temporary directory with multiple files
    temp_dir = Path("/tmp/batch_test")
    temp_dir.mkdir(exist_ok=True)

    files = []
    for i in range(3):
        file = temp_dir / f"module_{i}.py"
        file.write_text(SAMPLE_CODE)
        files.append(file)

    try:
        # Detect large files
        print("Detecting large files...")
        large_files = await detect_large_files(temp_dir, threshold=100)

        if large_files:
            print(f"Found {len(large_files)} large files:")
            for file, loc in large_files:
                print(f"  {file.name}: {loc} LOC")

        # Detect violations
        print("\nDetecting violations...")
        violations = await detect_violations(temp_dir)

        if violations:
            print(f"Found {len(violations)} violations:")
            violation_types = {}
            for v in violations:
                violation_types[v.violation_type] = violation_types.get(v.violation_type, 0) + 1

            for vtype, count in violation_types.items():
                print(f"  {vtype}: {count}")

        # Analyze each file
        print("\nAnalyzing individual files...")
        analyzer = CodeAnalyzer()

        for file in files:
            result = await analyzer.analyze_file(file)
            print(
                f"  {file.name}: Priority={result.priority}, "
                f"Complexity={result.metrics.cyclomatic_complexity}"
            )

    finally:
        # Cleanup
        import shutil

        if temp_dir.exists():
            shutil.rmtree(temp_dir)


async def main():
    """
    Run all examples.
    """
    print("\n" + "=" * 80)
    print("Hexagonal Refactoring Patterns - Examples")
    print("=" * 80)

    examples = [
        example_1_basic_analysis,
        example_2_complexity_analysis,
        example_3_class_extraction,
        example_4_concern_extraction,
        example_5_pattern_extraction,
        example_6_layer_extraction,
        example_7_port_adapter_validation,
        example_8_layer_validation,
        example_9_dependency_validation,
        example_10_batch_analysis,
    ]

    for example in examples:
        try:
            await example()
        except Exception as e:
            logger.error(f"Error in {example.__name__}: {e}", exc_info=True)

    print("\n" + "=" * 80)
    print("All examples completed!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
