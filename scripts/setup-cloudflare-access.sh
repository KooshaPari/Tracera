#!/usr/bin/env bash
# setup-cloudflare-access.sh — idempotent Cloudflare Access policy setup.
#
# Reuses an existing CI service token and attaches a Service Auth policy to the
# Access application protecting ACCESS_HOSTNAME.
#
# IMPORTANT: a newly-created Cloudflare service-token secret is returned only
# once. This script never prints that secret. Creation is allowed only when the
# caller supplies TOKEN_OUTPUT_FILE; credentials are written there with mode
# 0600 for an explicit secure handoff. CI should NOT set TOKEN_OUTPUT_FILE and
# therefore fails closed when the named token does not already exist.
#
# Requires:
#   CLOUDFLARE_API_TOKEN  — account token with Zero Trust edit permissions
#   CLOUDFLARE_ACCOUNT_ID — Cloudflare account id
#
# Optional:
#   ACCESS_HOSTNAME       — default t.tracera.pheno.studio
#   SERVICE_TOKEN_NAME    — default tracera-ci-smoke
#   TOKEN_OUTPUT_FILE     — secure file for one-time new-token credentials
#   OPERATOR_EMAIL        — add an Allow policy for this email
#   PUBLIC_BYPASS         — if "1", add a Bypass/everyone policy
#   PUBLIC_BYPASS_NAME    — bypass policy name
#
# Local creation example:
#   umask 077
#   TOKEN_OUTPUT_FILE=/secure/path/tracera-ci-smoke.env \
#     bash scripts/setup-cloudflare-access.sh
#
# The output file contains CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET.
# Move them into the intended secret store, then securely delete the file.

set -euo pipefail

CF_API="${CF_API_BASE:-https://api.cloudflare.com/client/v4}"
HOSTNAME="${ACCESS_HOSTNAME:-t.tracera.pheno.studio}"
TOKEN_NAME="${SERVICE_TOKEN_NAME:-tracera-ci-smoke}"
TOKEN_OUTPUT_FILE="${TOKEN_OUTPUT_FILE:-}"
PUBLIC_BYPASS="${PUBLIC_BYPASS:-0}"
PUBLIC_BYPASS_NAME="${PUBLIC_BYPASS_NAME:-Public Bypass}"

if [[ -z "${CLOUDFLARE_API_TOKEN:-}" || -z "${CLOUDFLARE_ACCOUNT_ID:-}" ]]; then
  echo "error: set CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID" >&2
  exit 1
fi

auth_header() {
  printf 'Authorization: Bearer %s' "$CLOUDFLARE_API_TOKEN"
}

cf_get() {
  local path="$1"
  curl -fsS -H "$(auth_header)" -H 'Content-Type: application/json' "${CF_API}${path}"
}

cf_post() {
  local path="$1"
  local body="$2"
  curl -fsS -X POST -H "$(auth_header)" -H 'Content-Type: application/json' --data "$body" "${CF_API}${path}"
}

