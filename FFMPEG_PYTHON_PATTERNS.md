# FFmpeg Python Integration Patterns

Production-ready Python patterns for FFmpeg integration.

---

## Pattern 1: Basic Synchronous Wrapper

**Best for:** Simple, blocking operations where waiting is acceptable.

```python
import subprocess
import json
from pathlib import Path
from typing import Dict, Optional

class FFmpegCommand:
    """Low-level wrapper for FFmpeg commands."""

    @staticmethod
    def run(cmd: list, timeout: int = 3600) -> tuple[bool, str, str]:
        """
        Execute FFmpeg command.

        Args:
            cmd: FFmpeg command as list
            timeout: Command timeout in seconds

        Returns:
            (success: bool, stdout: str, stderr: str)
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            return (
                result.returncode == 0,
                result.stdout,
                result.stderr
            )
        except subprocess.TimeoutExpired:
            return False, "", "Command timeout"
        except Exception as e:
            return False, "", str(e)

class SimpleFFmpeg:
    """Basic FFmpeg operations (synchronous)."""

    @staticmethod
    def extract_thumbnail(
        video_path: str,
        output_path: str,
        timestamp: str = "10"
    ) -> bool:
        """Extract single frame to thumbnail."""
        cmd = [
            'ffmpeg', '-ss', timestamp, '-i', video_path,
            '-frames:v', '1', '-q:v', '2', '-y', output_path
        ]

        success, _, stderr = FFmpegCommand.run(cmd)
        if not success:
            print(f"Error: {stderr}")
        return success

    @staticmethod
    def transcode_video(
        input_path: str,
        output_path: str,
        crf: int = 23
    ) -> bool:
        """Transcode video with H.264."""
        cmd = [
            'ffmpeg', '-i', input_path,
            '-c:v', 'libx264',
            '-crf', str(crf),
            '-preset', 'medium',
            '-c:a', 'aac',
            '-y', output_path
        ]

        success, _, stderr = FFmpegCommand.run(cmd)
        return success

# Usage
if __name__ == "__main__":
    SimpleFFmpeg.extract_thumbnail("video.mp4", "thumb.jpg")
    SimpleFFmpeg.transcode_video("video.mp4", "output.mp4")
```

---

## Pattern 2: Progress-Tracking with Subprocess

**Best for:** Long operations where user needs feedback.

```python
import subprocess
import re
from typing import Optional, Callable

class FFmpegProgress:
    """Execute FFmpeg with progress tracking."""

    def __init__(
        self,
        on_progress: Optional[Callable[[float], None]] = None,
        on_frame: Optional[Callable[[int], None]] = None
    ):
        self.on_progress = on_progress
        self.on_frame = on_frame
        self.duration_seconds = 0

    def get_duration(self, video_path: str) -> float:
        """Get video duration using ffprobe."""
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.duration_seconds = float(result.stdout.strip())
            return self.duration_seconds
        except (subprocess.CalledProcessError, ValueError):
            return 0

    def execute_with_progress(self, cmd: list) -> bool:
        """Execute FFmpeg command and track progress."""

        try:
            process = subprocess.Popen(
                cmd,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                universal_newlines=False,
                bufsize=1
            )

            while True:
                # Read stderr line by line
                line = process.stderr.readline()

                if not line:
                    break

                # Decode and look for frame/time information
                try:
                    line_str = line.decode('utf-8', errors='ignore').strip()

                    # Parse frame number
                    frame_match = re.search(r'frame=\s*(\d+)', line_str)
                    if frame_match:
                        frame_num = int(frame_match.group(1))
                        if self.on_frame:
                            self.on_frame(frame_num)

                    # Parse time position
                    time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line_str)
                    if time_match:
                        h, m, s = time_match.groups()
                        current_time = int(h) * 3600 + int(m) * 60 + float(s)

                        if self.duration_seconds > 0:
                            progress = (current_time / self.duration_seconds) * 100
                            if self.on_progress:
                                self.on_progress(min(progress, 100.0))

                except Exception:
                    continue

            returncode = process.wait()
            return returncode == 0

        except Exception as e:
            print(f"Execution error: {e}")
            return False

    def transcode_with_progress(
        self,
        input_path: str,
        output_path: str,
        crf: int = 23
    ) -> bool:
        """Transcode with progress reporting."""

        self.get_duration(input_path)

        cmd = [
            'ffmpeg', '-i', input_path,
            '-c:v', 'libx264',
            '-crf', str(crf),
            '-preset', 'fast',
            '-progress', 'pipe:2',
            '-y', output_path
        ]

        return self.execute_with_progress(cmd)

# Usage with progress callback
def on_progress(percent):
    print(f"Progress: {percent:.1f}%", end='\r')

processor = FFmpegProgress(on_progress=on_progress)
processor.transcode_with_progress("input.mp4", "output.mp4")
```

