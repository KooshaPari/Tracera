"""Core interfaces for pheno-docs.

This module defines the abstract base classes that all documentation implementations
must follow, ensuring consistency across the system.
"""

from abc import ABC, abstractmethod
from typing import Any

from .types import (
    DocumentationConfig,
    DocumentationContent,
    DocumentationFormat,
    GeneratorConfig,
    RendererConfig,
    TemplateConfig,
    ValidatorConfig,
)


class DocumentationGenerator(ABC):
    """
    Base interface for documentation generators.
    """

    def __init__(self, name: str, config: GeneratorConfig):
        self.name = name
        self.config = config

    @abstractmethod
    def generate_docs(self, source: str, output: str) -> list[DocumentationContent]:
        """Generate documentation from source.

        Args:
            source: Source directory or file
            output: Output directory

        Returns:
            List of generated documentation content
        """

    @abstractmethod
    def update_docs(self, source: str, output: str) -> list[DocumentationContent]:
        """Update existing documentation.

        Args:
            source: Source directory or file
            output: Output directory

        Returns:
            List of updated documentation content
        """

    @abstractmethod
    def validate_source(self, source: str) -> bool:
        """Validate source content.

        Args:
            source: Source directory or file

        Returns:
            True if source is valid
        """

    @abstractmethod
    def get_supported_formats(self) -> list[DocumentationFormat]:
        """Get supported output formats.

        Returns:
            List of supported formats
        """


class DocumentationRenderer(ABC):
    """
    Base interface for documentation renderers.
    """

    def __init__(self, name: str, config: RendererConfig):
        self.name = name
        self.config = config

    @abstractmethod
    def render(self, content: str, format: DocumentationFormat) -> str:
        """Render content to specified format.

        Args:
            content: Content to render
            format: Target format

        Returns:
            Rendered content
        """

    @abstractmethod
    def render_site(self, content_dir: str, output_dir: str) -> None:
        """Render entire documentation site.

        Args:
            content_dir: Content directory
            output_dir: Output directory
        """

    @abstractmethod
    def render_content(self, content: DocumentationContent) -> str:
        """Render documentation content.

        Args:
            content: Documentation content

        Returns:
            Rendered content
        """

    @abstractmethod
    def get_supported_formats(self) -> list[DocumentationFormat]:
        """Get supported output formats.

        Returns:
            List of supported formats
        """


class DocumentationValidator(ABC):
    """
    Base interface for documentation validators.
    """

    def __init__(self, name: str, config: ValidatorConfig):
        self.name = name
        self.config = config

    @abstractmethod
    def validate(self, content: str) -> bool:
        """Validate documentation content.

        Args:
            content: Content to validate

        Returns:
            True if content is valid
        """

    @abstractmethod
    def check_links(self, content: str) -> list[str]:
        """Check for broken links.

        Args:
            content: Content to check

        Returns:
            List of broken links
        """

    @abstractmethod
    def check_format(self, content: str) -> bool:
        """Check content format.

        Args:
            content: Content to check

        Returns:
            True if format is valid
        """

    @abstractmethod
    def validate_site(self, site_dir: str) -> dict[str, Any]:
        """Validate entire documentation site.

        Args:
            site_dir: Site directory to validate

        Returns:
            Validation results
        """


class DocumentationTemplate(ABC):
    """
    Base interface for documentation templates.
    """

    def __init__(self, name: str, config: TemplateConfig):
        self.name = name
        self.config = config

    @abstractmethod
    def render(self, variables: dict[str, Any]) -> str:
        """Render template with variables.

        Args:
            variables: Template variables

        Returns:
            Rendered content
        """

    @abstractmethod
    def get_variables(self) -> list[str]:
        """Get required template variables.

        Returns:
            List of required variables
        """

    @abstractmethod
    def validate_variables(self, variables: dict[str, Any]) -> bool:
        """Validate template variables.

        Args:
            variables: Variables to validate

        Returns:
            True if variables are valid
        """


class DocumentationManager(ABC):
    """
    Base interface for documentation management.
    """

    def __init__(self, name: str, config: DocumentationConfig):
        self.name = name
        self.config = config

    @abstractmethod
    def create_doc(self, content: DocumentationContent) -> str:
        """Create new documentation.

        Args:
            content: Documentation content

        Returns:
            Document ID
        """

    @abstractmethod
    def update_doc(self, doc_id: str, content: DocumentationContent) -> None:
        """Update existing documentation.

        Args:
            doc_id: Document ID
            content: Updated content
        """

    @abstractmethod
    def delete_doc(self, doc_id: str) -> None:
        """Delete documentation.

        Args:
            doc_id: Document ID
        """

    @abstractmethod
    def get_doc(self, doc_id: str) -> DocumentationContent | None:
        """Get documentation by ID.

        Args:
            doc_id: Document ID

        Returns:
            Documentation content or None
        """

    @abstractmethod
    def list_docs(self, filters: dict[str, Any] | None = None) -> list[DocumentationContent]:
        """List documentation with optional filters.

        Args:
            filters: Optional filters

        Returns:
            List of documentation content
        """

    @abstractmethod
    def search_docs(self, query: str) -> list[DocumentationContent]:
        """Search documentation.

        Args:
            query: Search query

        Returns:
            List of matching documentation content
        """
