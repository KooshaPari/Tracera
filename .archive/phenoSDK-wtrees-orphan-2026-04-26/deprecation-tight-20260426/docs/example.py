"""Example usage of pheno-docs library.

This module demonstrates how to use the unified documentation library for various
documentation scenarios.
"""

from . import GeneratorConfig, get_documentation_generator
from .generators import MarkdownGenerator


def main():
    """
    Example usage of the documentation library.
    """

    # Example 1: Basic documentation generation
    print("=== Basic Documentation Generation Example ===")

    # Create documentation generator
    config = GeneratorConfig(source_dir="source", output_dir="docs", verbose=True, validate=True)
    generator = get_documentation_generator("my_docs", config)

    print(f"✅ Documentation generator created with {len(generator._generators)} generators")

    # Example 2: Markdown documentation generation
    print("\n=== Markdown Documentation Generation Example ===")

    # Create markdown generator
    markdown_config = GeneratorConfig(
        source_dir="source",
        output_dir="docs",
        verbose=True,
        validate=True,
        metadata={
            "process_toc": True,
            "process_links": True,
            "process_images": True,
            "process_code_blocks": True,
        },
    )
    markdown_generator = MarkdownGenerator("markdown", markdown_config)
    generator.add_generator("markdown", markdown_generator)

    print(
        f"✅ Markdown generator added with supported formats: {markdown_generator.get_supported_formats()}",
    )

    # Example 3: Generate documentation from source
    print("\n=== Documentation Generation Example ===")

    # Create sample markdown content
    sample_content = """# Sample Documentation

This is a sample markdown document for testing the documentation generator.

## Features

- **Unified Interface**: Single API for all documentation operations
- **Multi-format Support**: Markdown, HTML, PDF, and more
- **Template System**: Easy template-based documentation creation
- **Validation**: Comprehensive documentation validation

## Usage

```python
from pheno_docs import get_documentation_generator

# Create generator
generator = get_documentation_generator("my_docs")

# Generate documentation
results = generator.generate_docs("source/", "output/")
```

## Configuration

The documentation generator supports various configuration options:

- `source_dir`: Source directory for documentation
- `output_dir`: Output directory for generated docs
- `verbose`: Enable verbose output
- `validate`: Enable content validation

## Examples

### Basic Generation

```python
# Generate all documentation
results = generator.generate_docs("source/", "output/")
```

### Update Documentation

```python
# Update existing documentation
results = generator.update_docs("source/", "output/")
```

### Validate Source

```python
# Validate source content
is_valid = generator.validate_source("source/")
```

## Conclusion

The pheno-docs library provides a comprehensive solution for documentation management across the pheno-sdk ecosystem.
"""

    # Write sample content to file
    import os

    os.makedirs("source", exist_ok=True)
    with open("source/sample.md", "w") as f:
        f.write(sample_content)

    print("✅ Sample markdown content created")

    # Generate documentation
    try:
        results = generator.generate_docs("source/", "docs/")
        print(f"✅ Generated {len(results)} documentation files")

        for result in results:
            print(f"  📄 {result.title} ({result.format.value})")
            print(f"    ID: {result.id}")
            print(f"    Word count: {result.metadata.get('word_count', 'N/A')}")
            print(f"    Line count: {result.metadata.get('line_count', 'N/A')}")

    except Exception as e:
        print(f"❌ Error generating documentation: {e}")

    # Example 4: Documentation validation
    print("\n=== Documentation Validation Example ===")

    # Validate source
    try:
        is_valid = generator.validate_source("source/")
        print(f"✅ Source validation: {'PASSED' if is_valid else 'FAILED'}")
    except Exception as e:
        print(f"❌ Validation error: {e}")

    # Example 5: Multiple format support
    print("\n=== Multiple Format Support Example ===")

    # Check supported formats
    supported_formats = generator.get_supported_formats()
    print(f"✅ Supported formats: {[f.value for f in supported_formats]}")

    # Example 6: Advanced configuration
    print("\n=== Advanced Configuration Example ===")

    # Advanced generator configuration
    advanced_config = GeneratorConfig(
        source_dir="source",
        output_dir="docs",
        verbose=True,
        validate=True,
        recursive=True,
        overwrite=True,
        include_patterns=["*.md", "*.rst"],
        exclude_patterns=["*.pyc", "__pycache__"],
        metadata={
            "process_toc": True,
            "process_links": True,
            "process_images": True,
            "process_code_blocks": True,
            "generate_index": True,
            "include_metadata": True,
        },
    )

    advanced_generator = get_documentation_generator("advanced_docs", advanced_config)
    print("✅ Advanced generator configured:")
    print(f"  Source directory: {advanced_config.source_dir}")
    print(f"  Output directory: {advanced_config.output_dir}")
    print(f"  Recursive: {advanced_config.recursive}")
    print(f"  Overwrite: {advanced_config.overwrite}")
    print(f"  Include patterns: {advanced_config.include_patterns}")
    print(f"  Exclude patterns: {advanced_config.exclude_patterns}")

    # Example 7: Documentation content management
    print("\n=== Documentation Content Management Example ===")

    # Create documentation content
    from datetime import datetime

    from .core.types import DocumentationContent, DocumentationFormat

    doc_content = DocumentationContent(
        id="example_doc",
        title="Example Documentation",
        content="This is an example documentation content.",
        format=DocumentationFormat.MARKDOWN,
        metadata={
            "author": "Pheno-Docs",
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
        },
        tags=["example", "documentation", "test"],
    )

    print("✅ Documentation content created:")
    print(f"  ID: {doc_content.id}")
    print(f"  Title: {doc_content.title}")
    print(f"  Format: {doc_content.format.value}")
    print(f"  Author: {doc_content.author}")
    print(f"  Tags: {doc_content.tags}")

    # Example 8: Documentation statistics
    print("\n=== Documentation Statistics Example ===")

    # Calculate statistics
    total_docs = len(results) if "results" in locals() else 0
    total_words = (
        sum(r.metadata.get("word_count", 0) for r in results) if "results" in locals() else 0
    )
    total_lines = (
        sum(r.metadata.get("line_count", 0) for r in results) if "results" in locals() else 0
    )

    print("📊 Documentation Statistics:")
    print(f"  Total documents: {total_docs}")
    print(f"  Total words: {total_words}")
    print(f"  Total lines: {total_lines}")
    print(f"  Average words per document: {total_words // max(total_docs, 1)}")
    print(f"  Average lines per document: {total_lines // max(total_docs, 1)}")

    # Example 9: Error handling
    print("\n=== Error Handling Example ===")

    # Test error handling
    try:
        # Try to generate from non-existent source
        results = generator.generate_docs("non_existent/", "output/")
        print("❌ Expected error but got results")
    except Exception as e:
        print(f"✅ Error handling works: {type(e).__name__}: {e}")

    # Example 10: Cleanup
    print("\n=== Cleanup Example ===")

    # Clean up generated files
    import shutil

    try:
        if os.path.exists("source"):
            shutil.rmtree("source")
        if os.path.exists("docs"):
            shutil.rmtree("docs")
        print("✅ Cleanup completed")
    except Exception as e:
        print(f"❌ Cleanup error: {e}")

    print("\n✅ All documentation examples completed!")


if __name__ == "__main__":
    main()
