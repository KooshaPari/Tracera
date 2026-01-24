"""Test grouping module for organizing tests by domain, story, file, or language."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .discovery import TestFile


@dataclass
class TestGroup:
    """Represents a group of tests organized by category."""
    group_name: str
    category: str  # "domain", "story", "file", or "language"
    tests: List[TestFile] = field(default_factory=list)

    def count(self) -> int:
        """Return the number of tests in this group."""
        return len(self.tests)

    def pass_rate(self) -> float:
        """Calculate aggregate pass rate (placeholder for future implementation)."""
        # TODO: Implement actual pass rate calculation when test results are available
        return 0.0 if self.tests else 100.0


class TestGrouper:
    """Groups discovered tests by domain, story, file, or language."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize TestGrouper with optional project root."""
        self.project_root = project_root or Path.cwd()

    def group_tests(self, tests: List[TestFile], by: str = "domain") -> List[TestGroup]:
        """
        Group tests by specified category.

        Args:
            tests: List of TestFile objects to group
            by: Grouping strategy - "domain", "story", "file", or "language"

        Returns:
            Sorted list of TestGroup objects
        """
        if not tests:
            return []

        if by == "domain":
            return self._group_by_domain(tests)
        elif by == "story":
            return self._group_by_story(tests)
        elif by == "file":
            return self._group_by_file(tests)
        elif by == "language":
            return self._group_by_language(tests)
        else:
            raise ValueError(f"Unknown grouping strategy: {by}")

    def _group_by_domain(self, tests: List[TestFile]) -> List[TestGroup]:
        """Group tests by domain extracted from directory path."""
        groups: dict[str, TestGroup] = {}

        for test in tests:
            # Extract domain from path: tests/component/services/ → "services"
            parts = Path(test.path).parts
            domain = self._extract_domain(parts)

            if domain not in groups:
                groups[domain] = TestGroup(
                    group_name=domain,
                    category="domain",
                    tests=[]
                )
            groups[domain].tests.append(test)

        return sorted(groups.values(), key=lambda g: (g.group_name, -g.count()))

    def _group_by_story(self, tests: List[TestFile]) -> List[TestGroup]:
        """Group tests by story (extracted from path depth)."""
        groups: dict[str, TestGroup] = {}

        for test in tests:
            # Extract story identifier from path
            parts = Path(test.path).parts
            story = self._extract_story(parts)

            if story not in groups:
                groups[story] = TestGroup(
                    group_name=story,
                    category="story",
                    tests=[]
                )
            groups[story].tests.append(test)

        return sorted(groups.values(), key=lambda g: (g.group_name, -g.count()))

    def _group_by_file(self, tests: List[TestFile]) -> List[TestGroup]:
        """Group all tests in the same file together."""
        groups: dict[str, TestGroup] = {}

        for test in tests:
            file_name = Path(test.path).name

            if file_name not in groups:
                groups[file_name] = TestGroup(
                    group_name=file_name,
                    category="file",
                    tests=[]
                )
            groups[file_name].tests.append(test)

        return sorted(groups.values(), key=lambda g: (g.group_name, -g.count()))

    def _group_by_language(self, tests: List[TestFile]) -> List[TestGroup]:
        """Group tests by language (python, go, typescript)."""
        groups: dict[str, TestGroup] = {}

        for test in tests:
            language = test.language

            if language not in groups:
                groups[language] = TestGroup(
                    group_name=language,
                    category="language",
                    tests=[]
                )
            groups[language].tests.append(test)

        return sorted(groups.values(), key=lambda g: (g.group_name, -g.count()))

    @staticmethod
    def _extract_domain(parts: tuple[str, ...]) -> str:
        """Extract domain from path parts.

        Examples:
            ('tests', 'component', 'services', 'test_*.py') → "services"
            ('tests', 'unit', 'api', 'test_*.py') → "api"
            ('frontend', 'apps', 'web', 'src', '__tests__', '*.test.tsx') → "__tests__"
        """
        if len(parts) >= 2:
            # For Python tests: tests/[type]/[domain]/test_*.py
            if parts[0] == "tests" and len(parts) >= 3:
                domain = parts[2]
                if isinstance(domain, str):
                    return domain
            # For TypeScript tests: frontend/apps/web/src/__tests__/...
            if "frontend" in parts and "__tests__" in parts:
                idx = parts.index("__tests__")
                if idx + 1 < len(parts):
                    domain = parts[idx + 1]
                    if isinstance(domain, str):
                        return domain
                return "__tests__"
            # Default: second-to-last non-file part
            if len(parts) > 1:
                domain = parts[-2]
                if isinstance(domain, str):
                    return domain
        return "root"

    @staticmethod
    def _extract_story(parts: tuple[str, ...]) -> str:
        """Extract story identifier from path parts.

        Uses directory hierarchy to identify logical story groups.
        """
        if len(parts) >= 2:
            if parts[0] == "tests":
                # Use test type (component/unit/e2e) + domain
                if len(parts) >= 3:
                    p1 = parts[1]
                    p2 = parts[2]
                    if isinstance(p1, str) and isinstance(p2, str):
                        return f"{p1}/{p2}"
            # Default: last meaningful directory
            if len(parts) > 1:
                result_parts = [p for p in parts[:-1] if isinstance(p, str)]
                if result_parts:
                    return "/".join(result_parts)
                p0 = parts[0]
                if isinstance(p0, str):
                    return p0
        return "unknown"
