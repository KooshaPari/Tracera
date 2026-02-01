# FFmpeg Quick Reference Guide

Fast lookup for common video processing tasks.

---

## GIF Conversion Recipes

### Basic GIF (Fast)
```bash
ffmpeg -i input.mp4 -vf "fps=10,scale=480:-1" output.gif
```
- Size: ~3-5 MB for 30-second video
- Quality: Good
- Speed: ~30 seconds

### High-Quality GIF (Recommended)
```bash
ffmpeg -i input.mp4 -vf "fps=10,scale=480:-1,palettegen" palette.png
ffmpeg -i input.mp4 -i palette.png -lavfi "fps=10,scale=480:-1[x];[x][1:v]paletteuse=dither=bayer" output.gif
```
- Size: ~2-4 MB
- Quality: Excellent
- Speed: ~1 minute

### Small GIF (Social Media)
```bash
ffmpeg -i input.mp4 -vf "fps=8,scale=320:-1,palettegen" palette.png
ffmpeg -i input.mp4 -i palette.png -lavfi "fps=8,scale=320:-1[x];[x][1:v]paletteuse=dither=none" output.gif
```
- Size: ~500 KB - 1 MB
- Quality: Good
- Best for: Twitter, Slack

---

## Thumbnail Recipes

### Single Thumbnail (Fast)
```bash
ffmpeg -ss 10 -i input.mp4 -frames:v 1 -q:v 2 thumb.jpg
```
- Speed: ~0.2s
- Size: ~50-80 KB

### Best Frame Thumbnail
```bash
ffmpeg -ss 10 -i input.mp4 -vf "thumbnail=n=100" -frames:v 1 -q:v 2 thumb.jpg
```
- Speed: ~2-3s
- Automatically selects best frame

### Aspect-Ratio Safe Thumbnail
```bash
ffmpeg -ss 10 -i input.mp4 \
  -vf "scale=640:480:force_original_aspect_ratio=decrease,pad=640:480:(ow-iw)/2:(oh-ih)/2" \
  -frames:v 1 -q:v 2 thumb.jpg
```
- No letterboxing issues

### Multiple Thumbnails (Storyboard)
```bash
ffmpeg -i input.mp4 -vf "scale=160:90,fps=1/10,tile=10x10" -frames:v 1 storyboard.png
```
- 100 thumbnails in one image
- Good for video scrubbing

---

## Video Encoding Recipes

### H.264 High Quality (Most Compatible)
```bash
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium output.mp4
```
- File size: ~45% of original
- Quality: Excellent
- Encoding time: ~1x real-time
- Compatibility: Universal

### H.265/HEVC (Best Compression)
```bash
ffmpeg -i input.mp4 -c:v libx265 -crf 28 -preset medium output.mp4
```
- File size: ~22% of original (50% smaller than H.264)
- Quality: Excellent
- Encoding time: ~3x real-time
- Compatibility: Modern devices only

### Fast Web Encoding
```bash
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset fast -movflags +faststart output.mp4
```
- Encoding time: ~0.5x real-time
- Quality: Excellent
- Optimized for streaming

### GPU Acceleration (NVIDIA)
```bash
ffmpeg -i input.mp4 -c:v h264_nvenc -preset fast output.mp4
```
- Encoding time: ~0.05x real-time (20x faster)
- Quality: Good
- Requires NVIDIA GPU

---

## Frame Extraction Recipes

### Extract Frames Every N Seconds
```bash
ffmpeg -i input.mp4 -vf "fps=1/5" -q:v 2 frame_%04d.jpg
# Extracts 1 frame every 5 seconds
```

### Extract Keyframes Only (Fast)
```bash
ffmpeg -i input.mp4 -vf "select='eq(pict_type,I)'" -q:v 2 keyframe_%04d.jpg
```
- 10-20x fewer frames
- ~2-5 seconds per minute of video

### Detect Scene Changes
```bash
ffmpeg -i input.mp4 -vf "select='gt(scene,0.4)',scale=640:480" scene_%04d.jpg
```
- `0.3` = Sensitive (many frames)
- `0.4` = Balanced (recommended)
- `0.5` = Conservative (major changes only)

