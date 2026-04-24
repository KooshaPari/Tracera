#!/bin/bash

# Script to automatically fix common unused code patterns

# Fix unused container declarations in tests
find src -type f \( -name "*.test.tsx" -o -name "*.test.ts" \) -exec sed -i '' \
  -e 's/const { container } = render(/render(/g' \
  {} \;

# Fix unused user declarations in tests (when userEvent.setup() is not used)
find src -type f \( -name "*.test.tsx" -o -name "*.test.ts" \) -exec perl -i -pe '
  if (/const user = userEvent\.setup\(\);/) {
    $_ = "" unless /await user\./;
  }
' {} \;

echo "Fixed common unused code patterns"
