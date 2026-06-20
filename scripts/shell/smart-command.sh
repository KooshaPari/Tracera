#!/bin/bash

# smart-command.sh: A wrapper to debounce high-impact commands and ensure service health.
# Usage: ./smart-command.sh <command_key> <real_command> [required_services...]

COMMAND_KEY=$1
shift
REAL_COMMAND=$1
shift
REQUIRED_SERVICES=$@

LOCK_FILE=".process-compose/locks/${COMMAND_KEY}.lock"
mkdir -p .process-compose/locks

# 1. Check if another instance is already running
if [ -f "$LOCK_FILE" ]; then
    # Check if process still exists
    PID=$(cat "$LOCK_FILE")
    if ps -p $PID > /dev/null; then
        echo "⚠️  Command '${COMMAND_KEY}' is already running (PID: $PID). Waiting or skipping..."
        # Optional: wait or just exit. For agents, skipping/waiting is better.
        # For simplicity, we'll wait up to 30s.
        COUNTER=0
        while ps -p $PID > /dev/null && [ $COUNTER -lt 30 ]; do
            sleep 1
            ((COUNTER++))
        done
        if ps -p $PID > /dev/null; then
            echo "❌ Timeout waiting for '${COMMAND_KEY}'. Proceeding with caution or use 'task clean:locks'."
        fi
    fi
fi

# 2. Record PID
echo $$ > "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

# 3. Check Required Services (via process-compose CLI if available)
if [ ! -z "$REQUIRED_SERVICES" ]; then
    echo "🔍 Checking health of services: $REQUIRED_SERVICES"
    for SVC in $REQUIRED_SERVICES; do
        # Use process-compose process list --json or similar to check health
        # For now, a simple check if it exists in the list
        if ! process-compose process list | grep -q "$SVC"; then
            echo "❌ Service '$SVC' is not running in process-compose. Use 'task dev' first."
            exit 1
        fi
    done
fi

# 4. Execute
echo "🚀 Executing: $REAL_COMMAND"
eval "$REAL_COMMAND"