---

## Pattern 3: Asynchronous Processing

**Best for:** Non-blocking operations, multiple concurrent jobs.

```python
import asyncio
import subprocess
from typing import Callable, Optional

class AsyncFFmpeg:
    """Asynchronous FFmpeg execution."""

    def __init__(self, on_progress: Optional[Callable[[float], None]] = None):
        self.on_progress = on_progress
        self.duration = 0

    async def get_duration(self, input_path: str) -> float:
        """Get duration asynchronously."""
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            input_path
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, _ = await proc.communicate()
            self.duration = float(stdout.decode().strip())
            return self.duration

        except (subprocess.CalledProcessError, ValueError):
            return 0

    async def execute(self, cmd: list) -> bool:
        """Execute FFmpeg command asynchronously."""

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Monitor stderr for progress
            while True:
                line = await proc.stderr.read(1024)

                if not line:
                    break

                # Parse progress from stderr
                try:
                    text = line.decode('utf-8', errors='ignore')
                    if 'time=' in text:
                        import re
                        match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', text)
                        if match and self.duration > 0:
                            h, m, s = match.groups()
                            current = int(h) * 3600 + int(m) * 60 + float(s)
                            progress = (current / self.duration) * 100
                            if self.on_progress:
                                self.on_progress(min(progress, 100.0))
                except Exception:
                    pass

            returncode = await proc.wait()
            return returncode == 0

        except Exception as e:
            print(f"Error: {e}")
            return False

    async def transcode(
        self,
        input_path: str,
        output_path: str,
        crf: int = 23
    ) -> bool:
        """Transcode video asynchronously."""

        await self.get_duration(input_path)

        cmd = [
            'ffmpeg', '-i', input_path,
            '-c:v', 'libx264',
            '-crf', str(crf),
            '-preset', 'fast',
            '-y', output_path
        ]

        return await self.execute(cmd)

    async def parallel_transcode(
        self,
        jobs: list[tuple[str, str]]
    ) -> list[bool]:
        """Run multiple transcodes in parallel."""

        tasks = [
            self.transcode(input_path, output_path)
            for input_path, output_path in jobs
        ]

        return await asyncio.gather(*tasks)

# Usage
async def main():
    def on_progress(p):
        print(f"Progress: {p:.1f}%", end='\r')

    processor = AsyncFFmpeg(on_progress=on_progress)

    # Single async transcode
    await processor.transcode("input.mp4", "output.mp4")

    # Parallel processing
    jobs = [
        ("input1.mp4", "output1.mp4"),
        ("input2.mp4", "output2.mp4"),
        ("input3.mp4", "output3.mp4"),
    ]
    results = await processor.parallel_transcode(jobs)
    print(f"Completed: {sum(results)}/{len(jobs)}")

# asyncio.run(main())
```

---

## Pattern 4: Error Handling and Validation

**Best for:** Production systems needing robustness.

