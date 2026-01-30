"""Recording services for QA Integration system.

Provides VHS CLI recording, Playwright web capture, and FFmpeg media processing.
"""

from tracertm.services.recording.ffmpeg_pipeline import FFmpegPipeline, VideoInfo, FFmpegError
from tracertm.services.recording.tape_generator import TapeFileGenerator
from tracertm.services.recording.vhs_service import VHSExecutionService, VHSExecutionError
from tracertm.services.recording.playwright_service import (
    PlaywrightExecutionService,
    PlaywrightExecutionError,
)

__all__ = [
    "FFmpegPipeline",
    "VideoInfo",
    "FFmpegError",
    "TapeFileGenerator",
    "VHSExecutionService",
    "VHSExecutionError",
    "PlaywrightExecutionService",
    "PlaywrightExecutionError",
]
