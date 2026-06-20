# Visual Feedback Quick Reference

Quick reference for using enhanced visual feedback in TraceRTM CLI.

## Error Display

### Basic Error

```python
from tracertm.cli.errors import TraceRTMError

# Simple error
raise TraceRTMError("Something went wrong")

# Error with suggestion
raise TraceRTMError(
    "Database connection failed",
    "Check your database URL in the configuration"
)
```

### Validation Error

```python
from tracertm.cli.errors import ValidationError

# Multiple validation errors displayed as a table
errors = [
    {"field": "email", "value": "invalid", "error": "Invalid email format"},
    {"field": "age", "value": "-5", "error": "Must be positive"},
    {"field": "username", "value": "", "error": "Username is required"},
]

raise ValidationError("User validation failed", errors=errors)
```

**Output**:
```
┌─ Validation Errors ──────────────────────────┐
│ Field      Value      Error                  │
├──────────────────────────────────────────────┤
│ email      invalid    Invalid email format   │
│ age        -5         Must be positive       │
│ username              Username is required   │
└──────────────────────────────────────────────┘

💡 Suggestion: Fix the validation errors shown above and try again
```

### Item Not Found Error

```python
from tracertm.cli.errors import ItemNotFoundError

# Automatically generates helpful suggestion
raise ItemNotFoundError("story", "STORY-123")
```

**Output**:
```
┌─ Error ──────────────────────────────────────┐
│ ✗ Story with ID 'STORY-123' not found        │
│                                               │
│ 💡 Suggestion: List available storys:        │
│    `rtm item list --type story`              │
└───────────────────────────────────────────────┘
```

### Invalid Format Error

```python
from tracertm.cli.errors import InvalidFormatError

# Format validation error
raise InvalidFormatError("JSON", "Missing closing brace")
```

**Output**:
```
┌─ Error ──────────────────────────────────────┐
│ ✗ Invalid JSON format: Missing closing brace │
│                                               │
│ 💡 Suggestion: Check the JSON syntax and try │
│    again                                      │
└───────────────────────────────────────────────┘
```

## Syntax Highlighting

### JSON Display

```python
from tracertm.cli.ui.formatters import display_json

data = {
    "key": "value",
    "items": [1, 2, 3],
    "nested": {"foo": "bar"}
}

display_json(data, title="API Response")
```

### YAML Display

```python
from tracertm.cli.ui.formatters import display_yaml

yaml_content = """
key: value
nested:
  foo: bar
items:
  - one
  - two
"""

display_yaml(yaml_content, title="Configuration")
```

### Python Code

```python
from tracertm.cli.ui.formatters import display_python

code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""

display_python(code, title="Example Function")
```

### SQL Query

```python
from tracertm.cli.ui.formatters import display_sql

query = """
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.status = 'active'
GROUP BY u.name
HAVING COUNT(o.id) > 5;
"""

display_sql(query, title="User Orders Query")
```

### Generic Code

```python
from tracertm.cli.ui.formatters import display_code

# JavaScript
js_code = "const greeting = 'Hello, world!';"
display_code(js_code, "javascript", title="Example JS")

# TypeScript
ts_code = "interface User { name: string; age: number; }"
display_code(ts_code, "typescript")

# Rust
rust_code = "fn main() { println!(\"Hello, world!\"); }"
display_code(rust_code, "rust")
```

### Diff Display

```python
from tracertm.cli.ui.formatters import display_diff

old_content = """
Line 1
Line 2
Line 3
"""

new_content = """
Line 1
Line 2 modified
Line 3
Line 4 added
"""

display_diff(old_content, new_content, title="Code Changes")
```

### XML Display

```python
from tracertm.cli.ui.formatters import display_xml

xml_content = """
<?xml version="1.0" encoding="UTF-8"?>
<root>
    <item id="1">Value 1</item>
    <item id="2">Value 2</item>
</root>
"""

display_xml(xml_content, title="XML Data")
```

### TOML Display

```python
from tracertm.cli.ui.formatters import display_toml

toml_content = """
[package]
name = "example"
version = "1.0.0"

[dependencies]
rich = "^13.0.0"
"""

display_toml(toml_content, title="Config File")
```

### Markdown Display

```python
from tracertm.cli.ui.formatters import display_markdown

markdown_content = """
# Example Document

This is a **markdown** document with:
- Lists
- **Bold** and *italic* text
- `code blocks`
"""

display_markdown(markdown_content)
```

## Error Handling in Commands

### Pattern 1: Try-Except with Custom Errors

