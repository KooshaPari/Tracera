"""Utilities for BMM workflow status and configuration."""

from __future__ import annotations

from pathlib import Path

import yaml


def get_project_root() -> Path:
    """Get project root directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".bmad").exists():
            return current
        current = current.parent
    return Path.cwd()


def load_workflow_status() -> dict[str, object] | None:
    """Load workflow status YAML."""
    project_root = get_project_root()
    status_file = project_root / "docs" / "bmm-workflow-status.yaml"
    if not status_file.exists():
        return None
    with status_file.open() as f:
        result = yaml.safe_load(f)
        return result if isinstance(result, dict) else None


def save_workflow_status(status: dict[str, object]) -> None:
    """Save workflow status YAML."""
    project_root = get_project_root()
    status_file = project_root / "docs" / "bmm-workflow-status.yaml"
    status_file.parent.mkdir(parents=True, exist_ok=True)
    with status_file.open("w") as f:
        yaml.safe_dump(status, f, default_flow_style=False, sort_keys=False)


def load_bmm_config() -> dict[str, object]:
    """Load BMM configuration."""
    project_root = get_project_root()
    config_file = project_root / ".bmad" / "bmm" / "config.yaml"
    if not config_file.exists():
        return {}
    with config_file.open() as f:
        result = yaml.safe_load(f)
        return result if isinstance(result, dict) else {}


def get_workflow_config(workflow_id: str) -> dict[str, object] | None:
    """Get configuration for a specific workflow."""
    status = load_workflow_status()
    if not status:
        return None

    workflow_status = status.get("workflow_status", {})
    if not isinstance(workflow_status, dict):
        return None

    for phase_data in workflow_status.values():
        if not isinstance(phase_data, dict):
            continue
        if workflow_id in phase_data:
            phase_wf = phase_data[workflow_id]
            return phase_wf if isinstance(phase_wf, dict) else None
    return None


def get_phase_workflows(phase: int) -> list[dict[str, object]]:
    """Get all workflows for a specific phase."""
    status = load_workflow_status()
    if not status:
        return []

    phase_key = f"phase_{phase}_" + ["discovery", "planning", "solutioning", "implementation"][phase]
    workflow_status = status.get("workflow_status", {})
    if not isinstance(workflow_status, dict):
        return []

    phase_data = workflow_status.get(phase_key, {})
    if not isinstance(phase_data, dict):
        return []

    workflows: list[dict[str, object]] = []
    for wf_id, wf_config in phase_data.items():
        if not isinstance(wf_config, dict):
            continue
        workflows.append({
            "id": wf_id,
            "name": wf_id.replace("-", " ").title(),
            **wf_config,
        })
    return workflows


def get_next_pending_workflow() -> dict[str, object] | None:
    """Get the next pending workflow."""
    status = load_workflow_status()
    if not status:
        return None

    workflow_status = status.get("workflow_status", {})
    if not isinstance(workflow_status, dict):
        return None

    for phase_data in workflow_status.values():
        if not isinstance(phase_data, dict):
            continue
        for wf_id, wf_config in phase_data.items():
            if not isinstance(wf_config, dict):
                continue
            current_status = wf_config.get("status", "")
            if (not isinstance(current_status, str) or not current_status.startswith("docs/")) and wf_config.get(
                "included",
                True,
            ):
                return {
                    "id": wf_id,
                    "name": wf_id.replace("-", " ").title(),
                    **wf_config,
                }
    return None


def get_status_data() -> dict[str, object]:
    """Return workflow status dict (sync). Used by get_status tool and by prompts/resources."""
    status = load_workflow_status()
    if not status:
        return {
            "initialized": False,
            "message": "Project not initialized. Run init_project first.",
        }

    total_workflows = 0
    completed_workflows = 0
    pending_workflows: list[dict[str, object]] = []

    workflow_status = status.get("workflow_status", {})
    if not isinstance(workflow_status, dict):
        workflow_status = {}

    for phase_data in workflow_status.values():
        if not isinstance(phase_data, dict):
            continue
        for wf_id, wf_config in phase_data.items():
            if not isinstance(wf_config, dict):
                continue
            if not wf_config.get("included", True):
                continue

            total_workflows += 1
            current_status = wf_config.get("status", "")

            if isinstance(current_status, str) and current_status.startswith("docs/"):
                completed_workflows += 1
            else:
                pending_workflows.append({
                    "id": wf_id,
                    "name": wf_id.replace("-", " ").title(),
                    "agent": wf_config.get("agent", "Unknown"),
                    "status_type": wf_config.get("status", "Unknown"),
                    "note": wf_config.get("note", ""),
                })

    next_workflow = get_next_pending_workflow()

    return {
        "initialized": True,
        "project": status.get("project", "Unknown"),
        "track": status.get("selected_track", "Unknown"),
        "field_type": status.get("field_type", "Unknown"),
        "generated": status.get("generated", "Unknown"),
        "total_workflows": total_workflows,
        "completed_workflows": completed_workflows,
        "pending_workflows": len(pending_workflows),
        "progress_percentage": round((completed_workflows / total_workflows * 100) if total_workflows > 0 else 0, 1),
        "next_workflow": next_workflow,
        "pending_list": pending_workflows[:5],
    }


__all__ = [
    "get_next_pending_workflow",
    "get_phase_workflows",
    "get_project_root",
    "get_status_data",
    "get_workflow_config",
    "load_bmm_config",
    "load_workflow_status",
    "save_workflow_status",
]
