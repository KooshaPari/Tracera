# Backend Hot Reload Guide

The TraceRTM backend server supports hot reload for development, automatically restarting when you make changes to Python files.

## Quick Start

### Option 1: Using the Script (Recommended)

```bash
# From project root
./scripts/dev-backend.sh
```

### Option 2: Using Make

```bash
# From project root
make dev-backend
```

### Option 3: Direct Python Command

```bash
# From project root
cd src/tracertm/api
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Option 4: Running main.py Directly

```bash
# From project root
python3 src/tracertm/api/main.py
```

The `main.py` file already has `reload=True` configured, so this will automatically enable hot reload.

## How Hot Reload Works

Uvicorn watches for file changes in:
- The current directory and subdirectories
- Python files (`.py`)
- When a file changes, it automatically restarts the server

## Configuration

### CORS Origins

Set the `CORS_ORIGINS` environment variable to customize allowed origins:

```bash
export CORS_ORIGINS="http://localhost:5173,http://localhost:3000,https://your-domain.com"
```

Or add it to your `.env` file:
```
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Port

Default port is `8000`. Change it by modifying:
- The script: `scripts/dev-backend.sh`
- The Makefile: `make dev-backend PORT=8080`
- Direct command: `--port 8080`

### Reload Directories

By default, uvicorn watches the entire project. To limit watching to specific directories:

```bash
uvicorn main:app --reload --reload-dir ./src --reload-dir ./tests
```

## What Gets Reloaded

✅ **Automatically reloaded:**
- Python files (`.py`)
- Configuration files (if imported)
- Environment variables (on restart)

❌ **NOT reloaded (requires manual restart):**
- Database connections (reconnect on restart)
- External service connections
- Cached data

## Troubleshooting

### Hot Reload Not Working

1. **Check file permissions**: Make sure Python can read the files
2. **Check file watcher limits**: On Linux, you might need to increase `fs.inotify.max_user_watches`
   ```bash
   echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
   sudo sysctl -p
   ```
3. **Check for syntax errors**: Syntax errors prevent reload
4. **Check logs**: Look for error messages in the console

### Port Already in Use

```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn main:app --port 8001 --reload
```

### Import Errors After Reload

Sometimes imports can get cached. Try:
1. Restart the server manually
2. Clear Python cache: `find . -type d -name __pycache__ -exec rm -r {} +`
3. Use `--reload-exclude` to exclude problematic directories

## Advanced Options

### Watch Specific Files Only

```bash
uvicorn main:app --reload --reload-include "*.py" --reload-exclude "tests/*"
```

### Custom Reload Delay

```bash
# Wait 2 seconds after file change before reloading
uvicorn main:app --reload --reload-delay 2
```

### Development vs Production

Hot reload is **only for development**. For production:

```bash
# Production (no reload)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Integration with Frontend

The backend hot reload works independently of the frontend:

- **Frontend** (Vite): `http://localhost:5173` - Hot reloads React/TypeScript
- **Backend** (FastAPI): `http://localhost:8000` - Hot reloads Python

Both can run simultaneously and reload independently.

## Example Workflow

1. Start backend: `./scripts/dev-backend.sh`
2. Start frontend: `cd frontend/apps/web && bun run dev`
3. Make changes to Python files → Backend auto-reloads
4. Make changes to React files → Frontend auto-reloads
5. Both work together seamlessly!

## Monitoring

Watch the console output for:
- `INFO:     Uvicorn running on http://0.0.0.0:8000`
- `INFO:     Application startup complete.`
- `INFO:     Detected file change in 'path/to/file.py'. Reloading...`
- `INFO:     Application startup complete.` (after reload)
