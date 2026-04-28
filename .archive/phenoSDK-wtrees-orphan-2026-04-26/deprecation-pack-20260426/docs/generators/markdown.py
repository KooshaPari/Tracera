"""Markdown documentation generator for pheno-docs.

This module provides a markdown-specific documentation generator with enhanced markdown
processing capabilities.
"""

import os
import re
from pathlib import Path

from ..core.interfaces import DocumentationGenerator
from ..core.types import (
    DocumentationContent,
    DocumentationFormat,
    GenerationError,
    GeneratorConfig,
)


class MarkdownGenerator(DocumentationGenerator):
    """
    Markdown documentation generator.
    """

    supported_formats = [DocumentationFormat.MARKDOWN]

    def __init__(self, name: str, config: GeneratorConfig):
        super().__init__(name, config)

        # Markdown processing options
        self.process_toc = config.metadata.get("process_toc", True)
        self.process_links = config.metadata.get("process_links", True)
        self.process_images = config.metadata.get("process_images", True)
        self.process_code_blocks = config.metadata.get("process_code_blocks", True)

    def generate_docs(self, source: str, output: str) -> list[DocumentationContent]:
        """Generate markdown documentation from source.

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
                return self._process_markdown_file(source, output)
            if os.path.isdir(source):
                return self._process_markdown_directory(source, output)
            raise GenerationError(f"Source path does not exist: {source}")

        except Exception as e:
            raise GenerationError(f"Failed to generate markdown documentation: {e}")

    def update_docs(self, source: str, output: str) -> list[DocumentationContent]:
        """Update existing markdown documentation.

        Args:
            source: Source directory or file
            output: Output directory

        Returns:
            List of updated documentation content
        """
        return self.generate_docs(source, output)

    def validate_source(self, source: str) -> bool:
        """Validate markdown source content.

        Args:
            source: Source directory or file

        Returns:
            True if source is valid
        """
        try:
            if os.path.isfile(source):
                return self._validate_markdown_file(source)
            if os.path.isdir(source):
                return self._validate_markdown_directory(source)
            return False

        except Exception as e:
            if self.config.verbose:
                print(f"Markdown validation error: {e}")
            return False

    def get_supported_formats(self) -> list[DocumentationFormat]:
        """Get supported output formats.

        Returns:
            List of supported formats
        """
        return self.supported_formats

    def _process_markdown_file(
        self, source_file: str, output_dir: str,
    ) -> list[DocumentationContent]:
        """
        Process a single markdown file.
        """
        content_list = []

        try:
            # Read source file
            with open(source_file, encoding="utf-8") as f:
                content = f.read()

            # Process markdown content
            processed_content = self._process_markdown_content(content, source_file)

            # Create documentation content
            doc_content = DocumentationContent(
                id=f"md_{Path(source_file).stem}",
                title=self._extract_title(processed_content),
                content=processed_content,
                format=DocumentationFormat.MARKDOWN,
                metadata={
                    "source_file": source_file,
                    "generated_at": self._get_timestamp(),
                    "generator": self.name,
                    "word_count": len(processed_content.split()),
                    "line_count": len(processed_content.splitlines()),
                },
            )

            # Generate output file
            output_file = self._generate_markdown_output(doc_content, output_dir)

            # Write processed content
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(processed_content)

            if self.config.verbose:
                print(f"Generated markdown: {output_file}")

            content_list.append(doc_content)

        except Exception as e:
            if self.config.verbose:
                print(f"Error processing markdown file {source_file}: {e}")

        return content_list

    def _process_markdown_directory(
        self, source_dir: str, output_dir: str,
    ) -> list[DocumentationContent]:
        """
        Process a directory of markdown files.
        """
        content_list = []

        try:
            # Create output directory structure
            os.makedirs(output_dir, exist_ok=True)

            # Walk through source directory
            for root, dirs, files in os.walk(source_dir):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not self._should_exclude(d)]

                # Process markdown files
                for file in files:
                    if file.endswith(".md") and self._should_include(file):
                        source_file = os.path.join(root, file)
                        relative_path = os.path.relpath(source_file, source_dir)
                        file_output_dir = os.path.join(output_dir, os.path.dirname(relative_path))

                        # Process file
                        file_content = self._process_markdown_file(source_file, file_output_dir)
                        content_list.extend(file_content)

        except Exception as e:
            if self.config.verbose:
                print(f"Error processing markdown directory {source_dir}: {e}")

        return content_list

    def _process_markdown_content(self, content: str, source_file: str) -> str:
        """
        Process markdown content with enhancements.
        """
        processed = content

        # Process table of contents
        if self.process_toc:
            processed = self._process_table_of_contents(processed)

        # Process links
        if self.process_links:
            processed = self._process_links(processed, source_file)

        # Process images
        if self.process_images:
            processed = self._process_images(processed, source_file)

        # Process code blocks
        if self.process_code_blocks:
            processed = self._process_code_blocks(processed)

        return processed

    def _process_table_of_contents(self, content: str) -> str:
        """
        Process table of contents generation.
        """
        # Look for TOC markers
        toc_pattern = r"<!-- TOC -->(.*?)<!-- /TOC -->"

        def generate_toc(match):
            # Extract headings from content
            headings = re.findall(r"^(#{1,6})\s+(.+)$", content, re.MULTILINE)

            if not headings:
                return match.group(0)

            toc_lines = []
            for level, title in headings:
                indent = "  " * (len(level) - 1)
                anchor = re.sub(r"[^a-zA-Z0-9\s-]", "", title.lower()).replace(" ", "-")
                toc_lines.append(f"{indent}- [{title}](#{anchor})")

            return f"<!-- TOC -->\n{chr(10).join(toc_lines)}\n<!-- /TOC -->"

        return re.sub(toc_pattern, generate_toc, content, flags=re.DOTALL)

    def _process_links(self, content: str, source_file: str) -> str:
        """
        Process and validate links.
        """

        # Convert relative links to absolute paths
        def process_link(match):
            link_text = match.group(1)
            link_url = match.group(2)

            # Skip external links
            if link_url.startswith(("http://", "https://", "mailto:")):
                return match.group(0)

            # Convert relative links
            if link_url.startswith("./") or not link_url.startswith("/"):
                source_dir = os.path.dirname(source_file)
                abs_url = os.path.normpath(os.path.join(source_dir, link_url))
                return f"[{link_text}]({abs_url})"

            return match.group(0)

        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        return re.sub(link_pattern, process_link, content)

    def _process_images(self, content: str, source_file: str) -> str:
        """
        Process and validate images.
        """

        # Convert relative image paths to absolute paths
        def process_image(match):
            alt_text = match.group(1)
            img_url = match.group(2)

            # Skip external images
            if img_url.startswith(("http://", "https://")):
                return match.group(0)

            # Convert relative image paths
            if img_url.startswith("./") or not img_url.startswith("/"):
                source_dir = os.path.dirname(source_file)
                abs_url = os.path.normpath(os.path.join(source_dir, img_url))
                return f"![{alt_text}]({abs_url})"

            return match.group(0)

        img_pattern = r"!\[([^\]]*)\]\(([^)]+)\)"
        return re.sub(img_pattern, process_image, content)

    def _process_code_blocks(self, content: str) -> str:
        """
        Process code blocks with syntax highlighting.
        """

        # Add line numbers to code blocks if not present
        def process_code_block(match):
            language = match.group(1) or ""
            code = match.group(2)

            # Add line numbers for certain languages
            if language in ["python", "javascript", "typescript", "java", "cpp"]:
                lines = code.split("\n")
                numbered_lines = []
                for i, line in enumerate(lines, 1):
                    numbered_lines.append(f"{i:3d}: {line}")
                code = "\n".join(numbered_lines)

            return f"```{language}\n{code}\n```"

        code_pattern = r"```(\w+)?\n(.*?)\n```"
        return re.sub(code_pattern, process_code_block, content, flags=re.DOTALL)

    def _extract_title(self, content: str) -> str:
        """
        Extract title from markdown content.
        """
        # Look for first heading
        heading_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if heading_match:
            return heading_match.group(1).strip()

        # Fallback to filename
        return "Untitled Document"

    def _generate_markdown_output(self, content: DocumentationContent, output_dir: str) -> str:
        """
        Generate output file path for markdown content.
        """
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Generate filename
        filename = f"{content.id}.md"
        return os.path.join(output_dir, filename)

    def _validate_markdown_file(self, file_path: str) -> bool:
        """
        Validate a single markdown file.
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Basic markdown validation
            if not content.strip():
                return False

            # Check for valid markdown structure
            if not re.search(r"^#+\s+", content, re.MULTILINE):
                # No headings found, might be valid but not well-structured
                pass

            return True

        except Exception:
            return False

    def _validate_markdown_directory(self, dir_path: str) -> bool:
        """
        Validate a directory of markdown files.
        """
        try:
            if not os.path.isdir(dir_path):
                return False

            # Check if directory contains valid markdown files
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    if file.endswith(".md"):
                        file_path = os.path.join(root, file)
                        if not self._validate_markdown_file(file_path):
                            return False

            return True

        except Exception:
            return False

    def _should_include(self, filename: str) -> bool:
        """
        Check if file should be included.
        """
        return filename.endswith(".md")

    def _should_exclude(self, dirname: str) -> bool:
        """
        Check if directory should be excluded.
        """
        return dirname.startswith(".") or dirname in ["__pycache__", "node_modules"]

    def _get_timestamp(self) -> str:
        """
        Get current timestamp.
        """
        from datetime import datetime

        return datetime.now().isoformat()
