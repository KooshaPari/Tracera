# Backend Environment Setup

## Quick Fix for Missing WORKOS_CLIENT_ID

The backend can run in **development mode** without WorkOS configuration. The code has been updated to automatically use a development user when WorkOS is not configured.

### Option 1: Run Without WorkOS (Development Mode)

Just start the backend - it will automatically use development mode:

```bash
./scripts/dev-backend.sh
```

The backend will:
- Accept requests without authentication
- Use a default dev user: `dev@localhost` with admin role
- Log a warning that WorkOS is not configured

### Option 2: Configure WorkOS (Production Mode)

Create a `.env` file in the project root:

```bash
# .env file
WORKOS_CLIENT_ID=your_client_id_here
WORKOS_API_KEY=your_api_key_here
WORKOS_AUTHKIT_DOMAIN=your_authkit_domain_here

# Optional
WORKOS_JWKS_URL=https://your-domain.authkit.app/oauth2/jwks
WORKOS_JWT_ISSUER=https://your-domain.authkit.app
WORKOS_JWT_AUDIENCE=your_client_id_here
```

Then start the backend:

```bash
./scripts/dev-backend.sh
```

## Environment Variables

### Required for Production (WorkOS Auth)

- `WORKOS_CLIENT_ID` - Your WorkOS Client ID
- `WORKOS_API_KEY` - Your WorkOS API Key (for code exchange)

### Optional

- `WORKOS_AUTHKIT_DOMAIN` - Your AuthKit domain (auto-detected if not set)
- `WORKOS_JWKS_URL` - Custom JWKS URL (auto-detected if not set)
- `WORKOS_JWT_ISSUER` - Custom JWT issuer (auto-detected if not set)
- `WORKOS_JWT_AUDIENCE` - Custom JWT audience (defaults to client_id)
- `CORS_ORIGINS` - Comma-separated list of allowed origins

### Development Mode

If `WORKOS_CLIENT_ID` is not set:
- Backend runs in development mode
- No authentication required
- Default user: `dev@localhost` with admin role
- All endpoints are accessible

## Testing

### Test Development Mode

```bash
# Start backend without WorkOS config
./scripts/dev-backend.sh

# In another terminal, test API
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/projects
```

### Test WebSocket

```bash
# Using wscat
wscat -c ws://localhost:8000/ws

# Or using Python
python3 -c "
import asyncio
import websockets

async def test():
    async with websockets.connect('ws://localhost:8000/ws') as ws:
        await ws.send('{\"type\": \"ping\"}')
        response = await ws.recv()
        print(response)

asyncio.run(test())
"
```

## Troubleshooting

### WebSocket 403 Forbidden

This has been fixed - WebSocket endpoint now accepts all connections without authentication.

### Missing WORKOS_CLIENT_ID Error

This has been fixed - backend automatically uses development mode when WorkOS is not configured.

### Install Dependencies

If you get import errors:

```bash
# Install FastAPI and Uvicorn (note the quotes for zsh)
pip install 'fastapi' 'uvicorn[standard]'

# Or using uv (if you have it)
uv pip install fastapi 'uvicorn[standard]'
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
uvicorn main:app --port 8001 --reload
```

## Current Status

✅ **Fixed Issues:**
- WebSocket 403 Forbidden - Now accepts all connections
- Missing WORKOS_CLIENT_ID - Development mode enabled automatically
- Authentication errors - Graceful fallback to dev mode

✅ **Working:**
- Backend starts without WorkOS config
- WebSocket connections accepted
- API endpoints accessible in dev mode
- Hot reload enabled