---

## CRF Values Quick Guide

| CRF | Quality | File Size | Use Case |
|-----|---------|-----------|----------|
| 18 | Near-lossless | 70% | Archival/Editing |
| 23 | High quality | 45% | YouTube/Streaming |
| 25 | Good quality | 35% | Web delivery |
| 28 | Acceptable | 25% | Social media |
| 32 | Visible loss | 15% | Low bandwidth |

**H.265 (HEVC): Use CRF value 4-6 points higher (e.g., CRF 28 ≈ CRF 23 H.264)**

---

## Python Examples

### Thumbnail Generation (Sync)
```python
import subprocess

def create_thumbnail(video: str, output: str, timestamp: str = "10"):
    cmd = [
        'ffmpeg', '-ss', timestamp, '-i', video,
        '-frames:v', '1', '-q:v', '2', '-y', output
    ]
    subprocess.run(cmd, capture_output=True, check=True)
```

### GIF Conversion (Async)
```python
import asyncio
import subprocess

async def create_gif(video: str, output: str):
    # Generate palette
    cmd1 = ['ffmpeg', '-i', video, '-vf', 'fps=10,scale=480:-1,palettegen', 'palette.png', '-y']
    await asyncio.create_subprocess_exec(*cmd1)

    # Create GIF
    cmd2 = ['ffmpeg', '-i', video, '-i', 'palette.png',
            '-lavfi', 'fps=10,scale=480:-1[x];[x][1:v]paletteuse', output, '-y']
    await asyncio.create_subprocess_exec(*cmd2)
```

### Batch Processing
```python
import concurrent.futures
import subprocess
from pathlib import Path

def convert_file(video: str):
    output = f"{Path(video).stem}_converted.mp4"
    cmd = ['ffmpeg', '-i', video, '-c:v', 'libx264', '-crf', '23', output, '-y']
    subprocess.run(cmd, capture_output=True, check=True)

files = list(Path('.').glob('*.mp4'))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(convert_file, files)
```

---

## Performance Tuning

| Parameter | Fast | Balanced | Quality |
|-----------|------|----------|---------|
| Preset | ultrafast | medium | veryslow |
| CRF (H.264) | 26 | 23 | 20 |
| CRF (H.265) | 32 | 28 | 24 |
| Scale | 480p | 720p | 1080p |

### Reduce Memory Usage
```bash
ffmpeg -i input.mp4 -c:v libx264 -threads 2 -bufsize 512k output.mp4
```

### Use All CPU Cores
```bash
ffmpeg -i input.mp4 -c:v libx264 -threads 0 output.mp4
```

### Parallel File Processing
```bash
parallel -j 4 ffmpeg -i {} -c:v libx264 -crf 23 {.}_converted.mp4 ::: *.mp4
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| GIF too large | Reduce fps to 8, scale to 320, use dither=none |
| Thumbnail not good | Try -ss before -i, use thumbnail filter |
| Slow encoding | Use preset=fast, enable GPU, reduce resolution |
| High memory | Reduce threads to 2, limit buffer to 512k |
| Pixelated video | Increase CRF (lower is better, use 18-23) |

---

## Common Parameter Reference

```bash
ffmpeg [global options] -i input.mp4 [input options] -c:v codec [encoding options] output.mp4

# Scale options
-vf "scale=640:480"              # Hard scale to 640x480
-vf "scale=640:-1"               # Scale width, auto height
-vf "scale=-1:480"               # Auto width, scale height

# Quality options (JPEG)
-q:v 2      # Highest quality (largest)
-q:v 5      # Balanced
-q:v 10     # Lower quality (smallest)

# Video codec options
-c:v libx264           # H.264 (most compatible)
-c:v libx265           # H.265 (smaller files)
-c:v h264_nvenc        # NVIDIA H.264
-c:v hevc_nvenc        # NVIDIA H.265

# Audio options
-c:a aac               # AAC audio
-b:a 128k              # 128k bitrate
-c:a copy              # Copy audio unchanged

# Frame options
-frames:v 1            # Extract 1 frame
-vf "fps=10"           # 10 frames per second
-vf "fps=1/5"          # 1 frame every 5 seconds
```

