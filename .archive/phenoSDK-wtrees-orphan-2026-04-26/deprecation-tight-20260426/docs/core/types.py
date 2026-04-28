"""Core types and exceptions for pheno-docs.

This module defines the fundamental types and exceptions used throughout the
documentation system.
"""

import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DocumentationFormat(Enum):
    """
    Documentation output formats.
    """

    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    JSON = "json"
    XML = "xml"
    RST = "rst"

    def __str__(self) -> str:
        return self.value


@dataclass
class DocumentationContent:
    """
    Documentation content structure.
    """

    id: str
    title: str
    content: str
    format: DocumentationFormat
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    author: str | None = None
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not hasattr(self, "id") or not self.id:
            self.id = str(uuid.uuid4())

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for serialization.
        """
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "format": self.format.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "author": self.author,
            "tags": self.tags,
        }


@dataclass
class DocumentationConfig:
    """
    Base documentation configuration.
    """

    output_dir: str = "docs"
    template_dir: str | None = None
    static_dir: str | None = None
    verbose: bool = False
    debug: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GeneratorConfig(DocumentationConfig):
    """
    Documentation generator configuration.
    """

    source_dir: str = "source"
    include_patterns: list[str] = field(default_factory=lambda: ["*.md", "*.py"])
    exclude_patterns: list[str] = field(default_factory=lambda: ["*.pyc", "__pycache__"])
    recursive: bool = True
    overwrite: bool = False
    validate: bool = True


@dataclass
class RendererConfig(DocumentationConfig):
    """
    Documentation renderer configuration.
    """

    input_dir: str = "content"
    output_format: DocumentationFormat = DocumentationFormat.HTML
    theme: str | None = None
    css_file: str | None = None
    js_file: str | None = None
    base_url: str | None = None


@dataclass
class ValidatorConfig(DocumentationConfig):
    """
    Documentation validator configuration.
    """

    check_links: bool = True
    check_format: bool = True
    check_syntax: bool = True
    strict_mode: bool = False
    ignore_patterns: list[str] = field(default_factory=list)


@dataclass
class TemplateConfig(DocumentationConfig):
    """
    Documentation template configuration.
    """

    template_name: str
    variables: dict[str, Any] = field(default_factory=dict)
    partials: dict[str, str] = field(default_factory=dict)
    helpers: dict[str, Callable] = field(default_factory=dict)


# Exception hierarchy
class DocumentationError(Exception):
    """
    Base exception for documentation errors.
    """

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}


class GenerationError(DocumentationError):
    """
    Raised when documentation generation fails.
    """



class RenderingError(DocumentationError):
    """
    Raised when documentation rendering fails.
    """



class ValidationError(DocumentationError):
    """
    Raised when documentation validation fails.
    """



class TemplateError(DocumentationError):
    """
    Raised when template operations fail.
    """



class RegistryError(DocumentationError):
    """
    Raised when registry operations fail.
    """



class ConfigurationError(DocumentationError):
    """
    Raised when configuration is invalid.
    """

