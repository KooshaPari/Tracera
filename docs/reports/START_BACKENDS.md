# 🚀 Start Backends - Simple Instructions

**Your data is ready! Just need to start the backend services.**

---

## Option 1: Quick Start (Recommended)

### Start Go Backend

```bash
# Terminal 1
cd backend
go run main.go
```

**Expected output:**
```
🚀 TraceRTM HTTP API starting on :8080
🔐 CLIProxy service starting on 127.0.0.1:8765
```

### Start Python Backend

```bash
# Terminal 2
cd src
uvicorn tracertm.api.main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

---

## Option 2: Background Start

```bash
# Start Go backend in background
cd backend && go run main.go > /tmp/go-backend.log 2>&1 &

# Start Python backend in background
cd src && uvicorn tracertm.api.main:app --port 8000 > /tmp/python-backend.log 2>&1 &

# Check they're running
lsof -i :8080,8000 | grep LISTEN
```

---

## Verify Backends

```bash
# Test Go backend
curl http://localhost:8080/health

# Test Python backend
curl http://localhost:4000/health

# Test CLIProxy
curl http://localhost:8765/health
```

**All should return JSON responses with "status": "healthy"**

---

## Then: Clear Browser Auth

**In browser console** (Cmd+Option+I):

```javascript
localStorage.clear(); sessionStorage.clear(); location.reload();
```

Sign in → View Graph → **See 5,686 nodes!** 🎉

---

## Troubleshooting

### Port Already in Use

```bash
# Find what's using the port
lsof -i :8080
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Database Connection Error

```bash
# Check PostgreSQL is running
psql postgresql://tracertm:tracertm_password@localhost:5432/tracertm -c "SELECT 1;"

# If not running, start it
brew services start postgresql@17
```

---

**Status:** Ready to start! Run the commands above. 🚀
