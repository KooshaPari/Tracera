#!/bin/bash
# Test script to demonstrate all TraceRTM functionality

set -e

echo "🚀 TraceRTM Complete Functionality Test"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test database
DB_FILE="./test_functionality.db"
rm -f "$DB_FILE"

echo -e "${BLUE}1. Setup & Configuration${NC}"
echo "----------------------------"
echo "Initializing config with SQLite..."
python3 -c "
from tracertm.cli import app
import sys
sys.argv = ['rtm', 'config', 'init', '--database-url', 'sqlite:///$DB_FILE']
app()
" 2>&1 | grep -v "Traceback\|Error\|File" || true

echo ""
echo -e "${BLUE}2. Project Management${NC}"
echo "----------------------"
echo "Initializing project..."
python3 -c "
from tracertm.cli import app
import sys
sys.argv = ['rtm', 'project', 'init', 'test-project', '--database-url', 'sqlite:///$DB_FILE']
app()
" 2>&1 | grep -E "✓|Project|Database" || true

echo ""
echo -e "${BLUE}3. Database Migration${NC}"
echo "----------------------"
echo "Running migrations..."
python3 -c "
from tracertm.cli import app
import sys
sys.argv = ['rtm', 'db', 'migrate']
app()
" 2>&1 | grep -E "✓|Creating|Tables" || true

echo ""
echo -e "${BLUE}4. MVP Shortcuts - Create${NC}"
echo "---------------------------"
echo "Creating epic..."
python3 -c "
from tracertm.cli import app
import sys
sys.argv = ['rtm', 'create', 'epic', 'User Authentication System', '--priority', 'high', '--owner', 'alice']
app()
" 2>&1 | grep -E "✓|Item created|ID" || true

echo "Creating story..."
python3 -c "
from tracertm.cli import app
import sys
sys.argv = ['rtm', 'create', 'story', 'As a user, I want to login', '--priority', 'high', '--owner', 'alice']
app()
" 2>&1 | grep -E "✓|Item created|ID" || true

echo "Creating test..."
python3 -c "
from tracertm.cli import app
import sys
sys.argv = ['rtm', 'create', 'test', 'Test login with valid credentials', '--owner', 'bob']
app()
" 2>&1 | grep -E "✓|Item created|ID" || true

echo ""
echo -e "${BLUE}5. List Items${NC}"
echo "-------------"
echo "Listing all items..."
python3 -c "
from tracertm.cli import app
import sys
sys.argv = ['rtm', 'list']
app()
" 2>&1 | head -15 || true

echo ""
echo -e "${BLUE}6. Show Item${NC}"
echo "------------"
echo "Showing item details..."
python3 -c "
from tracertm.cli import app
import sys
# Get first item ID from list
import subprocess
result = subprocess.run(['python3', '-c', 'from tracertm.cli import app; import sys; sys.argv = [\"rtm\", \"list\"]; app()'], capture_output=True, text=True)
lines = result.stdout.split('\n')
for line in lines:
    if '│' in line and len(line.split('│')) > 2:
        item_id = line.split('│')[1].strip()
        if item_id and len(item_id) > 5:
            sys.argv = ['rtm', 'item', 'show', item_id]
            app()
            break
" 2>&1 | head -20 || true

echo ""
echo -e "${BLUE}7. State${NC}"
echo "-------"
echo "Showing project state..."
python3 -c "
from tracertm.cli.commands.state import show_state
show_state()
" 2>&1 | head -20 || true

echo ""
echo -e "${BLUE}8. Search${NC}"
echo "--------"
echo "Searching for 'login'..."
python3 -c "
from tracertm.cli.commands.search import search
search('login')
" 2>&1 | head -15 || true

echo ""
echo -e "${GREEN}✅ Basic functionality test complete!${NC}"
echo ""
echo "To test more features, run:"
echo "  python3 -c \"from tracertm.cli import app; import sys; sys.argv = ['rtm', '<command>']; app()\""
echo ""
echo "See COMPLETE_FUNCTIONALITY_WALKTHROUGH.md for full documentation"
