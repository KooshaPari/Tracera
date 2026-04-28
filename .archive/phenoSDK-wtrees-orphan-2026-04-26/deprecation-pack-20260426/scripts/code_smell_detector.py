#!/usr/bin/env python3
"""
Code Smell Detector Comprehensive detection of code smells, maintainability issues, and
refactoring opportunities in Python codebases.
"""
import argparse
import ast
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class CodeSmell:
    """
    Represents a detected code smell.
    """

    type: str
    severity: str
    file: str
    line: int
    column: int
    message: str
    suggestion: str
    confidence: float


class CodeSmellDetector:
    """
    Detects various code smells in Python code.
    """

    def __init__(self):
        self.smells = []
        self.file_stats = {}

        # Thresholds for different code smells
        self.thresholds = {
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
        }

    def analyze_file(self, file_path: Path) -> dict[str, Any]:
        """
        Analyze a single file for code smells.
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            file_smells = []

            # Analyze different types of code smells
            file_smells.extend(self._detect_long_methods(tree, file_path))
            file_smells.extend(self._detect_large_classes(tree, file_path))
            file_smells.extend(self._detect_long_parameter_lists(tree, file_path))
            file_smells.extend(self._detect_duplicate_code(tree, file_path, content))
            file_smells.extend(self._detect_dead_code(tree, file_path))
            file_smells.extend(self._detect_magic_numbers(tree, file_path))
            file_smells.extend(self._detect_deep_nesting(tree, file_path))
            file_smells.extend(self._detect_long_chains(tree, file_path))
            file_smells.extend(self._detect_too_many_returns(tree, file_path))
            file_smells.extend(self._detect_cyclomatic_complexity(tree, file_path))
            file_smells.extend(self._detect_god_objects(tree, file_path))
            file_smells.extend(self._detect_feature_envy(tree, file_path))
            file_smells.extend(self._detect_data_clumps(tree, file_path))
            file_smells.extend(self._detect_primitive_obsession(tree, file_path))
            file_smells.extend(self._detect_speculative_generality(tree, file_path))
            file_smells.extend(self._detect_shotgun_surgery(tree, file_path))
            file_smells.extend(self._detect_divergent_change(tree, file_path))
            file_smells.extend(self._detect_parallel_inheritance(tree, file_path))
            file_smells.extend(self._detect_lazy_class(tree, file_path))
            file_smells.extend(self._detect_inappropriate_intimacy(tree, file_path))
            file_smells.extend(self._detect_message_chains(tree, file_path))
            file_smells.extend(self._detect_middle_man(tree, file_path))
            file_smells.extend(self._detect_incomplete_library_class(tree, file_path))
            file_smells.extend(self._detect_temporary_field(tree, file_path))
            file_smells.extend(self._detect_refused_bequest(tree, file_path))
            file_smells.extend(self._detect_alternative_classes(tree, file_path))
            file_smells.extend(self._detect_duplicate_code_blocks(tree, file_path, content))

            self.smells.extend(file_smells)

            return {
                "file": str(file_path),
                "smells": file_smells,
                "smell_count": len(file_smells),
                "severity_counts": self._count_by_severity(file_smells),
            }

        except Exception as e:
            return {"file": str(file_path), "error": str(e), "smells": [], "smell_count": 0}

    def _detect_long_methods(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect methods that are too long.
        """
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check line count
                if hasattr(node, "end_lineno") and node.end_lineno:
                    lines = node.end_lineno - node.lineno + 1
                    if lines > self.thresholds["long_method_lines"]:
                        smells.append(
                            CodeSmell(
                                type="long_method",
                                severity="high",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Method '{node.name}' is {lines} lines long (threshold: {self.thresholds['long_method_lines']})",
                                suggestion="Consider breaking this method into smaller, more focused methods",
                                confidence=0.9,
                            ),
                        )

                # Check cyclomatic complexity
                complexity = self._calculate_cyclomatic_complexity(node)
                if complexity > self.thresholds["long_method_complexity"]:
                    smells.append(
                        CodeSmell(
                            type="complex_method",
                            severity="high",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Method '{node.name}' has complexity {complexity} (threshold: {self.thresholds['long_method_complexity']})",
                            suggestion="Consider refactoring to reduce complexity",
                            confidence=0.8,
                        ),
                    )

        return smells

    def _detect_large_classes(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect classes that are too large.
        """
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Count methods
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(methods) > self.thresholds["large_class_methods"]:
                    smells.append(
                        CodeSmell(
                            type="large_class",
                            severity="medium",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Class '{node.name}' has {len(methods)} methods (threshold: {self.thresholds['large_class_methods']})",
                            suggestion="Consider splitting this class into smaller, more focused classes",
                            confidence=0.7,
                        ),
                    )

                # Check line count
                if hasattr(node, "end_lineno") and node.end_lineno:
                    lines = node.end_lineno - node.lineno + 1
                    if lines > self.thresholds["large_class_lines"]:
                        smells.append(
                            CodeSmell(
                                type="large_class",
                                severity="high",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Class '{node.name}' is {lines} lines long (threshold: {self.thresholds['large_class_lines']})",
                                suggestion="Consider breaking this class into smaller classes",
                                confidence=0.8,
                            ),
                        )

        return smells

    def _detect_long_parameter_lists(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect methods with too many parameters.
        """
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count parameters
                param_count = len(node.args.args)
                if param_count > self.thresholds["long_parameter_list"]:
                    smells.append(
                        CodeSmell(
                            type="long_parameter_list",
                            severity="medium",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Method '{node.name}' has {param_count} parameters (threshold: {self.thresholds['long_parameter_list']})",
                            suggestion="Consider using a parameter object or builder pattern",
                            confidence=0.7,
                        ),
                    )

        return smells

    def _detect_duplicate_code(
        self, tree: ast.AST, file_path: Path, content: str,
    ) -> list[CodeSmell]:
        """
        Detect duplicate code blocks.
        """
        smells = []

        # Simple duplicate detection based on line similarity
        lines = content.split("\n")
        line_groups = defaultdict(list)

        for i, line in enumerate(lines):
            if len(line.strip()) > 20:  # Only consider substantial lines
                line_groups[line.strip()].append(i + 1)

        for line_content, line_numbers in line_groups.items():
            if len(line_numbers) > 1:
                # Check if lines are close together (potential duplicate block)
                for i in range(len(line_numbers) - 1):
                    if line_numbers[i + 1] - line_numbers[i] < 10:  # Within 10 lines
                        smells.append(
                            CodeSmell(
                                type="duplicate_code",
                                severity="medium",
                                file=str(file_path),
                                line=line_numbers[i],
                                column=0,
                                message=f"Duplicate code found at lines {line_numbers[i]} and {line_numbers[i + 1]}",
                                suggestion="Consider extracting common code into a shared function",
                                confidence=0.6,
                            ),
                        )

        return smells

    def _detect_dead_code(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect dead code (unused functions, variables, etc.)
        """
        smells = []

        # Find all function definitions
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        function_names = {func.name for func in functions}

        # Find all function calls
        calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    calls.append(node.func.attr)

        # Check for unused functions
        for func in functions:
            if func.name not in calls and not func.name.startswith("_"):
                smells.append(
                    CodeSmell(
                        type="dead_code",
                        severity="low",
                        file=str(file_path),
                        line=func.lineno,
                        column=func.col_offset,
                        message=f"Function '{func.name}' appears to be unused",
                        suggestion="Consider removing unused code or adding tests",
                        confidence=0.5,
                    ),
                )

        return smells

    def _detect_magic_numbers(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect magic numbers in code.
        """
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if isinstance(node.value, int) and node.value > 10:
                    smells.append(
                        CodeSmell(
                            type="magic_number",
                            severity="low",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Magic number {node.value} found",
                            suggestion="Consider using a named constant",
                            confidence=0.6,
                        ),
                    )

        return smells

    def _detect_deep_nesting(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect deep nesting levels.
        """
        smells = []

        def check_nesting(node: ast.AST, level: int = 0):
            if level > self.thresholds["deep_nesting"]:
                smells.append(
                    CodeSmell(
                        type="deep_nesting",
                        severity="medium",
                        file=str(file_path),
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"Deep nesting level {level} found",
                        suggestion="Consider refactoring to reduce nesting",
                        confidence=0.7,
                    ),
                )

            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                    check_nesting(child, level + 1)
                else:
                    check_nesting(child, level)

        check_nesting(tree)
        return smells

    def _detect_long_chains(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect long method chaining.
        """
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                chain_length = self._get_chain_length(node)
                if chain_length > self.thresholds["long_chain_calls"]:
                    smells.append(
                        CodeSmell(
                            type="long_chain",
                            severity="medium",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Long method chain of {chain_length} calls found",
                            suggestion="Consider breaking the chain into intermediate variables",
                            confidence=0.6,
                        ),
                    )

        return smells

    def _detect_too_many_returns(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect methods with too many return statements.
        """
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                return_count = len([n for n in ast.walk(node) if isinstance(n, ast.Return)])
                if return_count > self.thresholds["too_many_returns"]:
                    smells.append(
                        CodeSmell(
                            type="too_many_returns",
                            severity="medium",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Method '{node.name}' has {return_count} return statements (threshold: {self.thresholds['too_many_returns']})",
                            suggestion="Consider refactoring to reduce return statements",
                            confidence=0.6,
                        ),
                    )

        return smells

    def _detect_cyclomatic_complexity(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect high cyclomatic complexity.
        """
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_cyclomatic_complexity(node)
                if complexity > self.thresholds["cyclomatic_complexity"]:
                    smells.append(
                        CodeSmell(
                            type="high_complexity",
                            severity="high",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Method '{node.name}' has cyclomatic complexity {complexity} (threshold: {self.thresholds['cyclomatic_complexity']})",
                            suggestion="Consider refactoring to reduce complexity",
                            confidence=0.8,
                        ),
                    )

        return smells

    def _detect_god_objects(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect god objects (classes that do too much)
        """
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for classes with too many responsibilities
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(methods) > 15:  # High threshold for god objects
                    smells.append(
                        CodeSmell(
                            type="god_object",
                            severity="high",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Class '{node.name}' appears to be a god object with {len(methods)} methods",
                            suggestion="Consider splitting into smaller, more focused classes",
                            confidence=0.7,
                        ),
                    )

        return smells

    def _detect_feature_envy(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect feature envy (methods that use more of another class than their own)
        """
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Simple feature envy detection based on external method calls
                external_calls = 0
                internal_calls = 0

                for call in ast.walk(node):
                    if isinstance(call, ast.Call):
                        if isinstance(call.func, ast.Attribute):
                            if isinstance(call.func.value, ast.Name):
                                external_calls += 1
                            else:
                                internal_calls += 1

                if external_calls > internal_calls * 2:  # More external than internal calls
                    smells.append(
                        CodeSmell(
                            type="feature_envy",
                            severity="medium",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Method '{node.name}' shows feature envy (more external calls than internal)",
                            suggestion="Consider moving this method to the class it's most interested in",
                            confidence=0.6,
                        ),
                    )

        return smells

    def _detect_data_clumps(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect data clumps (groups of data that always appear together)
        """
        smells = []

        # This is a simplified implementation
        # In practice, you'd need more sophisticated analysis
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for functions with many parameters of similar types
                params = node.args.args
                if len(params) > 3:
                    # Check if parameters have similar names (indicating they might be related)
                    param_names = [p.arg for p in params]
                    if len(set(param_names)) < len(param_names) * 0.8:  # Many similar names
                        smells.append(
                            CodeSmell(
                                type="data_clump",
                                severity="low",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Function '{node.name}' may have data clumps in parameters",
                                suggestion="Consider grouping related parameters into a data structure",
                                confidence=0.4,
                            ),
                        )

        return smells

    def _detect_primitive_obsession(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect primitive obsession (overuse of primitive types)
        """
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for functions with many string/int parameters that could be objects
                params = node.args.args
                primitive_count = 0
                for param in params:
                    if param.annotation is None:  # No type annotation
                        primitive_count += 1

                if primitive_count > len(params) * 0.7:  # Mostly primitive types
                    smells.append(
                        CodeSmell(
                            type="primitive_obsession",
                            severity="low",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' may have primitive obsession",
                            suggestion="Consider using custom types instead of primitives",
                            confidence=0.4,
                        ),
                    )

        return smells

    def _detect_speculative_generality(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect speculative generality (code written for future use that's never used)
        """
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for functions with generic names that might be speculative
                if any(
                    word in node.name.lower()
                    for word in ["generic", "future", "maybe", "potential"]
                ):
                    smells.append(
                        CodeSmell(
                            type="speculative_generality",
                            severity="low",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' may be speculative generality",
                            suggestion="Consider removing if not actually needed",
                            confidence=0.3,
                        ),
                    )

        return smells

    def _detect_shotgun_surgery(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect shotgun surgery (making changes in many places for one feature)
        """
        smells = []

        # This would require analysis across multiple files
        # For now, we'll detect potential issues within a single file
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for functions that modify many different variables
                assignments = [n for n in ast.walk(node) if isinstance(n, ast.Assign)]
                if len(assignments) > 10:  # Many assignments in one function
                    smells.append(
                        CodeSmell(
                            type="shotgun_surgery",
                            severity="medium",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' may be doing shotgun surgery",
                            suggestion="Consider breaking into smaller, more focused functions",
                            confidence=0.5,
                        ),
                    )

        return smells

    def _detect_divergent_change(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect divergent change (class changes for different reasons)
        """
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for classes with many different types of methods
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                method_types = set()
                for method in methods:
                    if "get" in method.name.lower():
                        method_types.add("getter")
                    elif "set" in method.name.lower():
                        method_types.add("setter")
                    elif "create" in method.name.lower():
                        method_types.add("creator")
                    elif "delete" in method.name.lower():
                        method_types.add("deleter")
                    elif "validate" in method.name.lower():
                        method_types.add("validator")

                if len(method_types) > 4:  # Many different types of methods
                    smells.append(
                        CodeSmell(
                            type="divergent_change",
                            severity="medium",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Class '{node.name}' may have divergent change",
                            suggestion="Consider splitting into classes with single responsibilities",
                            confidence=0.6,
                        ),
                    )

        return smells

    def _detect_parallel_inheritance(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect parallel inheritance hierarchies.
        """
        smells = []

        # This would require analysis across multiple files
        # For now, we'll detect potential issues within a single file
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        for i, class1 in enumerate(classes):
            for class2 in classes[i + 1 :]:
                # Check if classes have similar method names
                methods1 = {m.name for m in class1.body if isinstance(m, ast.FunctionDef)}
                methods2 = {m.name for m in class2.body if isinstance(m, ast.FunctionDef)}

                common_methods = methods1.intersection(methods2)
                if len(common_methods) > len(methods1) * 0.5:  # More than 50% common methods
                    smells.append(
                        CodeSmell(
                            type="parallel_inheritance",
                            severity="medium",
                            file=str(file_path),
                            line=class1.lineno,
                            column=class1.col_offset,
                            message=f"Classes '{class1.name}' and '{class2.name}' may have parallel inheritance",
                            suggestion="Consider using composition or shared base class",
                            confidence=0.5,
                        ),
                    )

        return smells

    def _detect_lazy_class(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect lazy classes (classes that don't do much)
        """
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(methods) < 3:  # Very few methods
                    smells.append(
                        CodeSmell(
                            type="lazy_class",
                            severity="low",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Class '{node.name}' may be a lazy class with only {len(methods)} methods",
                            suggestion="Consider merging with another class or removing",
                            confidence=0.4,
                        ),
                    )

        return smells

    def _detect_inappropriate_intimacy(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect inappropriate intimacy between classes.
        """
        smells = []

        # This would require analysis across multiple files
        # For now, we'll detect potential issues within a single file
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for functions that access many different classes
                class_accesses = set()
                for call in ast.walk(node):
                    if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute):
                        if isinstance(call.func.value, ast.Name):
                            class_accesses.add(call.func.value.id)

                if len(class_accesses) > 5:  # Accessing many different classes
                    smells.append(
                        CodeSmell(
                            type="inappropriate_intimacy",
                            severity="medium",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' accesses many different classes",
                            suggestion="Consider reducing dependencies between classes",
                            confidence=0.5,
                        ),
                    )

        return smells

    def _detect_message_chains(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect message chains (long chains of method calls)
        """
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                chain_length = self._get_chain_length(node)
                if chain_length > 3:  # Long message chain
                    smells.append(
                        CodeSmell(
                            type="message_chain",
                            severity="medium",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Message chain of {chain_length} calls found",
                            suggestion="Consider using intermediate variables or law of demeter",
                            confidence=0.6,
                        ),
                    )

        return smells

    def _detect_middle_man(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect middle man classes (classes that just delegate)
        """
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                delegation_count = 0

                for method in methods:
                    # Check if method just calls another method
                    calls = [n for n in ast.walk(method) if isinstance(n, ast.Call)]
                    if len(calls) == 1:  # Only one call
                        delegation_count += 1

                if delegation_count > len(methods) * 0.7:  # More than 70% delegation
                    smells.append(
                        CodeSmell(
                            type="middle_man",
                            severity="medium",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Class '{node.name}' may be a middle man",
                            suggestion="Consider removing the middle man and calling directly",
                            confidence=0.6,
                        ),
                    )

        return smells

    def _detect_incomplete_library_class(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect incomplete library class usage.
        """
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for classes that extend library classes but don't add much
                if node.bases:  # Has base classes
                    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    if len(methods) < 2:  # Very few methods
                        smells.append(
                            CodeSmell(
                                type="incomplete_library_class",
                                severity="low",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Class '{node.name}' may be incomplete library class",
                                suggestion="Consider using composition instead of inheritance",
                                confidence=0.4,
                            ),
                        )

        return smells

    def _detect_temporary_field(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect temporary fields (fields only used in some methods)
        """
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Find all assignments to self attributes
                assignments = []
                for method in ast.walk(node):
                    if isinstance(method, ast.Assign):
                        for target in method.targets:
                            if (
                                isinstance(target, ast.Attribute)
                                and isinstance(target.value, ast.Name)
                                and target.value.id == "self"
                            ):
                                assignments.append(target.attr)

                # Find all uses of self attributes
                uses = []
                for method in ast.walk(node):
                    if (
                        isinstance(method, ast.Attribute)
                        and isinstance(method.value, ast.Name)
                        and method.value.id == "self"
                    ):
                        uses.append(method.attr)

                # Check for fields that are assigned but rarely used
                for field in set(assignments):
                    if (
                        uses.count(field) < assignments.count(field) * 0.3
                    ):  # Used less than 30% of assignments
                        smells.append(
                            CodeSmell(
                                type="temporary_field",
                                severity="low",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Field '{field}' may be temporary",
                                suggestion="Consider using local variables instead",
                                confidence=0.4,
                            ),
                        )

        return smells

    def _detect_refused_bequest(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect refused bequest (subclasses that don't use inherited methods)
        """
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.bases:  # Has base classes
                    # Check if class overrides many methods without calling super()
                    overrides = []
                    for method in node.body:
                        if isinstance(method, ast.FunctionDef):
                            # Check if this method exists in base class
                            for base in node.bases:
                                if isinstance(base, ast.Name):
                                    overrides.append(method.name)

                    if len(overrides) > 3:  # Many overrides
                        smells.append(
                            CodeSmell(
                                type="refused_bequest",
                                severity="medium",
                                file=str(file_path),
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Class '{node.name}' may be refusing bequest",
                                suggestion="Consider using composition instead of inheritance",
                                confidence=0.5,
                            ),
                        )

        return smells

    def _detect_alternative_classes(self, tree: ast.AST, file_path: Path) -> list[CodeSmell]:
        """
        Detect alternative classes with different interfaces but same data.
        """
        smells = []

        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        for i, class1 in enumerate(classes):
            for class2 in classes[i + 1 :]:
                # Check if classes have similar method names but different interfaces
                methods1 = {m.name for m in class1.body if isinstance(m, ast.FunctionDef)}
                methods2 = {m.name for m in class2.body if isinstance(m, ast.FunctionDef)}

                common_methods = methods1.intersection(methods2)
                if len(common_methods) > 2:  # Some common methods
                    smells.append(
                        CodeSmell(
                            type="alternative_classes",
                            severity="low",
                            file=str(file_path),
                            line=class1.lineno,
                            column=class1.col_offset,
                            message=f"Classes '{class1.name}' and '{class2.name}' may be alternatives",
                            suggestion="Consider unifying the interfaces",
                            confidence=0.4,
                        ),
                    )

        return smells

    def _detect_duplicate_code_blocks(
        self, tree: ast.AST, file_path: Path, content: str,
    ) -> list[CodeSmell]:
        """
        Detect duplicate code blocks using AST comparison.
        """
        smells = []

        # This is a simplified implementation
        # In practice, you'd need more sophisticated AST comparison
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

        for i, func1 in enumerate(functions):
            for func2 in functions[i + 1 :]:
                # Simple similarity check based on structure
                if self._functions_similar(func1, func2):
                    smells.append(
                        CodeSmell(
                            type="duplicate_code_blocks",
                            severity="medium",
                            file=str(file_path),
                            line=func1.lineno,
                            column=func1.col_offset,
                            message=f"Functions '{func1.name}' and '{func2.name}' may be duplicates",
                            suggestion="Consider extracting common code into a shared function",
                            confidence=0.6,
                        ),
                    )

        return smells

    def _functions_similar(self, func1: ast.FunctionDef, func2: ast.FunctionDef) -> bool:
        """
        Check if two functions are similar.
        """
        # Simple similarity check based on structure
        if len(func1.body) != len(func2.body):
            return False

        # Check if they have similar structure
        for stmt1, stmt2 in zip(func1.body, func2.body, strict=False):
            if type(stmt1) != type(stmt2):
                return False

        return True

    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """
        Calculate cyclomatic complexity of a function.
        """
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)) or isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _get_chain_length(self, node: ast.Call) -> int:
        """
        Get the length of a method call chain.
        """
        length = 1
        current = node.func

        while isinstance(current, ast.Attribute):
            length += 1
            current = current.value

        return length

    def _count_by_severity(self, smells: list[CodeSmell]) -> dict[str, int]:
        """
        Count smells by severity.
        """
        counts = defaultdict(int)
        for smell in smells:
            counts[smell.severity] += 1
        return dict(counts)

    def generate_report(self) -> dict[str, Any]:
        """
        Generate comprehensive code smell report.
        """
        total_smells = len(self.smells)
        severity_counts = self._count_by_severity(self.smells)

        # Group by smell type
        smell_types = defaultdict(int)
        for smell in self.smells:
            smell_types[smell.type] += 1

        # Group by file
        file_smells = defaultdict(list)
        for smell in self.smells:
            file_smells[smell.file].append(smell)

        return {
            "summary": {
                "total_smells": total_smells,
                "severity_counts": severity_counts,
                "smell_types": dict(smell_types),
                "files_affected": len(file_smells),
            },
            "smells": [
                {
                    "type": smell.type,
                    "severity": smell.severity,
                    "file": smell.file,
                    "line": smell.line,
                    "column": smell.column,
                    "message": smell.message,
                    "suggestion": smell.suggestion,
                    "confidence": smell.confidence,
                }
                for smell in self.smells
            ],
            "files": {
                file: {
                    "smell_count": len(smells),
                    "severity_counts": self._count_by_severity(smells),
                }
                for file, smells in file_smells.items()
            },
        }


def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description="Code Smell Detector")
    parser.add_argument("path", help="Path to analyze")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--severity", choices=["low", "medium", "high"], help="Filter by severity")
    parser.add_argument("--type", help="Filter by smell type")
    parser.add_argument("--thresholds", help="Path to custom thresholds file")

    args = parser.parse_args()

    detector = CodeSmellDetector()

    # Load custom thresholds if provided
    if args.thresholds:
        with open(args.thresholds) as f:
            custom_thresholds = json.load(f)
            detector.thresholds.update(custom_thresholds)

    # Analyze files
    path = Path(args.path)
    if path.is_file():
        files = [path]
    else:
        files = list(path.rglob("*.py"))

    for file_path in files:
        detector.analyze_file(file_path)

    # Generate report
    report = detector.generate_report()

    # Filter results if requested
    if args.severity or args.type:
        filtered_smells = []
        for smell in report["smells"]:
            if args.severity and smell["severity"] != args.severity:
                continue
            if args.type and smell["type"] != args.type:
                continue
            filtered_smells.append(smell)
        report["smells"] = filtered_smells
        report["summary"]["total_smells"] = len(filtered_smells)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        # Pretty print report
        print("🔍 CODE SMELL DETECTION REPORT")
        print("=" * 50)
        print(f"Total smells found: {report['summary']['total_smells']}")
        print(f"Files affected: {report['summary']['files_affected']}")
        print()

        print("Severity breakdown:")
        for severity, count in report["summary"]["severity_counts"].items():
            print(f"  {severity}: {count}")
        print()

        print("Smell types:")
        for smell_type, count in report["summary"]["smell_types"].items():
            print(f"  {smell_type}: {count}")
        print()

        if report["smells"]:
            print("Detailed findings:")
            for smell in report["smells"]:
                print(
                    f"  {smell['severity'].upper()}: {smell['type']} in {smell['file']}:{smell['line']}",
                )
                print(f"    {smell['message']}")
                print(f"    Suggestion: {smell['suggestion']}")
                print()


if __name__ == "__main__":
    main()
