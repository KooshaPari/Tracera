#!/bin/bash

# Bundle Analysis Script
# Analyzes the production bundle to identify optimization opportunities

echo "======================================"
echo "Bundle Size Analysis"
echo "======================================"
echo ""

# Build the project
echo "Building project..."
bun run build

echo ""
echo "======================================"
echo "Bundle Size Summary"
echo "======================================"
echo ""

# List chunk sizes
echo "Chunk Sizes (in order):"
ls -lhS dist/assets/*.js | awk '{print $9, "\t", $5}'

echo ""
echo "======================================"
echo "Asset Totals"
echo "======================================"
echo ""

# Calculate totals
JS_SIZE=$(du -sh dist/assets/*.js 2>/dev/null | tail -1 | awk '{print $1}')
CSS_SIZE=$(du -sh dist/assets/*.css 2>/dev/null | tail -1 | awk '{print $1}')
TOTAL=$(du -sh dist 2>/dev/null | awk '{print $1}')

echo "JavaScript: $JS_SIZE"
echo "CSS: $CSS_SIZE"
echo "Total dist/: $TOTAL"

echo ""
echo "======================================"
echo "Top 10 Largest Chunks"
echo "======================================"
echo ""

ls -lhS dist/assets/*.js | head -10 | awk '{print $5 "\t" $9}'

echo ""
echo "======================================"
echo "Optimization Recommendations"
echo "======================================"
echo ""

# Check for specific large chunks
if ls dist/assets/*monaco* 1> /dev/null 2>&1; then
	echo "✓ Monaco chunk detected (separated)"
	MONACO_SIZE=$(ls -lh dist/assets/*monaco* | awk '{print $5}')
	echo "  Size: $MONACO_SIZE"
fi

if ls dist/assets/*graph* 1> /dev/null 2>&1; then
	echo "✓ Graph chunks detected (separated)"
	du -sh dist/assets/*graph* | awk '{print "  " $1 "\t" $2}'
fi

if ls dist/assets/*api* 1> /dev/null 2>&1; then
	echo "✓ API docs chunks detected (separated)"
	du -sh dist/assets/*api* | awk '{print "  " $1 "\t" $2}'
fi

echo ""
echo "======================================"
echo "Build Artifacts"
echo "======================================"
echo ""

echo "Output directory: dist/"
echo "Source maps: dist/assets/*.js.map"
echo ""
