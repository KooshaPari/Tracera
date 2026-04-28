from __future__ import annotations

from tools.shared.schema_builders import SchemaBuilder


def test_build_schema_includes_common_fields():
    schema = SchemaBuilder.build_schema(
        tool_specific_fields={"custom": {"type": "string"}},
        required_fields=["custom"],
        auto_mode=False,
    )
    props = schema["properties"]
    # Common fields present
    assert "temperature" in props
    assert "thinking_mode" in props
    assert "images" in props
    assert "continuation_id" in props
    # Files helper present
    assert "files" in props
    # Prompt default present and required
    assert "prompt" in props
    assert "prompt" in schema["required"]


def test_build_schema_model_field_auto_mode_behavior():
    # Auto mode: model included, not necessarily required
    auto_schema = SchemaBuilder.build_schema(
        tool_specific_fields={}, required_fields=[], auto_mode=True,
    )
    assert "model" in auto_schema["properties"]

    # Non auto-mode without explicit model schema: not included
    non_auto_schema = SchemaBuilder.build_schema(
        tool_specific_fields={}, required_fields=[], auto_mode=False,
    )
    assert "model" not in non_auto_schema["properties"]

    # Non auto-mode with explicit schema: included
    with_model = SchemaBuilder.build_schema(
        tool_specific_fields={},
        required_fields=[],
        auto_mode=False,
        model_field_schema=SchemaBuilder.default_model_field_schema(),
    )
    assert "model" in with_model["properties"]
