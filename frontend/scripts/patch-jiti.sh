#!/bin/bash
# Patch jiti for Node.js compatibility (NodeError from node:errors not available in older Node or when loaded by Vite)
# See: https://github.com/unjs/jiti/issues - NodeError is not defined
# Patches both root jiti and nested @tailwindcss/node/node_modules/jiti.

# Use # delimiter to avoid escaping slashes in replacement
PATCH_PATTERN='s#((e, t) => NodeError)(i, e)#((message, code) => { const err = new Error(message); err.code = code; return err; })(i, e)#g'
CHECK_PATTERN='const err = new Error(message); err.code = code'

patch_one() {
  local JITI_FILE="$1"
  if [ ! -f "$JITI_FILE" ]; then
    return 0
  fi
  if grep -q "$CHECK_PATTERN" "$JITI_FILE"; then
    echo "  already patched: $JITI_FILE"
    return 0
  fi
  if sed -i.bak "$PATCH_PATTERN" "$JITI_FILE" 2>/dev/null; then
    echo "  patched: $JITI_FILE"
    return 0
  fi
  # macOS sed -i requires backup extension
  sed -i.bak "$PATCH_PATTERN" "$JITI_FILE" && echo "  patched: $JITI_FILE" || return 1
}

echo "Patching jiti for NodeError compatibility..."
patch_one "node_modules/jiti/dist/jiti.cjs" || true
patch_one "node_modules/@tailwindcss/node/node_modules/jiti/dist/jiti.cjs" || true
echo "Done."