cf_delete() {
  local path="$1"
  curl -fsS -X DELETE -H "$(auth_header)" -H 'Content-Type: application/json' "${CF_API}${path}"
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
    if (app.get("domain") or "").rstrip(".") == hostname:
        print(app.get("id", ""))
        break
' "$HOSTNAME")

if [[ -z "$app_id" ]]; then
  echo "error: no Access application found for ${HOSTNAME}" >&2
  exit 1
fi
echo "[access] found app id=${app_id}"

if [[ "$PUBLIC_BYPASS" == "1" ]]; then
  echo "[access] ensuring public Bypass policy (${PUBLIC_BYPASS_NAME})"
  policies_json=$(cf_get "/accounts/${CLOUDFLARE_ACCOUNT_ID}/access/apps/${app_id}/policies?per_page=100")
  has_bypass=$(printf '%s' "$policies_json" | python3 -c '
import json, sys
name = sys.argv[1]
for policy in json.load(sys.stdin).get("result", []):
    if policy.get("decision") != "bypass":
        continue
    if policy.get("name") == name or any("everyone" in x for x in policy.get("include", [])):
        print("yes")
        break
' "$PUBLIC_BYPASS_NAME")
  if [[ "$has_bypass" != "yes" ]]; then
    cf_post "/accounts/${CLOUDFLARE_ACCOUNT_ID}/access/apps/${app_id}/policies"       "$(python3 -c 'import json,sys; print(json.dumps({"name":sys.argv[1],"decision":"bypass","include":[{"everyone":{}}],"precedence":1}))' "$PUBLIC_BYPASS_NAME")" >/dev/null
    echo "[access] attached public Bypass policy"
  else
    echo "[access] public Bypass policy already present"
  fi
  exit 0
fi

echo "[access] locating service token '${TOKEN_NAME}'"
tokens_json=$(cf_get "/accounts/${CLOUDFLARE_ACCOUNT_ID}/access/service_tokens?per_page=100")
token_id=$(printf '%s' "$tokens_json" | python3 -c '
import json, sys
name = sys.argv[1]
for token in json.load(sys.stdin).get("result", []):
    if token.get("name") == name:
        print(token.get("id", ""))
        break
' "$TOKEN_NAME")

if [[ -z "$token_id" ]]; then
  if [[ -z "$TOKEN_OUTPUT_FILE" ]]; then
    echo "error: service token '${TOKEN_NAME}' does not exist" >&2
    echo "error: refusing to create it because TOKEN_OUTPUT_FILE is unset." >&2
    echo "error: create it in an operator-controlled context with a secure output file," >&2
    echo "error: then store CF_ACCESS_CLIENT_ID/CF_ACCESS_CLIENT_SECRET in the intended secret store." >&2
    exit 2
  fi

  # Cloudflare returns the client secret only once. Prove the destination is
  # usable BEFORE creating the token so a local path error cannot orphan an
  # unrecoverable credential.
  if [[ -e "$TOKEN_OUTPUT_FILE" || -L "$TOKEN_OUTPUT_FILE" ]]; then
    echo "error: TOKEN_OUTPUT_FILE already exists or is a symlink; refusing: $TOKEN_OUTPUT_FILE" >&2
    exit 2
  fi
  output_parent=$(dirname -- "$TOKEN_OUTPUT_FILE")
  if [[ ! -d "$output_parent" || ! -w "$output_parent" ]]; then
    echo "error: TOKEN_OUTPUT_FILE parent is not an existing writable directory: $output_parent" >&2
    exit 2
  fi

  # The one-time Cloudflare secret must land in a directory private to this
  # effective user. This closes the cross-user rename/symlink race during the
  # network request. Root is still trusted as the host administrator.
  if ! python3 -c '
import os, stat, sys
p = sys.argv[1]
s = os.stat(p, follow_symlinks=False)
if not stat.S_ISDIR(s.st_mode):
    raise SystemExit(1)
if s.st_uid != os.geteuid():
    raise SystemExit(2)
if stat.S_IMODE(s.st_mode) & 0o077:
    raise SystemExit(3)
' "$output_parent"; then
    echo "error: TOKEN_OUTPUT_FILE parent must be owned by the current user and mode 0700 (or stricter): $output_parent" >&2
    exit 2
  fi

  umask 077
  if ! python3 -c '
import os, sys
path = sys.argv[1]
flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
flags |= getattr(os, "O_NOFOLLOW", 0)
fd = os.open(path, flags, 0o600)
os.close(fd)
' "$TOKEN_OUTPUT_FILE"; then
    echo "error: cannot securely create TOKEN_OUTPUT_FILE" >&2
    rm -f -- "$TOKEN_OUTPUT_FILE"
    exit 2
  fi
  output_identity=$(python3 -c '
import os, sys
s = os.lstat(sys.argv[1])
print(f"{s.st_dev}:{s.st_ino}")
' "$TOKEN_OUTPUT_FILE")

  if ! created=$(cf_post "/accounts/${CLOUDFLARE_ACCOUNT_ID}/access/service_tokens"     "$(python3 -c 'import json,sys; print(json.dumps({"name":sys.argv[1]}))' "$TOKEN_NAME")"); then
    rm -f -- "$TOKEN_OUTPUT_FILE"
    echo "error: service-token creation failed" >&2
    exit 1
  fi
  token_id=$(printf '%s' "$created" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["id"])')

  if ! printf '%s' "$created" | python3 -c '
import json, os, stat, sys
dst, expected = sys.argv[1], sys.argv[2]
expected_dev, expected_ino = map(int, expected.split(":"))
flags = os.O_WRONLY | os.O_TRUNC
flags |= getattr(os, "O_NOFOLLOW", 0)
fd = os.open(dst, flags)
try:
    st = os.fstat(fd)
    if not stat.S_ISREG(st.st_mode) or st.st_dev != expected_dev or st.st_ino != expected_ino:
        raise RuntimeError("credential destination identity changed")
    r = json.load(sys.stdin)["result"]
    payload = (
        "CF_ACCESS_CLIENT_ID=" + r["client_id"] + "\n"
        "CF_ACCESS_CLIENT_SECRET=" + r["client_secret"] + "\n"
    ).encode()
    view = memoryview(payload)
    offset = 0
    while offset < len(view):
        written = os.write(fd, view[offset:])
        if written <= 0:
            raise OSError("short credential write")
        offset += written
    os.fsync(fd)
    os.fchmod(fd, 0o600)
finally:
    os.close(fd)
' "$TOKEN_OUTPUT_FILE" "$output_identity"; then
    echo "error: failed to persist one-time service-token credentials; rolling token back" >&2
    rm -f -- "$TOKEN_OUTPUT_FILE"
    cf_delete "/accounts/${CLOUDFLARE_ACCOUNT_ID}/access/service_tokens/${token_id}" >/dev/null ||       echo "error: token rollback failed; disable/delete token id=${token_id} immediately" >&2
    exit 1
  fi
  echo "[access] created service token id=${token_id}"
  echo "[access] one-time credentials written to TOKEN_OUTPUT_FILE (value not logged)"
else
  echo "[access] reusing service token id=${token_id}"
fi

echo "[access] ensuring Service Auth policy on app ${app_id}"
policies_json=$(cf_get "/accounts/${CLOUDFLARE_ACCOUNT_ID}/access/apps/${app_id}/policies?per_page=100")
has_service_policy=$(printf '%s' "$policies_json" | python3 -c '
import json, sys
token_id = sys.argv[1]
for policy in json.load(sys.stdin).get("result", []):
    if policy.get("decision") != "non_identity":
        continue
    for inc in policy.get("include", []):
        if (inc.get("service_token") or {}).get("token_id") == token_id:
            print("yes")
            raise SystemExit
' "$token_id")

if [[ "$has_service_policy" != "yes" ]]; then
  cf_post "/accounts/${CLOUDFLARE_ACCOUNT_ID}/access/apps/${app_id}/policies"     "$(python3 -c 'import json,sys; print(json.dumps({"name":"Service Auth ("+sys.argv[2]+")","decision":"non_identity","include":[{"service_token":{"token_id":sys.argv[1]}}],"precedence":1}))' "$token_id" "$TOKEN_NAME")" >/dev/null
  echo "[access] attached Service Auth policy"
else
  echo "[access] Service Auth policy already present"
fi

if [[ -n "${OPERATOR_EMAIL:-}" ]]; then
  has_email_policy=$(printf '%s' "$policies_json" | python3 -c '
import json, sys
email = sys.argv[1]
for policy in json.load(sys.stdin).get("result", []):
    if policy.get("decision") != "allow":
        continue
    for inc in policy.get("include", []):
        if (inc.get("email") or {}).get("email") == email:
            print("yes")
            raise SystemExit
' "$OPERATOR_EMAIL")
  if [[ "$has_email_policy" != "yes" ]]; then
    cf_post "/accounts/${CLOUDFLARE_ACCOUNT_ID}/access/apps/${app_id}/policies"       "$(python3 -c 'import json,sys; print(json.dumps({"name":"Allow "+sys.argv[1],"decision":"allow","include":[{"email":{"email":sys.argv[1]}}],"precedence":2}))' "$OPERATOR_EMAIL")" >/dev/null
    echo "[access] added Allow policy for ${OPERATOR_EMAIL}"
  fi
fi

echo "[access] complete: hostname=${HOSTNAME} app=${app_id} service_token=${TOKEN_NAME} id=${token_id}"
