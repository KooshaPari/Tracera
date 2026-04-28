"""
SimpleTool base class composed from domain-specific mixins.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from ..base_tool import BaseTool
from ..schema_builders import SchemaBuilder
from .conversation import SimpleToolConversationMixin
from .execution import SimpleToolExecutionMixin
from .prompting import SimpleToolPromptMixin
from .validation import SimpleToolValidationMixin


class SimpleTool(
    SimpleToolValidationMixin,
    SimpleToolPromptMixin,
    SimpleToolConversationMixin,
    SimpleToolExecutionMixin,
    BaseTool,
):
    """Base class for simple (non-workflow) tools.

    Simple tools are request/response tools that don't require multi-step workflows.
    They benefit from:
    - Automatic schema generation using SchemaBuilder
    - Inherited conversation handling and file processing
    - Standardized model integration
    - Consistent error handling and response formatting

    To create a simple tool:
    1. Inherit from SimpleTool
    2. Implement get_tool_fields() to define tool-specific fields
    3. Implement prepare_prompt() for prompt preparation
    4. Optionally override format_response() for custom formatting
    5. Optionally override get_required_fields() for custom requirements
    """

    # Common field definitions that simple tools can reuse
    FILES_FIELD = SchemaBuilder.SIMPLE_FIELD_SCHEMAS["files"]
    IMAGES_FIELD = SchemaBuilder.COMMON_FIELD_SCHEMAS["images"]

    @abstractmethod
    def get_tool_fields(self) -> dict[str, dict[str, Any]]:
        """Return tool-specific field definitions.

        This method should return a dictionary mapping field names to their
        JSON schema definitions. Common fields (model, temperature, etc.)
        are added automatically by the base class.

        Returns:
            Dict mapping field names to JSON schema objects
        """

    def get_required_fields(self) -> list[str]:
        """Return list of required field names.

        Override this to specify which fields are required for your tool.
        The model field is automatically added if in auto mode.

        Returns:
            List of required field names
        """
        return []

    def get_annotations(self) -> dict[str, Any] | None:
        """Return tool annotations. Simple tools are read-only by default.

        All simple tools perform operations without modifying the environment.
        They may call external AI models for analysis or conversation, but they
        don't write files or make system changes.

        Override this method if your simple tool needs different annotations.

        Returns:
            Dictionary with readOnlyHint set to True
        """
        return {"readOnlyHint": True}

    def format_response(self, response: str, request, model_info: dict | None = None) -> str:
        """Format the AI response before returning to the client.

        This is a hook method that subclasses can override to customize
        response formatting. The default implementation returns the response as-is.

        Args:
            response: The raw response from the AI model
            request: The validated request object
            model_info: Optional model information dictionary

        Returns:
            Formatted response string
        """
        return response

    def get_input_schema(self) -> dict[str, Any]:
        """Generate the complete input schema using SchemaBuilder.

        This method automatically combines:
        - Tool-specific fields from get_tool_fields()
        - Common fields (temperature, thinking_mode, etc.)
        - Model field with proper auto-mode handling
        - Required fields from get_required_fields()

        Tools can override this method for custom schema generation while
        still benefiting from SimpleTool's convenience methods.

        Returns:
            Complete JSON schema for the tool
        """
        required_fields = list(self.get_required_fields())
        return SchemaBuilder.build_schema(
            tool_specific_fields=self.get_tool_fields(),
            required_fields=required_fields,
            model_field_schema=self.get_model_field_schema(),
            auto_mode=self.is_effective_auto_mode(),
        )

    def get_request_model(self):
        """Return the request model class.

        Simple tools use the base ToolRequest by default. Override this if your tool
        needs a custom request model.
        """
        from ..base_models import ToolRequest

        return ToolRequest

    # Hook methods for safe attribute access without hasattr/getattr

    def get_request_model_name(self, request) -> str | None:
        """Get model name from request.

        Override for custom model name handling.
        """
        try:
            return request.model
        except AttributeError:
            return None

    def get_request_images(self, request) -> list:
        """Get images from request.

        Override for custom image handling.
        """
        try:
            return request.images if request.images is not None else []
        except AttributeError:
            return []

    def get_request_continuation_id(self, request) -> str | None:
        """Get continuation_id from request.

        Override for custom continuation handling.
        """
        try:
            return request.continuation_id
        except AttributeError:
            return None

    def get_request_prompt(self, request) -> str:
        """Get prompt from request.

        Override for custom prompt handling.
        """
        try:
            return request.prompt
        except AttributeError:
            return ""

    def get_request_temperature(self, request) -> float | None:
        """Get temperature from request.

        Override for custom temperature handling.
        """
        try:
            return request.temperature
        except AttributeError:
            return None

    def get_validated_temperature(self, request, model_context: Any) -> tuple[float, list[str]]:
        """Get temperature from request and validate it against model constraints.

        This is a convenience method that combines temperature extraction and validation
        for simple tools. It ensures temperature is within valid range for the model.

        Args:
            request: The request object containing temperature
            model_context: Model context object containing model info

        Returns:
            Tuple of (validated_temperature, warning_messages)
        """
        temperature = self.get_request_temperature(request)
        if temperature is None:
            temperature = self.get_default_temperature()
        return self.validate_and_correct_temperature(temperature, model_context)

    def get_request_thinking_mode(self, request) -> str | None:
        """Get thinking_mode from request.

        Override for custom thinking mode handling.
        """
        try:
            return request.thinking_mode
        except AttributeError:
            return None

    def get_request_files(self, request) -> list:
        """Get files from request.

        Override for custom file handling.
        """
        try:
            return request.files if request.files is not None else []
        except AttributeError:
            return []

    def get_request_as_dict(self, request) -> dict:
        """Convert request to dictionary.

        Override for custom serialization.
        """
        try:
            # Try Pydantic v2 method first
            return request.model_dump()
        except AttributeError:
            try:
                # Fall back to Pydantic v1 method
                return request.dict()
            except AttributeError:
                # Last resort - convert to dict manually
                return {"prompt": self.get_request_prompt(request)}

    def set_request_files(self, request, files: list) -> None:
        """Set files on request.

        Override for custom file setting.
        """
        try:
            request.files = files
        except AttributeError:
            # If request doesn't support file setting, ignore silently
            pass

    def supports_custom_request_model(self) -> bool:
        """Indicate whether this tool supports custom request models.

        Simple tools support custom request models by default. Tools that override
        get_request_model() to return something other than ToolRequest should
        return True here.

        Returns:
            True if the tool uses a custom request model
        """
        from ..base_models import ToolRequest

        return self.get_request_model() != ToolRequest
