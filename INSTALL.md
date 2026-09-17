# Tracera - Agent-native Requirements Traceability

Multi-view requirements traceability and project management system for AI agents.

## Quick Install

### One-liner (Windows PowerShell)
```powershell
irm https://raw.githubusercontent.com/<REDACTED>/Tracera/main/install.ps1 | iex
```

### Chocolatey
```powershell
choco install tracera
```

### WinGet
```powershell
winget install <REDACTED>.Tracera
```

### From Source
```bash
git clone https://github.com/<REDACTED>/Tracera
cd Tracera
cargo build --release -p tracera-server -p tracera-cli
./target/release/tracera-server --port 8080
```

## Usage

```bash
tracera-server --port 8080   # Start the API server
tracera --help               # CLI
tracera up                   # Spin up dev environment
tracera status               # Check status
```

## Uninstall

```powershell
irm https://raw.githubusercontent.com/<REDACTED>/Tracera/main/uninstall.ps1 | iex
```

## Links

- [GitHub](https://github.com/<REDACTED>/Tracera)
- [Releases](https://github.com/<REDACTED>/Tracera/releases)
- [Documentation](https://github.com/<REDACTED>/Tracera/blob/main/README.md)

## License

MIT