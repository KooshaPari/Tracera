"""Test discovery module for scanning test files across multiple languages."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class TestFile:
    """Represents a discovered test file."""
    path: str
    language: str  # "python", "go", "typescript"
    file_path: Path


class TestDiscovery:
    """Discovers test files across multiple languages."""

    PYTHON_TEST_DIR = Path("tests")
    GO_TEST_DIR = Path("backend")
    TYPESCRIPT_TEST_DIR = Path("frontend/apps/web/src/__tests__")

    PATTERNS = {
        "python": "test_*.py",
        "go": "*_test.go",
        "typescript": ["*.test.ts", "*.test.tsx"],
    }

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize TestDiscovery with optional project root."""
        self.project_root = project_root or Path.cwd()

    def discover(
        self, languages: Optional[List[str]] = None, scope: str = "all"
    ) -> List[TestFile]:
        """Discover test files for specified languages and scope."""
        if languages is None:
            languages = ["python", "go", "typescript"]

        discovered = []
        for language in languages:
            if language == "python":
                discovered.extend(self._discover_python(scope))
            elif language == "go":
                discovered.extend(self._discover_go(scope))
            elif language == "typescript":
                discovered.extend(self._discover_typescript(scope))
        return discovered

    def _discover_python(self, scope: str) -> List[TestFile]:
        """Discover Python test files matching test_*.py pattern."""
        test_dir = self.project_root / self.PYTHON_TEST_DIR
        if not test_dir.exists():
            return []

        pattern = f"**/{self.PATTERNS['python']}" if scope == "all" else f"**/{scope}/**/{self.PATTERNS['python']}"
        return [
            TestFile(
                path=str(f.relative_to(self.project_root)),
                language="python",
                file_path=f,
            )
            for f in test_dir.glob(pattern) if f.is_file()
        ]

    def _discover_go(self, scope: str) -> List[TestFile]:
        """Discover Go test files matching *_test.go pattern."""
        test_dir = self.project_root / self.GO_TEST_DIR
        if not test_dir.exists():
            return []

        pattern = f"**/{self.PATTERNS['go']}" if scope == "all" else f"**/{scope}/**/{self.PATTERNS['go']}"
        return [
            TestFile(
                path=str(f.relative_to(self.project_root)),
                language="go",
                file_path=f,
            )
            for f in test_dir.glob(pattern) if f.is_file()
        ]

    def _discover_typescript(self, scope: str) -> List[TestFile]:
        """Discover TypeScript test files matching *.test.ts and *.test.tsx."""
        test_dir = self.project_root / self.TYPESCRIPT_TEST_DIR
        if not test_dir.exists():
            return []

        patterns = (
            [f"**/{p}" for p in self.PATTERNS["typescript"]]
            if scope == "all"
            else [f"**/{scope}/**/{p}" for p in self.PATTERNS["typescript"]]
        )
        discovered = []
        for pattern in patterns:
            discovered.extend([
                TestFile(
                    path=str(f.relative_to(self.project_root)),
                    language="typescript",
                    file_path=f,
                )
                for f in test_dir.glob(pattern) if f.is_file()
            ])
        return discovered

    def discover_by_language(
        self, language: str, scope: str = "all"
    ) -> List[TestFile]:
        """Discover test files for a specific language."""
        return self.discover(languages=[language], scope=scope)

    def count_tests(
        self, languages: Optional[List[str]] = None, scope: str = "all"
    ) -> dict[str, int]:
        """Get count of discovered test files by language."""
        discovered = self.discover(languages=languages, scope=scope)
        counts: dict[str, int] = {}
        for test_file in discovered:
            counts[test_file.language] = counts.get(test_file.language, 0) + 1
        return counts
