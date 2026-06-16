#!/bin/bash
# Contract coverage report stub — no contracts defined yet
mkdir -p "$(dirname "$0")/../docs"
cat > "$(dirname "$0")/../docs/coverage.md" << 'EOF'
# Contract Test Coverage

No contract tests defined yet. Coverage report will appear here once Pact consumer tests are added.
EOF
echo "Contract coverage report: no contracts defined yet — stub report generated"
exit 0