```python
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, Any

class FFmpegError(Exception):
    """Base FFmpeg exception."""
    pass

class VideoValidationError(FFmpegError):
    """Video validation failed."""
    pass

class FFmpegValidator:
    """Validate video files and FFmpeg availability."""

    @staticmethod
    def is_available() -> bool:
        """Check if FFmpeg is installed."""
        try:
            subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                check=True,
                timeout=5
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def get_video_info(video_path: str) -> Dict[str, Any]:
        """Get video metadata."""

        if not Path(video_path).exists():
            raise VideoValidationError(f"File not found: {video_path}")

        cmd = [
            'ffprobe', '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,r_frame_rate,duration,codec_name',
            '-of', 'json',
            video_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)

            if not data.get('streams'):
                raise VideoValidationError("No video stream found")

            stream = data['streams'][0]

            # Calculate FPS from frame rate
            fps_str = stream.get('r_frame_rate', '30/1')
            fps_parts = fps_str.split('/')
            fps = float(fps_parts[0]) / float(fps_parts[1])

            return {
                'width': stream.get('width'),
                'height': stream.get('height'),
                'fps': fps,
                'duration': float(stream.get('duration', 0)),
                'codec': stream.get('codec_name'),
                'file_size_mb': Path(video_path).stat().st_size / (1024 * 1024)
            }

        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            raise VideoValidationError(f"Cannot read video: {e}")

    @staticmethod
    def validate_video(video_path: str) -> tuple[bool, str]:
        """Comprehensive video validation."""

        try:
            # Check file exists
            if not Path(video_path).exists():
                return False, "File not found"

            # Check file size (reasonable limit)
            size_mb = Path(video_path).stat().st_size / (1024 * 1024)
            if size_mb > 100000:  # 100 GB
                return False, f"File too large: {size_mb:.0f} MB"

            # Get video info
            info = FFmpegValidator.get_video_info(video_path)

            if info['duration'] == 0:
                return False, "Video has zero duration"

            if info['width'] is None or info['height'] is None:
                return False, "Cannot determine video dimensions"

            return True, "Valid"

        except VideoValidationError as e:
            return False, str(e)

class SafeFFmpeg:
    """FFmpeg wrapper with validation."""

    def __init__(self):
        if not FFmpegValidator.is_available():
            raise FFmpegError("FFmpeg not installed or not in PATH")

    def transcode(
        self,
        input_path: str,
        output_path: str,
        crf: int = 23
    ) -> bool:
        """Transcode with validation."""

        # Validate input
        valid, msg = FFmpegValidator.validate_video(input_path)
        if not valid:
            raise VideoValidationError(f"Input invalid: {msg}")

        # Get info for progress estimation
        info = FFmpegValidator.get_video_info(input_path)
        print(f"Processing: {info['width']}x{info['height']}, {info['duration']:.1f}s")

        cmd = [
            'ffmpeg', '-i', input_path,
            '-c:v', 'libx264',
            '-crf', str(crf),
            '-preset', 'medium',
            '-c:a', 'aac',
            '-y', output_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)

            if result.returncode != 0:
                raise FFmpegError(f"Encoding failed: {result.stderr}")

            return True

        except subprocess.TimeoutExpired:
            Path(output_path).unlink(missing_ok=True)
            raise FFmpegError("Encoding timeout")

# Usage
try:
    ffmpeg = SafeFFmpeg()
    ffmpeg.transcode("input.mp4", "output.mp4")
except FFmpegError as e:
    print(f"Error: {e}")
```

---

## Pattern 5: Batch Processing with Resource Control

**Best for:** Processing multiple files efficiently.

