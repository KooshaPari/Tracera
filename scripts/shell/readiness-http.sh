#!/usr/bin/env bash
# HTTP readiness probe with detailed failure message.
# Usage: readiness-http.sh SERVICE_NAME HOST PORT PATH [EXPECTED_STATUS]
# On failure prints to stderr: service name, URL, received status, expected status.
# Exit 0 if HTTP status equals EXPECTED_STATUS (default 200), else 1.

set -e

SERVICE_NAME="${1:?missing SERVICE_NAME}"
HOST="${2:?missing HOST}"
PORT="${3:?missing PORT}"
PATH_REQ="${4:?missing PATH}"
EXPECTED="${5:-200}"

URL="http://${HOST}:${PORT}${PATH_REQ}"
BODY_FILE=$(mktemp)
trap 'rm -f "$BODY_FILE"' EXIT

HTTP_CODE=$(curl -s -o "$BODY_FILE" -w "%{http_code}" --connect-timeout 5 --max-time 10 "$URL" 2>/dev/null || echo "000")

if [[ "$HTTP_CODE" != "$EXPECTED" ]]; then
	echo "Readiness failed: $SERVICE_NAME GET $URL returned $HTTP_CODE (expected $EXPECTED)" >&2
	if [[ -s "$BODY_FILE" ]]; then
		HEAD=$(head -c 200 "$BODY_FILE" | tr -d '\0')
		if [[ -n "$HEAD" ]]; then
			echo "Response body (first 200 bytes): $HEAD" >&2
		fi
	fi
	exit 1
fi
exit 0
