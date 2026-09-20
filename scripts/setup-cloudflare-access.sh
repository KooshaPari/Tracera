#!/usr/bin/env bash
# setup-cloudflare-access.sh — idempotent Cloudflare Access unblock for tracera.pheno.studio
#
# Creates (or reuses) a CI service token and attaches a Service Auth policy to the
# Access application that protects tracera.pheno.studio.  After this script runs,
# automated clients can reach the hostname with:
#   CF-Access-Client-Id / CF-Access-Client-Secret
#
# Requires:
#   CLOUDFLARE_API_TOKEN  — Account token with Zero Trust: Edit
#   CLOUDFLARE_ACCOUNT_ID — Cloudflare account id
#
# Optional:
#   ACCESS_HOSTNAME       — default tracera.pheno.studio
#   SERVICE_TOKEN_NAME    — default tracera-ci-smoke
#   OPERATOR_EMAIL        — if set, adds an Allow policy for this email
#   PUBLIC_BYPASS         — if "1", add a Bypass/everyone policy (public, no login)
#   PUBLIC_BYPASS_NAME    — policy name for PUBLIC_BYPASS (default: Public Bypass)
#
# Usage (from repo root):
#   export CLOUDFLARE_API_TOKEN=...
#   export CLOUDFLARE_ACCOUNT_ID=...
#   bash scripts/setup-cloudflare-access.sh

set -euo pipefail

CF_API="${CF_API_BASE:-https://api.cloudflare.com/client/v4}"
HOSTNAME="${ACCESS_HOSTNAME:-tracera.pheno.studio}"
TOKEN_NAME="${SERVICE_TOKEN_NAME:-tracera-ci-smoke}"
PUBLIC_BYPASS="${PUBLIC_BYPASS:-0}"
PUBLIC_BYPASS_NAME="${PUBLIC_BYPASS_NAME:-Public Bypass}"

if [ -z "${CLOUDFLARE_API_TOKEN:-}" ] || [ -z "${CLOUDFLARE_ACCOUNT_ID:-}" ]; then
  echo "error: set CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID" >&2
  exit 1
fi

auth_header() {
  printf 'Authorization: Bearer %s' "$CLOUDFLARE_API_TOKEN"
}

cf_get() {
  curl -fsS -H "$(auth_header)" -H 'Content-Type: application/json' \
    "${CF_API}$1"
}

cf_post() {
  curl -fsS -X POST -H "$(auth_header)" -H 'Content-Type: application/json' \
    --data "$2" "${CF_API}$1"
}

echo "[access] verifying API token"
verify=$(cf_get '/user/tokens/verify' || true)
if ! printf '%s' "$verify" | grep -q '"success":true'; then
  echo "error: CLOUDFLARE_API_TOKEN is invalid or lacks API access" >&2
  exit 1
fi

