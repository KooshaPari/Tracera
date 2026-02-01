# VHS Code Examples & Integration Patterns

## Table of Contents

1. [Tape File Generation](#tape-file-generation)
2. [GitHub Actions Integration](#github-actions-integration)
3. [CI/CD Pipeline Examples](#cicd-pipeline-examples)
4. [Programmatic Usage](#programmatic-usage)
5. [Testing Patterns](#testing-patterns)
6. [Docker Integration](#docker-integration)

---

## Tape File Generation

### Python: Dynamic Tape Generator

```python
#!/usr/bin/env python3

import os
from pathlib import Path
from dataclasses import dataclass
from typing import List

@dataclass
class TapeCommand:
    """Represents a VHS tape command"""
    command: str

    def __str__(self):
        return self.command

class TapeBuilder:
    """Build VHS tapes programmatically"""

    def __init__(self, output: str):
        self.commands: List[TapeCommand] = []
        self.output = output

    def output_file(self, path: str, fmt: str = 'gif') -> 'TapeBuilder':
        """Set output file"""
        if not path.endswith(f'.{fmt}'):
            path = f"{path}.{fmt}"
        self.commands.append(TapeCommand(f"Output {path}"))
        return self

    def require(self, *programs: str) -> 'TapeBuilder':
        """Add program requirements"""
        for prog in programs:
            self.commands.append(TapeCommand(f"Require {prog}"))
        return self

    def set_shell(self, shell: str) -> 'TapeBuilder':
        """Set shell"""
        self.commands.append(TapeCommand(f'Set Shell "{shell}"'))
        return self

    def set_size(self, width: int, height: int) -> 'TapeBuilder':
        """Set terminal dimensions"""
        self.set_setting("Width", width)
        self.set_setting("Height", height)
        return self

    def set_font(self, family: str, size: int) -> 'TapeBuilder':
        """Set font"""
        self.commands.append(TapeCommand(f'Set FontFamily "{family}"'))
        self.set_setting("FontSize", size)
        return self

    def set_theme(self, theme: str) -> 'TapeBuilder':
        """Set color theme"""
        self.commands.append(TapeCommand(f'Set Theme "{theme}"'))
        return self

    def set_setting(self, name: str, value) -> 'TapeBuilder':
        """Set arbitrary setting"""
        if isinstance(value, str) and not value.replace('.', '').isdigit():
            value = f'"{value}"'
        self.commands.append(TapeCommand(f"Set {name} {value}"))
        return self

    def type(self, text: str, speed: str = None) -> 'TapeBuilder':
        """Type text"""
        speed_str = f"@{speed}" if speed else ""
        self.commands.append(TapeCommand(f'Type{speed_str} "{text}"'))
        return self

    def enter(self, count: int = 1) -> 'TapeBuilder':
        """Press Enter"""
        self.commands.append(TapeCommand(f"Enter {count}"))
        return self

    def sleep(self, duration: str) -> 'TapeBuilder':
        """Sleep (pause recording)"""
        self.commands.append(TapeCommand(f"Sleep {duration}"))
        return self

    def wait(self, pattern: str = None, scope: str = None, timeout: str = None) -> 'TapeBuilder':
        """Wait for condition"""
        cmd = "Wait"
        if scope:
            cmd += f"+{scope}"
        if timeout:
            cmd += f"@{timeout}"
        if pattern:
            cmd += f" /{pattern}/"
        self.commands.append(TapeCommand(cmd))
        return self

    def hide(self) -> 'TapeBuilder':
        """Stop capturing frames"""
        self.commands.append(TapeCommand("Hide"))
        return self

    def show(self) -> 'TapeBuilder':
        """Resume capturing frames"""
        self.commands.append(TapeCommand("Show"))
        return self

    def source(self, path: str) -> 'TapeBuilder':
        """Source another tape file"""
        self.commands.append(TapeCommand(f"Source {path}"))
        return self

    def env(self, key: str, value: str) -> 'TapeBuilder':
        """Set environment variable"""
        self.commands.append(TapeCommand(f'Env {key} "{value}"'))
        return self

    def arrow_key(self, direction: str, count: int = 1) -> 'TapeBuilder':
        """Press arrow key"""
        self.commands.append(TapeCommand(f"{direction.capitalize()} {count}"))
        return self

    def ctrl(self, key: str, modifiers: List[str] = None) -> 'TapeBuilder':
        """Send control sequence"""
        cmd = f"Ctrl+{key}"
        if modifiers:
            for mod in modifiers:
                cmd = f"{cmd.replace('Ctrl', '')}+{mod}" if cmd.startswith('Ctrl') else f"{mod}+{cmd}"
        self.commands.append(TapeCommand(cmd))
        return self

    def screenshot(self, path: str) -> 'TapeBuilder':
        """Take screenshot"""
        self.commands.append(TapeCommand(f"Screenshot {path}"))
        return self

    def build(self) -> str:
        """Generate tape file content"""
        return '\n'.join(str(cmd) for cmd in self.commands)

    def save(self, filepath: str) -> None:
        """Save to file"""
        Path(filepath).write_text(self.build())
        print(f"Saved to {filepath}")


# Example usage
if __name__ == "__main__":
    tape = (TapeBuilder("demo.gif")
            .output_file("demo.gif")
            .require("echo")
            .set_shell("bash")
            .set_font("JetBrains Mono", 24)
            .set_size(1024, 576)
            .set_theme("Catppuccin Frappe")
            .type("echo 'Hello from Python-generated tape!'")
            .enter()
            .sleep("1s")
            .type("date")
            .enter()
            .wait("2026")
            .sleep("2s")
            )

    tape.save("generated_demo.tape")
    print(tape.build())
```

### Bash: Template-Based Generation

```bash
#!/bin/bash

# Simple bash function to generate tape files
generate_demo_tape() {
    local output_file="$1"
    local command="$2"

    cat > "$output_file" << 'EOF'
Output demo.gif

Set FontSize 32
Set Width 1200
Set Height 600
Set Theme "Dracula"

Type "# Running demo..."
Enter
Sleep 500ms

Type "command_here"
Enter
Wait /done/
Sleep 1s
EOF

    # Replace placeholder
    sed -i "s|command_here|${command}|g" "$output_file"
    echo "Generated $output_file"
}

# Usage
generate_demo_tape "npm-demo.tape" "npm run build"
generate_demo_tape "cargo-demo.tape" "cargo build --release"
```

### Go: Programmatic Tape Builder

```go
package main

import (
    "fmt"
    "os"
    "strings"
)

type TapeBuilder struct {
    commands []string
}

func NewTapeBuilder() *TapeBuilder {
    return &TapeBuilder{commands: []string{}}
}

func (t *TapeBuilder) Output(path string) *TapeBuilder {
    t.commands = append(t.commands, fmt.Sprintf("Output %s", path))
    return t
}

func (t *TapeBuilder) SetShell(shell string) *TapeBuilder {
    t.commands = append(t.commands, fmt.Sprintf(`Set Shell "%s"`, shell))
    return t
}

func (t *TapeBuilder) SetSize(width, height int) *TapeBuilder {
    t.commands = append(t.commands, fmt.Sprintf("Set Width %d", width))
    t.commands = append(t.commands, fmt.Sprintf("Set Height %d", height))
    return t
}

func (t *TapeBuilder) SetFont(family string, size int) *TapeBuilder {
    t.commands = append(t.commands, fmt.Sprintf(`Set FontFamily "%s"`, family))
    t.commands = append(t.commands, fmt.Sprintf("Set FontSize %d", size))
    return t
}

func (t *TapeBuilder) SetTheme(theme string) *TapeBuilder {
    t.commands = append(t.commands, fmt.Sprintf(`Set Theme "%s"`, theme))
    return t
}

func (t *TapeBuilder) Type(text string) *TapeBuilder {
    t.commands = append(t.commands, fmt.Sprintf(`Type "%s"`, text))
    return t
}

func (t *TapeBuilder) Enter(count int) *TapeBuilder {
    t.commands = append(t.commands, fmt.Sprintf("Enter %d", count))
    return t
}

func (t *TapeBuilder) Sleep(duration string) *TapeBuilder {
    t.commands = append(t.commands, fmt.Sprintf("Sleep %s", duration))
    return t
}

func (t *TapeBuilder) Wait(pattern string, scope string) *TapeBuilder {
    cmd := "Wait"
    if scope != "" {
        cmd = fmt.Sprintf("Wait+%s", scope)
    }
    if pattern != "" {
        cmd = fmt.Sprintf("%s /%s/", cmd, pattern)
    }
    t.commands = append(t.commands, cmd)
    return t
}

func (t *TapeBuilder) Build() string {
    return strings.Join(t.commands, "\n")
}

func (t *TapeBuilder) Save(filename string) error {
    return os.WriteFile(filename, []byte(t.Build()), 0644)
}

func main() {
    tape := NewTapeBuilder().
        Output("demo.gif").
        SetShell("bash").
        SetFont("JetBrains Mono", 24).
        SetSize(1024, 576).
        SetTheme("Catppuccin Frappe").
        Type("echo 'Hello from Go!'").
        Enter(1).
        Sleep("1s").
        Type("date").
        Enter(1).
        Wait("2026", "").
        Sleep("2s")

    fmt.Println(tape.Build())

    // Save to file
    err := tape.Save("generated_demo.tape")
    if err != nil {
        fmt.Fprintf(os.Stderr, "Error: %v\n", err)
        os.Exit(1)
    }
    fmt.Println("Saved to generated_demo.tape")
}
```

---

## GitHub Actions Integration

### Basic Workflow

```yaml
# .github/workflows/vhs.yml

name: Generate Demo GIFs

on:
  push:
    paths:
      - '**.tape'
      - '.github/workflows/vhs.yml'
  pull_request:
  workflow_dispatch:

jobs:
  record:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Record GIFs with VHS
        uses: charmbracelet/vhs-action@v3
        with:
          path: demo.tape
          install-fonts: true

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: demo-gifs
          path: '*.gif'

      - name: Commit changes
        run: |
          git config user.name "VHS Bot"
          git config user.email "bot@charm.sh"
          git add demo.gif
          git diff --quiet && git diff --staged --quiet || \
            (git commit -m "chore: update demo.gif" && git push)
```

### Matrix Build (Multiple Demos)

```yaml
name: Generate Multiple Demos

on:
  push:
    paths:
      - 'demos/**.tape'

jobs:
  record:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        demo:
          - basic
          - advanced
          - cli-ui
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
          git commit -m "chore: update ${{ matrix.demo }}.gif" || true
          git push
```

### Comment GIF on PR

```yaml
name: VHS Comment PR

on:
  pull_request:

jobs:
  record-and-comment:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4

      - uses: charmbracelet/vhs-action@v3
        with:
          path: demo.tape
          install-fonts: true

      - name: Comment PR with GIF
        uses: actions/github-script@v7
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const fs = require('fs');
            const imageData = fs.readFileSync('demo.gif', { encoding: 'base64' });

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Demo Recording\n\n![Demo GIF](demo.gif)\n\n*Generated by VHS*`
            });
```

---

## CI/CD Pipeline Examples

### Pre-commit Hook (Local)

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check if any .tape files changed
changed_tapes=$(git diff --cached --name-only --diff-filter=ACM | grep '\.tape$')

if [ -z "$changed_tapes" ]; then
    exit 0
fi

echo "Detected changed .tape files. Regenerating GIFs..."

for tape in $changed_tapes; do
    output="${tape%.tape}.gif"
    echo "Rendering: $tape -> $output"
    vhs "$tape" || {
        echo "Error rendering $tape"
        exit 1
    }
    git add "$output"
done

echo "GIFs regenerated and staged."
```

### GitLab CI Pipeline

```yaml
# .gitlab-ci.yml

generate-demos:
  image: ghcr.io/charmbracelet/vhs:latest
  script:
    - for tape in demos/*.tape; do
        echo "Recording $tape..."
        vhs "$tape"
      done
  artifacts:
    paths:
      - demos/*.gif
    expire_in: 30 days
  only:
    changes:
      - demos/**.tape

pages:
  image: alpine:latest
  stage: deploy
  script:
    - mkdir -p public
    - cp demos/*.gif public/
    - |
      cat > public/index.html << 'EOF'
      <!DOCTYPE html>
      <html>
      <head><title>Demos</title></head>
      <body>
        <h1>Terminal Demos</h1>
        <img src="demo.gif" alt="Demo">
      </body>
      </html>
      EOF
  artifacts:
    paths:
      - public
  only:
    - main
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Generate Demos') {
            steps {
                script {
                    sh '''
                        docker run --rm -v $WORKSPACE:/vhs \
                            ghcr.io/charmbracelet/vhs:latest \
                            demo.tape
                    '''
                }
            }
        }

        stage('Archive') {
            steps {
                archiveArtifacts artifacts: '*.gif',
                                 allowEmptyArchive: false
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
```

---

## Programmatic Usage

### Running VHS from CLI (Bash)

```bash
#!/bin/bash

# Generate and run tape
generate_and_record() {
    local output="$1"

    # Create tape
    cat > temp.tape << EOF
Output ${output}.gif

Set FontSize 28
Set Width 960
Set Height 540

Type "echo 'Automated recording'"
Enter
Sleep 1s
EOF

    # Run VHS
    vhs temp.tape

    # Cleanup
    rm temp.tape

    echo "Recording saved to: ${output}.gif"
}

generate_and_record "my-demo"
```

### Docker Integration (Multi-Step)

```bash
#!/bin/bash

# Build, run test, record demo, all in Docker

docker run \
    --rm \
    -v $PWD:/workspace \
    -w /workspace \
    ghcr.io/charmbracelet/vhs:latest \
    bash -c '
        # Setup
        echo "=== Building ==="
        npm install
        npm run build

        # Record demo
        echo "=== Recording Demo ==="
        vhs demo.tape

        # Verify
        echo "=== Verifying Output ==="
        ls -lh demo.gif
    '
```

### SSH Server Remote Recording

```bash
#!/bin/bash

# Start VHS server in Docker
docker run -d \
    --name vhs-server \
    -p 1976:1976 \
    -e VHS_HOST=0.0.0.0 \
    ghcr.io/charmbracelet/vhs:latest \
    serve

# Wait for server
sleep 2

# Record via SSH
ssh -p 1976 localhost < demo.tape > demo.gif

# Cleanup
docker stop vhs-server
docker rm vhs-server
```

---

## Testing Patterns

### Golden File Testing

```bash
#!/bin/bash
# test-cli-output.sh

GOLDEN_FILE="golden.txt"
TAPE_FILE="cli-test.tape"

# Generate golden file (once)
if [ ! -f "$GOLDEN_FILE" ]; then
    echo "Generating golden file..."
    vhs "$TAPE_FILE" > "$GOLDEN_FILE"
fi

# Run test
echo "Running test..."
actual=$(vhs "$TAPE_FILE")
expected=$(cat "$GOLDEN_FILE")

if [ "$actual" = "$expected" ]; then
    echo "PASS: CLI output matches golden file"
    exit 0
else
    echo "FAIL: CLI output differs"
    diff <(echo "$expected") <(echo "$actual")
    exit 1
fi
```

### Integration Test Suite

```bash
#!/bin/bash
# test-integration.sh

TESTS=(
    "test-basic.tape"
    "test-error-handling.tape"
    "test-build.tape"
)

passed=0
failed=0

for test in "${TESTS[@]}"; do
    echo "Running $test..."

    if vhs "$test" > /tmp/output.txt 2>&1; then
        echo "  ✓ PASS"
        ((passed++))
    else
        echo "  ✗ FAIL"
        ((failed++))
        cat /tmp/output.txt
    fi
done

echo "---"
echo "Passed: $passed"
echo "Failed: $failed"

[ $failed -eq 0 ] || exit 1
```

### Regex Validation Test

```bash
#!/bin/bash
# test-output-validation.sh

# Test that output contains expected patterns

test_output_contains() {
    local tape="$1"
    local pattern="$2"

    echo "Testing: $pattern in $tape"

    if vhs "$tape" | grep -q "$pattern"; then
        echo "  ✓ Pattern found"
        return 0
    else
        echo "  ✗ Pattern NOT found"
        return 1
    fi
}

# Run tests
test_output_contains "test-help.tape" "^Usage:"
test_output_contains "test-version.tape" "v[0-9]+\.[0-9]+\.[0-9]+"
test_output_contains "test-error.tape" "Error:"
```

---

## Docker Integration

### Multi-Stage Dockerfile

```dockerfile
# Build demo images
FROM ghcr.io/charmbracelet/vhs:latest as vhs-builder

WORKDIR /demos

# Copy tape files
COPY demos/*.tape ./

# Generate GIFs
RUN for tape in *.tape; do \
        vhs "$tape"; \
    done

# Final stage - serve demos
FROM caddy:latest

COPY --from=vhs-builder /demos/*.gif /srv/

COPY Caddyfile /etc/caddy/

EXPOSE 80
```

### Docker Compose for VHS Server

```yaml
# docker-compose.yml

version: '3.8'

services:
  vhs-server:
    image: ghcr.io/charmbracelet/vhs:latest
    command: serve
    ports:
      - "1976:1976"
    environment:
      VHS_HOST: "0.0.0.0"
      VHS_PORT: "1976"
    volumes:
      - ./keys:/vhs/keys:ro
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./demos/outputs:/usr/share/nginx/html:ro
    depends_on:
      - vhs-server
```

---

## Advanced: Tape with External Data

### Template Tape with Environment Variables

```bash
#!/bin/bash

# Generate tape with injected values
VERSION=$(git describe --tags --always)
PROJECT_NAME=$(basename $PWD)

cat > demo.tape << EOF
Output demo.gif

Set FontSize 28
Set Width 1024
Set Height 576

Type "echo 'Project: ${PROJECT_NAME}'"
Enter
Type "echo 'Version: ${VERSION}'"
Enter
Sleep 1s
EOF

vhs demo.tape
```

### Dynamic Tape Based on Git History

```bash
#!/bin/bash

# Generate demo showing recent commits

cat > git-demo.tape << 'EOF'
Output git-demo.gif

Set FontSize 24
Set Width 960
Set Height 540

Type "git log --oneline -5"
Enter
Wait /commit/
Sleep 2s

Type "git status"
Enter
Wait /working tree/
Sleep 1s
EOF

vhs git-demo.tape
```

---

## Summary: Common Integration Patterns

```
┌─────────────────────────────────────┐
│   Local Development                 │
├─────────────────────────────────────┤
│ • Edit .tape file                   │
│ • Run: vhs demo.tape               │
│ • Test GIF output                   │
│ • Commit .tape and .gif files      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│   CI/CD Pipeline                    │
├─────────────────────────────────────┤
│ • Trigger on .tape changes          │
│ • Run: vhs ${tape}                  │
│ • Artifacts: .gif files             │
│ • Commit changes (auto-commit)       │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│   Programmatic Generation           │
├─────────────────────────────────────┤
│ • Generate tape from template       │
│ • Inject environment variables      │
│ • Run vhs with generated tape       │
│ • Store output                      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│   Testing & Validation              │
├─────────────────────────────────────┤
│ • Record expected output (golden)   │
│ • Test actual output against golden │
│ • Validate regex patterns           │
│ • Fail on mismatch                  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│   Remote/Distributed                │
├─────────────────────────────────────┤
│ • Start VHS SSH server              │
│ • SSH user@host < tape > output.gif │
│ • Docker container for deployment   │
└─────────────────────────────────────┘
```

---

**Last Updated:** January 28, 2026
**Associated Document:** VHS_COMPREHENSIVE_RESEARCH.md
