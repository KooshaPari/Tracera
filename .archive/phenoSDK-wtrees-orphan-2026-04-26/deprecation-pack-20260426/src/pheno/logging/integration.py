from __future__ import annotations

from typing import TYPE_CHECKING

from pheno.logging.core.logger import get_logger
from pheno.logging.core.types import LogLevel
from pheno.logging.handlers.registry import get_registry

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pheno.config.integration import (
        MorphIntegrationSettings,
        RouterIntegrationSettings,
    )


def configure_logging_from_settings(
    settings: MorphIntegrationSettings | RouterIntegrationSettings,
    *,
    logger_name: str = "pheno",
) -> None:
    """
    Apply logging configuration based on integration settings.
    """

    registry = get_registry()
    logger = get_logger(logger_name)

    level = LogLevel.from_string(getattr(settings, "logging_level", "INFO"))
    logger.set_level(level)

    # Clear existing handlers before reconfiguration
    current_handlers = list(getattr(logger, "_handlers", []))
    for handler in current_handlers:
        logger.remove_handler(handler)

    for sink in _normalise_sinks(settings.logging_sinks):
        try:
            handler = registry.create_handler(sink, {"level": level})
        except Exception as exc:
            logger.warning("logging_sink_creation_failed", sink=sink, error=str(exc))
            continue
        logger.add_handler(handler)


def _normalise_sinks(sinks: Iterable[str]) -> list[str]:
    normalised: list[str] = []
    for sink in sinks:
        sink_name = sink.strip().lower()
        if sink_name == "stdout":
            normalised.append("console")
        elif sink_name in {"json", "console", "file", "syslog"}:
            normalised.append(sink_name)
        else:
            normalised.append(sink_name)
    return normalised
