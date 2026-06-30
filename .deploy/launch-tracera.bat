# Tracera — Windows launcher
# Starts process-compose stack on E: drive, opens dashboard
@echo off
setlocal
set TRACERA_HOME=E:\phase-finish-stack\Tracera
cd /d "%TRACERA_HOME%"

echo === Tracera launcher ===
echo Starting process-compose stack...

REM Try process-compose if available
where process-compose >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    process-compose up -f process-compose.yml
    goto :open
)

REM Fallback: cargo run the server
where cargo >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo process-compose not found, falling back to cargo run
    start "tracera-server" cmd /k "cd /d %TRACERA_HOME%\crates\tracera-server && cargo run --release"
    timeout /t 5 >nul
    goto :open
)

echo ERROR: neither process-compose nor cargo found on PATH
pause
exit /b 1

:open
timeout /t 3 >nul
start "" http://localhost:8080
echo Stack started. Press any key to detach.
pause >nul
endlocal
