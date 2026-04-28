#!/usr/bin/env python3
"""Documentation validation script for PhenoSDK.

This script validates the complete documentation structure, checks for:
- Missing files referenced in nav
- Invalid internal links
- Broken external links
- Markdown syntax errors
- Code block formatting
- Coverage of all documented components
"""

import argparse
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
import yaml


class DocumentationValidator:
    """Validates PhenoSDK documentation structure and content."""

    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.mkdocs_file = Path("mkdocs.yml")
        self.errors = []
        self.warnings = []
        self.stats = {
            "files_total": 0,
            "files_valid": 0,
            "links_total": 0,
            "links_valid": 0,
            "external_links": 0,
            "external_valid": 0,
        }

        # File extensions to validate
        self.markdown_extensions = {".md"}

        # Patterns for validation
        self.link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        self.code_block_pattern = re.compile(r"```(\w+)?\n(.*?)\n```", re.DOTALL)
        self.heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

        # Load configuration
        self.load_config()

    def load_config(self):
        """Load MkDocs configuration."""
        try:
            with open(self.mkdocs_file) as f:
                self.config = yaml.safe_load(f)
                self.nav = self.config.get("nav", {})
        except Exception as e:
            self.add_error(f"Failed to load mkdocs.yml: {e}")

    def validate_all(self) -> bool:
        """Run all validation checks."""
        print("🔍 Starting documentation validation...\n")

        # 1. Validate navigation structure
        print("1️⃣ Validating navigation structure...")
        self.validate_navigation()

        # 2. Validate all files
        print("\n2️⃣ Validating files...")
        self.validate_all_files()

        # 3. Validate internal links
        print("\n3️⃣ Validating internal links...")
        self.validate_internal_links()

        # 4. Validate external links
        print("\n4️⃣ Validating external links...")
        self.validate_external_links()

        # 5. Validate markdown structure
        print("\n5️⃣ Validating markdown structure...")
        self.validate_markdown_structure()

        # 6. Validate code blocks
        print("\n6️⃣ Validating code blocks...")
        self.validate_code_blocks()

        # 7. Validate API documentation coverage
        print("\n7️⃣ Validating API documentation coverage...")
        self.validate_api_coverage()

        # 8. Validate image references
        print("\n8️⃣ Validating image references...")
        self.validate_images()

        # Generate report
        print("\n📊 Validation complete!\n")
        self.generate_report()

        return len(self.errors) == 0

    def validate_navigation(self):
        """Validate navigation structure in mkdocs.yml."""

        def validate_nav_item(item, path=""):
            if isinstance(item, dict):
                for key, value in item.items():
                    new_path = f"{path}/{key}" if path else key
                    self.validate_nav_item(value, new_path)
            elif isinstance(item, str):
                # Check if file exists
                file_path = self.docs_dir / item
                if not file_path.exists():
                    self.add_error(f"Navigation file not found: {item}")
                else:
                    self.stats["files_total"] += 1

        validate_nav_item(self.nav)

    def validate_all_files(self):
        """Validate all markdown files."""
        for md_file in self.docs_dir.rglob("*.md"):
            self.stats["files_total"] += 1

            with open(md_file, encoding="utf-8") as f:
                content = f.read()

            if self.validate_markdown_syntax(content):
                self.stats["files_valid"] += 1

    def validate_internal_links(self):
        """Validate all internal links."""
        self.build_link_map()

        for md_file in self.docs_dir.rglob("*.md"):
            with open(md_file, encoding="utf-8") as f:
                content = f.read()

            # Find all links
            for match in self.link_pattern.finditer(content):
                _text, link = match.groups()
                self.stats["links_total"] += 1

                # Check if internal link
                if not link.startswith(("http://", "https://", "mailto:", "tel:", "#")):
                    # Resolve relative link
                    if not link.startswith(("/", "../")):
                        # Relative to current file
                        base_path = md_file.parent.relative_to(self.docs_dir)
                        link_path = self.docs_dir / base_path / link
                    else:
                        # Absolute path
                        link_path = self.docs_dir / link.lstrip("/")

                    # Handle directory/index.md
                    if link_path.is_dir():
                        link_path = link_path / "index.md"
                    elif not link_path.suffix:
                        link_path = link_path.with_suffix(".md")

                    if not link_path.exists():
                        self.add_error(
                            f"Internal link not found: {link} in {md_file.relative_to(self.docs_dir)}",
                        )
                    else:
                        self.stats["links_valid"] += 1

    def validate_external_links(self, timeout=5):
        """Validate external links (with timeout)."""
        external_links = []

        for md_file in self.docs_dir.rglob("*.md"):
            with open(md_file, encoding="utf-8") as f:
                content = f.read()

            # Find all external links
            for match in self.link_pattern.finditer(content):
                _text, link = match.groups()

                if link.startswith(("http://", "https://")):
                    external_links.append((link, md_file.relative_to(self.docs_dir)))
                    self.stats["external_links"] += 1

        # Check links with threading
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_link = {
                executor.submit(self.check_link, url, timeout): url
                for url, _ in external_links
            }

            for future in as_completed(future_to_link):
                url = future_to_link[future]
                try:
                    if future.result():
                        self.stats["external_valid"] += 1
                except Exception as e:
                    self.add_error(f"External link failed: {url} - {e!s}")

    def check_link(self, url: str, timeout: int) -> bool:
        """Check if external link is accessible."""
        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            return response.status_code < 400
        except requests.RequestException:
            try:
                response = requests.get(url, timeout=timeout, allow_redirects=True)
                return response.status_code < 400
            except requests.RequestException:
                return False

    def validate_markdown_structure(self):
        """Validate markdown file structure."""
        required_elements = {
            "api/": ["API documentation"],
            "getting-started/": ["Getting Started", "Installation", "First App"],
            "examples/": ["Examples"],
            "deployment/": ["Deployment"],
        }

        for path, required_headers in required_elements.items():
            dir_path = self.docs_dir / path

            if not dir_path.exists():
                self.add_warning(f"Documentation directory missing: {path}")
                continue

            # Check for required headers
            index_file = dir_path / "index.md"
            if index_file.exists():
                with open(index_file, encoding="utf-8") as f:
                    content = f.read()

                for header in required_headers:
                    if header.lower() not in content.lower():
                        self.add_warning(
                            f"Missing header '{header}' in {index_file.relative_to(self.docs_dir)}",
                        )

    def validate_code_blocks(self):
        """Validate code blocks in markdown."""
        for md_file in self.docs_dir.rglob("*.md"):
            with open(md_file, encoding="utf-8") as f:
                content = f.read()

            # Find all code blocks
            for match in self.code_block_pattern.finditer(content):
                lang, code = match.groups()

                # Check for common issues
                if code and not code.strip():
                    self.add_warning(
                        f"Empty code block in {md_file.relative_to(self.docs_dir)}",
                    )

                # Language-specific checks
                if lang == "python":
                    self.validate_python_code(code, md_file)
                elif lang == "yaml":
                    self.validate_yaml_code(code, md_file)

    def validate_python_code(self, code: str, file: Path):
        """Validate Python code blocks."""
        try:
            compile(code, str(file), "exec")
        except SyntaxError as e:
            self.add_error(
                f"Python syntax error in {file.relative_to(self.docs_dir)}: {e}",
            )

    def validate_yaml_code(self, code: str, file: Path):
        """Validate YAML code blocks."""
        try:
            yaml.safe_load(code)
        except yaml.YAMLError as e:
            self.add_error(
                f"YAML syntax error in {file.relative_to(self.docs_dir)}: {e}",
            )

    def validate_api_coverage(self):
        """Validate API documentation coverage."""
        # Check for documented modules
        api_dir = self.docs_dir / "api"
        if not api_dir.exists():
            self.add_warning("API documentation directory missing")
            return

        # Expected API modules
        expected_modules = [
            "core",
            "adapters",
            "auth",
            "cli",
            "database",
            "storage",
            "testing",
            "llm",
            "vector",
            "workflow",
        ]

        for module in expected_modules:
            module_file = api_dir / f"{module}.md"
            module_dir = api_dir / module

            if not module_file.exists() and not module_dir.exists():
                self.add_warning(f"API module documentation missing: {module}")

    def validate_images(self):
        """Validate image references."""
        image_pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

        for md_file in self.docs_dir.rglob("*.md"):
            with open(md_file, encoding="utf-8") as f:
                content = f.read()

            # Find all images
            for match in image_pattern.finditer(content):
                _alt_text, image_path = match.groups()

                if not image_path.startswith(("http://", "https://")):
                    # Local image
                    img_path = self.docs_dir / image_path
                    if not img_path.exists():
                        self.add_error(
                            f"Image not found: {image_path} in {md_file.relative_to(self.docs_dir)}",
                        )

    def validate_markdown_syntax(self, content: str) -> bool:
        """Basic markdown syntax validation."""
        # Check for balanced code blocks
        backticks = content.count("```")
        if backticks % 2 != 0:
            return False

        # Check for balanced emphasis
        asterisks = content.count("**")
        if asterisks % 2 != 0:
            return False

        underscores = content.count("__")
        return underscores % 2 == 0

    def build_link_map(self) -> dict[str, Path]:
        """Build a map of all files for link validation."""
        link_map = {}

        for md_file in self.docs_dir.rglob("*.md"):
            # Map possible link targets to actual file
            relative_path = md_file.relative_to(self.docs_dir)

            # Map with .md extension
            link_map[str(relative_path)] = md_file

            # Map without .md extension
            link_map[str(relative_path.with_suffix(""))] = md_file

            # Map index pages to directory
            if relative_path.name == "index.md":
                link_map[str(relative_path.parent)] = md_file
                link_map[str(relative_path.parent) + "/"] = md_file

        return link_map

    def add_error(self, message: str):
        """Add an error message."""
        self.errors.append(message)

    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)

    def generate_report(self):
        """Generate and print validation report."""
        print("=" * 80)
        print("VALIDATION REPORT")
        print("=" * 80)

        # Statistics
        print("\n📈 STATISTICS:")
        print(f"  Files: {self.stats['files_valid']}/{self.stats['files_total']} valid")
        print(
            f"  Internal links: {self.stats['links_valid']}/{self.stats['links_total']} valid",
        )
        print(
            f"  External links: {self.stats['external_valid']}/{self.stats['external_links']} valid",
        )

        # Errors
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        else:
            print("\n✅ No errors found!")

        # Warnings
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")

        # Summary
        print("\n" + "=" * 80)
        if not self.errors:
            print("✅ All checks passed! Documentation is ready for deployment.")
            exit_code = 0
        else:
            print(f"❌ {len(self.errors)} error(s) found. Please fix before deploying.")
            exit_code = 1

        print("=" * 80)
        return exit_code

    def export_report(self, output_file: str = "validation-report.json"):
        """Export validation report to JSON file."""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "stats": self.stats,
            "errors": self.errors,
            "warnings": self.warnings,
        }

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"Report exported to {output_file}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Validate PhenoSDK documentation")
    parser.add_argument(
        "--docs-dir",
        default="docs",
        help="Path to documentation directory",
    )
    parser.add_argument(
        "--output",
        help="Output report file (JSON format)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=5,
        help="Timeout for external link checks (seconds)",
    )

    args = parser.parse_args()

    # Create validator
    validator = DocumentationValidator(args.docs_dir)

    # Run validation
    success = validator.validate_all()

    # Export report if requested
    if args.output:
        validator.export_report(args.output)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
