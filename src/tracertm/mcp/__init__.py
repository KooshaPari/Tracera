"""
TraceRTM MCP Server - FastMCP 3.0.0b1 based MCP server for AI-native CLI.

This module provides:
- Tools: Actions the AI can perform (CRUD, analysis, verification)
- Resources: Data the AI can access (projects, graphs, reports)
- Prompts: Reusable prompt templates (ADR creation, analysis)
- Monitoring: OpenTelemetry tracing, Prometheus metrics, structured logging
"""

from __future__ import annotations

from tracertm.mcp._exports import *
from tracertm.mcp._exports import __all__
