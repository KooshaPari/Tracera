"""
TraceRTM - Agent-native, multi-view requirements traceability system.

Version: 0.1.0
"""
# Disable Pydantic plugins (e.g. logfire) before any pydantic import.
import os
os.environ.setdefault("PYDANTIC_DISABLE_PLUGINS", "logfire-plugin")

__version__ = "0.1.0"
__author__ = "BMad"
