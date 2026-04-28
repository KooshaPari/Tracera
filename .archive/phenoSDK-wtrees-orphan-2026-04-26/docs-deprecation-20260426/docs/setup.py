"""Setup script for pheno-docs.

This script registers all available generators, renderers, and validators with the
global registries.
"""

from .generators.markdown import MarkdownGenerator
from .generators.registry import register_generator


def setup_documentation_library():
    """
    Register all generators and utilities with the global registries.
    """

    # Register documentation generators
    register_generator("markdown", MarkdownGenerator)


# Auto-setup when module is imported
setup_documentation_library()
