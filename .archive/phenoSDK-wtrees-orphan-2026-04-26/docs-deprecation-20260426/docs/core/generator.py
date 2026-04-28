"""Main documentation generator implementation for pheno-docs.

This module provides the central DocumentationGenerator class that orchestrates all
documentation generation operations across generators, renderers, and validators.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from .interfaces import (
    DocumentationGenerator,
    DocumentationRenderer,
    DocumentationValidator,
)
from .types import (
    DocumentationContent,
    DocumentationFormat,
    GenerationError,
    GeneratorConfig,
)


class DocumentationGeneratorImpl(DocumentationGenerator):
    """
    Main documentation generator implementation.
    """

    def __init__(self, name: str, config: GeneratorConfig):
        super().__init__(name, config)

        self._generators: dict[str, DocumentationGenerator] = {}
        self._renderers: dict[str, DocumentationRenderer] = {}
        self._validators: dict[str, DocumentationValidator] = {}

        # File processing patterns
        self.include_patterns = config.include_patterns
        self.exclude_patterns = config.exclude_patterns
        self.recursive = config.recursive
        self.overwrite = config.overwrite
        self.validate = config.validate

    def generate_docs(self, source: str, output: str) -> list[DocumentationContent]:
        """Generate documentation from source.

        Args:
            source: Source directory or file
            output: Output directory

        Returns:
            List of generated documentation content
        """
        try:
            # Ensure output directory exists
            os.makedirs(output, exist_ok=True)

            # Process source
            if os.path.isfile(source):
                return self._process_file(source, output)
            if os.path.isdir(source):
                return self._process_directory(source, output)
            raise GenerationError(f"Source path does not exist: {source}")

        except Exception as e:
            raise GenerationError(f"Failed to generate documentation: {e}")

    def update_docs(self, source: str, output: str) -> list[DocumentationContent]:
        """Update existing documentation.

        Args:
            source: Source directory or file
            output: Output directory

        Returns:
            List of updated documentation content
        """
        try:
            # Check if output exists
            if not os.path.exists(output):
                return self.generate_docs(source, output)

            # Process source for updates
            if os.path.isfile(source):
                return self._process_file(source, output, update=True)
            if os.path.isdir(source):
                return self._process_directory(source, output, update=True)
            raise GenerationError(f"Source path does not exist: {source}")

        except Exception as e:
            raise GenerationError(f"Failed to update documentation: {e}")

    def validate_source(self, source: str) -> bool:
        """Validate source content.

        Args:
            source: Source directory or file

        Returns:
            True if source is valid
        """
        try:
            if os.path.isfile(source):
                return self._validate_file(source)
            if os.path.isdir(source):
                return self._validate_directory(source)
            return False

        except Exception as e:
            if self.config.verbose:
                print(f"Validation error: {e}")
            return False

    def get_supported_formats(self) -> list[DocumentationFormat]:
        """Get supported output formats.

        Returns:
            List of supported formats
        """
        return [DocumentationFormat.MARKDOWN, DocumentationFormat.HTML]

    def add_generator(self, name: str, generator: DocumentationGenerator) -> None:
        """
        Add a documentation generator.
        """
        self._generators[name] = generator

    def add_renderer(self, name: str, renderer: DocumentationRenderer) -> None:
        """
        Add a documentation renderer.
        """
        self._renderers[name] = renderer

    def add_validator(self, name: str, validator: DocumentationValidator) -> None:
        """
        Add a documentation validator.
        """
        self._validators[name] = validator

    def _process_file(
        self, source_file: str, output_dir: str, update: bool = False,
    ) -> list[DocumentationContent]:
        """
        Process a single file.
        """
        content_list = []

        try:
            # Read source file
            with open(source_file, encoding="utf-8") as f:
                content = f.read()

            # Determine output format
            output_format = self._get_output_format(source_file)

            # Create documentation content
            doc_content = DocumentationContent(
                id=f"doc_{Path(source_file).stem}",
                title=Path(source_file).stem.replace("_", " ").title(),
                content=content,
                format=output_format,
                metadata={
                    "source_file": source_file,
                    "generated_at": datetime.now().isoformat(),
                    "generator": self.name,
                },
            )

            # Validate if required
            if self.validate and not self._validate_content(doc_content):
                if self.config.verbose:
                    print(f"Warning: Content validation failed for {source_file}")

            # Generate output file
            output_file = self._generate_output_file(doc_content, output_dir)

            # Copy to output directory
            if self.overwrite or not os.path.exists(output_file):
                shutil.copy2(source_file, output_file)
                if self.config.verbose:
                    print(f"Generated: {output_file}")

            content_list.append(doc_content)

        except Exception as e:
            if self.config.verbose:
                print(f"Error processing file {source_file}: {e}")

        return content_list

    def _process_directory(
        self, source_dir: str, output_dir: str, update: bool = False,
    ) -> list[DocumentationContent]:
        """
        Process a directory recursively.
        """
        content_list = []

        try:
            # Create output directory structure
            os.makedirs(output_dir, exist_ok=True)

            # Walk through source directory
            for root, dirs, files in os.walk(source_dir):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not self._should_exclude(d)]

                # Process files
                for file in files:
                    if self._should_include(file):
                        source_file = os.path.join(root, file)
                        relative_path = os.path.relpath(source_file, source_dir)
                        file_output_dir = os.path.join(output_dir, os.path.dirname(relative_path))

                        # Process file
                        file_content = self._process_file(source_file, file_output_dir, update)
                        content_list.extend(file_content)

        except Exception as e:
            if self.config.verbose:
                print(f"Error processing directory {source_dir}: {e}")

        return content_list

    def _validate_file(self, file_path: str) -> bool:
        """
        Validate a single file.
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Basic validation
            if not content.strip():
                return False

            # Check file extension
            if not self._should_include(file_path):
                return False

            return True

        except Exception:
            return False

    def _validate_directory(self, dir_path: str) -> bool:
        """
        Validate a directory.
        """
        try:
            if not os.path.isdir(dir_path):
                return False

            # Check if directory contains valid files
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    if self._should_include(file):
                        file_path = os.path.join(root, file)
                        if not self._validate_file(file_path):
                            return False

            return True

        except Exception:
            return False

    def _validate_content(self, content: DocumentationContent) -> bool:
        """
        Validate documentation content.
        """
        try:
            # Basic content validation
            if not content.content.strip():
                return False

            # Use validators if available
            for validator in self._validators.values():
                if not validator.validate(content.content):
                    return False

            return True

        except Exception:
            return False

    def _should_include(self, filename: str) -> bool:
        """
        Check if file should be included.
        """
        for pattern in self.include_patterns:
            if filename.endswith(pattern.replace("*", "")):
                return True
        return False

    def _should_exclude(self, dirname: str) -> bool:
        """
        Check if directory should be excluded.
        """
        for pattern in self.exclude_patterns:
            if dirname.startswith(pattern.replace("*", "")):
                return True
        return False

    def _get_output_format(self, source_file: str) -> DocumentationFormat:
        """
        Determine output format from source file.
        """
        ext = Path(source_file).suffix.lower()

        if ext == ".md":
            return DocumentationFormat.MARKDOWN
        if ext == ".html":
            return DocumentationFormat.HTML
        if ext == ".rst":
            return DocumentationFormat.RST
        return DocumentationFormat.MARKDOWN

    def _generate_output_file(self, content: DocumentationContent, output_dir: str) -> str:
        """
        Generate output file path.
        """
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Generate filename
        filename = f"{content.id}.{content.format.value}"
        return os.path.join(output_dir, filename)


# Global documentation generator registry
_documentation_generators: dict[str, DocumentationGeneratorImpl] = {}


def get_documentation_generator(
    name: str = "default", config: GeneratorConfig | None = None,
) -> DocumentationGeneratorImpl:
    """Get or create a documentation generator.

    Args:
        name: Generator name
        config: Generator configuration

    Returns:
        Documentation generator instance
    """
    if name not in _documentation_generators:
        _documentation_generators[name] = DocumentationGeneratorImpl(
            name, config or GeneratorConfig(),
        )
    return _documentation_generators[name]


def configure_documentation(config: dict[str, Any]) -> None:
    """Configure global documentation.

    Args:
        config: Documentation configuration
    """
    # This would configure global documentation settings
    # For now, it's a placeholder


def shutdown_documentation() -> None:
    """
    Shutdown all documentation generators.
    """
    _documentation_generators.clear()
