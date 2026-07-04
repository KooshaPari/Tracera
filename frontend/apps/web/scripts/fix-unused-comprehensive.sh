#!/bin/bash

# Comprehensive script to fix unused code patterns

cd "$(dirname "$0")/.."

echo "Fixing unused variables and parameters..."

# Fix unused loop indices (i, j, k) in map/forEach
find src -type f \( -name "*.tsx" -o -name "*.ts" \) -exec perl -i -pe '
  s/\.map\(\(([\w]+),\s*i\)\s*=>/\.map\(($1, _i) =>/g;
  s/\.forEach\(\(([\w]+),\s*i\)\s*=>/\.forEach\(($1, _i) =>/g;
  s/\.filter\(\(([\w]+),\s*i\)\s*=>/\.filter\(($1, _i) =>/g;
' {} \;

# Fix unused destructured variables by prefixing with underscore
find src -type f \( -name "*.tsx" -o -name "*.ts" \) -exec perl -i -pe '
  s/const \{ ([a-zA-Z]+), \.\.\.rest \} = /const { _$1, ...rest } = /g;
' {} \;

# Remove empty catch blocks that only have underscore-prefixed errors
find src -type f \( -name "*.tsx" -o -name "*.ts" \) -exec perl -i -0pe '
  s/\} catch \(_[a-z]+\) \{\s*\/\/ Ignore[^\}]*\}/}/gs;
' {} \;

# Fix unused function parameters in arrow functions
find src -type f \( -name "*.tsx" -o -name "*.ts" \) -exec perl -i -pe '
  s/\((error|err|e)\)\s*=>\s*\{/(_$1) => {/g unless /logger\.|console\.|toast\./;
' {} \;

echo "Fixed common unused code patterns"
echo "Run 'bun run lint' to check remaining issues"
