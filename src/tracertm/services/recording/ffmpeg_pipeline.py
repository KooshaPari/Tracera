"""FFmpeg media processing pipeline for QA Integration system.

Provides video-to-GIF conversion, thumbnail generation, video compression,
frame extraction, and scene detection using FFmpeg.
"""

import asyncio
import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

# Default timeout for FFmpeg subprocess (seconds)
DEFAULT_RUN_TIMEOUT = 300
# Expected "num/den" frame rate parts from ffprobe
FPS_RATE_PARTS = 2


@dataclass
class VideoToGifOptions:
    """Options for video-to-GIF conversion."""

    fps: int = 10
    scale: int = 640
    optimize_palette: bool = True
    dither_method: str = "bayer"
    bayer_scale: int = 5


@dataclass
class CompressVideoOptions:
    """Options for video compression."""

    codec: str = "libx264"
    crf: int = 23
    preset: str = "medium"
    audio_codec: str | None = "aac"
    audio_bitrate: str | None = "128k"


@dataclass
class CreateStoryboardOptions:
    """Options for creating a storyboard/sprite sheet."""

    columns: int = 10
    rows: int = 10
    thumb_width: int = 160
    thumb_height: int = 90


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


class FFmpegPipeline:
    """Reusable FFmpeg operations for video processing.

    Provides async methods for common video processing tasks including:
    - Video to GIF conversion (with optional palette optimization)
    - Thumbnail generation (fast or best-frame selection)
    - Video compression (H.264/H.265)
    - Frame extraction (interval, keyframe, or scene-based)
    - Video metadata extraction via ffprobe

    All methods are async and use asyncio subprocess for non-blocking execution.

    Example:
        pipeline = FFmpegPipeline()
        available, version = await pipeline.check_availability()
        if available:
            await pipeline.video_to_gif("input.webm", "output.gif")
    """

    def __init__(self, temp_dir: Path | None = None) -> None:
        """Initialize FFmpegPipeline.

        Args:
            temp_dir: Directory for temporary files. Defaults to system temp.
        """
        self._temp_dir = temp_dir or Path(tempfile.gettempdir())

    async def check_availability(self) -> tuple[bool, str]:
        """Check if FFmpeg is installed and working.

        Returns:
            Tuple of (is_available, message). Message contains version if available,
            or error description if not.
        """
        try:
            proc = await asyncio.create_subprocess_exec(
                "ffmpeg",
                "-version",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
        except FileNotFoundError:
            return False, "FFmpeg not found in PATH"
        else:
            if proc.returncode == 0:
                version = stdout.decode().split("\n")[0]
                return True, version
            return False, "FFmpeg not working properly"

    async def check_ffprobe_availability(self) -> tuple[bool, str]:
        """Check if ffprobe is installed and working.

        Returns:
            Tuple of (is_available, message).
        """
        try:
            proc = await asyncio.create_subprocess_exec(
                "ffprobe",
                "-version",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
        except FileNotFoundError:
            return False, "ffprobe not found in PATH"
        else:
            if proc.returncode == 0:
                version = stdout.decode().split("\n")[0]
                return True, version
            return False, "ffprobe not working properly"

    async def video_to_gif(
        self,
        input_path: str | Path,
        output_path: str | Path,
        options: VideoToGifOptions | None = None,
    ) -> Path:
        """Convert video to GIF.

        Two-pass with palette optimization produces 40-60% smaller files
        with better color accuracy.

        Args:
            input_path: Path to input video file.
            output_path: Path for output GIF file.
            options: Conversion options (fps, scale, palette, dither). Defaults if None.

        Returns:
            Path to created GIF file.

        Raises:
            FFmpegError: If conversion fails.
        """
        opts = options or VideoToGifOptions()
        input_path = Path(input_path)
        output_path = Path(output_path)

        if opts.optimize_palette:
            # Two-pass: Generate palette, then apply
            palette_path = self._temp_dir / f"palette_{uuid4()}.png"

            try:
                # Pass 1: Generate optimized palette
                await self._run([
                    "-i",
                    str(input_path),
                    "-vf",
                    f"fps={opts.fps},scale={opts.scale}:-1:flags=lanczos,palettegen=stats_mode=diff",
                    "-y",
                    str(palette_path),
                ])

                if opts.dither_method == "none":
                    palette_use = "paletteuse=dither=none"
                else:
                    palette_use = f"paletteuse=dither={opts.dither_method}:bayer_scale={opts.bayer_scale}"

                await self._run([
                    "-i",
                    str(input_path),
                    "-i",
                    str(palette_path),
                    "-lavfi",
                    f"fps={opts.fps},scale={opts.scale}:-1:flags=lanczos[x];[x][1:v]{palette_use}",
                    "-y",
                    str(output_path),
                ])
            finally:
                palette_path.unlink(missing_ok=True)
        else:
            await self._run([
                "-i",
                str(input_path),
                "-vf",
                f"fps={opts.fps},scale={opts.scale}:-1:flags=lanczos",
                "-y",
                str(output_path),
            ])

        return output_path

    async def generate_thumbnail(
        self,
        video_path: str | Path,
        output_path: str | Path,
        timestamp: float = 0.0,
        size: tuple[int, int] = (300, 300),
        quality: int = 2,
    ) -> Path:
        """Extract thumbnail from video at specified timestamp.

        Using -ss before -i is ~4x faster (input seeking vs output seeking).

        Args:
            video_path: Path to input video.
            output_path: Path for output thumbnail (jpg/png).
            timestamp: Time in seconds to capture frame. Default 0.
            size: Max width and height tuple. Aspect ratio preserved.
            quality: JPEG quality (1=best, 31=worst). Default 2.

        Returns:
            Path to created thumbnail.

        Raises:
            FFmpegError: If extraction fails.
        """
        await self._run([
            "-ss",
            str(timestamp),
            "-i",
            str(video_path),
            "-vframes",
            "1",
            "-vf",
            f"scale={size[0]}:{size[1]}:force_original_aspect_ratio=decrease",
            "-q:v",
            str(quality),
            "-y",
            str(output_path),
        ])
        return Path(output_path)

    async def generate_best_thumbnail(
        self,
        video_path: str | Path,
        output_path: str | Path,
        size: tuple[int, int] = (300, 300),
        sample_frames: int = 100,
    ) -> Path:
        """Select best frame automatically using thumbnail filter.

        Analyzes frames for sharpness/clarity and picks the best one.
        Slower than generate_thumbnail but produces better results.

        Args:
            video_path: Path to input video.
            output_path: Path for output thumbnail.
            size: Max width and height tuple.
            sample_frames: Number of frames to analyze. Default 100.

        Returns:
            Path to created thumbnail.

        Raises:
            FFmpegError: If extraction fails.
        """
        await self._run([
            "-i",
            str(video_path),
            "-vf",
            f"thumbnail=n={sample_frames},scale={size[0]}:{size[1]}:force_original_aspect_ratio=decrease",
            "-vframes",
            "1",
            "-q:v",
            "2",
            "-y",
            str(output_path),
        ])
        return Path(output_path)

    async def compress_video(
        self,
        input_path: str | Path,
        output_path: str | Path,
        options: CompressVideoOptions | None = None,
    ) -> Path:
        """Compress video with specified codec and quality.

        CRF Guide (H.264):
        - 18: Near-lossless, ~70% of original
        - 23: High quality, ~45% of original (default)
        - 28: Good quality, ~25% of original

        For H.265/HEVC (libx265): Use CRF 4-6 points higher for similar quality.

        Args:
            input_path: Path to input video.
            output_path: Path for output video.
            options: Compression options (codec, crf, preset, audio). Defaults if None.

        Returns:
            Path to compressed video.

        Raises:
            FFmpegError: If compression fails.
        """
        opts = options or CompressVideoOptions()
        args = [
            "-i",
            str(input_path),
            "-c:v",
            opts.codec,
            "-crf",
            str(opts.crf),
            "-preset",
            opts.preset,
            "-movflags",
            "+faststart",
        ]

        if opts.audio_codec:
            args.extend(["-c:a", opts.audio_codec, "-b:a", opts.audio_bitrate or "128k"])
        else:
            args.extend(["-c:a", "copy"])

        args.extend(["-y", str(output_path)])

        await self._run(args)
        return Path(output_path)

    async def extract_frames(
        self,
        video_path: str | Path,
        output_dir: str | Path,
        interval_seconds: float = 1.0,
        format: str = "jpg",
        quality: int = 2,
    ) -> list[Path]:
        """Extract frames at regular intervals.

        Args:
            video_path: Path to input video.
            output_dir: Directory for output frames.
            interval_seconds: Time between frames. Default 1.0.
            format: Output format ('jpg', 'png'). Default 'jpg'.
            quality: JPEG quality (1=best). Default 2.

        Returns:
            List of paths to extracted frames.

        Raises:
            FFmpegError: If extraction fails.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_pattern = str(output_dir / f"frame_%04d.{format}")

        await self._run([
            "-i",
            str(video_path),
            "-vf",
            f"fps=1/{interval_seconds}",
            "-q:v",
            str(quality),
            "-y",
            output_pattern,
        ])

        return sorted(output_dir.glob(f"frame_*.{format}"))

    async def extract_keyframes(
        self,
        video_path: str | Path,
        output_dir: str | Path,
        format: str = "jpg",
    ) -> list[Path]:
        """Extract only keyframes (I-frames).

        10-20x faster than regular frame extraction, captures major scene points.

        Args:
            video_path: Path to input video.
            output_dir: Directory for output frames.
            format: Output format ('jpg', 'png').

        Returns:
            List of paths to extracted keyframes.

        Raises:
            FFmpegError: If extraction fails.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_pattern = str(output_dir / f"keyframe_%04d.{format}")

        await self._run([
            "-i",
            str(video_path),
            "-vf",
            "select='eq(pict_type,I)'",
            "-vsync",
            "vfr",
            "-q:v",
            "2",
            "-y",
            output_pattern,
        ])

        return sorted(output_dir.glob(f"keyframe_*.{format}"))

    async def detect_scenes(
        self,
        video_path: str | Path,
        output_dir: str | Path,
        threshold: float = 0.4,
        format: str = "jpg",
    ) -> list[Path]:
        """Extract frames at scene changes.

        Threshold guide:
        - 0.3: Sensitive, many frames
        - 0.4: Balanced (recommended)
        - 0.5: Conservative, major changes only

        Args:
            video_path: Path to input video.
            output_dir: Directory for output frames.
            threshold: Scene change sensitivity (0.0-1.0). Default 0.4.
            format: Output format ('jpg', 'png').

        Returns:
            List of paths to extracted scene frames.

        Raises:
            FFmpegError: If extraction fails.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_pattern = str(output_dir / f"scene_%04d.{format}")

        await self._run([
            "-i",
            str(video_path),
            "-vf",
            f"select='gt(scene,{threshold})'",
            "-vsync",
            "vfr",
            "-q:v",
            "2",
            "-y",
            output_pattern,
        ])

        return sorted(output_dir.glob(f"scene_*.{format}"))

    async def create_storyboard(
        self,
        video_path: str | Path,
        output_path: str | Path,
        options: CreateStoryboardOptions | None = None,
    ) -> Path:
        """Create a storyboard/sprite sheet from video.

        Creates a single image with multiple thumbnails tiled together.
        Useful for video scrubbing in players.

        Args:
            video_path: Path to input video.
            output_path: Path for output storyboard image.
            options: Layout options (columns, rows, thumb size). Defaults if None.

        Returns:
            Path to created storyboard.

        Raises:
            FFmpegError: If creation fails.
        """
        opts = options or CreateStoryboardOptions()
        total_frames = opts.columns * opts.rows

        info = await self.get_video_info(video_path)
        fps = total_frames / info.duration if info.duration > 0 else 1

        await self._run([
            "-i",
            str(video_path),
            "-vf",
            f"scale={opts.thumb_width}:{opts.thumb_height},fps={fps},tile={opts.columns}x{opts.rows}",
            "-vframes",
            "1",
            "-y",
            str(output_path),
        ])

        return Path(output_path)

    async def get_video_info(self, video_path: str | Path) -> VideoInfo:
        """Get video metadata using ffprobe.

        Args:
            video_path: Path to video file.

        Returns:
            VideoInfo dataclass with duration, dimensions, fps, codec, size.

        Raises:
            FFmpegError: If video has no video stream or ffprobe fails.
        """
        proc = await asyncio.create_subprocess_exec(
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(video_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            msg = f"ffprobe failed: {stderr.decode()}"
            raise FFmpegError(msg)

        data = json.loads(stdout.decode())

        video_stream = next(
            (s for s in data.get("streams", []) if s.get("codec_type") == "video"),
            None,
        )

        if not video_stream:
            msg = "No video stream found"
            raise FFmpegError(msg)

        # Parse frame rate (usually "30000/1001" or "30/1")
        fps_parts = video_stream.get("r_frame_rate", "30/1").split("/")
        fps = (
            float(fps_parts[0]) / float(fps_parts[1])
            if len(fps_parts) == FPS_RATE_PARTS and float(fps_parts[1]) != 0
            else 30.0
        )

        return VideoInfo(
            duration=float(data.get("format", {}).get("duration", 0)),
            width=int(video_stream.get("width", 0)),
            height=int(video_stream.get("height", 0)),
            fps=fps,
            codec=video_stream.get("codec_name", "unknown"),
            size_bytes=int(data.get("format", {}).get("size", 0)),
        )

    async def trim_video(
        self,
        input_path: str | Path,
        output_path: str | Path,
        start_time: float,
        end_time: float | None = None,
        duration: float | None = None,
    ) -> Path:
        """Trim video to specified time range.

        Must provide either end_time or duration (not both).

        Args:
            input_path: Path to input video.
            output_path: Path for output video.
            start_time: Start time in seconds.
            end_time: End time in seconds.
            duration: Duration in seconds.

        Returns:
            Path to trimmed video.

        Raises:
            FFmpegError: If trim fails.
            ValueError: If neither or both end_time and duration provided.
        """
        if (end_time is None) == (duration is None):
            msg = "Provide either end_time or duration, not both"
            raise ValueError(msg)

        args = ["-ss", str(start_time), "-i", str(input_path)]

        if duration is not None:
            args.extend(["-t", str(duration)])
        elif end_time is not None:
            args.extend(["-to", str(end_time)])

        args.extend(["-c", "copy", "-y", str(output_path)])

        await self._run(args)
        return Path(output_path)

    async def _run(self, args: list[str]) -> None:
        """Run FFmpeg command with default timeout.

        Args:
            args: Arguments to pass to ffmpeg.

        Raises:
            FFmpegError: If command fails or times out.
        """
        proc: asyncio.subprocess.Process | None = None
        try:
            proc = await asyncio.create_subprocess_exec(
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "warning",
                *args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            _, stderr = await asyncio.wait_for(proc.communicate(), timeout=DEFAULT_RUN_TIMEOUT)

            if proc.returncode != 0:
                msg = f"FFmpeg failed: {stderr.decode()}"
                raise FFmpegError(msg)
        except TimeoutError:
            if proc is not None:
                proc.kill()
            msg = f"FFmpeg timed out after {DEFAULT_RUN_TIMEOUT} seconds"
            raise FFmpegError(msg) from None
