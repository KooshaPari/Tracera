"""Shared response/utility models for tools.

This module is intentionally minimal. Downstreams can use or ignore it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolOutput:
    """
    Standardized tool output format.
    """

    status: str
    content: str
    content_type: str = "text"
    metadata: dict[str, Any] = field(default_factory=dict)

    def model_dump_json(self) -> str:
        return json.dumps(
            {
                "status": self.status,
                "content": self.content,
                "content_type": self.content_type,
                "metadata": self.metadata,
            },
        )


__all__ = ["ToolOutput"]
