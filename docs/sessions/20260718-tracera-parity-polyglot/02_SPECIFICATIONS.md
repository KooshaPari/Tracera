# Specifications

## Frontend

- Keep endpoint paths centralized in `traceraClient.js`.
- Preserve graceful handling of unavailable or malformed responses.
- Route navigation must use the `trace` page identifier consistently.

## Go sidecar

- `TRACERA_SIDE_CAR_ENABLED` defaults to `false`.
- Configuration is environment-driven and validated at startup.
- Disabled mode exits cleanly; enabled mode emits periodic heartbeat logs.
- No write path, auth bypass, or compatibility shim is permitted in this slice.
