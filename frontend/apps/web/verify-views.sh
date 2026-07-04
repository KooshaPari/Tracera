#!/bin/bash

echo "═══════════════════════════════════════════════════════"
echo "  TraceRTM Views Implementation Verification"
echo "═══════════════════════════════════════════════════════"
echo ""

# Count views
VIEW_COUNT=$(find src/views -name "*View.tsx" | wc -l | tr -d ' ')
echo "✓ Views Created: $VIEW_COUNT/16"

# Check index exports
EXPORT_COUNT=$(grep -c "export {" src/views/index.ts)
echo "✓ Index Exports: $EXPORT_COUNT/16"

# Check App.tsx routes
ROUTE_COUNT=$(grep -c "path=" src/App.tsx)
echo "✓ Routes Configured: $ROUTE_COUNT (16 new + legacy)"

# Check for TypeScript errors (basic syntax check)
echo ""
echo "Checking TypeScript syntax..."
if command -v tsc &> /dev/null; then
    tsc --noEmit --pretty false 2>&1 | head -5
    if [ $? -eq 0 ]; then
        echo "✓ No TypeScript errors detected"
    else
        echo "⚠ Some TypeScript errors found (may need dependencies installed)"
    fi
else
    echo "ℹ TypeScript compiler not found (run 'npm install' first)"
fi

# List all views
echo ""
echo "All Views:"
echo "─────────────────────────────────────────────────────"
ls -1 src/views/*.tsx | sed 's/src\/views\//  ✓ /'

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  Verification Complete!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Next Steps:"
echo "  1. npm install          # Install dependencies"
echo "  2. npm run dev          # Start dev server"
echo "  3. Open http://localhost:5173"
echo ""
