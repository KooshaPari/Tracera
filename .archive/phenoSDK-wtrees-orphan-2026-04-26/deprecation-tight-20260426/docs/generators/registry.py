"""Generator registry for managing documentation generators.

This module provides a centralized registry for all documentation generators, making it
easy to register, discover, and create generators.
"""


from ..core.interfaces import DocumentationGenerator
from ..core.types import DocumentationError, GeneratorConfig


class GeneratorRegistry:
    """
    Central registry for documentation generators.
    """

    def __init__(self):
        self._generators: dict[str, type[DocumentationGenerator]] = {}
        self._instances: dict[str, DocumentationGenerator] = {}

    def register_generator(self, name: str, generator_class: type[DocumentationGenerator]) -> None:
        """Register a generator class.

        Args:
            name: Generator name
            generator_class: Generator class to register
        """
        if not issubclass(generator_class, DocumentationGenerator):
            raise ValueError("Generator class must inherit from DocumentationGenerator")

        self._generators[name] = generator_class

    def get_generator_class(self, name: str) -> type[DocumentationGenerator] | None:
        """Get a generator class by name.

        Args:
            name: Generator name

        Returns:
            Generator class or None if not found
        """
        return self._generators.get(name)

    def create_generator(self, name: str, config: GeneratorConfig) -> DocumentationGenerator:
        """Create a generator instance.

        Args:
            name: Generator name
            config: Generator configuration

        Returns:
            Generator instance

        Raises:
            DocumentationError: If generator not found or creation fails
        """
        generator_class = self.get_generator_class(name)
        if not generator_class:
            raise DocumentationError(f"Generator '{name}' not found")

        try:
            return generator_class(name, config)
        except Exception as e:
            raise DocumentationError(f"Failed to create generator '{name}': {e}")

    def get_or_create_generator(self, name: str, config: GeneratorConfig) -> DocumentationGenerator:
        """Get existing generator instance or create new one.

        Args:
            name: Generator name
            config: Generator configuration

        Returns:
            Generator instance
        """
        instance_key = f"{name}:{id(config)}"

        if instance_key not in self._instances:
            self._instances[instance_key] = self.create_generator(name, config)

        return self._instances[instance_key]

    def list_generators(self) -> list[str]:
        """List all registered generator names.

        Returns:
            List of generator names
        """
        return list(self._generators.keys())

    def get_generator_by_format(self, format_name: str) -> list[str]:
        """Get generators by supported format.

        Args:
            format_name: Format name to filter by

        Returns:
            List of generator names supporting the format
        """
        generators = []
        for name, generator_class in self._generators.items():
            # Check if generator class supports the format
            if (
                hasattr(generator_class, "supported_formats")
                and format_name in generator_class.supported_formats
            ):
                generators.append(name)
        return generators

    def unregister_generator(self, name: str) -> None:
        """Unregister a generator.

        Args:
            name: Generator name to unregister
        """
        if name in self._generators:
            del self._generators[name]

        # Remove any instances of this generator
        keys_to_remove = [k for k in self._instances.keys() if k.startswith(f"{name}:")]
        for key in keys_to_remove:
            del self._instances[key]

    def clear(self) -> None:
        """
        Clear all registered generators and instances.
        """
        self._generators.clear()
        self._instances.clear()


# Global registry instance
_global_registry = GeneratorRegistry()


def get_registry() -> GeneratorRegistry:
    """
    Get the global generator registry.
    """
    return _global_registry


def register_generator(name: str, generator_class: type[DocumentationGenerator]) -> None:
    """
    Register a generator with the global registry.
    """
    _global_registry.register_generator(name, generator_class)


def create_generator(name: str, config: GeneratorConfig) -> DocumentationGenerator:
    """
    Create a generator using the global registry.
    """
    return _global_registry.create_generator(name, config)
