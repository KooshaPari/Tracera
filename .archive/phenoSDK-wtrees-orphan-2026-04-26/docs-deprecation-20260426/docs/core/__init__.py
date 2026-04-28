"""Core documentation interfaces and types.

This module provides the foundational interfaces and types for the pheno-docs library,
ensuring consistency across all documentation implementations.
"""

from .generator import DocumentationGenerator as DocumentationGeneratorImpl
from .interfaces import (
    DocumentationContent,
    DocumentationError,
    DocumentationFormat,
    DocumentationGenerator,
    DocumentationManager,
    DocumentationRenderer,
    DocumentationTemplate,
    DocumentationValidator,
    GenerationError,
    RenderingError,
    ValidationError,
)
from .types import (
    DocumentationConfig,
    DocumentationContent,
    DocumentationError,
    DocumentationFormat,
    GenerationError,
    GeneratorConfig,
    RendererConfig,
    RenderingError,
    TemplateConfig,
    TemplateError,
    ValidationError,
    ValidatorConfig,
)

__all__ = [
    "DocumentationConfig",
    "DocumentationContent",
    "DocumentationError",
    "DocumentationFormat",
    "DocumentationGenerator",
    "DocumentationGeneratorImpl",
    "DocumentationManager",
    "DocumentationRenderer",
    "DocumentationTemplate",
    "DocumentationValidator",
    "GenerationError",
    "GeneratorConfig",
    "RendererConfig",
    "RenderingError",
    "TemplateConfig",
    "TemplateError",
    "ValidationError",
    "ValidatorConfig",
]
