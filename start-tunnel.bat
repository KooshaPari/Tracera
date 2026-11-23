@echo off
REM start-tunnel.bat — RETIRED shared-tunnel launcher.
REM
REM The live tracera-local Cloudflare Tunnel is shared infrastructure carrying
REM multiple Phenotype products. Starting another connector from Tracera's
REM intentionally partial route fragment can black-hole sibling routes.
REM Shared tunnel lifecycle belongs to the shared infrastructure owner/IaC.

echo [tunnel] ERROR: Tracera-local tunnel launch is retired. 1>&2
echo [tunnel] Use task tunnel-status for read-only status. 1>&2
echo [tunnel] Shared Cloudflare tunnel lifecycle is managed externally. 1>&2
exit /b 2
