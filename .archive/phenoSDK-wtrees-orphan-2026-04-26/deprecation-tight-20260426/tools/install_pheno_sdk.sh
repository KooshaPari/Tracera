#!/usr/bin/env bash
#
# Install the private pheno-sdk package using an SSH deploy key.
# Usage:
#   scripts/install_pheno_sdk.sh [pip args...]
# Environment:
#   PHENO_SDK_SSH_KEY   Path to the private key (default: ~/.ssh/privSSH)
#   PHENO_SDK_REF       Git ref/tag to install (default: main)

set -euo pipefail

KEY_PATH="${PHENO_SDK_SSH_KEY:-$HOME/.ssh/privSSH}"
GIT_REF="${PHENO_SDK_REF:-main}"
EXTRAS="${PHENO_SDK_EXTRAS:-}"

if [[ -n "$EXTRAS" ]]; then
  PACKAGE_URL="pheno-sdk[${EXTRAS}] @ git+ssh://git@github.com/KooshaPari/phenoSDK.git@${GIT_REF}"
else
  PACKAGE_URL="pheno-sdk @ git+ssh://git@github.com/KooshaPari/phenoSDK.git@${GIT_REF}"
fi

if [[ ! -f "$KEY_PATH" ]]; then
  >&2 echo "Error: SSH key not found at $KEY_PATH."
  >&2 echo "Set PHENO_SDK_SSH_KEY to the path of the deploy key (privSSH)."
  exit 1
fi

chmod 600 "$KEY_PATH"

export GIT_SSH_COMMAND="ssh -i $KEY_PATH -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"
pip install "$PACKAGE_URL" "$@"
