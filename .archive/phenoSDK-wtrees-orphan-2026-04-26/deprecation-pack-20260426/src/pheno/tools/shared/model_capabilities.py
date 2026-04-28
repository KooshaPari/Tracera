"""
Model capability definitions for tool integration.
"""

from __future__ import annotations

from .temperature import TemperatureConstraint, create_temperature_constraint

__all__ = [
    "ModelCapabilities",
]


class ModelCapabilities:
    """
    Describes a model's capabilities for tool routing and validation.
    """

    def __init__(
        self,
        *,
        temperature_constraint: TemperatureConstraint | None = None,
        supports_images: bool = False,
        supports_extended_thinking: bool = False,
        max_tokens: int | None = None,
        max_image_count: int | None = None,
        max_image_size_mb: int | None = None,
    ):
        """Initialize model capabilities.

        Args:
            temperature_constraint: Constraint for temperature validation
            supports_images: Whether the model can process images
            supports_extended_thinking: Whether the model supports <thinking> tags
            max_tokens: Maximum tokens the model can output
            max_image_count: Maximum number of images the model can process
            max_image_size_mb: Maximum image size in MB
        """
        self.temperature_constraint = temperature_constraint
        self.supports_images = supports_images
        self.supports_extended_thinking = supports_extended_thinking
        self.max_tokens = max_tokens
        self.max_image_count = max_image_count
        self.max_image_size_mb = max_image_size_mb

    @classmethod
    def for_model(
        cls, model_name: str, constraint_hint: str | None = None,
    ) -> ModelCapabilities:
        """
        Create capabilities for a specific model using heuristics.
        """
        temp_constraint = create_temperature_constraint(model_name, constraint_hint)

        # Infer image support from model name patterns
        model_lower = model_name.lower()
        supports_images = any(
            pattern in model_lower
            for pattern in ["gpt-4-v", "gemini", "claude-3", "vision", "multimodal"]
        )

        # Infer extended thinking support
        supports_thinking = any(
            pattern in model_lower for pattern in ["o1", "o3", "thinking", "reasoning"]
        )

        return cls(
            temperature_constraint=temp_constraint,
            supports_images=supports_images,
            supports_extended_thinking=supports_thinking,
        )

    @property
    def supports_temperature(self) -> bool:
        """
        Check if the model supports temperature tuning.
        """
        return isinstance(
            self.temperature_constraint, (RangeTemperatureConstraint, DiscreteTemperatureConstraint),
        )