```python
import concurrent.futures
import threading
from pathlib import Path
from typing import Callable, Optional, List, Dict
import subprocess

class BatchFFmpeg:
    """Batch processing with resource management."""

    def __init__(
        self,
        max_workers: int = 4,
        max_cpu_cores: int = 8,
        on_complete: Optional[Callable[[str, bool], None]] = None
    ):
        self.max_workers = max_workers
        self.max_cpu_cores = max_cpu_cores
        self.on_complete = on_complete
        self.results: Dict[str, bool] = {}
        self.lock = threading.Lock()

    def _calculate_threads_per_job(self) -> int:
        """Calculate threads to use per FFmpeg job."""
        import os
        available_cores = os.cpu_count() or 8
        threads_per_job = max(1, available_cores // self.max_workers)
        return min(threads_per_job, 4)  # Cap at 4 per job

    def transcode_file(
        self,
        input_path: str,
        output_path: str,
        crf: int = 23
    ) -> bool:
        """Transcode single file."""

        threads = self._calculate_threads_per_job()

        cmd = [
            'ffmpeg', '-i', input_path,
            '-c:v', 'libx264',
            '-crf', str(crf),
            '-preset', 'fast',
            '-threads', str(threads),
            '-y', output_path
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=3600,
                check=True
            )

            with self.lock:
                self.results[input_path] = True

            if self.on_complete:
                self.on_complete(input_path, True)

            return True

        except Exception as e:
            print(f"Failed: {input_path} - {e}")

            with self.lock:
                self.results[input_path] = False

            if self.on_complete:
                self.on_complete(input_path, False)

            return False

    def process_directory(
        self,
        input_dir: str,
        output_dir: str,
        pattern: str = "*.mp4"
    ) -> Dict[str, bool]:
        """Process all videos in directory."""

        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        files = list(input_path.glob(pattern))

        if not files:
            print(f"No files matching {pattern} in {input_dir}")
            return {}

        print(f"Processing {len(files)} files with {self.max_workers} workers...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}

            for video_file in files:
                output_file = output_path / f"{video_file.stem}_converted.mp4"

                future = executor.submit(
                    self.transcode_file,
                    str(video_file),
                    str(output_file)
                )

                futures[future] = video_file

            # Monitor completion
            completed = 0
            for future in concurrent.futures.as_completed(futures):
                completed += 1
                video_file = futures[future]
                success = future.result()
                status = "✓" if success else "✗"
                print(f"{status} [{completed}/{len(files)}] {video_file.name}")

        return self.results

# Usage
def on_file_complete(filename: str, success: bool):
    status = "completed" if success else "failed"
    print(f"  {filename} {status}")

batch = BatchFFmpeg(
    max_workers=4,
    on_complete=on_file_complete
)

results = batch.process_directory(
    input_dir="./videos",
    output_dir="./converted"
)

successful = sum(1 for s in results.values() if s)
print(f"\nCompleted: {successful}/{len(results)}")
```

---

## Pattern 6: Pipeline with Filters and Multi-Pass

**Best for:** Complex workflows (GIF creation, thumbnails).