```python
@app.command()
def my_command(item_id: str):
    """Example command with error handling."""
    try:
        # Your logic here
        item = get_item(item_id)
        if not item:
            raise ItemNotFoundError("item", item_id)

        # Process item
        console.print("[green]✓[/green] Success!")

    except TraceRTMError as e:
        e.display()
        raise typer.Exit(code=1)
    except Exception as e:
        from tracertm.cli.errors import handle_error
        handle_error(e)
        raise typer.Exit(code=1)
```

### Pattern 2: Validation with Table

```python
@app.command()
def create_user(name: str, email: str, age: int):
    """Create a user with validation."""
    errors = []

    # Validate fields
    if len(name) < 3:
        errors.append({
            "field": "name",
            "value": name,
            "error": "Too short (min 3 chars)"
        })

    if "@" not in email:
        errors.append({
            "field": "email",
            "value": email,
            "error": "Invalid email format"
        })

    if age < 0:
        errors.append({
            "field": "age",
            "value": age,
            "error": "Must be positive"
        })

    # Raise validation error if any errors
    if errors:
        raise ValidationError("User validation failed", errors=errors)

    # Create user...
    console.print("[green]✓[/green] User created!")
```

### Pattern 3: Debug Mode

```python
@app.command()
def risky_operation(debug: bool = False):
    """Operation that might fail."""
    try:
        # Risky operation
        result = perform_operation()

    except Exception as e:
        from tracertm.cli.errors import handle_error

        # Show full traceback in debug mode
        handle_error(e, debug=debug)
        raise typer.Exit(code=1)
```

## Best Practices

### 1. Use Specific Error Classes

**Good**:
```python
raise ItemNotFoundError("story", story_id)
raise ValidationError("Invalid input", errors)
raise InvalidFormatError("JSON", reason)
```

**Avoid**:
```python
raise TraceRTMError(f"Story {story_id} not found")  # Less helpful
```

### 2. Provide Actionable Suggestions

**Good**:
```python
TraceRTMError(
    "Database not initialized",
    "Run 'rtm db init' to initialize the database"
)
```

**Avoid**:
```python
TraceRTMError("Database error")  # Not helpful
```

### 3. Use Syntax Highlighting for Output

**Good**:
```python
if json_output:
    display_json(data, title="Results")
else:
    # Table output
    table = Table(...)
    console.print(table)
```

**Avoid**:
```python
console.print(json.dumps(data))  # Plain text, hard to read
```

### 4. Group Related Validation Errors

**Good**:
```python
errors = []
# Collect all validation errors
for field in fields:
    if not validate(field):
        errors.append({...})

if errors:
    raise ValidationError("Validation failed", errors)
```

**Avoid**:
```python
# Raising errors one at a time
if not valid_name:
    raise TraceRTMError("Invalid name")
if not valid_email:
    raise TraceRTMError("Invalid email")
```

### 5. Use Consistent Titles

**Good**:
```python
display_json(data, title="Export Results")
display_yaml(config, title="Configuration")
display_sql(query, title="Generated Query")
```

**Avoid**:
```python
display_json(data)  # No title
display_yaml(config, title="yaml")  # Lowercase, not descriptive
```

## Supported Languages

Syntax highlighting supports all languages from Pygments:

- **Backend**: Python, Go, Rust, Java, C, C++, C#
- **Frontend**: JavaScript, TypeScript, JSX, TSX, HTML, CSS, SCSS
- **Data**: JSON, YAML, XML, TOML, CSV
- **Query**: SQL, GraphQL, Cypher
- **Config**: Dockerfile, NGINX, Apache
- **Scripting**: Bash, PowerShell, Batch
- **Markup**: Markdown, reStructuredText, AsciiDoc
- **And many more...**

## Color Scheme

All syntax highlighting uses the **Monokai** theme for consistency.

**Theme Colors**:
- Keywords: Pink/Magenta
- Strings: Yellow
- Comments: Gray
- Numbers: Purple
- Functions: Green
- Operators: White

## Common Issues

### 1. Import Error

**Error**: `ModuleNotFoundError: No module named 'tracertm.cli.errors'`

**Solution**: Make sure you're running from the project root and tracertm is installed:
```bash
cd /path/to/trace
pip install -e .
```

### 2. Rich Console Issues

**Error**: Output not displaying colors

**Solution**: Check if your terminal supports ANSI colors:
```python
from rich.console import Console
console = Console()
console.print("[red]Test[/red]")
```

### 3. Missing Traceback in Debug Mode

**Error**: Debug mode not showing full traceback

**Solution**: Make sure you're passing `debug=True`:
```python
handle_error(e, debug=True)
```

## Examples in Commands

See these commands for real-world examples:
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/cli/commands/export.py`
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/cli/commands/query.py`
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/cli/test_visual_feedback.py`

## Full API Reference

See the implementation report for complete details:
`/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/docs/reports/VISUAL_FEEDBACK_ENHANCEMENTS.md`
