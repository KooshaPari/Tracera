"""Unified entry point for quality analysis tooling."""

from pheno.core.unified_manager import UnifiedManager

quality_manager = UnifiedManager()

__all__ = ["UnifiedManager", "quality_manager"]
