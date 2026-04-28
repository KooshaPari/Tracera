"""Setup script for pheno-logging.

This script registers all available handlers, formatters, and monitors with the global
registries.
"""

from .handlers.console import ConsoleHandler
from .handlers.file import FileHandler
from .handlers.json import JSONHandler
from .handlers.registry import register_handler
from .handlers.syslog import SyslogHandler


def setup_logging_library():
    """
    Register all handlers with the global registries.
    """

    # Register log handlers
    register_handler("console", ConsoleHandler)
    register_handler("file", FileHandler)
    register_handler("json", JSONHandler)
    register_handler("syslog", SyslogHandler)


# Auto-setup when module is imported
setup_logging_library()
