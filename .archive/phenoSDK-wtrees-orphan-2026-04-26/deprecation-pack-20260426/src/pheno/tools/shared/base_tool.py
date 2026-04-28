"""
Base class for all tools with shared functionality.
"""

from __future__ import annotations

import logging
from abc import abstractmethod
from typing import Any

from .model_capabilities import ModelCapabilities

logger = logging.getLogger(__name__)


class ModelContext:
    """
    Context object containing model information and capabilities.
    """

    def __init__(
        self,
        model_name: str,
        provider: Any = None,
        capabilities: ModelCapabilities | None = None,
    ):
        self.model_name = model_name
        self.provider = provider
        self.capabilities = capabilities or ModelCapabilities.for_model(model_name)


class BaseTool:
    """
    Base class for all tools providing common functionality.
    """

    def __init__(self) -> None:
        self._current_arguments: dict[str, Any] = {}
        self._model_context: ModelContext | None = None
        self._current_model_name: str | None = None

    @abstractmethod
    def get_name(self) -> str:
        """
        Return the tool's name.
        """

    @abstractmethod
    def get_description(self) -> str:
        """
        Return the tool's description.
        """

    def get_annotations(self) -> dict[str, Any] | None:
        """
        Return optional annotations for this tool.
        """
        return {"readOnlyHint": True}

    def requires_model(self) -> bool:
        """
        Return whether this tool requires AI model access.
        """
        return True

    def is_effective_auto_mode(self) -> bool:
        """
        Check if we're in effective auto mode for schema generation.
        """
        # For pheno-sdk, default to False (caller should specify)
        return False

    def get_system_prompt(self) -> str:
        """
        Return the system prompt for this tool.
        """
        return ""

    def get_model_category(self) -> str:
        """
        Return the model category (fast, balanced, powerful).
        """
        return "balanced"

    def get_default_temperature(self) -> float:
        """
        Return the default temperature for this tool.
        """
        return 0.7

    def get_default_thinking_mode(self) -> str | None:
        """
        Return the default thinking mode.
        """
        return None

    def get_language_instruction(self) -> str:
        """
        Return the language instruction prompt.
        """
        return ""

    def _augment_system_prompt_with_capabilities(
        self, base_prompt: str, capabilities: ModelCapabilities,
    ) -> str:
        """
        Add capability-specific instructions to the system prompt.
        """
        additions = []

        if capabilities.supports_images:
            additions.append(
                "This model can process images. When images are provided, analyze them along with the text.",
            )

        if capabilities.supports_extended_thinking:
            additions.append(
                "This model supports extended thinking. Use <thinking> tags for complex reasoning when helpful.",
            )

        if additions:
            addition_text = "\n\n".join(additions)
            suffix = "" if base_prompt.endswith("\n\n") else "\n\n"
            return f"{base_prompt}{suffix}{addition_text}"

        return base_prompt

    def validate_and_correct_temperature(
        self, temperature: float, model_context: Any,
    ) -> tuple[float, list[str]]:
        """
        Validate and correct temperature for the specified model.
        """
        try:
            capabilities = model_context.capabilities
            constraint = capabilities.temperature_constraint

            warnings = []
            if not constraint.validate(temperature):
                corrected = constraint.get_corrected_value(temperature)
                warning = (
                    f"Temperature {temperature} invalid for {model_context.model_name}. "
                    f"{constraint.get_description()}. Using {corrected} instead."
                )
                warnings.append(warning)
                return corrected, warnings

            return temperature, warnings

        except Exception as e:
            logger.warning(f"Temperature validation failed for {model_context.model_name}: {e}")
            return temperature, [f"Temperature validation failed: {e}"]

    def _validate_image_limits(
        self,
        images: list[str] | None,
        model_context: ModelContext | None = None,
        continuation_id: str | None = None,
    ) -> dict | None:
        """
        Validate image size and count against model capabilities.
        """
        if not images:
            return None

        if not model_context:
            model_context = getattr(self, "_model_context", None)

        if not model_context:
            return {"status": "error", "content": "No model context available for image validation"}

        try:
            capabilities = model_context.capabilities
            model_name = model_context.model_name
        except Exception as e:
            return {"status": "error", "content": f"Failed to get capabilities: {e}"}

        # Check if model supports images
        if not capabilities.supports_images:
            return {
                "status": "error",
                "content": f"Image support not available: Model '{model_name}' does not support image processing. "
                "Please use a vision-capable model.",
                "metadata": {"error_type": "unsupported_images", "model_name": model_name},
            }

        return None  # Validation passed

    def _build_model_unavailable_message(self, model_name: str) -> str:
        """
        Build message for when a model is not available.
        """
        return (
            f"Model '{model_name}' is not available with current configuration. "
            "Please check that the required provider is configured with a valid API key."
        )

    # Hook methods for safe attribute access
    def get_request_model_name(self, request: Any) -> str | None:
        """
        Get model name from request.
        """
        try:
            return request.model
        except AttributeError:
            return None

    def get_request_images(self, request: Any) -> list:
        """
        Get images from request.
        """
        try:
            return request.images if request.images is not None else []
        except AttributeError:
            return []

    def get_request_continuation_id(self, request: Any) -> str | None:
        """
        Get continuation_id from request.
        """
        try:
            return request.continuation_id
        except AttributeError:
            return None

    def get_request_prompt(self, request: Any) -> str:
        """
        Get prompt from request.
        """
        try:
            return request.prompt
        except AttributeError:
            return ""

    def get_request_temperature(self, request: Any) -> float | None:
        """
        Get temperature from request.
        """
        try:
            return request.temperature
        except AttributeError:
            return None

    def get_request_thinking_mode(self, request: Any) -> str | None:
        """
        Get thinking_mode from request.
        """
        try:
            return request.thinking_mode
        except AttributeError:
            return None

    def get_request_files(self, request: Any) -> list:
        """
        Get files from request.
        """
        try:
            return request.files if request.files is not None else []
        except AttributeError:
            return []

    def _validate_file_paths(self, request: Any) -> str | None:
        """
        Validate file paths for security.
        """
        # Basic validation - subclass should override for specific security rules
        return None

    async def prepare_prompt(self, request: Any) -> str:
        """
        Prepare the prompt for the AI model.
        """
        return self.get_request_prompt(request)
