"""
Logging Framework for Pheno SDK
===============================

Provides structured logging with fallbacks for Pheno SDK projects.
"""

import logging


def setup_logging(
    name: str,
    level: str = "INFO",
    use_structured: bool = True,
    service_name: str | None = None,
    environment: str = "local",
) -> logging.Logger:
    """Set up logging for a Pheno SDK project.

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_structured: Whether to use structured logging if available
        service_name: Service name for structured logging
        environment: Environment name

    Returns:
        Configured logger instance
    """
    # Try to use structured logging if available and requested
    if use_structured:
        try:
            from observability import LogLevel, StructuredLogger

            log_level = getattr(LogLevel, level.upper(), LogLevel.INFO)
            return StructuredLogger(
                name, service_name=service_name or name, environment=environment, level=log_level,
            )
        except ImportError:
            # Fall back to standard logging
            pass

    # Set up standard logging
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    return logging.getLogger(name)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.
    """
    return logging.getLogger(name)


class LoggingMixin:
    """
    Mixin class to add logging capabilities to CLI frameworks.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger: logging.Logger | None = None

    @property
    def logger(self) -> logging.Logger:
        """
        Get the logger instance.
        """
        if self._logger is None:
            self._logger = setup_logging(
                name=getattr(self, "name", "pheno-sdk"),
                level=getattr(self, "log_level", "INFO"),
                use_structured=getattr(self, "use_structured_logging", True),
                service_name=getattr(self, "service_name", None),
                environment=getattr(self, "environment", "local"),
            )
        return self._logger

    def log_info(self, message: str, **kwargs):
        """
        Log informational messages.
        """
        if hasattr(self.logger, "info"):
            if isinstance(self.logger, logging.Logger):
                self.logger.info(message)
            else:
                # Structured logger
                self.logger.info(message, **kwargs)

    def log_error(self, message: str, **kwargs):
        """
        Log error messages.
        """
        if hasattr(self.logger, "error"):
            if isinstance(self.logger, logging.Logger):
                self.logger.error(message)
            else:
                # Structured logger
                self.logger.error(message, **kwargs)

    def log_warning(self, message: str, **kwargs):
        """
        Log warning messages.
        """
        if hasattr(self.logger, "warning"):
            if isinstance(self.logger, logging.Logger):
                self.logger.warning(message)
            else:
                # Structured logger
                self.logger.warning(message, **kwargs)

    def log_debug(self, message: str, **kwargs):
        """
        Log debug messages.
        """
        if hasattr(self.logger, "debug"):
            if isinstance(self.logger, logging.Logger):
                self.logger.debug(message)
            else:
                # Structured logger
                self.logger.debug(message, **kwargs)
