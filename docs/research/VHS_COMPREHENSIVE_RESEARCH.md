# VHS (charmbracelet/vhs) - Comprehensive Research Document

**Last Updated:** January 28, 2026
**Research Focus:** CLI Terminal Recording Tool with CLI Demo & Integration Testing Capabilities
**Primary Repository:** https://github.com/charmbracelet/vhs (18.4K stars)

---

## Executive Summary

VHS is a production-grade CLI tool for recording terminal sessions as GIFs, MP4s, and WebM videos. It's written in Go and combines `ttyd` (terminal emulator) with `ffmpeg` (video processing) to create professional demo recordings and perform CLI integration testing. The tool supports programmatic tape file generation, GitHub Actions integration, and self-hosted SSH server deployment for CI/CD pipelines.

**Key Capabilities:**
- Record terminal sessions as video/GIF outputs
- Programmatically generate tape files with complete command scripting
- Integrate with GitHub Actions for automated GIF updates
- Self-host as SSH server for distributed recording
- Support for 150+ color themes
- Customizable terminal appearance (fonts, dimensions, styling)
- Integration testing via ASCII/text output capture
- Real-time frame capturing with configurable framerates

---

## Table of Contents

1. [Tape File Syntax Reference](#tape-file-syntax-reference)
2. [Installation & Dependencies](#installation--dependencies)
3. [Integration Patterns](#integration-patterns)
4. [Output Formats](#output-formats)
5. [Advanced Features](#advanced-features)
6. [Best Practices](#best-practices)
7. [Known Limitations & Workarounds](#known-limitations--workarounds)
8. [Real-World Examples](#real-world-examples)

---

## Tape File Syntax Reference

### File Structure

Tape files are plain text files with `.tape` extension containing commands that VHS executes sequentially. Comments begin with `#`.

```elixir
# This is a comment
Output output.gif

Set Shell "bash"
Set FontSize 32
Set Width 1200
Set Height 600

Type "echo 'Hello World'"
Enter
Sleep 1s
```

### Settings (Must be defined at top of tape)

Settings commands must appear before any action commands (Type, Enter, Sleep, etc.).

#### Shell Configuration

```elixir
Set Shell "bash"          # Set shell (bash, fish, zsh, etc)
Set Shell "fish"
```

#### Display Settings

```elixir
Set FontSize 32           # Font size in pixels (default: varies by platform)
Set FontFamily "Monoflow" # Font family (quoted string)
Set Width 1200            # Terminal width in pixels
Set Height 600            # Terminal height in pixels
Set Padding 0             # Padding around terminal in pixels
Set Margin 60             # Margin around entire output in pixels
Set MarginFill "#6B50FF"  # Margin fill color (hex or file path)
Set BorderRadius 10       # Border radius for terminal window
Set CursorBlink false     # Enable/disable cursor blinking (default: true)

# Letter and line spacing
Set LetterSpacing 20      # Pixels between characters (tracking)
Set LineHeight 1.8        # Line height multiplier (1.0 = normal)

# Color theme
Set Theme "Catppuccin Frappe"  # Theme by name
Set Theme { "name": "Custom", "black": "#535178", "red": "#ef6487", ... } # Custom theme JSON
```

#### Window Decoration

```elixir
Set WindowBar Colorful        # Window bar type options:
                              # - Colorful (default left)
                              # - ColorfulRight
                              # - Rings
                              # - RingsRight
Set WindowBarSize 40          # Height of window bar in pixels
```

#### Video/Rendering Settings

```elixir
Set Framerate 60              # Frame capture rate (default: 60)
Set PlaybackSpeed 1.0         # Playback multiplier:
                              # - 0.5 (2x slower)
                              # - 1.0 (normal, default)
                              # - 2.0 (2x faster)
Set LoopOffset 5              # Start GIF loop at frame 5
Set LoopOffset 50%            # Start GIF loop at 50% through
Set TypingSpeed 500ms         # Delay between typed characters
                              # Can be: 100ms, 1s, 0.1, etc
```

### Output

Specify one or more output files. Supported formats:
- `.gif` - Animated GIF
- `.mp4` - MP4 video (h264 codec)
- `.webm` - WebM video (VP9 codec)
- Directory path - Sequence of PNG frames

```elixir
Output demo.gif
Output demo.mp4
Output demo.webm
Output frames/                # Creates PNG sequence in directory
Output out.ascii              # ASCII art for integration testing
Output out.txt                # Plain text output
```

### Requirements

Ensure programs exist before running tape.

```elixir
Require echo
Require gum
Require glow
```

Must be defined at top, before any non-setting/non-output commands.

### Action Commands

#### Type Command

Emulate typing into terminal with optional custom speed.

```elixir
Type "echo 'Hello World'"
Type@500ms "Slower typing at 500ms per character"
Type `VAR="Escaped quotes work with backticks"`
```

**Escaping Quotes:**
- Use backticks to escape single and double quotes
- Example: `` Type `echo "test"` ``

**Per-Command Speed Override:**
```elixir
Set TypingSpeed 100ms
Type "Normal speed at 100ms"
Type@50ms "Fast speed at 50ms"
```

#### Key Commands

All key commands support optional timing `@<duration>` and optional repeat count.

```elixir
# Syntax: Key[@<time>] [count]
```

**Arrow Keys:**
```elixir
Up 2              # Press Up arrow 2 times
Down              # Press Down arrow once
Left              # Press Left arrow once
Right             # Press Right arrow once
Up@100ms 3        # Press Up 3 times with 100ms between presses
```

**Navigation Keys:**
```elixir
PageUp 3
PageDown 5
Home              # Go to start of line
End               # Go to end of line
```

**Text Control:**
```elixir
Enter 2           # Press Enter twice (new lines)
Backspace 18      # Press Backspace 18 times
Delete 5          # Press Delete 5 times
Insert            # Toggle insert mode
Tab@500ms 2       # Press Tab twice with 500ms between
Space 10          # Press Space 10 times
```

**Special Keys:**
```elixir
Escape            # Press Escape (often cancels)
```

#### Control & Modifier Keys

Control sequences with optional modifiers.

```elixir
Ctrl+C            # Send Ctrl+C (interrupt)
Ctrl+R            # Ctrl+R (reverse history search in bash)
Ctrl+D            # Ctrl+D (EOF/exit)
Ctrl+A            # Ctrl+A (go to line start)
Ctrl+E            # Ctrl+E (go to line end)

# Combinations
Ctrl+Alt+V        # Ctrl+Alt+V
Ctrl+Shift+A      # Ctrl+Shift+A
Ctrl+Alt+Shift+X  # Multiple modifiers

# With timing
Ctrl+C@100ms      # Ctrl+C with 100ms delay
```

**Supported Modifiers:**
- `Shift` (Upper case letters become Shift)
- `Alt` (Meta key)
- `Ctrl` (Control key)

#### Wait Command

Wait for specific conditions before continuing (useful for spinners, loading states).

```elixir
Wait              # Default: wait for prompt (/>$/) on last line, 15s timeout
Wait /pattern/    # Wait for regex pattern on last line
Wait+Screen /pattern/  # Wait for pattern anywhere on screen
Wait+Line /pattern/    # Wait for pattern on last line (default scope)
Wait@10ms /pattern/    # Custom timeout (10ms here, typically use seconds)
Wait+Line@5s /pattern/ # Combined: wait on line with 5s timeout
```

**Default Behavior:**
- Pattern: `/>$/` (prompt at end of line)
- Timeout: `15s`
- Scope: `Line` (check last line only)

**Common Patterns:**
```elixir
Wait /✓/          # Wait for checkmark
Wait /done/       # Wait for "done" text
Wait /Build complete/
Wait+Screen /error/
```

#### Sleep Command

Pause recording (continues capturing frames) for visual delays.

```elixir
Sleep 0.5         # 500 milliseconds
Sleep 2           # 2 seconds
Sleep 100ms       # Explicit milliseconds
Sleep 1s          # Explicit seconds
```

Useful for showing spinners, animations, or command output.

#### Hide / Show

Control whether frames are captured.

```elixir
Hide              # Stop capturing frames
# ... hidden commands execute but don't appear in output ...
Show              # Resume capturing frames
```

**Common Pattern - Setup/Cleanup:**
```elixir
Output demo.gif

# Hidden setup
Hide
Type "go build -o ./demo . && clear"
Enter
Show

# Recording starts here
Type "Running ./demo"
Enter

# Hidden cleanup
Hide
Type "rm demo"
Enter
```

#### Screenshot

Capture current frame as PNG.

```elixir
Screenshot path/to/screenshot.png
```

#### Copy / Paste

Clipboard operations (emulates copying text).

```elixir
Copy "https://github.com/charmbracelet"
Type "open "
Sleep 500ms
Paste
```

#### Env

Set environment variables for the tape session.

```elixir
Env HELLO "WORLD"

Type "echo $HELLO"
Enter
Sleep 1s

# Output: WORLD
```

#### Source

Include commands from another tape file.

```elixir
Source config.tape
Source ./common-setup.tape
```

Allows modular tape organization - common setup/config in separate files.

---

## Installation & Dependencies

### Required Dependencies

**VHS requires TWO external tools:**

1. **ttyd** (Terminal.js TUI daemon)
   - Acts as virtual terminal emulator
   - Minimum version: 1.7.2
   - Provides pty/shell interface
   - Repository: https://github.com/tsl0922/ttyd

2. **ffmpeg** (Multimedia framework)
   - Converts frame sequences to video
   - Performs encoding to MP4/WebM
   - No strict version requirement in code
   - Usually latest stable works
   - Repository: https://ffmpeg.org

### Platform-Specific Installation

#### macOS / Linux (Homebrew)

```bash
brew install vhs
# Installs VHS + ffmpeg
# Note: ttyd must be installed separately from tsl0922/ttyd tap

brew tap tsl0922/ttyd
brew install ttyd
```

#### Arch Linux

```bash
pacman -S vhs
# Usually includes all dependencies
```

#### Nix

```bash
nix-env -iA nixpkgs.vhs
```

#### Windows

```bash
# Using scoop
scoop install vhs

# Using winget
winget install charmbracelet.vhs
```

Note: ttyd installation on Windows may require manual setup.

#### Debian / Ubuntu

```bash
# Add charm.sh repository
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://repo.charm.sh/apt/gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/charm.gpg
echo "deb [signed-by=/etc/apt/keyrings/charm.gpg] https://repo.charm.sh/apt/ * *" | sudo tee /etc/apt/sources.list.d/charm.list

# Install
sudo apt update && sudo apt install vhs ffmpeg

# ttyd must be installed separately
# Download from: https://github.com/tsl0922/ttyd/releases
```

#### Fedora / RHEL

```bash
echo '[charm]
name=Charm
baseurl=https://repo.charm.sh/yum/
enabled=1
gpgcheck=1
gpgkey=https://repo.charm.sh/yum/gpg.key' | sudo tee /etc/yum.repos.d/charm.repo

sudo yum install vhs ffmpeg

# ttyd from GitHub releases
```

#### From Source (Go)

```bash
go install github.com/charmbracelet/vhs@latest
```

### Docker

Complete containerized solution with all dependencies:

```bash
docker run --rm -v $PWD:/vhs ghcr.io/charmbracelet/vhs demo.tape
```

**Dockerfile analysis shows:**
- Base: Alpine Linux (font collector) → Debian stable slim
- Includes: ttyd, ffmpeg, chromium, bash
- Pre-installed fonts: JetBrains Mono, Hack, FiraCode, DejaVu, etc.
- Environment variables pre-configured

### Dependency Version Requirements

```go
// From go.mod - VHS dependencies:
github.com/creack/pty v1.1.24  // PTY support
github.com/go-rod/rod v0.116.2 // Browser automation (for Playwright)
github.com/hashicorp/go-version v1.8.0 // Version parsing
github.com/charmbracelet/ssh v0.0.0-20250128164007-98fd5ae11894 // SSH server
github.com/charmbracelet/wish v1.4.7 // SSH framework
```

**Go Version:** 1.24.1+

---

## Integration Patterns

### GitHub Actions (vhs-action)

Official GitHub Action for automated GIF generation and CI/CD integration.

**Repository:** https://github.com/charmbracelet/vhs-action
**Stars:** 239

#### Installation

Create `.github/workflows/vhs.yml`:

```yaml
name: VHS
on:
  push:
  pull_request:

jobs:
  vhs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate GIFs
        uses: charmbracelet/vhs-action@v3
        with:
          path: demo.tape          # Path to .tape file
          version: latest          # VHS version
          install-fonts: true      # Install extra fonts
```

#### Action Configuration

**Inputs:**

| Input | Description | Default |
|-------|-------------|---------|
| `path` | VHS tape file path | "" (install only) |
| `version` | VHS version to use | "latest" |
| `token` | GitHub token for downloading VHS | `${{ github.token }}` |
| `install-fonts` | Install extra fonts (nerd fonts) | "false" |

**Default Fonts:**
- JetBrains Mono (always installed)

**Extra Fonts (when `install-fonts: true`):**
- Bitstream Vera Sans Mono
- DejaVu / DejaVu Sans Mono
- Fira Code
- Hack / Hack Nerd Font
- IBM Plex Mono
- Inconsolata
- Liberation
- Roboto Mono
- Source Code Pro
- Ubuntu Mono

#### Common Workflows

**Auto-Commit Generated GIFs:**

```yaml
name: VHS Auto-Commit
on:
  push:
    paths:
      - '**.tape'

jobs:
  vhs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Record GIFs
        uses: charmbracelet/vhs-action@v3
        with:
          path: demo.tape

      - name: Commit changes
        run: |
          git config user.name "VHS Bot"
          git config user.email "vhs@charm.sh"
          git add demo.gif
          git commit -m "chore: update GIF" || true
          git push
```

**Comment GIF on Pull Request:**

```yaml
name: VHS Comment PR
on:
  pull_request:

jobs:
  vhs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Record and Upload
        uses: charmbracelet/vhs-action@v3
        with:
          path: demo.tape

      - name: Upload and Comment
        uses: actions/upload-artifact@v3
        with:
          name: demo-gif
          path: demo.gif

      - name: Comment PR
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '![Demo](./demo.gif)'
            })
```

### Self-Hosted SSH Server

VHS can run as an SSH server for remote recording.

**Configuration Environment Variables:**

```bash
VHS_PORT=1976                          # Listen port (default: 1976)
VHS_HOST=0.0.0.0                       # Bind host (default: localhost)
VHS_UID=1000                           # Run as UID
VHS_GID=1000                           # Run as GID
VHS_KEY_PATH=/path/to/vhs_ed25519      # SSH private key path
VHS_AUTHORIZED_KEYS_PATH=/path/to/keys # Authorized keys file (empty = public)
```

**Starting Server:**

```bash
vhs serve
```

**Remote Usage:**

```bash
ssh vhs.example.com < demo.tape > demo.gif
```

**Docker with SSH Server:**

```dockerfile
# VHS container runs on port 1976
docker run -p 1976:1976 -e VHS_HOST=0.0.0.0 ghcr.io/charmbracelet/vhs serve
```

Then connect via SSH:

```bash
ssh -p 1976 user@vhs.example.com < tape.tape > output.gif
```

### Programmatic Tape Generation

VHS tapes are plain text - can be generated programmatically:

**Python Example:**

```python
def generate_demo_tape(output_file):
    tape = """
Output demo.gif

Set FontSize 32
Set Width 1200
Set Height 600

Type "echo 'Generated by VHS'"
Enter
Sleep 1s
"""

    with open(output_file, 'w') as f:
        f.write(tape)

generate_demo_tape('demo.tape')
```

**Go Example:**

```go
package main

import (
    "fmt"
    "os"
)

func generateTape(filename string) error {
    tape := `Output demo.gif

Set FontSize 32
Set Width 1200
Set Height 600

Type "echo 'Hello from Go'"
Enter
Sleep 1s
`

    return os.WriteFile(filename, []byte(tape), 0644)
}
```

**Template-Based Generation (Recommended for CI/CD):**

```bash
#!/bin/bash
cat > demo.tape << 'EOF'
Output demo.gif
Set Shell "bash"
Set FontSize 32
Set Width 1200
Set Height 600

Type "echo 'CI/CD Generated Demo'"
Enter
Sleep 1s
EOF

vhs demo.tape
```

---

## Output Formats

### Video Formats

#### GIF (Animated)

```elixir
Output demo.gif
```

**Characteristics:**
- Most compatible format
- Larger file sizes (especially for long recordings)
- No audio support
- Recommended for web/documentation
- Width/height preserved exactly

**File Size Optimization:**
- Reduce Framerate: `Set Framerate 30` (vs 60 default)
- Reduce PlaybackSpeed: `Set PlaybackSpeed 2.0` (speeds up rendering, smaller GIF)
- Reduce terminal dimensions: `Set Width 800 Set Height 400`
- Reduce recording duration: Use `Sleep` judiciously

#### MP4 (H.264)

```elixir
Output demo.mp4
```

**Characteristics:**
- Smaller file size than GIF
- Wide browser support
- No audio support in VHS output
- Progressive playback
- Better for video hosting

#### WebM (VP9)

```elixir
Output demo.webm
```

**Characteristics:**
- Modern codec (VP9)
- Good compression
- Smaller than MP4 for same quality
- Best for newer browsers
- Fallback to MP4 for IE/older browsers

#### PNG Sequence

```elixir
Output frames/
```

**Characteristics:**
- Creates directory with numbered PNG files: `frame-000000.png`, etc.
- One PNG per frame
- Useful for:
  - Custom post-processing
  - Selective frame extraction
  - High-quality archival
  - Integration with other tools

### Text Output (Integration Testing)

#### ASCII Art Output

```elixir
Output golden.ascii
```

**Purpose:** Integration testing and golden file comparison

**Use Case:**
```bash
# Generate golden file
vhs record.tape  # With Output golden.ascii

# In tests
actual=$(vhs test.tape | grep -v timestamp)
expected=$(cat golden.ascii)
if [ "$actual" != "$expected" ]; then
    echo "Test failed: output differs"
    exit 1
fi
```

#### Plain Text Output

```elixir
Output output.txt
```

Captures terminal output as plain text, useful for:
- Command output verification
- Log generation
- Documentation
- Test assertions

---

## Advanced Features

### Record Interactive Sessions

VHS can record real terminal sessions:

```bash
vhs record > cassette.tape
```

**Process:**
1. Starts recording shell session
2. User performs actions manually
3. Type `exit` to stop recording
4. Outputs `.tape` file with recorded commands and timing
5. Manually edit for cleanup/adjustments

**Editing Generated Tapes:**

Generated tapes often need refinement:

```elixir
# vhs record output needs:
# 1. Output command at top
# 2. Settings configuration
# 3. Timing adjustments
# 4. Hidden setup/cleanup commands

Output demo.gif
Set FontSize 32
Set Width 1200
Set Height 600
Require echo

# Setup (hidden)
Hide
Type "clear"
Enter
Show

# ... rest of recorded commands ...
```

### Publishing Generated GIFs

VHS provides hosted GIF sharing:

```bash
vhs publish demo.gif
```

**Output:**
- Browser link (vhs.charm.sh/...)
- HTML embed code
- Markdown link

**Useful for:**
- Pull request discussions
- GitHub issues
- Team communication
- Documentation

### Custom Theme Definition

Themes use base-16 color format with standard ANSI colors:

```elixir
Set Theme {
  "name": "CustomTheme",
  "black": "#000000",
  "red": "#ff0000",
  "green": "#00ff00",
  "yellow": "#ffff00",
  "blue": "#0000ff",
  "magenta": "#ff00ff",
  "cyan": "#00ffff",
  "white": "#ffffff",
  "brightBlack": "#808080",
  "brightRed": "#ff8080",
  "brightGreen": "#80ff80",
  "brightYellow": "#ffff80",
  "brightBlue": "#8080ff",
  "brightMagenta": "#ff80ff",
  "brightCyan": "#80ffff",
  "brightWhite": "#ffffff",
  "background": "#1a1a1a",
  "foreground": "#e0e0e0",
  "selection": "#333333",
  "cursor": "#e0e0e0"
}
```

**Available Named Themes (150+):**
- Dracula (popular)
- Catppuccin (Latte/Frappe/Macchiato/Mocha)
- Solarized (Light/Dark)
- Atom One (Light/Dark)
- Nord
- Gruvbox
- Monokai
- Vim-specific themes
- And 100+ more (see `vhs themes`)

**View All Themes:**

```bash
vhs themes                # List all 150+ themes
vhs manual               # Full CLI documentation
```

### Modular Tape Organization

Use `Source` for DRY principles:

```elixir
# setup.tape
Require git
Require gh

Env DEMO_DIR "/tmp/demo"
Hide
Type "cd $DEMO_DIR && rm -rf . && git init"
Enter
Show
```

```elixir
# main.tape
Source setup.tape

Type "git add ."
Enter
Sleep 1s

Type "git commit -m 'Initial commit'"
Enter
Sleep 2s
```

### Frame Control and Timing

**Precise timing for complex demos:**

```elixir
Set Framerate 60          # Capture rate (FPS)
Set PlaybackSpeed 0.5    # Playback 2x slower (double duration)
Set LoopOffset 25%       # GIF loop starts at 25% through
Set TypingSpeed 50ms     # Very fast typing

Type "npm install"       # Will display as very fast
Sleep 2s
Type@500ms "Slow text"   # Override to 500ms per char
```

**Frame Timing Strategy:**
- Use `Sleep` for passive waits (spinners, API calls)
- Use `Wait` for active conditions (file appears, prompt changes)
- Adjust `PlaybackSpeed` to fit intended viewing length

---

## Best Practices

### 1. GIF Optimization for Web

```elixir
Output demo.gif

Set Width 960           # 16:9 aspect ratio for modern screens
Set Height 540         # 540p is sufficient for clarity

Set Framerate 30        # 30 FPS is sufficient (vs 60 default)
Set PlaybackSpeed 2.0   # Speed up playback 2x (halves GIF size)

Set Padding 10
Set FontSize 24         # Larger font = smaller GIF
```

**Typical File Sizes:**
- 10-second demo, 960x540, 30fps: 2-4 MB
- 10-second demo, 960x540, 60fps: 4-8 MB
- Same with PlaybackSpeed 2.0: 1-2 MB

### 2. CI/CD Integration Best Practices

**Tape File Organization:**

```bash
project/
├── .github/workflows/
│   └── vhs.yml
├── demos/
│   ├── setup.tape      # Common setup
│   ├── basic.tape      # Basic demo
│   ├── advanced.tape   # Advanced demo
│   └── outputs/        # Generated GIFs
└── docs/
    └── getting-started.md  # References demos/outputs
```

**GitHub Actions Pattern:**

```yaml
name: VHS
on:
  push:
    paths:
      - 'demos/**/*.tape'
      - '.github/workflows/vhs.yml'

jobs:
  record:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        demo: [basic, advanced]
    steps:
      - uses: actions/checkout@v4

      - uses: charmbracelet/vhs-action@v3
        with:
          path: demos/${{ matrix.demo }}.tape
          install-fonts: true

      - name: Move output
        run: mv demos/${{ matrix.demo }}.gif demos/outputs/

      - name: Commit
        run: |
          git config user.name "VHS Bot"
          git config user.email "bot@charm.sh"
          git add demos/outputs/
          git commit -m "chore: update ${{ matrix.demo }} demo" || true
          git push
```

### 3. Recording Complex Interactive CLIs

**Strategy for TUI Applications:**

```elixir
Output demo.gif

Require myapp

# Start app hidden for clean start
Hide
Type "myapp"
Enter
Show

# Wait for specific UI state
Wait /Select an option/

# Navigate UI
Type "j"            # Down
Type "j"
Wait /Option 2 selected/

Type "Enter"        # Select
Wait /Processing/
Wait /Done!/

Sleep 2s

Type "q"            # Quit
Wait /Goodbye/
```

**Key Techniques:**
1. Use `Hide`/`Show` for clean recording start
2. Use `Wait` with UI patterns (prompts, status messages)
3. Use `Sleep` for animations/spinners
4. Test locally before committing to CI

### 4. Documentation Demos

```elixir
Output docs/demo.gif

Set Width 1024
Set Height 576
Set FontSize 24
Set Theme "Catppuccin Frappe"
Set Padding 20

Require docker

Type "# Building with Docker"
Enter
Sleep 500ms

Type "docker build -t myapp ."
Enter
Wait /Successfully tagged/
Sleep 1s

Type "docker run myapp"
Enter
Wait /Ready on port/
Sleep 2s
```

### 5. Testing CLI Output

**Golden File Testing:**

```bash
#!/bin/bash

# Generate golden file (only once)
# vhs test.tape > golden.txt

# In CI/test
actual=$(vhs test.tape)
golden=$(cat golden.txt)

if [ "$actual" != "$golden" ]; then
    echo "CLI output changed!"
    diff <(echo "$golden") <(echo "$actual")
    exit 1
fi
```

**VHS for Integration Testing:**

```elixir
Output test-output.txt

Require myapp

Type "myapp --help"
Enter
Wait /Usage:/
Sleep 1s

Type "myapp --version"
Enter
Wait /myapp version/
Sleep 1s
```

### 6. Styling Consistency

**Reusable Theme Setup:**

```elixir
# theme-setup.tape
Set Theme "Catppuccin Frappe"
Set FontSize 24
Set FontFamily "JetBrains Mono"
Set Width 1024
Set Height 576
Set Padding 15
Set Margin 20
Set MarginFill "#1e1e1e"
Set BorderRadius 8
Set WindowBar Colorful
```

**Main Tape:**

```elixir
Source theme-setup.tape
Output demo.gif

Type "echo 'Demo with consistent styling'"
Enter
Sleep 1s
```

---

## Known Limitations & Workarounds

### 1. Platform-Specific Issues

**Linux (Headless Servers):**
- Issue: ttyd requires PTY (pseudo-terminal)
- Workaround: Use Docker container with VHS pre-installed
- Example: `docker run --rm -v $PWD:/vhs ghcr.io/charmbracelet/vhs demo.tape`

**macOS M1/M2 (ARM64):**
- Issue: Some dependencies (Chromium for Playwright) may need native ARM builds
- Status: Modern versions support ARM64
- Workaround: Use latest VHS version

**Windows:**
- Issue: ttyd installation may require manual setup
- Workaround: Use WSL2 with Linux installation, or Docker
- Status: Improving with each release

### 2. Recording Limitations

**Long Sessions:**
- Issue: Very long recordings (30+ min) create huge GIFs
- Workaround: Split into multiple smaller tapes
- Best practice: Keep demos under 2 minutes

**Dynamic Content:**
- Issue: Variable output (timestamps, random IDs) breaks golden files
- Workaround: Mock/stub APIs, use fixed seeds, filter output
- Example: `Type "date +%Y-%m-%d"` might vary

**Hidden Commands Visibility:**
- Issue: `Hide`/`Show` sections don't appear in output, but background processes continue
- Limitation: Can't completely hide background operations from timing
- Workaround: Use `Wait` with `+Screen` to detect completion

### 3. Font and Rendering Issues

**Custom Fonts Not Appearing:**
- Issue: Font not installed in rendering environment
- Solution: Use `install-fonts: true` in GitHub Actions
- Or manually install in CI: `sudo apt install fonts-firacode`

**Emoji Rendering:**
- Status: Some terminals/fonts have limited emoji support
- Workaround: Test with `Set FontFamily "JetBrains Mono"` (has emoji)
- Docker image includes noto-emoji fonts

**Ligatures:**
- Status: Terminal rendering may not support font ligatures
- Limitation: Some fonts (Fira Code) show ligatures differently
- Workaround: Choose fonts with consistent rendering

### 4. Performance Optimization

**Slow Recording (High CPU):**
- Issue: High framerate + large dimensions = high CPU
- Workaround: Reduce Framerate or PlaybackSpeed
- Example: `Set Framerate 30` instead of 60

**Large Output Files:**
- GIF encoding is slow for long sessions
- Use WebM/MP4 for shorter encoding time
- Use `Set PlaybackSpeed 2.0` to double-speed (smaller file)

**Memory Usage:**
- Docker container default memory may be insufficient
- Workaround: `docker run -m 2g ghcr.io/charmbracelet/vhs demo.tape`

### 5. Timing and Synchronization

**Race Conditions:**
- Issue: Commands execute faster than expected UI updates
- Solution: Use `Wait` instead of fixed `Sleep` times
- Example: `Wait /Ready/` instead of `Sleep 3s`

**Different Performance in CI vs Local:**
- CI runners may be slower than local machine
- Workaround: Extend `Wait` timeouts for CI
- Better: Use relative timeouts `Wait@30s /pattern/`

**Variable Typing Speed:**
- Network delay, system load affects perceived timing
- Use `Wait` for deterministic points
- Example: Don't rely on `Sleep 2s`, use `Wait /Output:/`

### 6. Dependency Version Conflicts

**ttyd Version Requirement:**
- Minimum: 1.7.2
- Check: `ttyd --version`
- Update: `brew upgrade ttyd` or download from releases

**ffmpeg Codec Support:**
- Some systems may have ffmpeg without H.264 or VP9
- Verify: `ffmpeg -codecs | grep hevc && ffmpeg -codecs | grep vp9`
- Docker version includes all codecs

### 7. SSH Server Mode Limitations

**SSH Server Issues:**
- Port 1976 may be blocked in corporate networks
- Workaround: Use Docker with port mapping
- Security: Use `VHS_AUTHORIZED_KEYS_PATH` for key-based auth

**TTY Negotiation:**
- VHS SSH server doesn't support interactive PTY allocation
- Limitation: Can only accept tape via stdin
- Pipe tapes: `ssh user@host < demo.tape > demo.gif`

---

## Real-World Examples

### Example 1: Simple CLI Demo

```elixir
# demo.tape - Basic echo demo

Output demo.gif

Set FontSize 32
Set Width 1200
Set Height 600
Set Theme "Dracula"

Type "echo 'Welcome to VHS Demo!'"
Enter
Sleep 1s

Type "echo 'Recording terminal sessions as code'"
Enter
Sleep 2s
```

**Run:**
```bash
vhs demo.tape
```

### Example 2: Interactive CLI App

```elixir
# tui-demo.tape - Recording TUI application

Output tui-demo.gif

Require gum

Set FontSize 24
Set Width 960
Set Height 540

Hide
Type "clear"
Enter
Show

Type "gum choose --no-limit 'Apple' 'Banana' 'Cherry' 'Date'"
Enter
Wait /selected/

Type "j"  # Navigate down
Wait /Banana/

Type "Space"  # Select
Type "Enter"

Wait /Your selection/
Sleep 2s
```

### Example 3: Build Tool Demo with Hidden Setup

```elixir
# build-demo.tape

Output build.gif

Require cargo

Set FontSize 28
Set Width 1024
Set Height 576

# Hidden setup
Hide
Type "cd /tmp && rm -rf myproject && cargo new myproject"
Enter
Type "cd myproject"
Enter
Show

Type "cargo build --release"
Enter
Wait /Finished/
Sleep 2s

Type "cargo run --release"
Enter
Wait /Hello, world!/
Sleep 1s
```

### Example 4: GitHub Actions Workflow

```yaml
# .github/workflows/record-demo.yml

name: Record Demo

on:
  push:
    paths:
      - 'demo.tape'
      - '.github/workflows/record-demo.yml'
  workflow_dispatch:

jobs:
  record:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Record demo
        uses: charmbracelet/vhs-action@v3
        with:
          path: demo.tape
          install-fonts: true

      - name: Commit updated demo
        run: |
          git config user.email "action@github.com"
          git config user.name "GitHub Action"
          git add demo.gif
          git diff --quiet && git diff --staged --quiet || \
            (git commit -m "chore: update demo.gif" && git push)
```

### Example 5: Modular Tape with Sourcing

```elixir
# common.tape
Env PROJECT_DIR "/tmp/myproject"
Env OUTPUT_DIR "$HOME/output"

Set Theme "Catppuccin Mocha"
Set FontSize 24
Set Width 1024
Set Height 576
```

```elixir
# main-demo.tape
Output demo.gif

Source common.tape

Hide
Type "cd $PROJECT_DIR && make clean && make"
Enter
Wait /Build complete/
Show

Type "make demo"
Enter
Wait /Running demo/
Sleep 3s
```

---

## Summary Table: Command Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `Output` | Specify output file(s) | `Output demo.gif` |
| `Require` | Check for dependencies | `Require docker` |
| `Set` | Configure terminal/rendering | `Set FontSize 32` |
| `Type` | Emit typed text | `Type "echo hello"` |
| `Enter` | Press Enter key | `Enter 2` |
| `Up/Down/Left/Right` | Arrow keys | `Down 3` |
| `Tab` | Tab key | `Tab 2` |
| `Backspace` | Delete previous char | `Backspace 5` |
| `Ctrl+<key>` | Control sequences | `Ctrl+C` |
| `Space` | Space bar | `Space 10` |
| `Wait` | Wait for condition | `Wait /prompt/` |
| `Sleep` | Pause recording | `Sleep 2s` |
| `Hide` | Stop capturing frames | `Hide` |
| `Show` | Resume capturing | `Show` |
| `Screenshot` | Capture PNG frame | `Screenshot frame.png` |
| `Copy` | Copy to clipboard | `Copy "text"` |
| `Paste` | Paste from clipboard | `Paste` |
| `Env` | Set environment var | `Env KEY value` |
| `Source` | Include another tape | `Source setup.tape` |

---

## Resources and Links

**Official Repositories:**
- Main VHS: https://github.com/charmbracelet/vhs
- GitHub Action: https://github.com/charmbracelet/vhs-action
- Tree-sitter (Syntax Highlighting): https://github.com/charmbracelet/tree-sitter-vhs

**Dependencies:**
- ttyd: https://github.com/tsl0922/ttyd
- ffmpeg: https://ffmpeg.org
- Charm.sh: https://charm.sh

**Documentation:**
- CLI Manual: `vhs manual`
- Theme List: `vhs themes`
- Help: `vhs --help`

**Community:**
- Charm Discord: https://charm.sh/chat
- Twitter: @charmcli
- Fediverse: mastodon.social/@charmcli

---

**Document Version:** 1.0
**Last Research Update:** January 28, 2026
**Next Update Recommended:** Q3 2026 (for new VHS features)
