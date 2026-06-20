"""Recording services for QA Integration system.

Provides VHS CLI recording, Playwright web capture, and FFmpeg media processing.
"""

from tracertm.services.recording.ffmpeg_pipeline import FFmpegError, FFmpegPipeline, VideoInfo
from tracertm.services.recording.playwright_service import (
    PlaywrightExecutionError,
    PlaywrightExecutionService,
)
from tracertm.services.recording.tape_generator import TapeFileGenerator
from tracertm.services.recording.vhs_service import VHSExecutionError, VHSExecutionService

__all__ = [
    "FFmpegError",
    "FFmpegPipeline",
    "PlaywrightExecutionError",
    "PlaywrightExecutionService",
    "TapeFileGenerator",
    "VHSExecutionError",
    "VHSExecutionService",
    "VideoInfo",
]
