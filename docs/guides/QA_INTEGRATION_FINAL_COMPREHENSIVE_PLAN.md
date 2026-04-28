# Quality Engineering Integration System
## Final Comprehensive Implementation Plan

**Version:** 1.0.0
**Date:** January 28, 2026
**Status:** Ready for Implementation

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Database Schema](#4-database-schema)
5. [VHS CLI Recording Integration](#5-vhs-cli-recording-integration)
6. [Playwright Web Testing Integration](#6-playwright-web-testing-integration)
7. [FFmpeg Media Pipeline](#7-ffmpeg-media-pipeline)
8. [Codex CLI Agent Integration](#8-codex-cli-agent-integration)
9. [Docker Execution Environment](#9-docker-execution-environment)
10. [Enhanced Node Visualization](#10-enhanced-node-visualization)
11. [API Endpoints](#11-api-endpoints)
12. [Implementation Roadmap](#12-implementation-roadmap)
13. [Security Considerations](#13-security-considerations)
14. [Quick Reference](#14-quick-reference)

---

## 1. Executive Summary

### Objective

Build a comprehensive Quality Engineering/QA+QC integration system that:

- **Records CLI demos** using VHS (charmbracelet/vhs)
- **Captures web tests** using Playwright with video/screenshots
- **Converts media** using FFmpeg (video→GIF pipeline)
- **Reviews artifacts** using Codex CLI as an AI agent
- **Executes tests** in sandboxed Docker containers
- **Visualizes QA data** in enhanced graph nodes with expandable popups

### Key Constraints

- **No paid cloud services** - Local filesystem + SQLite only
- **OAuth credentials** - Codex uses ChatGPT login, not API keys
- **Codebase-aligned execution** - Docker containers mirror project environment

### Technology Choices

| Component | Technology | Rationale |
|-----------|------------|-----------|
| CLI Recording | VHS | Declarative .tape files, GIF output, CI-friendly |
| Web Testing | Playwright Python | Native video/trace, cross-browser, async API |
| Video→GIF | FFmpeg (2-pass palette) | Best quality, smallest files |
| AI Agent | Codex CLI + OAuth | Your OAuth creds, no API key, full-auto mode |
| Storage | Local filesystem + SQLite | No cloud costs |
| Containers | Docker | Sandboxed, reproducible |

---

## 2. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          TRIGGER LAYER                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ GitHub Push  │  │ GitHub PR    │  │   Webhook    │  │   Manual     │    │
│  │   Event      │  │   Event      │  │   Trigger    │  │   Trigger    │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         └──────────────────┴─────────────────┴─────────────────┘            │
│                                     │                                        │
│                            ┌────────▼────────┐                              │
│                            │ ExecutionService │                              │
│                            │   (Orchestrator) │                              │
│                            └────────┬────────┘                              │
│                                     │                                        │
├─────────────────────────────────────┼────────────────────────────────────────┤
│                          EXECUTION LAYER                                     │
├─────────────────────────────────────┼────────────────────────────────────────┤
│         ┌───────────────────────────┼───────────────────────────┐           │
│         │                           │                           │           │
│  ┌──────▼──────┐  ┌─────────────────▼───────────────┐  ┌───────▼───────┐   │
│  │   Docker    │  │        Recording Services        │  │  Codex Agent  │   │
│  │ Orchestrator│  │  ┌───────────┐  ┌───────────┐   │  │    Service    │   │
│  │             │  │  │    VHS    │  │ Playwright │   │  │   (OAuth)     │   │
│  │ - Lifecycle │  │  │  Service  │  │  Service   │   │  │               │   │
│  │ - Resources │  │  │           │  │            │   │  │ - Review      │   │
│  │ - Cleanup   │  │  │ - .tape   │  │ - Video    │   │  │ - Analyze     │   │
│  └──────┬──────┘  │  │ - GIF     │  │ - Screen   │   │  │ - Generate    │   │
│         │         │  │ - Record  │  │ - Trace    │   │  └───────┬───────┘   │
│         │         │  └─────┬─────┘  └─────┬──────┘   │          │           │
│         │         │        └──────┬───────┘          │          │           │
│         │         └───────────────┼──────────────────┘          │           │
│         │                         │                              │           │
│         │                ┌────────▼────────┐                    │           │
│         │                │  FFmpeg Pipeline │                    │           │
│         │                │                  │                    │           │
│         │                │  - video→gif     │                    │           │
│         │                │  - thumbnails    │                    │           │
│         │                │  - compression   │                    │           │
│         │                └────────┬─────────┘                    │           │
│         │                         │                              │           │
│         └─────────────────────────┼──────────────────────────────┘           │
│                                   │                                          │
├───────────────────────────────────┼──────────────────────────────────────────┤
│                          STORAGE LAYER                                       │
├───────────────────────────────────┼──────────────────────────────────────────┤
│                          ┌────────▼────────┐                                │
│                          │ Artifact Storage │                                │
│                          │   (Local FS)     │                                │
│                          │                  │                                │
│  Storage Layout:         │  ~/.tracertm/    │                                │
│                          │  └── artifacts/  │                                │
│                          │      └── {proj}/ │                                │
│                          │          └── ... │                                │
│                          └────────┬─────────┘                                │
│                                   │                                          │
│                          ┌────────▼────────┐                                │
│                          │     SQLite      │                                │
│                          │   (Metadata)    │                                │
│                          │                 │                                │
│                          │ - Execution     │                                │
│                          │ - Artifact      │                                │
│                          │ - Agent Task    │                                │
│                          └─────────────────┘                                │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                       VISUALIZATION LAYER                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                       QA Enhanced Graph Node                            │ │
│  │  ┌────────────────────────────────────────────────┬─────────────────┐  │ │
│  │  │ Title Header                                   │  ✅ 85% Pass   │  │ │
│  │  │ Subheader | feature                            │     Rate       │  │ │
│  │  ├────────────────────────────────────────────────┴─────────────────┤  │ │
│  │  │  ┌────────────────────────────────────────────────────────────┐  │  │ │
│  │  │  │        [Rounded Pill Image - SEPARATELY CLICKABLE]         │  │  │ │
│  │  │  │        Hover: "Click to expand" | Demo available           │  │  │ │
│  │  │  └────────────────────────────────────────────────────────────┘  │  │ │
│  │  │  🔗 12 links  |  ⏱️ 2.3s  |  🧪 8/10 tests  |  📊 78% coverage  │  │ │
│  │  └──────────────────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    Node Expand Popup (Modal)                            │ │
│  │  ┌─────┬────────────────────────────────────────────────────────────┐  │ │
│  │  │ 📸  │  ARTIFACTS TAB                                              │  │ │
│  │  │     │  Screenshot gallery + Video recordings + Log viewer         │  │ │
│  │  ├─────┼────────────────────────────────────────────────────────────┤  │ │
│  │  │ ▶️  │  DEMO TAB                                                   │  │ │
│  │  │     │  Live iframe sandbox OR enlarged screenshot/video           │  │ │
│  │  ├─────┼────────────────────────────────────────────────────────────┤  │ │
│  │  │ 🧪  │  TEST RESULTS TAB                                           │  │ │
│  │  │     │  Pass/fail breakdown + Flaky tests + Coverage details       │  │ │
│  │  ├─────┼────────────────────────────────────────────────────────────┤  │ │
│  │  │ 📊  │  METRICS TAB                                                │  │ │
│  │  │     │  Performance trends + Duration analysis + History           │  │ │
│  │  ├─────┼────────────────────────────────────────────────────────────┤  │ │
│  │  │ ⚙️  │  ACTIONS TAB                                                │  │ │
│  │  │     │  Re-run tests + Download artifacts + Open in browser        │  │ │
│  │  └─────┴────────────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. TRIGGER (GitHub/Webhook/Manual)
       │
       ▼
2. ExecutionService creates Execution record
       │
       ▼
3. DockerOrchestrator spins up container
       │
       ├──► VHSService generates .tape → runs VHS → outputs GIF
       │
       ├──► PlaywrightService runs tests → captures video/screenshots
       │
       └──► CodexAgentService reviews artifacts (if configured)
               │
               ▼
4. FFmpegPipeline converts video→GIF, generates thumbnails
       │
       ▼
5. ArtifactStorageService stores files to local filesystem
       │
       ▼
6. Update TestRun/TestResult records with artifact references
       │
       ▼
7. Frontend QAEnhancedNode displays metrics + artifacts
```

---

## 3. Technology Stack

### Core Technologies

| Technology | Version | Purpose | Installation |
|------------|---------|---------|--------------|
| **VHS** | Latest | CLI recording | `brew install vhs` |
| **ttyd** | 1.7.2+ | Terminal emulation (VHS dep) | `brew tap tsl0922/ttyd && brew install ttyd` |
| **FFmpeg** | 6.0+ | Video processing | `brew install ffmpeg` |
| **Playwright** | 1.40+ | Web automation | `pip install playwright && playwright install` |
| **Docker** | 24.0+ | Container orchestration | Docker Desktop |
| **Codex CLI** | Latest | AI agent | `npm install -g @openai/codex` |

### Python Dependencies

```toml
# pyproject.toml additions
[project.dependencies]
docker = "^7.0.0"           # Docker SDK
playwright = "^1.40.0"      # Browser automation
aiodocker = "^0.21.0"       # Async Docker SDK (optional)
```

### System Requirements

```bash
# Verify all dependencies
vhs --version          # VHS installed
ttyd --version         # ttyd installed (1.7.2+)
ffmpeg -version        # FFmpeg installed
docker --version       # Docker running
codex --version        # Codex CLI installed
playwright --version   # Playwright installed
```

---

## 4. Database Schema

### New Tables (Alembic Migration)

```python
# alembic/versions/018_add_execution_system.py

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import JSON

def upgrade():
    # Execution: Tracks test/recording runs
    op.create_table(
        'execution',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('project.id', ondelete='CASCADE'), nullable=False),
        sa.Column('test_run_id', sa.String(36), sa.ForeignKey('test_run.id'), nullable=True),

        sa.Column('execution_type', sa.String(50), nullable=False),  # vhs, playwright, codex, custom
        sa.Column('trigger_source', sa.String(50), nullable=False),  # github_pr, github_push, webhook, manual
        sa.Column('trigger_ref', sa.String(255), nullable=True),     # PR number, commit SHA

        sa.Column('status', sa.String(20), nullable=False, default='pending'),  # pending, running, passed, failed, cancelled
        sa.Column('container_id', sa.String(64), nullable=True),

        sa.Column('config', JSON, nullable=True),           # Execution configuration
        sa.Column('environment', sa.Text, nullable=True),   # Encrypted env vars

        sa.Column('started_at', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('duration_ms', sa.Integer, nullable=True),

        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('exit_code', sa.Integer, nullable=True),

        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # ExecutionArtifact: Screenshots, videos, GIFs, logs
    op.create_table(
        'execution_artifact',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('execution_id', sa.String(36), sa.ForeignKey('execution.id', ondelete='CASCADE'), nullable=False),
        sa.Column('item_id', sa.String(36), sa.ForeignKey('item.id'), nullable=True),  # Link to graph node

        sa.Column('artifact_type', sa.String(50), nullable=False),  # screenshot, video, gif, log, trace
        sa.Column('file_path', sa.String(500), nullable=False),     # Local filesystem path
        sa.Column('thumbnail_path', sa.String(500), nullable=True),

        sa.Column('file_size', sa.Integer, nullable=True),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('metadata', JSON, nullable=True),  # dimensions, duration, etc.

        sa.Column('captured_at', sa.DateTime, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # CodexAgentInteraction: AI agent task history
    op.create_table(
        'codex_agent_interaction',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('execution_id', sa.String(36), sa.ForeignKey('execution.id'), nullable=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('project.id', ondelete='CASCADE'), nullable=False),

        sa.Column('task_type', sa.String(50), nullable=False),  # review_image, review_video, code_review, generate_test
        sa.Column('input_data', JSON, nullable=True),
        sa.Column('output_data', JSON, nullable=True),

        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('started_at', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),

        sa.Column('tokens_used', sa.Integer, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),

        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # ExecutionEnvironmentConfig: Per-project settings
    op.create_table(
        'execution_environment_config',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('project.id', ondelete='CASCADE'), nullable=False, unique=True),

        sa.Column('docker_image', sa.String(255), default='node:20-alpine'),
        sa.Column('resource_limits', JSON, nullable=True),   # CPU, memory limits
        sa.Column('environment_vars', sa.Text, nullable=True),  # Encrypted

        sa.Column('vhs_enabled', sa.Boolean, default=True),
        sa.Column('playwright_enabled', sa.Boolean, default=True),
        sa.Column('codex_enabled', sa.Boolean, default=True),

        sa.Column('artifact_retention_days', sa.Integer, default=30),
        sa.Column('storage_path', sa.String(500), nullable=True),

        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Indexes
    op.create_index('idx_execution_project_id', 'execution', ['project_id'])
    op.create_index('idx_execution_status', 'execution', ['status'])
    op.create_index('idx_execution_artifact_execution_id', 'execution_artifact', ['execution_id'])
    op.create_index('idx_execution_artifact_item_id', 'execution_artifact', ['item_id'])
    op.create_index('idx_codex_agent_interaction_project_id', 'codex_agent_interaction', ['project_id'])

def downgrade():
    op.drop_table('execution_environment_config')
    op.drop_table('codex_agent_interaction')
    op.drop_table('execution_artifact')
    op.drop_table('execution')
```

### Storage Layout

```
~/.tracertm/
├── tracertm.db                    # Global SQLite database
├── artifacts/                      # Artifact storage root
│   └── {project_id}/
│       └── {execution_id}/
│           ├── screenshots/
│           │   ├── {artifact_id}.png
│           │   └── {artifact_id}_thumb.jpg
│           ├── videos/
│           │   ├── {artifact_id}.webm
│           │   └── {artifact_id}.gif
│           ├── logs/
│           │   └── {artifact_id}.txt
│           └── traces/
│               └── {artifact_id}.zip
└── codex/                          # Codex credentials (managed by Codex CLI)
    └── auth.json
```

---

## 5. VHS CLI Recording Integration

### Overview

VHS (charmbracelet/vhs) records terminal sessions as GIF/video using declarative `.tape` files.

### Installation

```bash
# macOS
brew install vhs && brew tap tsl0922/ttyd && brew install ttyd

# Ubuntu/Debian
sudo apt update && sudo apt install vhs ffmpeg

# Docker (no local install needed)
docker run --rm -v $PWD:/vhs ghcr.io/charmbracelet/vhs demo.tape
```

### TapeFileGenerator Class

```python
# src/tracertm/services/recording/tape_generator.py

from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class TapeFileGenerator:
    """Fluent API for generating VHS .tape files programmatically."""

    _settings: list[str] = field(default_factory=list)
    _requires: list[str] = field(default_factory=list)
    _commands: list[str] = field(default_factory=list)

    # === Output Configuration ===

    def output(self, path: str) -> "TapeFileGenerator":
        """Set output file path. Supports: .gif, .mp4, .webm, directory for frames."""
        self._settings.append(f'Output "{path}"')
        return self

    # === Display Settings ===

    def set_shell(self, shell: str = "bash") -> "TapeFileGenerator":
        self._settings.append(f"Set Shell {shell}")
        return self

    def set_font_size(self, size: int = 14) -> "TapeFileGenerator":
        self._settings.append(f"Set FontSize {size}")
        return self

    def set_font_family(self, family: str = "JetBrains Mono") -> "TapeFileGenerator":
        self._settings.append(f'Set FontFamily "{family}"')
        return self

    def set_width(self, width: int = 1200) -> "TapeFileGenerator":
        self._settings.append(f"Set Width {width}")
        return self

    def set_height(self, height: int = 600) -> "TapeFileGenerator":
        self._settings.append(f"Set Height {height}")
        return self

    def set_theme(self, theme: str = "Dracula") -> "TapeFileGenerator":
        """Set theme. Run `vhs themes` for full list."""
        self._settings.append(f'Set Theme "{theme}"')
        return self

    def set_padding(self, padding: int = 10) -> "TapeFileGenerator":
        self._settings.append(f"Set Padding {padding}")
        return self

    def set_framerate(self, fps: int = 30) -> "TapeFileGenerator":
        self._settings.append(f"Set Framerate {fps}")
        return self

    def set_typing_speed(self, speed: str = "50ms") -> "TapeFileGenerator":
        self._settings.append(f"Set TypingSpeed {speed}")
        return self

    def set_playback_speed(self, speed: float = 1.0) -> "TapeFileGenerator":
        self._settings.append(f"Set PlaybackSpeed {speed}")
        return self

    # === Requirements ===

    def require(self, program: str) -> "TapeFileGenerator":
        """Fail early if program not in PATH."""
        self._requires.append(f"Require {program}")
        return self

    # === Environment ===

    def env(self, key: str, value: str) -> "TapeFileGenerator":
        self._commands.append(f'Env {key} "{value}"')
        return self

    def source(self, tape_path: str) -> "TapeFileGenerator":
        """Include commands from another tape file."""
        self._commands.append(f'Source "{tape_path}"')
        return self

    # === Text Input ===

    def type(self, text: str, speed: Optional[str] = None) -> "TapeFileGenerator":
        """Type text. Optional speed override (e.g., "100ms")."""
        escaped = text.replace('"', '\\"')
        if speed:
            self._commands.append(f'Type@{speed} "{escaped}"')
        else:
            self._commands.append(f'Type "{escaped}"')
        return self

    def enter(self) -> "TapeFileGenerator":
        self._commands.append("Enter")
        return self

    def backspace(self, count: int = 1) -> "TapeFileGenerator":
        self._commands.append(f"Backspace {count}" if count > 1 else "Backspace")
        return self

    def space(self, count: int = 1) -> "TapeFileGenerator":
        self._commands.append(f"Space {count}" if count > 1 else "Space")
        return self

    def tab(self) -> "TapeFileGenerator":
        self._commands.append("Tab")
        return self

    # === Navigation ===

    def up(self, count: int = 1) -> "TapeFileGenerator":
        self._commands.append(f"Up {count}" if count > 1 else "Up")
        return self

    def down(self, count: int = 1) -> "TapeFileGenerator":
        self._commands.append(f"Down {count}" if count > 1 else "Down")
        return self

    def left(self, count: int = 1) -> "TapeFileGenerator":
        self._commands.append(f"Left {count}" if count > 1 else "Left")
        return self

    def right(self, count: int = 1) -> "TapeFileGenerator":
        self._commands.append(f"Right {count}" if count > 1 else "Right")
        return self

    # === Control Keys ===

    def ctrl(self, key: str) -> "TapeFileGenerator":
        self._commands.append(f"Ctrl+{key}")
        return self

    def alt(self, key: str) -> "TapeFileGenerator":
        self._commands.append(f"Alt+{key}")
        return self

    # === Timing ===

    def sleep(self, seconds: float) -> "TapeFileGenerator":
        self._commands.append(f"Sleep {seconds}s")
        return self

    def wait(self, pattern: Optional[str] = None, timeout: Optional[str] = None, search_screen: bool = False) -> "TapeFileGenerator":
        """Wait for pattern on last line (or screen if search_screen=True)."""
        cmd = "Wait"
        if search_screen:
            cmd += "+Screen"
        if timeout:
            cmd += f"@{timeout}"
        if pattern:
            cmd += f" /{pattern}/"
        self._commands.append(cmd)
        return self

    # === Visibility ===

    def hide(self) -> "TapeFileGenerator":
        """Hide subsequent commands from recording."""
        self._commands.append("Hide")
        return self

    def show(self) -> "TapeFileGenerator":
        """Show subsequent commands in recording."""
        self._commands.append("Show")
        return self

    # === Screenshots ===

    def screenshot(self, filename: str) -> "TapeFileGenerator":
        self._commands.append(f'Screenshot "{filename}"')
        return self

    # === Build ===

    def build(self) -> str:
        """Generate the complete .tape file content."""
        lines = []
        lines.extend(self._settings)
        if self._settings:
            lines.append("")
        lines.extend(self._requires)
        if self._requires:
            lines.append("")
        lines.extend(self._commands)
        return "\n".join(lines)

    def write(self, path: str | Path) -> None:
        """Write tape content to file."""
        Path(path).write_text(self.build())

    # === Convenience Methods ===

    def run_command(self, command: str, wait_pattern: Optional[str] = None, wait_seconds: float = 1.0) -> "TapeFileGenerator":
        """Type command, press enter, optionally wait for pattern or sleep."""
        self.type(command)
        self.enter()
        if wait_pattern:
            self.wait(wait_pattern)
        else:
            self.sleep(wait_seconds)
        return self

    def hidden_setup(self, commands: list[str]) -> "TapeFileGenerator":
        """Run setup commands hidden from recording."""
        self.hide()
        for cmd in commands:
            self.type(cmd)
            self.enter()
        self.type("clear")
        self.enter()
        self.show()
        return self
```

### VHSExecutionService

```python
# src/tracertm/services/recording/vhs_service.py

import asyncio
import tempfile
from pathlib import Path
from uuid import uuid4
from datetime import datetime

from .tape_generator import TapeFileGenerator
from ..execution.artifact_storage import ArtifactStorageService
from ...models.execution_artifact import ExecutionArtifact


class VHSExecutionError(Exception):
    """Raised when VHS execution fails."""
    pass


class VHSExecutionService:
    """Execute VHS recordings and store artifacts."""

    def __init__(self, artifact_storage: ArtifactStorageService):
        self.artifact_storage = artifact_storage
        self._temp_dir = Path(tempfile.gettempdir()) / "tracertm_vhs"
        self._temp_dir.mkdir(exist_ok=True)

    async def check_availability(self) -> tuple[bool, str]:
        """Check if VHS and dependencies are installed."""
        checks = [
            ("vhs", ["vhs", "--version"]),
            ("ttyd", ["ttyd", "--version"]),
            ("ffmpeg", ["ffmpeg", "-version"]),
        ]

        for name, cmd in checks:
            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await proc.communicate()
                if proc.returncode != 0:
                    return False, f"{name} not working properly"
            except FileNotFoundError:
                return False, f"{name} not found in PATH"

        return True, "All dependencies available"

    async def record(
        self,
        tape_content: str,
        execution_id: str,
        output_format: str = "gif",
        working_dir: str | None = None,
        timeout: int = 300
    ) -> ExecutionArtifact:
        """Execute VHS recording from tape content."""

        # Write tape to temp file
        tape_id = str(uuid4())[:8]
        tape_path = self._temp_dir / f"{tape_id}.tape"
        output_path = self._temp_dir / f"{tape_id}.{output_format}"

        # Inject output path into tape content
        tape_with_output = f'Output "{output_path}"\n\n{tape_content}'
        tape_path.write_text(tape_with_output)

        try:
            # Run VHS
            proc = await asyncio.create_subprocess_exec(
                "vhs", str(tape_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir
            )

            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout
            )

            if proc.returncode != 0:
                raise VHSExecutionError(f"VHS failed: {stderr.decode()}")

            if not output_path.exists():
                raise VHSExecutionError("VHS did not produce output file")

            # Store artifact
            artifact = await self.artifact_storage.store_artifact(
                execution_id=execution_id,
                artifact_type="gif" if output_format == "gif" else "video",
                file_data=output_path,
                metadata={
                    "format": output_format,
                    "tape_content": tape_content,
                    "source": "vhs"
                }
            )

            return artifact

        finally:
            # Cleanup temp files
            tape_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)

    async def record_command(
        self,
        command: str,
        execution_id: str,
        wait_seconds: float = 5.0,
        theme: str = "Dracula",
        width: int = 960,
        height: int = 540
    ) -> ExecutionArtifact:
        """Convenience method to record a single command execution."""

        tape = (
            TapeFileGenerator()
            .set_shell("bash")
            .set_font_size(14)
            .set_width(width)
            .set_height(height)
            .set_theme(theme)
            .set_framerate(30)
            .type(command)
            .enter()
            .sleep(wait_seconds)
        )

        return await self.record(
            tape_content=tape.build(),
            execution_id=execution_id
        )

    async def record_test_run(
        self,
        test_command: str,
        execution_id: str,
        setup_commands: list[str] | None = None,
        wait_pattern: str | None = None
    ) -> ExecutionArtifact:
        """Record a test run with optional setup."""

        tape = (
            TapeFileGenerator()
            .set_shell("bash")
            .set_font_size(14)
            .set_width(1200)
            .set_height(600)
            .set_theme("Catppuccin Frappe")
            .set_framerate(30)
        )

        # Hidden setup
        if setup_commands:
            tape.hidden_setup(setup_commands)

        # Run test command
        tape.type(test_command)
        tape.enter()

        if wait_pattern:
            tape.wait(wait_pattern, timeout="120s")
        else:
            tape.sleep(30)

        return await self.record(
            tape_content=tape.build(),
            execution_id=execution_id
        )
```

### Example Usage

```python
# Record npm test
tape = (
    TapeFileGenerator()
    .output("test-demo.gif")
    .set_shell("bash")
    .set_font_size(14)
    .set_width(960)
    .set_height(540)
    .set_theme("Dracula")
    .require("npm")
    .hidden_setup(["cd /path/to/project", "npm install"])
    .type("npm test -- --coverage")
    .enter()
    .wait("Tests:", timeout="120s")
    .sleep(2)
)

# Write to file
tape.write("/tmp/test-demo.tape")

# Or execute via service
artifact = await vhs_service.record(
    tape_content=tape.build(),
    execution_id="exec-123"
)
```

---

## 6. Playwright Web Testing Integration

### PlaywrightExecutionService

```python
# src/tracertm/services/recording/playwright_service.py

import asyncio
from pathlib import Path
from uuid import uuid4
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from .ffmpeg_pipeline import FFmpegPipeline
from ..execution.artifact_storage import ArtifactStorageService
from ...models.execution_artifact import ExecutionArtifact


@dataclass
class PlaywrightAction:
    """Single action to perform on a page."""
    action: str  # click, type, goto, wait, screenshot
    selector: Optional[str] = None
    value: Optional[str] = None
    options: dict = field(default_factory=dict)


@dataclass
class PlaywrightTestConfig:
    """Configuration for Playwright test execution."""
    url: Optional[str] = None
    test_file: Optional[str] = None
    test_command: Optional[str] = None
    browser: str = "chromium"  # chromium, firefox, webkit
    headless: bool = True
    video: bool = True
    trace: bool = True
    screenshots: str = "on"  # on, off, only-on-failure
    viewport_width: int = 1280
    viewport_height: int = 720
    timeout_ms: int = 30000


class PlaywrightExecutionService:
    """Execute Playwright tests with video/screenshot capture."""

    def __init__(
        self,
        artifact_storage: ArtifactStorageService,
        ffmpeg_pipeline: FFmpegPipeline
    ):
        self.artifact_storage = artifact_storage
        self.ffmpeg_pipeline = ffmpeg_pipeline

    async def capture_screenshot(
        self,
        url: str,
        execution_id: str,
        viewport: tuple[int, int] = (1280, 720),
        full_page: bool = False,
        wait_for: str = "networkidle",
        item_id: Optional[str] = None
    ) -> ExecutionArtifact:
        """Capture screenshot of a URL."""

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": viewport[0], "height": viewport[1]}
            )
            page = await context.new_page()

            await page.goto(url, wait_until=wait_for)

            screenshot_bytes = await page.screenshot(full_page=full_page)

            await context.close()
            await browser.close()

        # Store artifact
        artifact = await self.artifact_storage.store_artifact(
            execution_id=execution_id,
            artifact_type="screenshot",
            file_data=screenshot_bytes,
            item_id=item_id,
            metadata={
                "url": url,
                "viewport": viewport,
                "full_page": full_page,
                "source": "playwright"
            }
        )

        return artifact

    async def record_interaction(
        self,
        url: str,
        actions: list[PlaywrightAction],
        execution_id: str,
        viewport: tuple[int, int] = (1280, 720),
        item_id: Optional[str] = None
    ) -> tuple[ExecutionArtifact, ExecutionArtifact]:
        """Record a sequence of interactions as video, convert to GIF."""

        video_dir = Path(f"/tmp/playwright_video_{uuid4()}")
        video_dir.mkdir(exist_ok=True)

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={"width": viewport[0], "height": viewport[1]},
                    record_video_dir=str(video_dir),
                    record_video_size={"width": viewport[0], "height": viewport[1]}
                )
                page = await context.new_page()

                await page.goto(url, wait_until="networkidle")

                # Execute actions
                for action in actions:
                    await self._execute_action(page, action)

                # Close to finalize video
                await page.close()
                await context.close()
                await browser.close()

            # Find video file
            video_files = list(video_dir.glob("*.webm"))
            if not video_files:
                raise RuntimeError("No video file produced")

            video_path = video_files[0]

            # Convert to GIF
            gif_path = video_dir / f"{video_path.stem}.gif"
            await self.ffmpeg_pipeline.video_to_gif(
                video_path, gif_path,
                fps=10, scale=min(viewport[0], 640)
            )

            # Store both artifacts
            video_artifact = await self.artifact_storage.store_artifact(
                execution_id=execution_id,
                artifact_type="video",
                file_data=video_path,
                item_id=item_id,
                metadata={"url": url, "format": "webm", "source": "playwright"}
            )

            gif_artifact = await self.artifact_storage.store_artifact(
                execution_id=execution_id,
                artifact_type="gif",
                file_data=gif_path,
                item_id=item_id,
                metadata={"url": url, "format": "gif", "source": "playwright"}
            )

            return video_artifact, gif_artifact

        finally:
            # Cleanup temp directory
            import shutil
            shutil.rmtree(video_dir, ignore_errors=True)

    async def run_test_file(
        self,
        config: PlaywrightTestConfig,
        execution_id: str
    ) -> dict:
        """Run Playwright test file and capture results."""

        cmd = ["npx", "playwright", "test"]

        if config.test_file:
            cmd.append(config.test_file)

        if config.video:
            cmd.extend(["--video", "on"])

        if config.trace:
            cmd.extend(["--trace", "on"])

        cmd.extend(["--reporter", "json"])

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await asyncio.wait_for(
            proc.communicate(),
            timeout=config.timeout_ms / 1000
        )

        return {
            "success": proc.returncode == 0,
            "output": stdout.decode(),
            "errors": stderr.decode(),
            "exit_code": proc.returncode
        }

    async def _execute_action(self, page: Page, action: PlaywrightAction):
        """Execute a single action on the page."""

        if action.action == "click":
            await page.click(action.selector, **action.options)

        elif action.action == "type":
            await page.fill(action.selector, action.value, **action.options)

        elif action.action == "goto":
            await page.goto(action.value, **action.options)

        elif action.action == "wait":
            if action.selector:
                await page.wait_for_selector(action.selector, **action.options)
            elif action.value:
                await page.wait_for_timeout(int(action.value))

        elif action.action == "screenshot":
            await page.screenshot(path=action.value, **action.options)

        elif action.action == "hover":
            await page.hover(action.selector, **action.options)
```

### Example Usage

```python
# Capture screenshot
screenshot = await playwright_service.capture_screenshot(
    url="https://example.com",
    execution_id="exec-123",
    full_page=True
)

# Record interaction
actions = [
    PlaywrightAction(action="click", selector="button.login"),
    PlaywrightAction(action="type", selector="input[name=email]", value="user@example.com"),
    PlaywrightAction(action="type", selector="input[name=password]", value="password"),
    PlaywrightAction(action="click", selector="button[type=submit]"),
    PlaywrightAction(action="wait", selector=".dashboard"),
]

video, gif = await playwright_service.record_interaction(
    url="https://example.com",
    actions=actions,
    execution_id="exec-123"
)
```

---

## 7. FFmpeg Media Pipeline

### FFmpegPipeline Class

```python
# src/tracertm/services/recording/ffmpeg_pipeline.py

import asyncio
from pathlib import Path
from uuid import uuid4
from dataclasses import dataclass
from typing import Optional


@dataclass
class VideoInfo:
    """Information about a video file."""
    duration: float  # seconds
    width: int
    height: int
    fps: float
    codec: str
    size_bytes: int


class FFmpegError(Exception):
    """Raised when FFmpeg command fails."""
    pass


class FFmpegPipeline:
    """Reusable FFmpeg operations for video processing."""

    async def check_availability(self) -> tuple[bool, str]:
        """Check if FFmpeg is installed."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "ffmpeg", "-version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            if proc.returncode == 0:
                version = stdout.decode().split("\n")[0]
                return True, version
            return False, "FFmpeg not working properly"
        except FileNotFoundError:
            return False, "FFmpeg not found in PATH"

    async def video_to_gif(
        self,
        input_path: str | Path,
        output_path: str | Path,
        fps: int = 10,
        scale: int = 640,
        optimize_palette: bool = True
    ) -> Path:
        """
        Convert video to GIF.

        Two-pass with palette optimization produces 40-60% smaller files
        with better color accuracy.
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        if optimize_palette:
            # Two-pass: Generate palette, then apply
            palette_path = Path(f"/tmp/palette_{uuid4()}.png")

            try:
                # Pass 1: Generate optimized palette
                await self._run([
                    "-i", str(input_path),
                    "-vf", f"fps={fps},scale={scale}:-1:flags=lanczos,palettegen=stats_mode=diff",
                    "-y", str(palette_path)
                ])

                # Pass 2: Apply palette with dithering
                await self._run([
                    "-i", str(input_path),
                    "-i", str(palette_path),
                    "-lavfi", f"fps={fps},scale={scale}:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5",
                    "-y", str(output_path)
                ])
            finally:
                palette_path.unlink(missing_ok=True)
        else:
            # Single pass (faster, larger file)
            await self._run([
                "-i", str(input_path),
                "-vf", f"fps={fps},scale={scale}:-1:flags=lanczos",
                "-y", str(output_path)
            ])

        return output_path

    async def generate_thumbnail(
        self,
        video_path: str | Path,
        output_path: str | Path,
        timestamp: float = 0.0,
        size: tuple[int, int] = (300, 300),
        quality: int = 2
    ) -> Path:
        """
        Extract thumbnail from video at specified timestamp.

        Using -ss before -i is ~4x faster (input seeking vs output seeking).
        """
        await self._run([
            "-ss", str(timestamp),
            "-i", str(video_path),
            "-vframes", "1",
            "-vf", f"scale={size[0]}:{size[1]}:force_original_aspect_ratio=decrease",
            "-q:v", str(quality),
            "-y", str(output_path)
        ])
        return Path(output_path)

    async def generate_best_thumbnail(
        self,
        video_path: str | Path,
        output_path: str | Path,
        size: tuple[int, int] = (300, 300),
        sample_frames: int = 100
    ) -> Path:
        """
        Select best frame automatically using thumbnail filter.

        Analyzes frames for sharpness/clarity and picks the best one.
        """
        await self._run([
            "-i", str(video_path),
            "-vf", f"thumbnail=n={sample_frames},scale={size[0]}:{size[1]}:force_original_aspect_ratio=decrease",
            "-vframes", "1",
            "-q:v", "2",
            "-y", str(output_path)
        ])
        return Path(output_path)

    async def compress_video(
        self,
        input_path: str | Path,
        output_path: str | Path,
        codec: str = "libx264",
        crf: int = 23,
        preset: str = "medium"
    ) -> Path:
        """
        Compress video with specified codec and quality.

        CRF Guide:
        - 18: Near-lossless, ~70% of original
        - 23: High quality, ~45% of original (default)
        - 28: Good quality, ~25% of original
        """
        await self._run([
            "-i", str(input_path),
            "-c:v", codec,
            "-crf", str(crf),
            "-preset", preset,
            "-movflags", "+faststart",  # Web optimization
            "-y", str(output_path)
        ])
        return Path(output_path)

    async def extract_frames(
        self,
        video_path: str | Path,
        output_dir: str | Path,
        interval_seconds: float = 1.0,
        format: str = "jpg"
    ) -> list[Path]:
        """Extract frames at regular intervals."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_pattern = str(output_dir / f"frame_%04d.{format}")

        await self._run([
            "-i", str(video_path),
            "-vf", f"fps=1/{interval_seconds}",
            "-q:v", "2",
            "-y", output_pattern
        ])

        return sorted(output_dir.glob(f"frame_*.{format}"))

    async def extract_keyframes(
        self,
        video_path: str | Path,
        output_dir: str | Path,
        format: str = "jpg"
    ) -> list[Path]:
        """
        Extract only keyframes (I-frames).

        10-20x faster than regular frame extraction.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_pattern = str(output_dir / f"keyframe_%04d.{format}")

        await self._run([
            "-i", str(video_path),
            "-vf", "select='eq(pict_type,I)'",
            "-vsync", "vfr",
            "-q:v", "2",
            "-y", output_pattern
        ])

        return sorted(output_dir.glob(f"keyframe_*.{format}"))

    async def detect_scenes(
        self,
        video_path: str | Path,
        output_dir: str | Path,
        threshold: float = 0.4,
        format: str = "jpg"
    ) -> list[Path]:
        """
        Extract frames at scene changes.

        Threshold guide:
        - 0.3: Sensitive, many frames
        - 0.4: Balanced (recommended)
        - 0.5: Conservative, major changes only
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_pattern = str(output_dir / f"scene_%04d.{format}")

        await self._run([
            "-i", str(video_path),
            "-vf", f"select='gt(scene,{threshold})'",
            "-vsync", "vfr",
            "-q:v", "2",
            "-y", output_pattern
        ])

        return sorted(output_dir.glob(f"scene_*.{format}"))

    async def get_video_info(self, video_path: str | Path) -> VideoInfo:
        """Get video metadata using ffprobe."""
        import json

        proc = await asyncio.create_subprocess_exec(
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(video_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, _ = await proc.communicate()
        data = json.loads(stdout.decode())

        video_stream = next(
            (s for s in data["streams"] if s["codec_type"] == "video"),
            None
        )

        if not video_stream:
            raise FFmpegError("No video stream found")

        fps_parts = video_stream.get("r_frame_rate", "30/1").split("/")
        fps = float(fps_parts[0]) / float(fps_parts[1]) if len(fps_parts) == 2 else 30.0

        return VideoInfo(
            duration=float(data["format"].get("duration", 0)),
            width=int(video_stream.get("width", 0)),
            height=int(video_stream.get("height", 0)),
            fps=fps,
            codec=video_stream.get("codec_name", "unknown"),
            size_bytes=int(data["format"].get("size", 0))
        )

    async def _run(self, args: list[str], timeout: int = 300) -> None:
        """Run FFmpeg command."""
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        _, stderr = await asyncio.wait_for(
            proc.communicate(),
            timeout=timeout
        )

        if proc.returncode != 0:
            raise FFmpegError(f"FFmpeg failed: {stderr.decode()}")
```

### Quick Reference

```python
# Video to GIF (optimized)
await ffmpeg.video_to_gif("video.webm", "output.gif", fps=10, scale=480)

# Fast thumbnail
await ffmpeg.generate_thumbnail("video.mp4", "thumb.jpg", timestamp=5.0)

# Best frame thumbnail
await ffmpeg.generate_best_thumbnail("video.mp4", "thumb.jpg")

# Compress video
await ffmpeg.compress_video("input.mp4", "output.mp4", crf=28)

# Extract frames every 2 seconds
frames = await ffmpeg.extract_frames("video.mp4", "./frames", interval_seconds=2.0)

# Scene detection
scenes = await ffmpeg.detect_scenes("video.mp4", "./scenes", threshold=0.4)
```

---

## 8. Codex CLI Agent Integration

### CodexAgentService

```python
# src/tracertm/services/agents/codex_service.py

import asyncio
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from uuid import uuid4
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..execution.artifact_storage import ArtifactStorageService
from ..recording.ffmpeg_pipeline import FFmpegPipeline
from ...models.codex_agent_interaction import CodexAgentInteraction


@dataclass
class CodexTask:
    """Definition of a Codex agent task."""
    task_type: str  # review_image, review_video, code_review, generate_test, custom
    prompt: str
    input_files: Optional[list[str]] = None
    codebase_dir: Optional[str] = None
    full_auto: bool = False  # --full-auto for CI/CD
    sandbox: str = "workspace-write"  # read-only, workspace-write, danger-full-access
    timeout_seconds: int = 300
    model: str = "o3"  # o3, o4-mini, gpt-4


class CodexAgentService:
    """
    Integration with OpenAI Codex CLI using OAuth authentication.

    Authentication Methods:
    1. OAuth (default): codex login - opens browser for ChatGPT login
    2. Device Code: codex login --device-auth - for headless/SSH environments
    3. API Key: OPENAI_API_KEY env var - for CI/CD
    """

    def __init__(
        self,
        db: AsyncSession,
        artifact_storage: ArtifactStorageService,
        ffmpeg_pipeline: FFmpegPipeline
    ):
        self.db = db
        self.artifact_storage = artifact_storage
        self.ffmpeg_pipeline = ffmpeg_pipeline

    async def check_availability(self) -> tuple[bool, str]:
        """Check if Codex CLI is installed."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "codex", "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            if proc.returncode == 0:
                return True, stdout.decode().strip()
            return False, "Codex CLI not working"
        except FileNotFoundError:
            return False, "Codex CLI not found (npm install -g @openai/codex)"

    async def check_auth_status(self) -> tuple[bool, str]:
        """Check if authenticated with Codex."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "codex", "auth", "status",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            output = stdout.decode().lower()
            authenticated = "authenticated" in output or "logged in" in output
            return authenticated, stdout.decode().strip()
        except Exception as e:
            return False, str(e)

    async def setup_oauth(self) -> str:
        """
        Initiate OAuth flow with device code authentication.

        Returns URL for user to visit and enter code.
        """
        proc = await asyncio.create_subprocess_exec(
            "codex", "login", "--device-auth",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        return stdout.decode()

    async def run_task(
        self,
        task: CodexTask,
        project_id: str,
        execution_id: Optional[str] = None
    ) -> CodexAgentInteraction:
        """Execute a Codex agent task."""

        # Create interaction record
        interaction = CodexAgentInteraction(
            id=str(uuid4()),
            project_id=project_id,
            execution_id=execution_id,
            task_type=task.task_type,
            input_data=asdict(task),
            status="pending"
        )
        self.db.add(interaction)
        await self.db.commit()

        try:
            # Build command
            cmd = ["codex", "exec"]

            cmd.extend(["--task", task.prompt])
            cmd.extend(["--model", task.model])
            cmd.extend(["--sandbox", task.sandbox])

            if task.full_auto:
                cmd.append("--full-auto")

            if task.codebase_dir:
                cmd.extend(["--cwd", task.codebase_dir])

            if task.input_files:
                for file_path in task.input_files:
                    cmd.extend(["--file", file_path])

            # Update status
            interaction.status = "running"
            interaction.started_at = datetime.utcnow()
            await self.db.commit()

            # Execute
            env = self._get_sanitized_env()

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )

            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=task.timeout_seconds
            )

            output_text = stdout.decode()

            interaction.output_data = {
                "raw_output": output_text,
                "parsed": self._parse_output(output_text),
                "exit_code": proc.returncode
            }
            interaction.status = "completed" if proc.returncode == 0 else "failed"
            interaction.completed_at = datetime.utcnow()

            if proc.returncode != 0:
                interaction.error_message = stderr.decode()

        except asyncio.TimeoutError:
            interaction.status = "failed"
            interaction.error_message = f"Task timed out after {task.timeout_seconds}s"
            interaction.completed_at = datetime.utcnow()
        except Exception as e:
            interaction.status = "failed"
            interaction.error_message = str(e)
            interaction.completed_at = datetime.utcnow()

        await self.db.commit()
        return interaction

    async def review_image(
        self,
        image_path: str,
        prompt: str,
        project_id: str
    ) -> CodexAgentInteraction:
        """Have Codex review an image (screenshot, diagram, etc.)."""
        task = CodexTask(
            task_type="review_image",
            prompt=f"Review this image: {prompt}",
            input_files=[image_path],
            sandbox="read-only"
        )
        return await self.run_task(task, project_id)

    async def review_video(
        self,
        video_path: str,
        prompt: str,
        project_id: str,
        max_frames: int = 10
    ) -> CodexAgentInteraction:
        """
        Have Codex review a video by analyzing key frames.

        Extracts frames at regular intervals and sends to Codex.
        """
        import tempfile

        frame_dir = tempfile.mkdtemp(prefix="codex_frames_")

        try:
            # Extract frames
            frames = await self.ffmpeg_pipeline.extract_frames(
                video_path,
                frame_dir,
                interval_seconds=2.0
            )

            # Limit frames
            frames = frames[:max_frames]

            task = CodexTask(
                task_type="review_video",
                prompt=f"Review these video frames showing a user interaction: {prompt}",
                input_files=[str(f) for f in frames],
                sandbox="read-only"
            )
            return await self.run_task(task, project_id)

        finally:
            import shutil
            shutil.rmtree(frame_dir, ignore_errors=True)

    async def code_review(
        self,
        file_paths: list[str],
        prompt: str,
        project_id: str,
        codebase_dir: Optional[str] = None
    ) -> CodexAgentInteraction:
        """Have Codex review code files."""
        task = CodexTask(
            task_type="code_review",
            prompt=prompt,
            input_files=file_paths,
            codebase_dir=codebase_dir,
            sandbox="read-only"
        )
        return await self.run_task(task, project_id)

    async def generate_tests(
        self,
        source_file: str,
        project_id: str,
        test_framework: str = "pytest"
    ) -> CodexAgentInteraction:
        """Have Codex generate tests for a source file."""
        task = CodexTask(
            task_type="generate_test",
            prompt=f"Generate comprehensive {test_framework} tests for this file with edge cases and error handling",
            input_files=[source_file],
            sandbox="workspace-write"
        )
        return await self.run_task(task, project_id)

    def _get_sanitized_env(self) -> dict:
        """Get environment with sensitive variables removed."""
        env = os.environ.copy()

        # Keep OPENAI_API_KEY if using API key auth
        sensitive_vars = [
            "ANTHROPIC_API_KEY", "GOOGLE_AI_KEY",
            "AWS_SECRET_ACCESS_KEY", "GITHUB_TOKEN",
            "DATABASE_URL", "SECRET_KEY", "JWT_SECRET"
        ]

        for var in sensitive_vars:
            env.pop(var, None)

        return env

    def _parse_output(self, output: str) -> dict:
        """Parse structured output from Codex."""
        # Try to extract JSON if present
        try:
            if "```json" in output:
                start = output.index("```json") + 7
                end = output.index("```", start)
                return {"json": json.loads(output[start:end]), "text": output}
        except (ValueError, json.JSONDecodeError):
            pass

        return {"text": output}
```

### Quick Reference

```bash
# Authentication
codex login                    # OAuth (browser)
codex login --device-auth      # Device code (headless)
export OPENAI_API_KEY="sk-..." # API key (CI/CD)

# Check status
codex auth status

# Run task
codex exec --task "Review this code" --file app.py
codex exec --task "Generate tests" --full-auto

# Sandbox modes
--sandbox read-only            # Safest, analysis only
--sandbox workspace-write      # Can write to workspace (default)
--sandbox danger-full-access   # Full access (containers only!)
```

---

## 9. Docker Execution Environment

### DockerOrchestrator

```python
# src/tracertm/services/execution/docker_orchestrator.py

import asyncio
import docker
from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4


@dataclass
class ResourceLimits:
    """Container resource constraints."""
    cpu_count: float = 2.0       # Number of CPUs
    memory_mb: int = 2048        # Memory limit in MB
    memory_swap_mb: int = -1     # Swap limit (-1 = same as memory)
    disk_mb: int = 5120          # Disk limit (if supported)
    network_disabled: bool = False
    read_only_fs: bool = True    # Read-only root filesystem


@dataclass
class ContainerConfig:
    """Container configuration."""
    image: str = "node:20-alpine"
    command: Optional[str] = None
    working_dir: str = "/app"
    environment: dict = field(default_factory=dict)
    volumes: dict = field(default_factory=dict)  # host_path: container_path
    resource_limits: ResourceLimits = field(default_factory=ResourceLimits)
    user: str = "1000:1000"      # Non-root user
    tmpfs: dict = field(default_factory=lambda: {"/tmp": "size=100m"})


class DockerOrchestrator:
    """Manage Docker container lifecycle for test execution."""

    def __init__(self):
        self.client = docker.from_env()

    async def create_container(self, config: ContainerConfig) -> str:
        """Create a new container with security constraints."""

        # Build volume bindings
        volumes = {}
        for host_path, container_path in config.volumes.items():
            volumes[host_path] = {"bind": container_path, "mode": "ro"}  # Read-only

        # Resource limits
        limits = config.resource_limits

        container = self.client.containers.create(
            image=config.image,
            command=config.command,
            working_dir=config.working_dir,
            environment=config.environment,
            volumes=volumes,
            user=config.user,

            # Resource constraints
            mem_limit=f"{limits.memory_mb}m",
            memswap_limit=f"{limits.memory_swap_mb}m" if limits.memory_swap_mb > 0 else None,
            cpu_count=int(limits.cpu_count),

            # Security
            read_only=limits.read_only_fs,
            tmpfs=config.tmpfs,
            network_disabled=limits.network_disabled,
            cap_drop=["ALL"],  # Drop all capabilities
            security_opt=["no-new-privileges:true"],

            # Prevent privilege escalation
            privileged=False,

            detach=True
        )

        return container.id

    async def start_container(self, container_id: str) -> None:
        """Start a container."""
        container = self.client.containers.get(container_id)
        container.start()

    async def stop_container(self, container_id: str, timeout: int = 10) -> None:
        """Stop a container gracefully."""
        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=timeout)
        except docker.errors.NotFound:
            pass

    async def remove_container(self, container_id: str, force: bool = True) -> None:
        """Remove a container."""
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force, v=True)  # v=True removes volumes
        except docker.errors.NotFound:
            pass

    async def get_logs(self, container_id: str, tail: int = 100) -> str:
        """Get container logs."""
        container = self.client.containers.get(container_id)
        return container.logs(tail=tail).decode()

    async def wait_for_completion(
        self,
        container_id: str,
        timeout: int = 300
    ) -> int:
        """Wait for container to complete and return exit code."""
        container = self.client.containers.get(container_id)

        # Poll for completion
        start_time = asyncio.get_event_loop().time()
        while True:
            container.reload()
            if container.status in ("exited", "dead"):
                return container.attrs["State"]["ExitCode"]

            if asyncio.get_event_loop().time() - start_time > timeout:
                await self.stop_container(container_id)
                raise asyncio.TimeoutError(f"Container timed out after {timeout}s")

            await asyncio.sleep(1)

    async def run_command(
        self,
        image: str,
        command: str,
        codebase_path: str,
        environment: dict = None,
        timeout: int = 300
    ) -> tuple[int, str, str]:
        """Run a command in a new container and return result."""

        config = ContainerConfig(
            image=image,
            command=command,
            volumes={codebase_path: "/app"},
            environment=environment or {}
        )

        container_id = await self.create_container(config)

        try:
            await self.start_container(container_id)
            exit_code = await self.wait_for_completion(container_id, timeout)

            container = self.client.containers.get(container_id)
            stdout = container.logs(stdout=True, stderr=False).decode()
            stderr = container.logs(stdout=False, stderr=True).decode()

            return exit_code, stdout, stderr

        finally:
            await self.remove_container(container_id)

    async def cleanup_old_containers(self, label: str = "tracertm") -> int:
        """Remove old containers with matching label."""
        count = 0
        for container in self.client.containers.list(all=True, filters={"label": label}):
            try:
                container.remove(force=True)
                count += 1
            except Exception:
                pass
        return count
```

---

## 10. Enhanced Node Visualization

### QAEnhancedNode Component

```tsx
// frontend/apps/web/src/components/graph/nodes/QAEnhancedNode.tsx

import { memo, useCallback, useState } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import { Badge } from "@tracertm/ui/components/Badge";
import { Card } from "@tracertm/ui/components/Card";
import { Dialog, DialogContent, DialogTrigger } from "@tracertm/ui/components/Dialog";
import {
  CheckCircle2, XCircle, Clock, Image, Play, Link2,
  Camera, Video, FileText, BarChart3, Settings
} from "lucide-react";

// === Types ===

export interface QANodeMetrics {
  passRate: number;        // 0-100
  testCount: number;
  passCount: number;
  failCount: number;
  coverage?: number;       // 0-100
  avgDuration?: number;    // ms
  flakiness?: number;      // 0-100
  lastRunAt?: string;
}

export interface QANodePreview {
  thumbnailUrl?: string;
  screenshotUrl?: string;
  videoUrl?: string;
  gifUrl?: string;
  hasLiveDemo?: boolean;
  demoUrl?: string;
}

export interface QANodeArtifact {
  id: string;
  type: "screenshot" | "video" | "gif" | "log" | "trace";
  url: string;
  thumbnailUrl?: string;
  capturedAt: string;
}

export interface QAEnhancedNodeData {
  id: string;
  item: Item;
  label: string;
  type: string;
  status: string;
  description?: string;
  metrics?: QANodeMetrics;
  preview?: QANodePreview;
  artifacts?: QANodeArtifact[];
  connections: { incoming: number; outgoing: number; total: number };
  onExpandPopup?: (nodeId: string) => void;
  onRunTests?: (nodeId: string) => void;
}

// === Main Component ===

function QAEnhancedNodeComponent({ data, selected }: NodeProps<QAEnhancedNodeData>) {
  const [popupOpen, setPopupOpen] = useState(false);

  const hasPreview = !!data.preview?.thumbnailUrl;
  const passRate = data.metrics?.passRate ?? 0;

  const getPassRateColor = (rate: number) => {
    if (rate >= 90) return "text-green-500 bg-green-500/10 border-green-500/30";
    if (rate >= 70) return "text-yellow-500 bg-yellow-500/10 border-yellow-500/30";
    return "text-red-500 bg-red-500/10 border-red-500/30";
  };

  const handleImageClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    setPopupOpen(true);
  }, []);

  return (
    <>
      <Handle type="target" position={Position.Left} className="!w-3 !h-3" />

      <Dialog open={popupOpen} onOpenChange={setPopupOpen}>
        <Card className={`w-[280px] overflow-hidden transition-all ${
          selected ? "ring-2 ring-primary ring-offset-2" : ""
        }`}>
          {/* Header Row */}
          <div className="flex items-center justify-between p-3 border-b bg-muted/30">
            <div className="flex items-center gap-2 min-w-0 flex-1">
              <div className="flex flex-col min-w-0">
                <h4 className="font-semibold text-sm truncate">{data.label}</h4>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <Badge variant="outline" className="text-[10px] h-4 px-1.5">
                    {data.type}
                  </Badge>
                  <Badge variant="secondary" className="text-[10px] h-4 px-1.5">
                    {data.status}
                  </Badge>
                </div>
              </div>
            </div>

            {/* Pass Rate Badge */}
            {data.metrics && (
              <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold border ${getPassRateColor(passRate)}`}>
                {passRate >= 90 ? (
                  <CheckCircle2 className="h-3.5 w-3.5" />
                ) : passRate >= 70 ? (
                  <Clock className="h-3.5 w-3.5" />
                ) : (
                  <XCircle className="h-3.5 w-3.5" />
                )}
                {passRate}%
              </div>
            )}
          </div>

          {/* Image Pill - Separately Clickable */}
          {hasPreview && (
            <DialogTrigger asChild>
              <div
                className="relative mx-3 my-2 rounded-xl overflow-hidden cursor-pointer group border-2 border-dashed border-transparent hover:border-primary/50 transition-all"
                onClick={handleImageClick}
              >
                <img
                  src={data.preview.thumbnailUrl}
                  alt={data.label}
                  className="w-full h-28 object-cover transition-transform group-hover:scale-105"
                />

                {/* Hover Overlay */}
                <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-1">
                  {data.preview.hasLiveDemo ? (
                    <>
                      <Play className="h-8 w-8 text-white" />
                      <span className="text-white text-xs font-medium">Run Demo</span>
                    </>
                  ) : (
                    <>
                      <Image className="h-6 w-6 text-white" />
                      <span className="text-white text-xs font-medium">Click to Expand</span>
                    </>
                  )}
                </div>

                {/* Artifact Count Badge */}
                {data.artifacts && data.artifacts.length > 0 && (
                  <div className="absolute top-2 right-2 bg-black/70 text-white text-[10px] px-1.5 py-0.5 rounded-full">
                    {data.artifacts.length} artifacts
                  </div>
                )}
              </div>
            </DialogTrigger>
          )}

          {/* Metrics Footer */}
          <div className="flex items-center justify-between px-3 py-2 text-[10px] text-muted-foreground border-t bg-muted/20">
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-0.5">
                <Link2 className="h-3 w-3" />
                {data.connections.total}
              </span>

              {data.metrics?.avgDuration && (
                <span className="flex items-center gap-0.5">
                  <Clock className="h-3 w-3" />
                  {data.metrics.avgDuration}ms
                </span>
              )}

              {data.metrics && (
                <span className="flex items-center gap-0.5">
                  🧪 {data.metrics.passCount}/{data.metrics.testCount}
                </span>
              )}
            </div>

            {data.metrics?.coverage !== undefined && (
              <span className="font-medium">
                📊 {data.metrics.coverage}%
              </span>
            )}
          </div>
        </Card>

        {/* Expand Popup */}
        <DialogContent className="max-w-4xl h-[80vh] p-0 flex overflow-hidden">
          <NodeExpandPopup
            data={data}
            onClose={() => setPopupOpen(false)}
          />
        </DialogContent>
      </Dialog>

      <Handle type="source" position={Position.Right} className="!w-3 !h-3" />
    </>
  );
}

export const QAEnhancedNode = memo(QAEnhancedNodeComponent);

// === Popup Component ===

interface NodeExpandPopupProps {
  data: QAEnhancedNodeData;
  onClose: () => void;
}

function NodeExpandPopup({ data, onClose }: NodeExpandPopupProps) {
  const [activeTab, setActiveTab] = useState<string>("artifacts");

  const tabs = [
    { id: "artifacts", icon: Camera, label: "Artifacts", badge: data.artifacts?.length },
    { id: "demo", icon: Play, label: "Demo" },
    { id: "tests", icon: FileText, label: "Tests" },
    { id: "metrics", icon: BarChart3, label: "Metrics" },
    { id: "actions", icon: Settings, label: "Actions" },
  ];

  return (
    <div className="flex w-full h-full">
      {/* Vertical Tab Sidebar */}
      <div className="w-20 bg-muted border-r flex flex-col gap-1 p-2 shrink-0">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`flex flex-col items-center gap-1 p-2.5 rounded-lg text-[10px] transition-colors ${
              activeTab === tab.id
                ? "bg-primary text-primary-foreground"
                : "hover:bg-accent text-muted-foreground hover:text-foreground"
            }`}
            onClick={() => setActiveTab(tab.id)}
          >
            <tab.icon className="h-5 w-5" />
            <span className="font-medium">{tab.label}</span>
            {tab.badge !== undefined && tab.badge > 0 && (
              <Badge variant="secondary" className="text-[9px] h-4 px-1">
                {tab.badge}
              </Badge>
            )}
          </button>
        ))}
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-auto p-6">
        {activeTab === "artifacts" && <ArtifactsTab artifacts={data.artifacts} />}
        {activeTab === "demo" && <DemoTab preview={data.preview} />}
        {activeTab === "tests" && <TestsTab metrics={data.metrics} />}
        {activeTab === "metrics" && <MetricsTab metrics={data.metrics} />}
        {activeTab === "actions" && <ActionsTab nodeId={data.id} />}
      </div>
    </div>
  );
}

// Tab content components would be defined here...
// (ArtifactsTab, DemoTab, TestsTab, MetricsTab, ActionsTab)
```

---

## 11. API Endpoints

### Execution Endpoints

```python
# Add to src/tracertm/api/main.py

@app.post("/api/v1/projects/{project_id}/executions")
async def create_execution(
    project_id: str,
    data: ExecutionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new execution."""
    pass

@app.get("/api/v1/projects/{project_id}/executions")
async def list_executions(
    project_id: str,
    status: str = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """List executions for a project."""
    pass

@app.get("/api/v1/executions/{execution_id}")
async def get_execution(
    execution_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get execution details."""
    pass

@app.post("/api/v1/executions/{execution_id}/start")
async def start_execution(
    execution_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Start a pending execution."""
    pass

@app.post("/api/v1/executions/{execution_id}/stop")
async def stop_execution(
    execution_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Stop a running execution."""
    pass

@app.get("/api/v1/executions/{execution_id}/artifacts")
async def list_artifacts(
    execution_id: str,
    artifact_type: str = None,
    db: AsyncSession = Depends(get_db)
):
    """List artifacts for an execution."""
    pass

@app.get("/api/v1/artifacts/{artifact_id}/download")
async def download_artifact(
    artifact_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Download an artifact file."""
    pass

# Codex Agent endpoints
@app.post("/api/v1/projects/{project_id}/codex/review-image")
async def codex_review_image(
    project_id: str,
    data: CodexReviewRequest,
    db: AsyncSession = Depends(get_db)
):
    """Have Codex review an image."""
    pass

@app.post("/api/v1/projects/{project_id}/codex/review-video")
async def codex_review_video(
    project_id: str,
    data: CodexReviewRequest,
    db: AsyncSession = Depends(get_db)
):
    """Have Codex review a video."""
    pass

@app.get("/api/v1/projects/{project_id}/codex/interactions")
async def list_codex_interactions(
    project_id: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """List Codex agent interactions."""
    pass
```

---

## 12. Implementation Roadmap

### Phase Overview

```
Week 1-2    Week 3-4    Week 5-6    Week 7-8    Week 9-10
   │           │           │           │           │
   ▼           ▼           ▼           ▼           ▼
┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐
│Phase1│──►│Phase2│──►│Phase3│──►│Phase4│──►│Phase5│
│Found.│   │Record│   │Agent │   │ UI   │   │Integ.│
└──────┘   └──────┘   └──────┘   └──────┘   └──────┘
```

### Phase 1: Foundation (Weeks 1-2)

| Task | Priority | Effort |
|------|----------|--------|
| Database migration (4 new tables) | P0 | 1 day |
| FFmpegPipeline service | P0 | 2 days |
| ArtifactStorageService | P0 | 2 days |
| DockerOrchestrator | P0 | 3 days |
| ExecutionService (basic CRUD) | P0 | 2 days |

**Deliverables:**
- Migration applied
- Local artifact storage working
- Docker container lifecycle functional
- FFmpeg video→GIF working

### Phase 2: Recording Services (Weeks 3-4)

| Task | Priority | Effort |
|------|----------|--------|
| TapeFileGenerator | P0 | 1 day |
| VHSExecutionService | P0 | 2 days |
| PlaywrightExecutionService | P0 | 3 days |
| Integration tests | P1 | 2 days |

**Deliverables:**
- VHS CLI recording working
- Playwright screenshot/video capture
- Automatic GIF conversion

### Phase 3: Codex Agent (Weeks 5-6)

| Task | Priority | Effort |
|------|----------|--------|
| CodexAgentService | P0 | 3 days |
| OAuth setup flow | P0 | 1 day |
| Image/video review tasks | P0 | 2 days |
| Code review integration | P1 | 2 days |
| Rate limiting/error handling | P1 | 1 day |

**Deliverables:**
- Codex CLI integrated with OAuth
- Image and video review working
- Agent task audit trail

### Phase 4: Frontend Visualization (Weeks 7-8)

| Task | Priority | Effort |
|------|----------|--------|
| QAEnhancedNode component | P0 | 3 days |
| ImagePill (separately selectable) | P0 | 1 day |
| NodeExpandPopup with tabs | P0 | 3 days |
| ArtifactGallery tab | P0 | 1 day |
| DemoRunner tab | P1 | 1 day |
| TestResultsPanel tab | P1 | 1 day |

**Deliverables:**
- Enhanced nodes with QA metrics
- Expandable popup with vertical tabs
- Artifact gallery with lightbox

### Phase 5: Integration & Polish (Weeks 9-10)

| Task | Priority | Effort |
|------|----------|--------|
| GitHub webhook triggers | P1 | 2 days |
| API endpoints | P0 | 2 days |
| End-to-end testing | P0 | 3 days |
| Documentation | P1 | 2 days |
| Performance optimization | P2 | 1 day |

**Deliverables:**
- Complete API surface
- GitHub integration for triggers
- Production-ready system

---

## 13. Security Considerations

### Container Security

```yaml
# Security defaults for all containers
security:
  read_only_fs: true           # Read-only root filesystem
  non_root_user: "1000:1000"   # Non-root execution
  cap_drop: ["ALL"]            # Drop all capabilities
  no_new_privileges: true      # Prevent privilege escalation
  network_disabled: false      # Can be disabled per-task
```

### Codex Security

```python
# Sandbox modes
sandbox_modes = {
    "read-only": "Analysis only, no writes",
    "workspace-write": "Can write to workspace (default)",
    "danger-full-access": "Full access - containers only!"
}

# Never use in production
FORBIDDEN_FLAGS = [
    "--dangerously-bypass-approvals-and-sandbox"
]
```

### Artifact Storage

- All file paths sanitized to prevent directory traversal
- Symlink attacks prevented via path resolution
- File size limits enforced (10MB default)
- Automatic cleanup of old artifacts

---

## 14. Quick Reference

### Installation Commands

```bash
# macOS
brew install vhs ffmpeg
brew tap tsl0922/ttyd && brew install ttyd
npm install -g @openai/codex
pip install playwright && playwright install

# Verify
vhs --version && ffmpeg -version && codex --version
```

### Common Operations

```python
# VHS Recording
tape = TapeFileGenerator().type("npm test").enter().sleep(5)
artifact = await vhs_service.record(tape.build(), execution_id)

# Playwright Screenshot
artifact = await playwright_service.capture_screenshot(url, execution_id)

# FFmpeg GIF
await ffmpeg.video_to_gif("video.webm", "output.gif", fps=10)

# Codex Review
result = await codex_service.review_image(image_path, "Check for UI bugs", project_id)
```

### Environment Variables

```bash
# Required
TRACERTM_ARTIFACT_PATH=~/.tracertm/artifacts
TRACERTM_ARTIFACT_RETENTION_DAYS=30

# Optional (Codex uses OAuth by default)
OPENAI_API_KEY=sk-...  # For CI/CD only
```

### File Locations

```
src/tracertm/services/
├── execution/
│   ├── execution_service.py
│   ├── docker_orchestrator.py
│   └── artifact_storage.py
├── recording/
│   ├── tape_generator.py
│   ├── vhs_service.py
│   ├── playwright_service.py
│   └── ffmpeg_pipeline.py
└── agents/
    └── codex_service.py

frontend/apps/web/src/components/graph/
├── nodes/
│   └── QAEnhancedNode.tsx
└── popups/
    └── NodeExpandPopup.tsx
```

---

## Appendix: Research Sources

- [VHS - CLI Recording Tool](https://github.com/charmbracelet/vhs)
- [Codex CLI Authentication](https://developers.openai.com/codex/auth/)
- [Codex CLI Features](https://developers.openai.com/codex/cli/features/)
- [Codex Agents SDK](https://developers.openai.com/codex/guides/agents-sdk/)
- [Playwright Python](https://playwright.dev/python/)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [Docker SDK for Python](https://docker-py.readthedocs.io/)

---

**Document Version:** 1.0.0
**Last Updated:** January 28, 2026
**Status:** Ready for Implementation