echo "[access] locating Access application for ${HOSTNAME}"
apps_json=$(cf_get "/accounts/${CLOUDFLARE_ACCOUNT_ID}/access/apps?per_page=100")
app_id=$(printf '%s' "$apps_json" | python3 -c '
import json, sys
hostname = sys.argv[1]
data = json.load(sys.stdin)
for app in data.get("result", []):
    domain = (app.get("domain") or "").rstrip(".")
    if domain == hostname:
        print(app.get("id", ""))
        break
' "$HOSTNAME")

if [ -z "$app_id" ]; then
  echo "error: no Access application found for ${HOSTNAME}" >&2
  echo "Create a self-hosted Access app in Zero Trust -> Access -> Applications first." >&2
  exit 1
fi
echo "[access] found app id=${app_id}"

if [ "$PUBLIC_BYPASS" = "1" ]; then
  echo "[access] ensuring public Bypass policy (${PUBLIC_BYPASS_NAME})"
  policies_json=$(cf_get "/accounts/${CLOUDFLARE_ACCOUNT_ID}/access/apps/${app_id}/policies?per_page=100")
  has_bypass=$(printf '%s' "$policies_json" | python3 -c '
import json, sys
name = sys.argv[1]
data = json.load(sys.stdin)
for policy in data.get("result", []):
    if policy.get("decision") != "bypass":
        continue
    if policy.get("name") == name:
        print("yes")
        raise SystemExit
    for inc in policy.get("include", []):
        if "everyone" in inc:
            print("yes")
            raise SystemExit
' "$PUBLIC_BYPASS_NAME")
  if [ "$has_bypass" != "yes" ]; then
    cf_post "/accounts/${CLOUDFLARE_ACCOUNT_ID}/access/apps/${app_id}/policies" \
      "$(python3 - <<'PY' "$PUBLIC_BYPASS_NAME"
import json, sys
print(json.dumps({
  "name": sys.argv[1],
  "decision": "bypass",
  "include": [{"everyone": {}}],
  "precedence": 1,
}))
PY
)" >/dev/null
    echo "[access] attached public Bypass policy"
  else
    echo "[access] public Bypass policy already present"
  fi
  echo
  echo "=== Cloudflare Access public bypass complete ==="
  echo "Hostname: ${HOSTNAME}"
  echo "Access app: ${app_id}"
  echo "Smoke with:"
  echo "  curl -sS -o /dev/null -w '%{http_code}\n' -L --max-time 30 https://${HOSTNAME}/"
  exit 0
fi

echo "[access] ensuring service token '${TOKEN_NAME}'"
tokens_json=$(cf_get "/accounts/${CLOUDFLARE_ACCOUNT_ID}/access/service_tokens?per_page=100")
existing_token_id=$(printf '%s' "$tokens_json" | python3 -c '
import json, sys
name = sys.argv[1]
data = json.load(sys.stdin)
for token in data.get("result", []):
    if token.get("name") == name:
        print(token.get("id", ""))
        break
' "$TOKEN_NAME")

if [ -n "$existing_token_id" ]; then
  echo "[access] reusing service token id=${existing_token_id}"
  token_id="$existing_token_id"
  client_id=""
  client_secret=""
else
  created=$(cf_post "/accounts/${CLOUDFLARE_ACCOUNT_ID}/access/service_tokens" \
    "$(python3 - <<'PY' "$TOKEN_NAME"
import json, sys
print(json.dumps({"name": sys.argv[1]}))
PY
)")
  token_id=$(printf '%s' "$created" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["id"])')
  client_id=$(printf '%s' "$created" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["client_id"])')
  client_secret=$(printf '%s' "$created" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["client_secret"])')
  echo "[access] created service token id=${token_id}"
fi

echo "[access] ensuring Service Auth policy on app ${app_id}"
policies_json=$(cf_get "/accounts/${CLOUDFLARE_ACCOUNT_ID}/access/apps/${app_id}/policies?per_page=100")
has_service_policy=$(printf '%s' "$policies_json" | python3 -c '
import json, sys
token_id = sys.argv[1]
data = json.load(sys.stdin)
for policy in data.get("result", []):
    if policy.get("decision") != "non_identity":
        continue
    for inc in policy.get("include", []):
        st = inc.get("service_token") or {}
        if st.get("token_id") == token_id:
            print("yes")
            raise SystemExit
' "$token_id")

if [ "$has_service_policy" != "yes" ]; then
  cf_post "/accounts/${CLOUDFLARE_ACCOUNT_ID}/access/apps/${app_id}/policies" \
    "$(python3 - <<'PY' "$token_id" "$TOKEN_NAME"
import json, sys
token_id, name = sys.argv[1], sys.argv[2]
print(json.dumps({
  "name": f"Service Auth ({name})",
  "decision": "non_identity",
  "include": [{"service_token": {"token_id": token_id}}],
  "precedence": 1,
}))
PY
)" >/dev/null
  echo "[access] attached Service Auth policy"
else
  echo "[access] Service Auth policy already present"
fi

if [ -n "${OPERATOR_EMAIL:-}" ]; then
  has_email_policy=$(printf '%s' "$policies_json" | python3 -c '
import json, sys
email = sys.argv[1]
data = json.load(sys.stdin)
for policy in data.get("result", []):
    if policy.get("decision") != "allow":
        continue
    for inc in policy.get("include", []):
        em = inc.get("email") or {}
        if em.get("email") == email:
            print("yes")
            raise SystemExit
' "$OPERATOR_EMAIL")
  if [ "$has_email_policy" != "yes" ]; then
    cf_post "/accounts/${CLOUDFLARE_ACCOUNT_ID}/access/apps/${app_id}/policies" \
      "$(python3 - <<'PY' "$OPERATOR_EMAIL"
import json, sys
print(json.dumps({
  "name": f"Allow {sys.argv[1]}",
  "decision": "allow",
  "include": [{"email": {"email": sys.argv[1]}}],
  "precedence": 2,
}))
PY
)" >/dev/null
    echo "[access] added Allow policy for ${OPERATOR_EMAIL}"
  else
    echo "[access] Allow policy for ${OPERATOR_EMAIL} already present"
  fi
fi

echo
echo "=== Cloudflare Access unblock complete ==="
echo "Hostname: ${HOSTNAME}"
echo "Access app: ${app_id}"
echo "Service token: ${TOKEN_NAME} (${token_id})"
if [ -n "$client_id" ]; then
  echo
  echo "Store these as GitHub repo secrets (shown once for a new token):"
  echo "  gh secret set CF_ACCESS_CLIENT_ID --repo <owner>/Tracera --body '${client_id}'"
  echo "  gh secret set CF_ACCESS_CLIENT_SECRET --repo <owner>/Tracera --body '${client_secret}'"
else
  echo
  echo "Reused an existing service token; client credentials were not rotated."
  echo "If CI secrets are missing, create a new token in Zero Trust or delete '${TOKEN_NAME}' and re-run."
fi
echo
echo "Smoke with:"
echo "  curl -H 'CF-Access-Client-Id: <id>' -H 'CF-Access-Client-Secret: <secret>' https://${HOSTNAME}/"
