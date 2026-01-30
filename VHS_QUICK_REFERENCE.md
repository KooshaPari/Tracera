# VHS Quick Reference Guide

## Installation (One-Liner by Platform)

```bash
# macOS
brew install vhs && brew tap tsl0922/ttyd && brew install ttyd

# Ubuntu/Debian
sudo apt update && sudo apt install vhs ffmpeg

# Docker (No installation needed)
docker run --rm -v $PWD:/vhs ghcr.io/charmbracelet/vhs demo.tape
```

---

## Basic Tape Template

```elixir
# Output configuration
Output demo.gif

# Settings (must come before actions)
Set Shell "bash"
Set FontSize 32
Set Width 1200
Set Height 600
Set Theme "Catppuccin Frappe"

# Actions
Type "echo 'Hello VHS!'"
Enter
Sleep 1s
```

---

## Settings Quick Lookup

```elixir
# Display & Style
Set FontSize 32
Set FontFamily "JetBrains Mono"
Set Width 1200
Set Height 600
Set Padding 10
Set Theme "Dracula"

# Rendering
Set Framerate 60
Set PlaybackSpeed 1.0
Set LoopOffset 5

# Typing
Set TypingSpeed 100ms
```

---

## Action Commands Quick Lookup

```elixir
# Text input
Type "command"
Type@500ms "slower typing"

# Keys
Enter
Tab
Backspace 5
Space 3

# Navigation
Up
Down
Left
Right
PageUp
PageDown

# Control keys
Ctrl+C
Ctrl+A
Ctrl+Alt+V

# Waiting (use instead of Sleep when possible)
Wait
Wait /pattern/
Wait+Screen /error/
Wait+Line /prompt/
Wait@5s /done/

# Visibility control
Hide
Show

# Other
Sleep 1s
Screenshot frame.png
Copy "text"
Paste
```

---

## Output Formats

```elixir
Output demo.gif      # Animated GIF (web, documents)
Output demo.mp4      # MP4 video (better compression)
Output demo.webm     # WebM video (modern browsers)
Output frames/       # PNG sequence
Output output.txt    # Text output (testing)
```

---

## Common Patterns

**Hidden Setup:**
```elixir
Hide
Type "npm install && clear"
Enter
Show
```

**Wait for Completion:**
```elixir
Type "npm run build"
Enter
Wait /Build complete/
```

**Modular Tapes:**
```elixir
Source common-settings.tape
Source setup.tape
```

**Environment Variables:**
```elixir
Env PATH "$PATH:/custom/bin"
Type "echo $PATH"
Enter
```

---

## Performance Optimization

**Smaller GIFs:**
```elixir
Set Framerate 30       # Instead of 60
Set PlaybackSpeed 2.0  # Double speed (halves size)
Set Width 960
Set Height 540
```

**Faster Rendering:**
```elixir
Set PlaybackSpeed 2.0  # Speeds up output generation
```

---

## GitHub Actions Setup

```yaml
- uses: charmbracelet/vhs-action@v3
  with:
    path: demo.tape
    install-fonts: true
```

---

## Typing Speed Tricks

```elixir
Set TypingSpeed 100ms        # Global speed

Type "default speed"         # Uses 100ms
Type@500ms "very slow"       # Override to 500ms
Type@10ms "very fast"        # Override to 10ms
```

---

## Wait Command Variations

```elixir
Wait              # Wait for />$/ (default prompt) on last line, 15s timeout
Wait /pattern/    # Wait for regex on last line
Wait+Screen       # Search entire screen instead of last line
Wait@30s /pat/    # Custom timeout
```

---

## Available Themes (Popular)

```
Dracula
Catppuccin Frappe / Latte / Macchiato / Mocha
Solarized Dark / Light
Atom One Dark / Light
Nord
Gruvbox
Monokai
```

**List all:** `vhs themes`

---

## Dependency Check

```bash
vhs --version          # Check VHS version
ttyd --version         # Check ttyd (min 1.7.2)
ffmpeg -version        # Check ffmpeg

# or run diagnostic
vhs manual             # Full docs
```

