"""
Helper types for validating model temperature parameters.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

__all__ = [
    "DiscreteTemperatureConstraint",
    "FixedTemperatureConstraint",
    "RangeTemperatureConstraint",
    "TemperatureConstraint",
    "create_temperature_constraint",
]

# Common heuristics for determining temperature support when explicit
# capabilities are unavailable (e.g., custom/local models).
_TEMP_UNSUPPORTED_PATTERNS = {
    "o1",
    "o3",
    "o4",  # OpenAI O-series reasoning models
    "deepseek-reasoner",
    "deepseek-r1",
    "r1",  # DeepSeek reasoner variants
}

_TEMP_UNSUPPORTED_KEYWORDS = {
    "reasoner",  # Catch additional DeepSeek-style naming patterns
}


class TemperatureConstraint(ABC):
    """Contract for temperature validation used by model capabilities.

    Concrete providers describe their temperature behaviour by creating
    subclasses that expose three operations:
    * `validate` – decide whether a requested temperature is acceptable.
    * `get_corrected_value` – coerce out-of-range values into a safe default.
    * `get_description` – provide a human readable error message for users.

    Providers call these hooks before sending traffic to the underlying API so
    that unsupported temperatures never reach the remote service.
    """

    @abstractmethod
    def validate(self, temperature: float) -> bool:
        """
        Return True when the temperature may be sent to the backend.
        """

    @abstractmethod
    def get_corrected_value(self, temperature: float) -> float:
        """
        Return a valid substitute for an out-of-range temperature.
        """

    @abstractmethod
    def get_description(self) -> str:
        """
        Describe the acceptable range to include in error messages.
        """

    @abstractmethod
    def get_default(self) -> float:
        """
        Return the default temperature for the model.
        """

    @staticmethod
    def infer_support(model_name: str) -> tuple[bool, str]:
        """
        Heuristically determine whether a model supports temperature.
        """

        model_lower = model_name.lower()

        for pattern in _TEMP_UNSUPPORTED_PATTERNS:
            conditions = (
                pattern == model_lower,
                model_lower.startswith(f"{pattern}-"),
                model_lower.startswith(f"openai/{pattern}"),
                model_lower.startswith(f"deepseek/{pattern}"),
                model_lower.endswith(f"-{pattern}"),
                f"/{pattern}" in model_lower,
                f"-{pattern}-" in model_lower,
            )
            if any(conditions):
                return False, f"detected pattern '{pattern}'"

        for keyword in _TEMP_UNSUPPORTED_KEYWORDS:
            if keyword in model_lower:
                return False, f"detected keyword '{keyword}'"

        return True, "default assumption for models without explicit metadata"


class FixedTemperatureConstraint(TemperatureConstraint):
    """Constraint for models that only support a single temperature value.

    Used by reasoning models (o1, o3, etc.) that require specific temperature settings
    for proper functionality.
    """

    def __init__(self, value: float):
        self.value = value

    def validate(self, temperature: float) -> bool:
        # Allow a small tolerance for floating point precision
        return abs(temperature - self.value) < 1e-6

    def get_corrected_value(self, temperature: float) -> float:
        return self.value

    def get_description(self) -> str:
        return f"temperature must be exactly {self.value}"

    def get_default(self) -> float:
        return self.value


class RangeTemperatureConstraint(TemperatureConstraint):
    """Constraint for models that support a continuous range of temperature values.

    Most GPT-style models use this constraint type.
    """

    def __init__(self, min_value: float, max_value: float, default: float):
        self.min_value = min_value
        self.max_value = max_value
        self.default = default

        # Validate the range is sensible
        if min_value > max_value:
            raise ValueError(
                f"min_value ({min_value}) cannot be greater than max_value ({max_value})",
            )
        if not (min_value <= default <= max_value):
            raise ValueError(f"default ({default}) must be within range [{min_value}, {max_value}]")

    def validate(self, temperature: float) -> bool:
        return self.min_value <= temperature <= self.max_value

    def get_corrected_value(self, temperature: float) -> float:
        if temperature < self.min_value:
            return self.min_value
        if temperature > self.max_value:
            return self.max_value
        return temperature

    def get_description(self) -> str:
        return f"temperature must be between {self.min_value} and {self.max_value}"

    def get_default(self) -> float:
        return self.default


class DiscreteTemperatureConstraint(TemperatureConstraint):
    """Constraint for models that only support specific discrete temperature values.

    Some models might only support certain preset temperature settings.
    """

    def __init__(self, allowed_values: list[float], default: float):
        if not allowed_values:
            raise ValueError("allowed_values cannot be empty")

        self.allowed_values = sorted(allowed_values)
        self.default = default

        if default not in allowed_values:
            raise ValueError(f"default ({default}) must be one of the allowed values")

    def validate(self, temperature: float) -> bool:
        # Allow a small tolerance for floating point precision
        return any(abs(temperature - value) < 1e-6 for value in self.allowed_values)

    def get_corrected_value(self, temperature: float) -> float:
        # Find the closest allowed value
        return min(self.allowed_values, key=lambda x: abs(x - temperature))

    def get_description(self) -> str:
        values_str = ", ".join(str(v) for v in self.allowed_values)
        return f"temperature must be one of: {values_str}"

    def get_default(self) -> float:
        return self.default


def create_temperature_constraint(
    model_name: str,
    constraint_hint: str | None = None,
) -> TemperatureConstraint:
    """
    Create the appropriate temperature constraint for a model.
    """

    supports_temp, _diagnosis = TemperatureConstraint.infer_support(model_name)

    if not supports_temp:
        # Use fixed temperature for models that don't support temperature
        return FixedTemperatureConstraint(1.0)

    if constraint_hint == "fixed":
        return FixedTemperatureConstraint(1.0)
    if constraint_hint == "range":
        return RangeTemperatureConstraint(0.0, 2.0, 0.7)
    if constraint_hint == "discrete":
        return DiscreteTemperatureConstraint([0.0, 0.7, 1.0, 1.5, 2.0], 0.7)

    # Default assumption: most models support 0.0-2.0 range
    return RangeTemperatureConstraint(0.0, 2.0, 0.7)
