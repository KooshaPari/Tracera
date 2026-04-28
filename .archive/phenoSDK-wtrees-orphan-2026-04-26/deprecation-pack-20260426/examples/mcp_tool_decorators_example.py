"""MCP Tool Decorators - Comprehensive Integration Examples.

This module demonstrates real-world usage patterns for MCP tool decorators
across different frameworks and scenarios.

Features Demonstrated:
    1. Basic tool registration with auto-schema
    2. Multi-framework conversion (FastMCP, LangChain, Anthropic)
    3. Input validation and type coercion
    4. Error handling and deprecation
    5. Batch tool registration
    6. Framework-specific integration

Run with: python examples/mcp_tool_decorators_example.py
"""

import asyncio
import json
import logging
from typing import Any

from pheno.mcp.tools import (
    ToolFramework,
    coerce_types,
    deprecated,
    generate_schema_from_signature,
    mcp_tool,
    register_mcp_tools,
    to_anthropic_tool,
    to_fastmcp_tool,
    to_langchain_tool,
    validate_tool_input,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# SECTION 1: Basic Tool Registration with Auto-Schema
# ============================================================================


@mcp_tool(
    name="analyze_code",
    description="Analyze Python code structure and return metrics",
    category="code_analysis",
    tags=["python", "analysis", "static"],
)
async def analyze_code(file_path: str, depth: int = 1, show_complexity: bool = False) -> dict:
    """Analyze code structure and return comprehensive metrics.

    Args:
        file_path: Path to Python file to analyze
        depth: Analysis depth (1-5, default 1)
        show_complexity: Include cyclomatic complexity analysis

    Returns:
        Dictionary with analysis results
    """
    await asyncio.sleep(0.1)  # Simulate I/O

    metrics = {
        "file": file_path,
        "lines_of_code": 150,
        "functions": 5,
        "classes": 2,
        "depth": depth,
    }

    if show_complexity:
        metrics["complexity"] = {"avg": 2.5, "max": 4}

    return metrics


@mcp_tool(
    name="format_code",
    description="Format Python code according to PEP 8 standards",
    category="code_formatting",
    tags=["python", "formatting"],
)
def format_code(file_path: str, line_length: int = 88, use_tabs: bool = False) -> dict:
    """Format code with customizable options.

    Args:
        file_path: Path to file to format
        line_length: Line length limit (default 88)
        use_tabs: Use tabs instead of spaces

    Returns:
        Formatting results
    """
    return {
        "file": file_path,
        "formatted": True,
        "lines": 150,
        "changes": 12,
        "config": {"line_length": line_length, "use_tabs": use_tabs},
    }


@mcp_tool(
    name="document_code",
    description="Generate documentation for Python code",
    category="documentation",
    tags=["python", "docs", "ai"],
)
async def document_code(
    file_path: str, style: str = "google", include_examples: bool = True
) -> dict:
    """Generate comprehensive documentation.

    Args:
        file_path: Path to code file
        style: Documentation style (google, numpy, sphinx)
        include_examples: Include usage examples

    Returns:
        Generated documentation metadata
    """
    await asyncio.sleep(0.2)  # Simulate processing

    return {
        "file": file_path,
        "style": style,
        "docstrings": 7,
        "examples": 3 if include_examples else 0,
        "coverage": "85%",
    }


# ============================================================================
# SECTION 2: Advanced Features - Validation & Type Coercion
# ============================================================================


@mcp_tool(
    name="process_data", validate_inputs=True, description="Process data with strict validation"
)
def process_data(count: int, threshold: float, tags: list[str] = None) -> dict:
    """Process data with strict validation.

    Args:
        count: Number of items to process
        threshold: Processing threshold
        tags: Optional list of tags

    Returns:
        Processing results
    """
    return {
        "processed": count,
        "threshold": threshold,
        "tags": tags or [],
        "success": count > 0 and threshold > 0,
    }


@mcp_tool(
    name="train_model",
    validate_inputs=True,
    coerce_types=True,
    description="Train ML model with automatic type coercion",
)
async def train_model(
    epochs: int, learning_rate: float, batch_size: int, save_best: bool = False
) -> dict:
    """Train ML model with automatic type coercion.

    Args:
        epochs: Number of training epochs
        learning_rate: Learning rate (0.0-1.0)
        batch_size: Batch size
        save_best: Save best model checkpoint

    Returns:
        Training results
    """
    await asyncio.sleep(0.15)

    return {
        "epochs": epochs,
        "learning_rate": learning_rate,
        "batch_size": batch_size,
        "final_loss": 0.0523,
        "best_saved": save_best,
    }


# ============================================================================
# SECTION 3: Error Handling & Deprecation
# ============================================================================


@mcp_tool(name="risky_operation", description="Operation that might fail with error handling")
async def risky_operation(value: float, operation: str = "sqrt") -> dict:
    """Operation that might fail with error handling.

    Args:
        value: Input value
        operation: Operation type (sqrt, log, reciprocal)

    Returns:
        Operation result or error dict
    """
    if operation == "sqrt":
        if value < 0:
            raise ValueError("Cannot compute sqrt of negative number")
        return {"result": value**0.5, "operation": operation}
    elif operation == "log":
        if value <= 0:
            raise ValueError("Log requires positive number")
        import math

        return {"result": math.log(value), "operation": operation}
    elif operation == "reciprocal":
        if value == 0:
            raise ValueError("Cannot divide by zero")
        return {"result": 1 / value, "operation": operation}
    else:
        raise ValueError(f"Unknown operation: {operation}")


@deprecated("Use search_v2 instead", version="2.0")
@mcp_tool(name="search_v1", category="search", tags=["deprecated"])
def search_v1(query: str, limit: int = 10) -> dict:
    """Deprecated search function.

    Args:
        query: Search query
        limit: Result limit

    Returns:
        Search results
    """
    return {"query": query, "results": [], "count": 0, "version": 1}


@mcp_tool(name="search_v2", category="search", tags=["current"], version="2.0")
async def search_v2(query: str, limit: int = 10, filter_by: str = None) -> dict:
    """Improved search function (v2).

    Args:
        query: Search query
        limit: Result limit
        filter_by: Optional filter

    Returns:
        Search results with pagination
    """
    await asyncio.sleep(0.1)

    return {
        "query": query,
        "results": [{"id": i, "title": f"Result {i}"} for i in range(min(limit, 5))],
        "count": min(limit, 5),
        "filter": filter_by,
        "version": 2,
    }


# ============================================================================
# SECTION 4: Framework-Specific Declarations
# ============================================================================


@mcp_tool(
    name="fastmcp_specific",
    framework=ToolFramework.FASTMCP,
    tags=["mcp", "fastmcp"],
)
async def fastmcp_specific_tool(query: str) -> dict:
    """Tool optimized for FastMCP framework.

    Args:
        query: Query string

    Returns:
        Results
    """
    return {"query": query, "framework": "fastmcp", "optimized": True}


@mcp_tool(
    name="langchain_specific",
    framework=ToolFramework.LANGCHAIN,
    tags=["chain", "agent"],
)
def langchain_specific_tool(input_text: str, format: str = "json") -> str:
    """Tool optimized for LangChain.

    Args:
        input_text: Input text
        format: Output format (json, text, csv)

    Returns:
        Formatted output
    """
    return json.dumps({"input": input_text, "format": format, "status": "processed"})


@mcp_tool(
    name="anthropic_specific",
    framework=ToolFramework.ANTHROPIC,
    tags=["claude", "anthropic"],
)
def anthropic_specific_tool(prompt: str, max_tokens: int = 1000) -> dict:
    """Tool optimized for Anthropic Claude.

    Args:
        prompt: Input prompt
        max_tokens: Maximum tokens

    Returns:
        Processing metadata
    """
    return {
        "prompt_length": len(prompt),
        "max_tokens": max_tokens,
        "estimated_cost": max_tokens * 0.0001,
    }


# ============================================================================
# SECTION 5: Demonstration Functions
# ============================================================================


def demo_basic_registration():
    """
    Demonstrate basic tool registration and schema generation.
    """
    print("\n" + "=" * 70)
    print("DEMO 1: Basic Tool Registration & Schema Generation")
    print("=" * 70)

    # Access metadata
    metadata = analyze_code.__mcp_metadata__
    print(f"\nTool Name: {metadata.name}")
    print(f"Description: {metadata.description}")
    print(f"Category: {metadata.annotations['category']}")
    print(f"Tags: {metadata.annotations['tags']}")

    # Show schema
    schema = metadata.schema
    print(f"\nGenerated Schema:")
    print(json.dumps(schema, indent=2))

    # Show required vs optional fields
    required = schema.get("required", [])
    properties = schema.get("properties", {})

    print(f"\nRequired fields: {required}")
    print("Optional fields:")
    for field_name, field_info in properties.items():
        if field_name not in required:
            default = field_info.get("default", "None")
            print(f"  - {field_name} (default: {default})")


def demo_validation_and_coercion():
    """
    Demonstrate input validation and type coercion.
    """
    print("\n" + "=" * 70)
    print("DEMO 2: Input Validation & Type Coercion")
    print("=" * 70)

    schema = train_model.__mcp_metadata__.schema

    # Test 1: Valid input
    print("\nTest 1: Valid input")
    inputs = {"epochs": 10, "learning_rate": 0.001, "batch_size": 32}
    is_valid, error = validate_tool_input(inputs, schema)
    print(f"  Valid: {is_valid}, Error: {error}")

    # Test 2: Missing required field
    print("\nTest 2: Missing required field")
    inputs = {"epochs": 10, "learning_rate": 0.001}
    is_valid, error = validate_tool_input(inputs, schema)
    print(f"  Valid: {is_valid}, Error: {error}")

    # Test 3: Wrong type
    print("\nTest 3: Wrong type (without coercion)")
    inputs = {"epochs": "10", "learning_rate": "0.001", "batch_size": 32}
    is_valid, error = validate_tool_input(inputs, schema)
    print(f"  Valid: {is_valid}, Error: {error}")

    # Test 4: Coerce types
    print("\nTest 4: With type coercion")
    inputs = {"epochs": "10", "learning_rate": "0.001", "batch_size": "32"}
    coerced = coerce_types(inputs, schema)
    print(f"  Original: {inputs}")
    print(f"  Coerced: {coerced}")
    print(
        f"  Types: epochs={type(coerced['epochs']).__name__}, "
        f"learning_rate={type(coerced['learning_rate']).__name__}, "
        f"batch_size={type(coerced['batch_size']).__name__}"
    )


async def demo_execution_and_errors():
    """
    Demonstrate tool execution and error handling.
    """
    print("\n" + "=" * 70)
    print("DEMO 3: Tool Execution & Error Handling")
    print("=" * 70)

    # Test 1: Successful execution
    print("\nTest 1: Successful execution")
    result = await analyze_code("/path/to/file.py", depth=2, show_complexity=True)
    print(f"  Result: {json.dumps(result, indent=2)}")

    # Test 2: Sync function execution
    print("\nTest 2: Sync function execution")
    result = format_code("/path/to/file.py", line_length=100)
    print(f"  Result: {json.dumps(result, indent=2)}")

    # Test 3: Custom error handling
    print("\nTest 3: Custom error handling (risky_operation)")
    result = await risky_operation(-5, "sqrt")
    print(f"  Result (error case): {json.dumps(result, indent=2)}")

    # Test 4: Deprecation warning
    print("\nTest 4: Deprecated tool")
    import warnings

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = search_v1("test")
        if w:
            print(f"  Warning: {w[0].message}")


def demo_framework_conversion():
    """
    Demonstrate conversion to different framework formats.
    """
    print("\n" + "=" * 70)
    print("DEMO 4: Framework-Specific Conversion")
    print("=" * 70)

    # Convert to FastMCP format
    print("\nFastMCP Format:")
    fastmcp = to_fastmcp_tool(analyze_code)
    print(f"  Keys: {list(fastmcp.keys())}")
    print(f"  Name: {fastmcp['name']}")

    # Convert to LangChain format
    print("\nLangChain Format:")
    lc = to_langchain_tool(analyze_code)
    print(f"  Keys: {list(lc.keys())}")
    print(f"  Name: {lc['name']}")

    # Convert to Anthropic format
    print("\nAnthropic Format:")
    anthropic = to_anthropic_tool(analyze_code)
    print(f"  Keys: {list(anthropic.keys())}")
    print(f"  Name: {anthropic['name']}")


def demo_batch_registration():
    """
    Demonstrate batch tool registration.
    """
    print("\n" + "=" * 70)
    print("DEMO 5: Batch Tool Registration")
    print("=" * 70)

    # Register all tools
    registry = register_mcp_tools(
        analyze_code,
        format_code,
        document_code,
        process_data,
        fastmcp_specific_tool,
        langchain_specific_tool,
        anthropic_specific_tool,
    )

    print(f"\nRegistered {len(registry)} tools:")
    for tool_name, tool_config in registry.items():
        print(f"  - {tool_name}: {tool_config['description'][:50]}...")

    # Show framework-specific conversion
    print("\nFramework-Specific Conversion:")

    # Convert specific tools to their target formats
    fastmcp_tool = to_fastmcp_tool(fastmcp_specific_tool)
    print(f"  FastMCP Tool: {fastmcp_tool['name']}")

    lc_tool = to_langchain_tool(langchain_specific_tool)
    print(f"  LangChain Tool: {lc_tool['name']}")

    anthropic_tool = to_anthropic_tool(anthropic_specific_tool)
    print(f"  Anthropic Tool: {anthropic_tool['name']}")


async def main():
    """
    Run all demonstrations.
    """
    print("\n" + "=" * 70)
    print("MCP Tool Decorators - Integration Examples")
    print("=" * 70)

    # Run demonstrations
    demo_basic_registration()
    demo_validation_and_coercion()
    await demo_execution_and_errors()
    demo_framework_conversion()
    demo_batch_registration()

    print("\n" + "=" * 70)
    print("All demonstrations completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
