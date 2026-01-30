"""
Utilities for BMM workflow status and configuration.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml


def get_project_root() -> Path:
    """Get project root directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".bmad").exists():
            return current
        current = current.parent
    return Path.cwd()


def load_workflow_status() -> Optional[Dict[str, Any]]:
    """Load workflow status YAML."""
    project_root = get_project_root()
    status_file = project_root / "docs" / "bmm-workflow-status.yaml"
    if not status_file.exists():
        return None
    with open(status_file) as f:
        return yaml.safe_load(f)


def save_workflow_status(status: Dict[str, Any]) -> None:
    """Save workflow status YAML."""
    project_root = get_project_root()
    status_file = project_root / "docs" / "bmm-workflow-status.yaml"
    status_file.parent.mkdir(parents=True, exist_ok=True)
    with open(status_file, "w") as f:
        yaml.safe_dump(status, f, default_flow_style=False, sort_keys=False)


def load_bmm_config() -> Dict[str, Any]:
    """Load BMM configuration."""
    project_root = get_project_root()
    config_file = project_root / ".bmad" / "bmm" / "config.yaml"
    if not config_file.exists():
        return {}
    with open(config_file) as f:
        return yaml.safe_load(f)


def get_workflow_config(workflow_id: str) -> Optional[Dict[str, Any]]:
    """Get configuration for a specific workflow."""
    status = load_workflow_status()
    if not status:
        return None

    for phase_key, phase_data in status.get("workflow_status", {}).items():
        if workflow_id in phase_data:
            return phase_data[workflow_id]
    return None


def get_phase_workflows(phase: int) -> List[Dict[str, Any]]:
    """Get all workflows for a specific phase."""
    status = load_workflow_status()
    if not status:
        return []

    phase_key = f"phase_{phase}_" + ["discovery", "planning", "solutioning", "implementation"][phase]
    phase_data = status.get("workflow_status", {}).get(phase_key, {})

    workflows: List[Dict[str, Any]] = []
    for wf_id, wf_config in phase_data.items():
        workflows.append({
            "id": wf_id,
            "name": wf_id.replace("-", " ").title(),
            **wf_config,
        })
    return workflows


def get_next_pending_workflow() -> Optional[Dict[str, Any]]:
    """Get the next pending workflow."""
    status = load_workflow_status()
    if not status:
        return None

    for phase_key, phase_data in status.get("workflow_status", {}).items():
        for wf_id, wf_config in phase_data.items():
            current_status = wf_config.get("status", "")
            if not isinstance(current_status, str) or not current_status.startswith("docs/"):
                if wf_config.get("included", True):
                    return {
                        "id": wf_id,
                        "name": wf_id.replace("-", " ").title(),
                        **wf_config,
                    }
    return None


__all__ = [
    "get_project_root",
    "load_workflow_status",
    "save_workflow_status",
    "load_bmm_config",
    "get_workflow_config",
    "get_phase_workflows",
    "get_next_pending_workflow",
]
