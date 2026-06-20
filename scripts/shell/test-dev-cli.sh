#!/bin/bash
# Test script for development CLI

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEV_CLI="$SCRIPT_DIR/dev"

echo "Testing TraceRTM Development CLI"
echo "================================="
echo

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_count=0
pass_count=0
fail_count=0

run_test() {
    local test_name="$1"
    local test_cmd="$2"

    test_count=$((test_count + 1))
    echo -n "Testing: $test_name... "

    if eval "$test_cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        pass_count=$((pass_count + 1))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        fail_count=$((fail_count + 1))
        return 1
    fi
}

# Test 1: CLI is executable
run_test "CLI is executable" "test -x $DEV_CLI"

# Test 2: CLI shows help
run_test "CLI shows help" "$DEV_CLI --help"

# Test 3: Health command exists
run_test "Health command exists" "$DEV_CLI health --help"

# Test 4: Seed command exists
run_test "Seed command exists" "$DEV_CLI seed --help"

# Test 5: Clear command exists
run_test "Clear command exists" "$DEV_CLI clear --help"

# Test 6: Logs command exists
run_test "Logs command exists" "$DEV_CLI logs --help"

# Test 7: Status command exists
run_test "Status command exists" "$DEV_CLI status --help"

# Test 8: Generate command exists
run_test "Generate command exists" "$DEV_CLI generate --help"

# Test 9: Init command exists
run_test "Init command exists" "$DEV_CLI init --help"

# Test 10: Utils package exists
run_test "Utils package exists" "test -f $SCRIPT_DIR/utils/__init__.py"

# Test 11: DB utils module exists
run_test "DB utils module exists" "test -f $SCRIPT_DIR/utils/db_utils.py"

# Test 12: Service utils module exists
run_test "Service utils module exists" "test -f $SCRIPT_DIR/utils/service_utils.py"

# Test 13: Requirements file exists
run_test "Requirements file exists" "test -f $SCRIPT_DIR/dev-requirements.txt"

# Test 14: README exists
run_test "README exists" "test -f $SCRIPT_DIR/README_DEV_CLI.md"

echo
echo "================================="
echo "Test Results:"
echo "  Total:  $test_count"
echo -e "  ${GREEN}Passed: $pass_count${NC}"
echo -e "  ${RED}Failed: $fail_count${NC}"
echo "================================="

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
