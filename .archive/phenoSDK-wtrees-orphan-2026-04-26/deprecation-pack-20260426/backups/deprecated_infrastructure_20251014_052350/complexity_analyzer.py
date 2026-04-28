"""Code complexity analysis."""

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ComplexityMetrics:
    """Code complexity metrics.
    
    Attributes:
        total_lines: Total lines of code
        code_lines: Lines of actual code (excluding comments/blanks)
        comment_lines: Lines of comments
        blank_lines: Blank lines
        cyclomatic_complexity: Average cyclomatic complexity
        high_complexity_functions: Functions with high complexity
        maintainability_index: Overall maintainability score
        comment_ratio: Ratio of comments to code
    """
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    cyclomatic_complexity: float
    high_complexity_functions: list[dict]
    maintainability_index: float
    comment_ratio: float

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_lines": self.total_lines,
            "code_lines": self.code_lines,
            "comment_lines": self.comment_lines,
            "blank_lines": self.blank_lines,
            "cyclomatic_complexity": round(self.cyclomatic_complexity, 2),
            "high_complexity_functions": self.high_complexity_functions,
            "maintainability_index": round(self.maintainability_index, 2),
            "comment_ratio": round(self.comment_ratio, 3),
        }


class ComplexityAnalyzer:
    """Analyze code complexity metrics."""

    def __init__(self):
        """Initialize the complexity analyzer."""
        self.complexity_threshold = 10  # Functions above this are "complex"

    def analyze_project(self, root_path: str, file_patterns: list[str] = None) -> ComplexityMetrics:
        """Analyze complexity for entire project.
        
        Args:
            root_path: Root directory of project
            file_patterns: File patterns to analyze (default: ["*.py"])
            
        Returns:
            ComplexityMetrics with complete analysis
        """
        file_patterns = file_patterns or ["*.py"]

        total_lines = 0
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        complexities = []
        high_complexity_funcs = []

        root = Path(root_path)

        # Collect all Python files
        python_files = []
        for pattern in file_patterns:
            python_files.extend(root.rglob(pattern))

        # Analyze each file
        for file_path in python_files:
            if not file_path.is_file():
                continue

            try:
                file_metrics = self._analyze_file(str(file_path))

                total_lines += file_metrics["total_lines"]
                code_lines += file_metrics["code_lines"]
                comment_lines += file_metrics["comment_lines"]
                blank_lines += file_metrics["blank_lines"]

                # Collect function complexities
                for func_complexity in file_metrics["function_complexities"]:
                    complexities.append(func_complexity["complexity"])

                    if func_complexity["complexity"] > self.complexity_threshold:
                        high_complexity_funcs.append({
                            "file": str(file_path),
                            "function": func_complexity["name"],
                            "complexity": func_complexity["complexity"],
                            "line": func_complexity["line"],
                        })

            except Exception:
                continue

        # Calculate averages
        avg_complexity = sum(complexities) / len(complexities) if complexities else 0
        comment_ratio = comment_lines / code_lines if code_lines > 0 else 0

        # Calculate maintainability index (simplified)
        maintainability = self._calculate_maintainability(
            code_lines, avg_complexity, comment_ratio,
        )

        return ComplexityMetrics(
            total_lines=total_lines,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            cyclomatic_complexity=avg_complexity,
            high_complexity_functions=high_complexity_funcs,
            maintainability_index=maintainability,
            comment_ratio=comment_ratio,
        )

    def _analyze_file(self, file_path: str) -> dict:
        """Analyze a single file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file metrics
        """
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
            source = "".join(lines)

        # Count line types
        total_lines = len(lines)
        comment_lines = 0
        blank_lines = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
            elif stripped.startswith("#"):
                comment_lines += 1

        code_lines = total_lines - comment_lines - blank_lines

        # Analyze functions
        function_complexities = []

        try:
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_cyclomatic_complexity(node)
                    function_complexities.append({
                        "name": node.name,
                        "complexity": complexity,
                        "line": node.lineno,
                    })

        except Exception:
            pass

        return {
            "total_lines": total_lines,
            "code_lines": code_lines,
            "comment_lines": comment_lines,
            "blank_lines": blank_lines,
            "function_complexities": function_complexities,
        }

    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function.
        
        Cyclomatic complexity = number of decision points + 1
        
        Args:
            node: AST node for function
            
        Returns:
            Cyclomatic complexity score
        """
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            # Count decision points
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)) or isinstance(child, ast.ExceptHandler) or isinstance(child, ast.With, ast.AsyncWith):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # Each boolean operator adds complexity
                complexity += len(child.values) - 1
            elif isinstance(child, ast.comprehension):
                # List/dict/set comprehensions
                complexity += 1
                if child.ifs:
                    complexity += len(child.ifs)

        return complexity

    def _calculate_maintainability(
        self,
        code_lines: int,
        avg_complexity: float,
        comment_ratio: float,
    ) -> float:
        """Calculate maintainability index (simplified).
        
        Based on Microsoft's maintainability index formula (simplified):
        MI = max(0, (171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(L)) * 100 / 171)
        
        Where:
        - V = Halstead Volume (approximated by LOC)
        - G = Cyclomatic Complexity
        - L = Lines of Code
        
        Simplified version for our purposes.
        
        Args:
            code_lines: Lines of code
            avg_complexity: Average cyclomatic complexity
            comment_ratio: Ratio of comments to code
            
        Returns:
            Maintainability index (0-100, higher is better)
        """
        import math

        if code_lines == 0:
            return 100.0

        # Simplified calculation
        # Start with 100 and subtract penalties
        score = 100.0

        # Penalty for high complexity
        if avg_complexity > 10:
            score -= (avg_complexity - 10) * 2

        # Penalty for low comment ratio
        if comment_ratio < 0.1:
            score -= (0.1 - comment_ratio) * 100

        # Penalty for large codebase (harder to maintain)
        if code_lines > 10000:
            score -= math.log10(code_lines / 10000) * 10

        # Ensure score is in valid range
        return max(0.0, min(100.0, score))

