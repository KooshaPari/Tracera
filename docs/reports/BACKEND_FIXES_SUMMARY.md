# Backend CORS and WebSocket Fixes

## Issues Fixed

### 1. CORS Configuration Error ✅
**Problem:** The CORS middleware was configured with `allow_origins=["*"]` and `allow_credentials=True`, which is incompatible. Browsers reject this combination for security reasons.

**Solution:** Changed to explicitly allow frontend origins:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (alternative port)
- `http://127.0.0.1:5173` and `http://127.0.0.1:3000` (IP variants)

**Configuration:** The CORS origins can now be configured via the `CORS_ORIGINS` environment variable:
```bash
export CORS_ORIGINS="http://localhost:5173,http://localhost:3000"
```

### 2. Missing WebSocket Endpoint ✅
**Problem:** Frontend was trying to connect to `/ws` but no WebSocket endpoint existed.

**Solution:** Added a WebSocket endpoint at `/ws` that:
- Accepts connections
- Handles ping/pong for keepalive
- Supports subscription/unsubscription to channels
- Echoes messages for testing
- Properly handles disconnections

## Files Modified

1. **`src/tracertm/api/main.py`**
   - Fixed CORS middleware configuration (lines ~366-373)
   - Added WebSocket endpoint at `/ws` (lines ~411-465)
   - Added necessary imports (`WebSocket`, `WebSocketDisconnect`)

## How to Test

### 1. Start the Backend Server

```bash
# From project root
cd src/tracertm/api
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Or if you have the package installed:
python -m tracertm.api.main
```

### 2. Verify CORS is Working

```bash
# Test CORS headers
curl -H "Origin: http://localhost:5173" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     http://localhost:4000/api/v1/health \
     -v
```

You should see `Access-Control-Allow-Origin: http://localhost:5173` in the response headers.

### 3. Test WebSocket Connection

```bash
# Using wscat (install with: npm install -g wscat)
wscat -c ws://localhost:4000/ws

# Or using Python
python -c "
import asyncio
import websockets

async def test():
    async with websockets.connect('ws://localhost:4000/ws') as ws:
        await ws.send('{\"type\": \"ping\"}')
        response = await ws.recv()
        print(response)

asyncio.run(test())
"
```

### 4. Test API Endpoints

```bash
# Health check
curl http://localhost:4000/health

# API health check
curl http://localhost:4000/api/v1/health

# Test with CORS (from browser console)
fetch('http://localhost:4000/api/v1/health')
  .then(r => r.json())
  .then(console.log)
```

## Environment Variables

You can configure CORS origins via environment variable:

```bash
# .env file or export
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://your-production-domain.com
```

## Next Steps

1. **Start the backend server** - The server should now accept requests from the frontend
2. **Verify WebSocket connection** - The frontend WebSocket manager should now connect successfully
3. **Test API calls** - API requests from the frontend should no longer have CORS errors
4. **Monitor logs** - Check backend logs for any connection issues

## Notes

- The WebSocket endpoint is basic and handles ping/pong and subscriptions
- For production, you may want to add authentication to the WebSocket endpoint
- Consider adding rate limiting for WebSocket connections
- The CORS configuration supports multiple origins via comma-separated list
