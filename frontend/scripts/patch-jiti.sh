#!/bin/bash
# Patch jiti for Node.js 25+ compatibility
# See: https://github.com/unjs/jiti/issues - NodeError is not defined

JITI_FILE="node_modules/jiti/dist/jiti.cjs"

if [ -f "$JITI_FILE" ]; then
  # Check if patch is already applied
  if grep -q "const err = new Error(message); err.code = code" "$JITI_FILE"; then
    echo "jiti already patched"
  else
    # Apply patch: Replace NodeError reference with inline error creation
    sed -i.bak 's/((e, t) => NodeError)(i, e)/((code, message) => { const err = new Error(message); err.code = code; return err; })(i, e)/g' "$JITI_FILE"
    echo "jiti patched for Node.js 25+ compatibility"
  fi
else
  echo "jiti not found, skipping patch"
fi