---

## Common Troubleshooting

**ttyd not found:**
```bash
# macOS
brew tap tsl0922/ttyd && brew install ttyd

# Linux - download binary
wget https://github.com/tsl0922/ttyd/releases/download/1.7.4/ttyd.x86_64
chmod +x ttyd.x86_64 && sudo mv ttyd.x86_64 /usr/local/bin/ttyd
```

**ffmpeg not found:**
```bash
brew install ffmpeg    # macOS
sudo apt install ffmpeg  # Linux
```

**Docker alternative (no setup):**
```bash
docker run --rm -v $PWD:/vhs ghcr.io/charmbracelet/vhs tape.tape
```

---

## Real Example: Simple Demo

```elixir
Output demo.gif

Set FontSize 24
Set Width 1024
Set Height 576

Type "whoami"
Enter
Sleep 500ms

Type "date"
Enter
Sleep 500ms

Type "ls -la"
Enter
Wait /total/
Sleep 1s
```

---

## Real Example: Build Tool Demo

```elixir
Output build-demo.gif

Require cargo

Set FontSize 28
Set Width 960
Set Height 540

Hide
Type "cd /tmp && cargo new demo && cd demo"
Enter
Show

Type "cargo build --release"
Enter
Wait /Finished/
Sleep 2s

Type "ls -la target/release/"
Enter
Wait /demo/
Sleep 1s
```

---

## Real Example: TUI Application

```elixir
Output tui-demo.gif

Require gum

Set FontSize 24
Set Width 960
Set Height 540

Type "gum choose 'Option 1' 'Option 2' 'Option 3'"
Enter
Wait /selected/
Sleep 1s
```

---

## Key Resources

| Resource | Command |
|----------|---------|
| Full documentation | `vhs manual` |
| Theme list | `vhs themes` |
| Help | `vhs --help` |
| Record session | `vhs record > output.tape` |
| Version info | `vhs --version` |

---

## SSH Server Mode

```bash
# Start server
vhs serve

# Remote usage
ssh user@vhs.example.com < demo.tape > demo.gif

# With port
ssh -p 1976 user@host < demo.tape > demo.gif
```

---

## Environment Variables (SSH Server)

```bash
VHS_PORT=1976
VHS_HOST=0.0.0.0
VHS_UID=1000
VHS_GID=1000
VHS_KEY_PATH=/path/to/key
VHS_AUTHORIZED_KEYS_PATH=/path/to/keys
```

---

## File Size Comparison (10-second demo, 1024x576)

| Config | GIF Size | Duration |
|--------|----------|----------|
| 60 fps, normal | 8-10 MB | 10s |
| 30 fps, normal | 4-5 MB | 10s |
| 30 fps, 2x speed | 2-3 MB | 5s |
| 60 fps, 2x speed | 4-5 MB | 5s |

---

## Tips & Tricks

1. **Use `Wait` over `Sleep`** - More reliable timing
2. **Test locally first** - Before committing to CI
3. **Hide setup commands** - For cleaner demos
4. **Version control `.tape` files** - Not the outputs
5. **Use GitHub Actions** - Keep GIFs auto-updated
6. **Modular tapes** - Use `Source` for reusable configs
7. **Theme consistency** - Use common theme setup tape
8. **Test in CI** - Timing may differ from local
9. **GIF optimization** - Lower framerate + higher playback speed
10. **Document changes** - Update tape file comments with demo intent

---

## Integration Testing Example

```bash
#!/bin/bash

# Generate expected output
vhs test.tape > expected.txt

# In test
actual=$(vhs test.tape)
if [ "$actual" = "$(cat expected.txt)" ]; then
    echo "PASS: CLI output matches"
else
    echo "FAIL: CLI output differs"
    diff expected.txt <(echo "$actual")
    exit 1
fi
```

---

**Last Updated:** January 28, 2026
**For Full Details:** See VHS_COMPREHENSIVE_RESEARCH.md
