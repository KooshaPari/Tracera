"""Parameterized MCP tools organized by domain."""

from ._lazy_stub import (
    agent_manage,
    benchmark_manage,
    chaos_manage,
    design_manage,
    progress_manage,
    tui_manage,
)
from .config import config_manage
from .database import database_manage
from .graph import graph_analyze
from .io_operations import export_manage, import_manage, ingestion_manage
from .item import item_manage
from .link import link_manage
from .project import project_manage
from .query_test import saved_query_manage, test_manage
from .specification import specification_manage
from .storage import backup_manage, file_watch_manage, sync_manage
from .trace import quality_analyze, trace_analyze

__all__ = [
    "agent_manage",
    "backup_manage",
    "benchmark_manage",
    "chaos_manage",
    "config_manage",
    "database_manage",
    "design_manage",
    "export_manage",
    "file_watch_manage",
    "graph_analyze",
    "import_manage",
    "ingestion_manage",
    "item_manage",
    "link_manage",
    "progress_manage",
    "project_manage",
    "quality_analyze",
    "saved_query_manage",
    "specification_manage",
    "sync_manage",
    "test_manage",
    "trace_analyze",
    "tui_manage",
]
