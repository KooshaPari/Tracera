# QA/QC Integration System - Implementation Plan

## Executive Summary

This document outlines the implementation plan for a comprehensive Quality Engineering/QA+QC integration system with:

- **VHS** for CLI recording/simulation
- **Playwright** for web testing with screenshots/video
- **FFmpeg** pipeline for video→GIF conversion
- **Codex CLI** for AI agent tasks with OAuth
- **Enhanced graph nodes** with QA metrics and expandable popups
- **Local-only storage** (no paid cloud services)

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| CLI Recording | [VHS](https://github.com/charmbracelet/vhs) | Terminal session recording as GIF/video |
| Web Testing | Playwright (Python) | Browser automation, screenshots, video |
| Video Processing | FFmpeg | Video→GIF, thumbnails, compression |
| AI Agent | [Codex CLI](https://developers.openai.com/codex/cli/) | Code review, test generation, media review |
| Containers | Docker | Sandboxed execution environments |
| Storage | Local filesystem + SQLite | Artifact storage (no cloud) |
| Frontend | React + React Flow | Enhanced node visualization |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         EXECUTION LAYER                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ VHS Service │  │ Playwright  │  │ Codex Agent │  │   Docker    │    │
│  │ (.tape gen) │  │   Service   │  │   Service   │  │ Orchestrator│    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         │                │                │                │            │
│         └────────────────┴────────────────┴────────────────┘            │
│                                   │                                     │
│                          ┌────────▼────────┐                            │
│                          │  FFmpeg Pipeline │                            │
│                          │  (video→gif)     │                            │
│                          └────────┬────────┘                            │
│                                   │                                     │
│                          ┌────────▼────────┐                            │
│                          │ Artifact Storage │                            │
│                          │ (local FS+SQLite)│                            │
│                          └─────────────────┘                            │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                         DATA LAYER                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────────────┐    │
│  │   Execution    │  │ ExecutionArtifact│ │ CodexAgentInteraction │    │
│  │   (runs)       │  │   (media)       │  │   (agent tasks)       │    │
│  └────────────────┘  └────────────────┘  └────────────────────────┘    │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │ ExecutionEnvironmentConfig (per-project settings)              │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                      VISUALIZATION LAYER                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    QA Enhanced Node                               │  │
│  │  ┌──────────────────────────────────────────┬─────────────────┐  │  │
│  │  │ Title Header                             │  85% ✓ Pass    │  │  │
│  │  │ Subheader | type                         │  Rate Badge    │  │  │
│  │  ├──────────────────────────────────────────┴─────────────────┤  │  │
│  │  │  ┌──────────────────────────────────────────────────────┐  │  │  │
│  │  │  │     [Rounded Pill Image - CLICKABLE]                 │  │  │  │
│  │  │  │     Click → Opens NodeExpandPopup                    │  │  │  │
│  │  │  └──────────────────────────────────────────────────────┘  │  │  │
│  │  │  🔗 12 links  |  ⏱️ 2.3s  |  🧪 8/10  |  📊 78%            │  │  │
│  │  └────────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    Node Expand Popup                              │  │
│  │  ┌────┬─────────────────────────────────────────────────────┐    │  │
│  │  │ 📸 │  Artifact Gallery (screenshots, videos, logs)       │    │  │
│  │  ├────┤                                                      │    │  │
│  │  │ ▶️ │  Demo Runner (iframe sandbox OR enlarged media)      │    │  │
│  │  ├────┤                                                      │    │  │
│  │  │ 🧪 │  Test Results (pass/fail, coverage, flaky tests)    │    │  │
│  │  ├────┤                                                      │    │  │
│  │  │ 📊 │  Metrics (trends, duration, history)                 │    │  │
│  │  ├────┤                                                      │    │  │
│  │  │ ⚙️ │  Actions (re-run, download, open in browser)        │    │  │
│  │  └────┴─────────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Database Models

### New Tables

```sql
-- Execution: Tracks execution runs
CREATE TABLE execution (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    test_run_id TEXT REFERENCES test_run(id),
    execution_type TEXT NOT NULL,  -- 'vhs', 'playwright', 'codex', 'custom'
    trigger_source TEXT NOT NULL,  -- 'github_pr', 'github_push', 'webhook', 'manual'
    trigger_ref TEXT,
    status TEXT NOT NULL DEFAULT 'pending',  -- pending, running, passed, failed, cancelled
    container_id TEXT,
    config JSON,
    environment JSON,  -- encrypted
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    error_message TEXT,
    exit_code INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ExecutionArtifact: Stores media/log references
CREATE TABLE execution_artifact (
    id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL REFERENCES execution(id) ON DELETE CASCADE,
    item_id TEXT REFERENCES item(id),
    artifact_type TEXT NOT NULL,  -- 'screenshot', 'video', 'gif', 'log', 'trace'
    file_path TEXT NOT NULL,
    thumbnail_path TEXT,
    file_size INTEGER,
    mime_type TEXT,
    metadata JSON,
    captured_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CodexAgentInteraction: AI agent task history
CREATE TABLE codex_agent_interaction (
    id TEXT PRIMARY KEY,
    execution_id TEXT REFERENCES execution(id),
    project_id TEXT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    task_type TEXT NOT NULL,  -- 'review_image', 'review_video', 'code_review', 'generate_test'
    input_data JSON,
    output_data JSON,
    status TEXT NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    tokens_used INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ExecutionEnvironmentConfig: Per-project settings
CREATE TABLE execution_environment_config (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL UNIQUE REFERENCES project(id) ON DELETE CASCADE,
    docker_image TEXT DEFAULT 'node:20-alpine',
    resource_limits JSON,
    environment_vars JSON,  -- encrypted
    vhs_enabled BOOLEAN DEFAULT TRUE,
    playwright_enabled BOOLEAN DEFAULT TRUE,
    codex_enabled BOOLEAN DEFAULT TRUE,
    artifact_retention_days INTEGER DEFAULT 30,
    storage_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_execution_project_id ON execution(project_id);
CREATE INDEX idx_execution_status ON execution(status);
CREATE INDEX idx_execution_artifact_execution_id ON execution_artifact(execution_id);
CREATE INDEX idx_execution_artifact_item_id ON execution_artifact(item_id);
CREATE INDEX idx_codex_agent_interaction_project_id ON codex_agent_interaction(project_id);
```

---

## Service Layer

### File Structure

```
src/tracertm/services/
├── execution/
│   ├── __init__.py
│   ├── execution_service.py      # Main execution orchestration
│   ├── docker_orchestrator.py    # Docker container lifecycle
│   ├── artifact_storage.py       # Local filesystem storage
│   └── models.py                 # Pydantic models
├── recording/
│   ├── __init__.py
│   ├── vhs_service.py            # VHS execution
│   ├── tape_generator.py         # .tape file generation
│   ├── playwright_service.py     # Playwright execution
│   └── ffmpeg_pipeline.py        # Video processing
├── agents/
│   ├── __init__.py
│   └── codex_service.py          # Codex CLI integration
```

---

## VHS Integration

### Tape File Generator

```python
# src/tracertm/services/recording/tape_generator.py

class TapeFileGenerator:
    """Fluent API for generating VHS .tape files."""

    def __init__(self):
        self._settings: list[str] = []
        self._requires: list[str] = []
        self._commands: list[str] = []

    def output(self, path: str) -> "TapeFileGenerator":
        self._settings.append(f'Output "{path}"')
        return self

    def set_shell(self, shell: str = "bash") -> "TapeFileGenerator":
        self._settings.append(f"Set Shell {shell}")
        return self

    def set_font_size(self, size: int) -> "TapeFileGenerator":
        self._settings.append(f"Set FontSize {size}")
        return self

    def set_width(self, width: int) -> "TapeFileGenerator":
        self._settings.append(f"Set Width {width}")
        return self

    def set_height(self, height: int) -> "TapeFileGenerator":
        self._settings.append(f"Set Height {height}")
        return self

    def require(self, program: str) -> "TapeFileGenerator":
        self._requires.append(f"Require {program}")
        return self

    def type(self, text: str, speed: str = "50ms") -> "TapeFileGenerator":
        escaped = text.replace('"', '\\"')
        self._commands.append(f'Type "{escaped}" {speed}')
        return self

    def enter(self) -> "TapeFileGenerator":
        self._commands.append("Enter")
        return self

    def sleep(self, seconds: float) -> "TapeFileGenerator":
        self._commands.append(f"Sleep {seconds}s")
        return self

    def ctrl(self, key: str) -> "TapeFileGenerator":
        self._commands.append(f"Ctrl+{key}")
        return self

    def build(self) -> str:
        lines = []
        lines.extend(self._settings)
        lines.extend(self._requires)
        lines.append("")  # Blank line
        lines.extend(self._commands)
        return "\n".join(lines)

    def write(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.build())
```

### Usage Example

```python
tape = (
    TapeFileGenerator()
    .output("demo.gif")
    .set_shell("bash")
    .set_font_size(14)
    .set_width(800)
    .set_height(400)
    .require("npm")
    .type("npm test -- --coverage")
    .enter()
    .sleep(5)
    .type("echo 'Done!'")
    .enter()
    .sleep(2)
)

tape.write("/tmp/demo.tape")

# Execute:
# vhs /tmp/demo.tape
```

---

## FFmpeg Pipeline

```python
# src/tracertm/services/recording/ffmpeg_pipeline.py

import asyncio
from pathlib import Path
from dataclasses import dataclass
from uuid import uuid4

@dataclass
class VideoInfo:
    duration: float
    width: int
    height: int
    fps: float
    codec: str
    size_bytes: int

class FFmpegPipeline:
    """Reusable FFmpeg operations for video processing."""

    async def check_availability(self) -> tuple[bool, str]:
        try:
            proc = await asyncio.create_subprocess_exec(
                "ffmpeg", "-version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            return (proc.returncode == 0, "")
        except FileNotFoundError:
            return (False, "FFmpeg not found in PATH")

    async def video_to_gif(
        self,
        input_path: str | Path,
        output_path: str | Path,
        fps: int = 10,
        scale: int = 640,
        optimize_palette: bool = True
    ) -> Path:
        """Convert video to GIF with optional palette optimization."""

        if optimize_palette:
            # Two-pass for better quality + smaller size
            palette_path = f"/tmp/palette_{uuid4()}.png"

            # Pass 1: Generate palette
            await self._run([
                "-i", str(input_path),
                "-vf", f"fps={fps},scale={scale}:-1:flags=lanczos,palettegen",
                "-y", palette_path
            ])

            # Pass 2: Apply palette
            await self._run([
                "-i", str(input_path),
                "-i", palette_path,
                "-lavfi", f"fps={fps},scale={scale}:-1:flags=lanczos[x];[x][1:v]paletteuse",
                "-y", str(output_path)
            ])

            Path(palette_path).unlink(missing_ok=True)
        else:
            await self._run([
                "-i", str(input_path),
                "-vf", f"fps={fps},scale={scale}:-1:flags=lanczos",
                "-y", str(output_path)
            ])

        return Path(output_path)

    async def generate_thumbnail(
        self,
        video_path: str | Path,
        output_path: str | Path,
        timestamp: float = 0.0,
        size: tuple[int, int] = (300, 300)
    ) -> Path:
        """Extract frame as thumbnail at specified timestamp."""

        await self._run([
            "-ss", str(timestamp),
            "-i", str(video_path),
            "-vframes", "1",
            "-vf", f"scale={size[0]}:{size[1]}:force_original_aspect_ratio=decrease",
            "-y", str(output_path)
        ])

        return Path(output_path)

    async def compress_video(
        self,
        input_path: str | Path,
        output_path: str | Path,
        crf: int = 28,
        preset: str = "medium"
    ) -> Path:
        """Compress video with H.264 codec."""

        await self._run([
            "-i", str(input_path),
            "-c:v", "libx264",
            "-crf", str(crf),
            "-preset", preset,
            "-y", str(output_path)
        ])

        return Path(output_path)

    async def extract_frames(
        self,
        video_path: str | Path,
        output_dir: str | Path,
        interval_seconds: float = 1.0,
        format: str = "png"
    ) -> list[Path]:
        """Extract frames at specified intervals."""

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_pattern = str(output_dir / f"frame_%04d.{format}")

        await self._run([
            "-i", str(video_path),
            "-vf", f"fps=1/{interval_seconds}",
            "-y", output_pattern
        ])

        return sorted(output_dir.glob(f"frame_*.{format}"))

    async def _run(self, args: list[str], timeout: int = 300) -> None:
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
            raise FFmpegError(stderr.decode())

class FFmpegError(Exception):
    pass
```

---

## Codex CLI Integration

```python
# src/tracertm/services/agents/codex_service.py

import asyncio
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from uuid import uuid4

@dataclass
class CodexTask:
    task_type: str  # review_image, review_video, code_review, generate_test
    prompt: str
    input_files: list[str] | None = None
    codebase_dir: str | None = None
    full_auto: bool = False
    timeout_seconds: int = 300

class CodexAgentService:
    """Integration with OpenAI Codex CLI using OAuth."""

    def __init__(self, db, artifact_storage):
        self.db = db
        self.artifact_storage = artifact_storage

    async def check_availability(self) -> tuple[bool, str]:
        try:
            proc = await asyncio.create_subprocess_exec(
                "codex", "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            return (proc.returncode == 0, stdout.decode().strip())
        except FileNotFoundError:
            return (False, "Codex CLI not found")

    async def check_auth_status(self) -> tuple[bool, str]:
        """Check if user is authenticated with Codex."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "codex", "auth", "status",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            authenticated = "authenticated" in stdout.decode().lower()
            return (authenticated, stdout.decode().strip())
        except Exception as e:
            return (False, str(e))

    async def setup_oauth(self) -> str:
        """Initiate OAuth flow with device code auth."""
        # Codex uses device code flow for CLI auth
        proc = await asyncio.create_subprocess_exec(
            "codex", "login", "--device-auth",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()

        # Parse URL from output
        # Format: "Visit https://... and enter code: XXXX-XXXX"
        output = stdout.decode()
        for line in output.split("\n"):
            if "https://" in line:
                return line.strip()

        return output

    async def run_task(
        self,
        task: CodexTask,
        project_id: str,
        execution_id: str | None = None
    ):
        """Execute a Codex agent task."""
        from tracertm.models.codex_agent_interaction import CodexAgentInteraction

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
            cmd = ["codex"]

            if task.full_auto:
                cmd.append("--full-auto")

            if task.codebase_dir:
                cmd.extend(["--cwd", task.codebase_dir])

            # Add input files if reviewing media
            if task.input_files:
                for file_path in task.input_files:
                    cmd.extend(["--file", file_path])

            cmd.append(task.prompt)

            # Update status
            interaction.status = "running"
            interaction.started_at = datetime.utcnow()
            await self.db.commit()

            # Execute
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=task.timeout_seconds
            )

            # Parse output
            output_text = stdout.decode()
            interaction.output_data = {
                "raw_output": output_text,
                "parsed": self._parse_output(output_text)
            }
            interaction.status = "completed" if proc.returncode == 0 else "failed"
            interaction.completed_at = datetime.utcnow()

            if proc.returncode != 0:
                interaction.error_message = stderr.decode()

        except asyncio.TimeoutError:
            interaction.status = "failed"
            interaction.error_message = "Task timed out"
        except Exception as e:
            interaction.status = "failed"
            interaction.error_message = str(e)

        await self.db.commit()
        return interaction

    async def review_image(
        self,
        image_path: str,
        prompt: str,
        project_id: str
    ):
        """Have Codex review an image."""
        task = CodexTask(
            task_type="review_image",
            prompt=f"Review this image and {prompt}",
            input_files=[image_path]
        )
        return await self.run_task(task, project_id)

    async def review_video(
        self,
        video_path: str,
        prompt: str,
        project_id: str
    ):
        """Have Codex review a video (via frames)."""
        # Extract key frames first
        frames = await self.ffmpeg.extract_frames(
            video_path,
            "/tmp/codex_frames",
            interval_seconds=2.0
        )

        task = CodexTask(
            task_type="review_video",
            prompt=f"Review these video frames and {prompt}",
            input_files=[str(f) for f in frames[:10]]  # Limit frames
        )
        return await self.run_task(task, project_id)

    async def code_review(
        self,
        file_paths: list[str],
        prompt: str,
        project_id: str,
        codebase_dir: str | None = None
    ):
        """Have Codex review code files."""
        task = CodexTask(
            task_type="code_review",
            prompt=prompt,
            input_files=file_paths,
            codebase_dir=codebase_dir
        )
        return await self.run_task(task, project_id)

    def _parse_output(self, output: str) -> dict:
        """Parse structured output from Codex."""
        # Try to extract JSON if present
        try:
            # Look for JSON block
            if "```json" in output:
                start = output.index("```json") + 7
                end = output.index("```", start)
                return json.loads(output[start:end])
        except (ValueError, json.JSONDecodeError):
            pass

        return {"text": output}
```

---

## Frontend Components

### QAEnhancedNode

```tsx
// frontend/apps/web/src/components/graph/nodes/QAEnhancedNode.tsx

import { memo, useCallback } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import { Badge } from "@tracertm/ui/components/Badge";
import { Card } from "@tracertm/ui/components/Card";
import { CheckCircle2, XCircle, Clock, Image, Play } from "lucide-react";

export interface QANodeMetrics {
  passRate: number;
  testCount: number;
  passCount: number;
  failCount: number;
  coverage?: number;
  avgDuration?: number;
  flakiness?: number;
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

export interface QAEnhancedNodeData {
  id: string;
  item: Item;
  label: string;
  type: string;
  status: string;
  description?: string;
  metrics?: QANodeMetrics;
  preview?: QANodePreview;
  connections: { incoming: number; outgoing: number; total: number };
  onImageClick?: (nodeId: string) => void;
  onExpandPopup?: (nodeId: string) => void;
}

function QAEnhancedNodeComponent({ data, selected }: NodeProps<QAEnhancedNodeData>) {
  const hasPreview = !!data.preview?.thumbnailUrl;
  const passRate = data.metrics?.passRate ?? 0;

  const handleImageClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    data.onImageClick?.(data.id);
  }, [data]);

  const getPassRateColor = (rate: number) => {
    if (rate >= 90) return "text-green-500 bg-green-500/10";
    if (rate >= 70) return "text-yellow-500 bg-yellow-500/10";
    return "text-red-500 bg-red-500/10";
  };

  return (
    <>
      <Handle type="target" position={Position.Left} />

      <Card className={`w-[260px] overflow-hidden ${selected ? "ring-2 ring-primary" : ""}`}>
        {/* Header */}
        <div className="flex items-center justify-between p-3 border-b">
          <div className="flex items-center gap-2 min-w-0">
            <div className="flex flex-col min-w-0">
              <h4 className="font-semibold text-sm truncate">{data.label}</h4>
              <Badge variant="outline" className="text-[10px] w-fit">
                {data.type}
              </Badge>
            </div>
          </div>

          {/* Pass Rate Badge */}
          {data.metrics && (
            <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getPassRateColor(passRate)}`}>
              {passRate >= 90 ? <CheckCircle2 className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
              {passRate}%
            </div>
          )}
        </div>

        {/* Image Pill - Separately Clickable */}
        {hasPreview && (
          <div
            className="relative mx-3 my-2 rounded-lg overflow-hidden cursor-pointer group"
            onClick={handleImageClick}
          >
            <img
              src={data.preview.thumbnailUrl}
              alt={data.label}
              className="w-full h-24 object-cover transition-transform group-hover:scale-105"
            />
            <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
              {data.preview.hasLiveDemo ? (
                <Play className="h-8 w-8 text-white" />
              ) : (
                <Image className="h-6 w-6 text-white" />
              )}
              <span className="ml-2 text-white text-sm">
                {data.preview.hasLiveDemo ? "Run Demo" : "Expand"}
              </span>
            </div>
          </div>
        )}

        {/* Metrics Footer */}
        <div className="flex items-center gap-3 px-3 py-2 text-[10px] text-muted-foreground border-t">
          <span className="flex items-center gap-0.5">
            🔗 {data.connections.total}
          </span>

          {data.metrics?.avgDuration && (
            <span className="flex items-center gap-0.5">
              <Clock className="h-3 w-3" />
              {data.metrics.avgDuration}ms
            </span>
          )}

          {data.metrics && (
            <span>
              🧪 {data.metrics.passCount}/{data.metrics.testCount}
            </span>
          )}

          {data.metrics?.coverage !== undefined && (
            <span>📊 {data.metrics.coverage}%</span>
          )}
        </div>
      </Card>

      <Handle type="source" position={Position.Right} />
    </>
  );
}

export const QAEnhancedNode = memo(QAEnhancedNodeComponent);
```

---

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
- [ ] STORY-001: Database models
- [ ] STORY-006: FFmpeg pipeline (can be done in parallel)

### Phase 2: Execution Infrastructure (Weeks 3-4)
- [ ] STORY-002: ExecutionService + Docker
- [ ] STORY-003: Artifact storage

### Phase 3: Recording Services (Weeks 5-6)
- [ ] STORY-004: TapeFileGenerator
- [ ] STORY-005: VHSExecutionService
- [ ] STORY-007: PlaywrightExecutionService

### Phase 4: Agent Integration (Weeks 7-8)
- [ ] STORY-008: CodexAgentService

### Phase 5: Frontend Visualization (Weeks 9-10)
- [ ] STORY-009: QAEnhancedNode
- [ ] STORY-010: NodeExpandPopup

---

## Dependencies & Prerequisites

### System Requirements
- Docker installed and running
- VHS: `brew install vhs` or `go install github.com/charmbracelet/vhs@latest`
- FFmpeg: `brew install ffmpeg`
- ttyd: `brew install ttyd` (VHS dependency)
- Codex CLI: `npm install -g @openai/codex-cli`

### Python Dependencies
```toml
# pyproject.toml additions
[project.dependencies]
docker = "^7.0.0"
playwright = "^1.40.0"
```

### Environment Variables
```bash
# Codex uses OAuth, no API key needed
# But for fallback/testing:
OPENAI_API_KEY=sk-...  # Optional

# Docker
DOCKER_HOST=unix:///var/run/docker.sock

# Artifact storage
TRACERTM_ARTIFACT_PATH=~/.tracertm/artifacts
TRACERTM_ARTIFACT_RETENTION_DAYS=30
```

---

## Sources

- [VHS - CLI Recording Tool](https://github.com/charmbracelet/vhs)
- [Codex CLI Authentication](https://developers.openai.com/codex/auth/)
- [Codex CLI Features](https://developers.openai.com/codex/cli/features/)
- [Codex with Agents SDK](https://developers.openai.com/codex/guides/agents-sdk/)
- [Playwright Python](https://playwright.dev/python/)
