#!/bin/bash
# Verify inline metadata coverage across the project

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "================================================================"
echo "Inline Metadata Coverage Report"
echo "================================================================"
echo ""

# Python modules
echo "📦 Python Module Docstrings"
echo "----------------------------"
PYTHON_TOTAL=$(find src/pheno -name "__init__.py" | wc -l | tr -d ' ')
PYTHON_WITH_STATE=$(grep -r "^State:" src/pheno/**/__init__.py 2>/dev/null | wc -l | tr -d ' ')
PYTHON_PERCENT=$((PYTHON_WITH_STATE * 100 / PYTHON_TOTAL))
echo "  Modules with State metadata: $PYTHON_WITH_STATE / $PYTHON_TOTAL ($PYTHON_PERCENT%)"

PYTHON_WITH_SPECS=$(grep -r "^Specs:" src/pheno/**/__init__.py 2>/dev/null | wc -l | tr -d ' ')
echo "  Modules with Spec links: $PYTHON_WITH_SPECS / $PYTHON_TOTAL"

PYTHON_WITH_TESTS=$(grep -r "^Tests:" src/pheno/**/__init__.py 2>/dev/null | wc -l | tr -d ' ')
echo "  Modules with Test links: $PYTHON_WITH_TESTS / $PYTHON_TOTAL"

echo ""

# Test markers
echo "🧪 Pytest Markers"
echo "------------------"
TEST_FILES=$(find tests -name "test_*.py" | wc -l | tr -d ' ')
TESTS_WITH_SPEC=$(grep -r "@pytest.mark.spec" tests/ 2>/dev/null | wc -l | tr -d ' ')
TESTS_WITH_STORY=$(grep -r "@pytest.mark.story" tests/ 2>/dev/null | wc -l | tr -d ' ')
echo "  Tests with @pytest.mark.spec: $TESTS_WITH_SPEC"
echo "  Tests with @pytest.mark.story: $TESTS_WITH_STORY"
echo "  Total test files: $TEST_FILES"

echo ""

# MkDocs files
echo "📄 MkDocs Markdown Files"
echo "------------------------"
if [ -d "docs" ]; then
    MKDOCS_TOTAL=$(find docs -name "*.md" -not -path "docs/archive/*" -not -path "docs/sphinx/*" | wc -l | tr -d ' ')
    MKDOCS_WITH_FM=$(grep -l "^---" docs/**/*.md 2>/dev/null | wc -l | tr -d ' ')
    if [ "$MKDOCS_TOTAL" -gt 0 ]; then
        MKDOCS_PERCENT=$((MKDOCS_WITH_FM * 100 / MKDOCS_TOTAL))
        echo "  Files with frontmatter: $MKDOCS_WITH_FM / $MKDOCS_TOTAL ($MKDOCS_PERCENT%)"
    else
        echo "  Files with frontmatter: $MKDOCS_WITH_FM / $MKDOCS_TOTAL (0%)"
    fi
else
    echo "  docs/ directory not found"
fi

echo ""

# Fumadocs MDX files
echo "📝 Fumadocs MDX Files"
echo "---------------------"
if [ -d "apps/docs/content/docs" ]; then
    MDX_TOTAL=$(find apps/docs/content/docs -name "*.mdx" | wc -l | tr -d ' ')
    MDX_WITH_STATE=$(grep -l "^state:" apps/docs/content/docs/**/*.mdx 2>/dev/null | wc -l | tr -d ' ')
    MDX_WITH_SPECS=$(grep -l "^specs:" apps/docs/content/docs/**/*.mdx 2>/dev/null | wc -l | tr -d ' ')
    if [ "$MDX_TOTAL" -gt 0 ]; then
        MDX_PERCENT=$((MDX_WITH_STATE * 100 / MDX_TOTAL))
        echo "  Files with state metadata: $MDX_WITH_STATE / $MDX_TOTAL ($MDX_PERCENT%)"
        echo "  Files with spec links: $MDX_WITH_SPECS / $MDX_TOTAL"
    else
        echo "  Files with state metadata: $MDX_WITH_STATE / $MDX_TOTAL (0%)"
        echo "  Files with spec links: $MDX_WITH_SPECS / $MDX_TOTAL"
    fi
else
    echo "  apps/docs/content/docs directory not found"
fi

echo ""

# Summary
echo "================================================================"
echo "Summary"
echo "================================================================"
echo ""
echo "  ✅ Coverage Levels:"
echo "     Python Modules: $PYTHON_PERCENT%"
if [ -d "apps/docs/content/docs" ] && [ "$MDX_TOTAL" -gt 0 ]; then
    echo "     MDX Files: $MDX_PERCENT%"
fi
echo ""
echo "  📊 Cross-References:"
echo "     Spec links in code: $PYTHON_WITH_SPECS modules"
echo "     Test markers: $TESTS_WITH_SPEC @spec, $TESTS_WITH_STORY @story"
echo ""

# Goals
echo "  🎯 Target: 100% coverage across all systems"
echo ""
echo "  Next steps:"
echo "    1. Run: python scripts/add_inline_metadata.py"
echo "    2. Add test markers: @pytest.mark.spec('SPEC-XXX-YYY')"
echo "    3. Update MDX frontmatter with state/specs/stories"
echo "    4. Re-run this script to verify progress"
echo ""