```python
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import List

@dataclass
class FilterStep:
    """Represents a filter step in FFmpeg pipeline."""
    name: str
    filters: str  # FFmpeg filter string
    input_stream: str = "[0:v]"
    output_stream: str

class FFmpegPipeline:
    """Build complex FFmpeg pipelines."""

    def __init__(self, input_file: str):
        self.input_file = input_file
        self.steps: List[FilterStep] = []

    def add_fps_filter(self, fps: int) -> 'FFmpegPipeline':
        """Add FPS filter."""
        self.steps.append(FilterStep(
            name="fps",
            filters=f"fps={fps}",
            input_stream="[0:v]",
            output_stream=f"[fps_out]"
        ))
        return self

    def add_scale_filter(self, width: int, height: int = -1) -> 'FFmpegPipeline':
        """Add scale filter."""
        prev_output = self.steps[-1].output_stream if self.steps else "[0:v]"

        self.steps.append(FilterStep(
            name="scale",
            filters=f"scale={width}:{height}",
            input_stream=prev_output,
            output_stream=f"[scaled]"
        ))
        return self

    def add_palette_filter(self) -> 'FFmpegPipeline':
        """Add palette generation filter."""
        prev_output = self.steps[-1].output_stream if self.steps else "[0:v]"

        self.steps.append(FilterStep(
            name="palettegen",
            filters="palettegen",
            input_stream=prev_output,
            output_stream=f"[palette]"
        ))
        return self

    def add_dither_filter(self, dither: str = "bayer") -> 'FFmpegPipeline':
        """Add dithering filter (for palette)."""
        # Note: This combines scaled output with palette
        self.steps.append(FilterStep(
            name="dither",
            filters=f"paletteuse=dither={dither}",
            input_stream="[scaled][palette]",
            output_stream="[out]"
        ))
        return self

    def build_filter_complex(self) -> str:
        """Build complete filter_complex string."""
        if not self.steps:
            return ""

        parts = []

        for step in self.steps:
            if len(step.input_stream) > 10:  # Multiple inputs
                parts.append(f"{step.input_stream}{step.filters}{step.output_stream}")
            else:
                parts.append(f"{step.input_stream}{step.filters}{step.output_stream}")

        return ";".join(parts)

    def execute_two_pass_gif(self, output_file: str) -> bool:
        """Execute two-pass GIF creation."""

        # Pass 1: Generate palette
        palette_cmd = [
            'ffmpeg', '-i', self.input_file,
            '-vf', f"{self.steps[0].input_stream}fps=10{self.steps[0].output_stream};[fps_out]scale=480:-1[scaled];[scaled]palettegen[palette]",
            'palette.png',
            '-y'
        ]

        # Simplify to direct command
        palette_cmd = [
            'ffmpeg', '-i', self.input_file,
            '-vf', 'fps=10,scale=480:-1,palettegen',
            'palette.png',
            '-y'
        ]

        try:
            subprocess.run(palette_cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Palette generation failed: {e}")
            return False

        # Pass 2: Create GIF with palette
        gif_cmd = [
            'ffmpeg', '-i', self.input_file,
            '-i', 'palette.png',
            '-lavfi', 'fps=10,scale=480:-1[x];[x][1:v]paletteuse',
            output_file,
            '-y'
        ]

        try:
            subprocess.run(gif_cmd, check=True, capture_output=True)
            Path('palette.png').unlink()
            return True
        except subprocess.CalledProcessError as e:
            print(f"GIF creation failed: {e}")
            return False

# Usage
pipeline = FFmpegPipeline("input.mp4")
pipeline.add_fps_filter(10).add_scale_filter(480)
success = pipeline.execute_two_pass_gif("output.gif")
```

---

## Best Practices Summary

### 1. Always Validate Input
```python
if not Path(input_file).exists():
    raise FileNotFoundError()

info = FFmpegValidator.get_video_info(input_file)
```

### 2. Use Subprocess Correctly
```python
# Good: No shell injection, timeout
subprocess.run(cmd, check=True, timeout=3600, capture_output=True)

# Bad: Shell injection risk, no timeout
subprocess.run(f"ffmpeg -i {input_file}", shell=True)
```

### 3. Handle Errors Gracefully
```python
try:
    result = subprocess.run(cmd, check=True, timeout=3600)
except subprocess.TimeoutExpired:
    # Clean up output file
    Path(output_file).unlink(missing_ok=True)
except subprocess.CalledProcessError as e:
    print(e.stderr)
```

### 4. Resource Management
```python
# Limit parallelism based on CPU cores
max_workers = min(4, cpu_count() // 2)

# Limit threads per FFmpeg job
threads_per_job = cpu_count() // max_workers
```

### 5. Progress Monitoring
```python
# Parse time from stderr
match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', stderr_line)
if match and duration > 0:
    current_time = parse_time(match)
    progress = (current_time / duration) * 100
```

---

## Choosing a Pattern

| Use Case | Pattern | Why |
|----------|---------|-----|
| Simple one-off | Basic (1) | Minimal code, works immediately |
| User feedback needed | Progress (2) | Shows real-time status |
| Batch processing | Async (3) | Non-blocking, efficient |
| Production system | Error Handling (4) | Robust and validated |
| Multiple files | Batch (5) | Resource-aware parallelism |
| Complex workflows | Pipeline (6) | Composable, reusable |

