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
  # Reserve atomically and capture identity in the same operation. A failed
  # reservation owns nothing and must not remove another caller's file.
  if ! output_identity=$(python3 -c '
import os, sys
fd = os.open(sys.argv[1], os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
try:
    st = os.fstat(fd)
    print(f"{st.st_dev}:{st.st_ino}")
finally:
    os.close(fd)
' "$TOKEN_OUTPUT_FILE"); then
    echo "error: cannot securely reserve TOKEN_OUTPUT_FILE" >&2
    exit 2
  fi
  cleanup_owned_output() {
    python3 -c '
import os, sys
try:
    st = os.lstat(sys.argv[1])
    if f"{st.st_dev}:{st.st_ino}" == sys.argv[2]:
        os.unlink(sys.argv[1])
except FileNotFoundError:
    pass
' "$TOKEN_OUTPUT_FILE" "$output_identity"
  }
  trap cleanup_owned_output EXIT

  # An indeterminate request is never retried: it may already have created a token.
  if ! created=$(cf_post "/accounts/${CLOUDFLARE_ACCOUNT_ID}/access/service_tokens" \
    "$(python3 -c 'import json,sys; print(json.dumps({"name":sys.argv[1]}))' "$TOKEN_NAME")"); then
    echo "error: token creation indeterminate; revocation unconfirmed; inspect service tokens manually" >&2
    exit 1
  fi
  # Extract a rollback-safe identifier independently of credential validation.
  rollback_id=$(printf '%s' "$created" | python3 -c '
import json, re, sys
try:
    d = json.load(sys.stdin)
    r = d.get("result") if isinstance(d, dict) else None
    v = r.get("id") if isinstance(r, dict) else None
    if isinstance(v, str) and re.fullmatch(r"[A-Za-z0-9_-]+", v):
        print(v)
except (ValueError, TypeError):
    pass
')
  rollback_created() {
    cleanup_owned_output
    if [[ -z "$rollback_id" ]]; then
      echo "error: unusable token id; revocation unconfirmed; inspect service tokens manually" >&2
      return
    fi
    if ! rollback_response=$(cf_delete "/accounts/${CLOUDFLARE_ACCOUNT_ID}/access/service_tokens/${rollback_id}"); then
      echo "error: rollback transport failed; manually revoke token id=${rollback_id}" >&2
    elif ! printf '%s' "$rollback_response" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
    ok = isinstance(d, dict) and d.get("success") is True
except (ValueError, TypeError):
    ok = False
raise SystemExit(0 if ok else 1)
'; then
      echo "error: rollback API failed; manually revoke token id=${rollback_id}" >&2
    fi
  }
  if ! printf '%s' "$created" | python3 -c '
import json, os, re, stat, sys
try:
    d = json.load(sys.stdin)
    if not isinstance(d, dict) or d.get("success") is not True:
        raise ValueError("unsuccessful response")
    r = d.get("result")
    if not isinstance(r, dict):
        raise ValueError("invalid result")
    for k in ("id", "client_id", "client_secret"):
        v = r.get(k)
        if not isinstance(v, str) or not v or any(ord(c) < 32 or ord(c) == 127 for c in v):
            raise ValueError("invalid credential field")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", r["id"]):
        raise ValueError("invalid token id")
    dst, expected = sys.argv[1:]
    fd = os.open(dst, os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or f"{st.st_dev}:{st.st_ino}" != expected:
            raise ValueError("credential destination changed")
        os.ftruncate(fd, 0)
        payload = ("CF_ACCESS_CLIENT_ID=" + r["client_id"] + "\nCF_ACCESS_CLIENT_SECRET=" + r["client_secret"] + "\n").encode()
        offset = 0
        while offset < len(payload):
            n = os.write(fd, payload[offset:])
            if n <= 0:
                raise OSError("short credential write")
            offset += n
        os.fsync(fd)
        os.fchmod(fd, 0o600)
    finally:
        os.close(fd)
except Exception:
    print("error: invalid token response or credential persistence failed", file=sys.stderr)
    raise SystemExit(1)
' "$TOKEN_OUTPUT_FILE" "$output_identity"; then
    rollback_created
    exit 1
  fi
  token_id="$rollback_id"
  trap - EXIT
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
