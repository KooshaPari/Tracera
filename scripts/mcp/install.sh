#!/bin/bash
# BMM MCP Server & CLI - Installation Script

set -e  # Exit on error

echo "🚀 BMM MCP Server & CLI - Installation"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

echo -e "${BLUE}Project root: ${PROJECT_ROOT}${NC}"
echo ""

# Step 1: Check for .venv
echo -e "${BLUE}[1/7] Checking for virtual environment...${NC}"
if [ -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "${GREEN}✅ Found .venv${NC}"
    VENV_PATH="$PROJECT_ROOT/.venv"
    PYTHON_CMD="$VENV_PATH/bin/python"
    # Use python -m pip instead of direct pip command
    PIP_CMD="$PYTHON_CMD -m pip"
else
    echo -e "${YELLOW}⚠️  No .venv found, using system Python${NC}"
    PYTHON_CMD="python3"
    PIP_CMD="python3 -m pip"
fi
echo ""

# Step 2: Check Python version
echo -e "${BLUE}[2/7] Checking Python version...${NC}"
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo -e "${RED}❌ Python not found. Please install Python 3.8+${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python ${PYTHON_VERSION} found${NC}"
echo -e "${BLUE}Using: $PYTHON_CMD${NC}"
echo ""

# Step 3: Activate venv if exists
if [ -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "${BLUE}[3/7] Activating virtual environment...${NC}"
    source "$VENV_PATH/bin/activate"
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
    echo ""
fi

# Step 4: Ensure pip is available
echo -e "${BLUE}[4/8] Ensuring pip is available...${NC}"
if ! $PYTHON_CMD -m pip --version > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  pip not found, installing ensurepip...${NC}"
    $PYTHON_CMD -m ensurepip --upgrade --default-pip
fi
echo -e "${GREEN}✅ pip available${NC}"
echo ""

# Step 5: Install dependencies
echo -e "${BLUE}[5/8] Installing dependencies...${NC}"
$PYTHON_CMD -m pip install -r "$SCRIPT_DIR/requirements.txt" --quiet
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Step 6: Make scripts executable
echo -e "${BLUE}[6/8] Making scripts executable...${NC}"
chmod +x "$SCRIPT_DIR/bmm_server.py"
chmod +x "$SCRIPT_DIR/bmm_cli.py"
echo -e "${GREEN}✅ Scripts are now executable${NC}"
echo ""

# Step 7: Test installation
echo -e "${BLUE}[7/8] Testing installation...${NC}"

# Test FastMCP
if $PYTHON_CMD -c "import fastmcp; print(f'FastMCP {fastmcp.__version__}')" 2>/dev/null; then
    echo -e "${GREEN}✅ FastMCP installed${NC}"
else
    echo -e "${RED}❌ FastMCP installation failed${NC}"
    echo -e "${RED}❌ FastMCP not available${NC}"
    exit 1
fi

# Test Typer
if $PYTHON_CMD -c "import typer" 2>/dev/null; then
    echo -e "${GREEN}✅ Typer installed${NC}"
else
    echo -e "${RED}❌ Typer installation failed${NC}"
    exit 1
fi

# Test Rich
if $PYTHON_CMD -c "import rich" 2>/dev/null; then
    echo -e "${GREEN}✅ Rich installed${NC}"
else
    echo -e "${RED}❌ Rich installation failed${NC}"
    exit 1
fi

# Test CLI
if $PYTHON_CMD "$SCRIPT_DIR/bmm_cli.py" --help > /dev/null 2>&1; then
    echo -e "${GREEN}✅ CLI working${NC}"
else
    echo -e "${YELLOW}⚠️  CLI test skipped (may need configuration)${NC}"
fi

echo ""

# Step 8: Create alias and wrapper script
echo -e "${BLUE}[8/8] Setting up 'bmm' command...${NC}"

# Create a wrapper script in a location that can be added to PATH
WRAPPER_SCRIPT="$SCRIPT_DIR/bmm"
cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
# BMM CLI Wrapper
exec "$PYTHON_CMD" "$SCRIPT_DIR/bmm_cli.py" "\$@"
EOF
chmod +x "$WRAPPER_SCRIPT"
echo -e "${GREEN}✅ Wrapper script created: $WRAPPER_SCRIPT${NC}"

# Detect shell and add alias
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    SHELL_RC="$HOME/.profile"
fi

ALIAS_LINE="alias bmm='$PYTHON_CMD $SCRIPT_DIR/bmm_cli.py'"

# Check if alias already exists
if grep -q "alias bmm=" "$SHELL_RC" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Alias already exists in $SHELL_RC${NC}"
else
    echo "" >> "$SHELL_RC"
    echo "# BMM MCP CLI alias" >> "$SHELL_RC"
    echo "$ALIAS_LINE" >> "$SHELL_RC"
    echo -e "${GREEN}✅ Alias added to $SHELL_RC${NC}"
fi

echo ""
echo -e "${YELLOW}To use 'bmm' command, run one of:${NC}"
echo -e "  ${BLUE}source $SHELL_RC${NC}  (to load alias)"
echo -e "  ${BLUE}export PATH=\"\$PATH:$SCRIPT_DIR\"${NC}  (to use wrapper script)"
echo ""

echo ""
echo -e "${GREEN}======================================"
echo "✅ Installation Complete!"
echo "======================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo "1. Activate the 'bmm' command:"
echo -e "   ${YELLOW}source $SHELL_RC${NC}"
echo ""
echo "2. Test the CLI:"
echo -e "   ${YELLOW}bmm status${NC}"
echo ""
echo "3. Initialize your project:"
echo -e "   ${YELLOW}bmm init${NC}"
echo ""
echo "4. Make sure droid is installed (for workflow execution):"
echo -e "   ${YELLOW}curl -fsSL https://app.factory.ai/cli | sh${NC}"
echo -e "   ${YELLOW}export FACTORY_API_KEY=fk-...${NC}"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo -e "   ${YELLOW}$SCRIPT_DIR/INDEX.md${NC}"
echo -e "   ${YELLOW}$SCRIPT_DIR/DROID_SETUP.md${NC}"
echo ""
echo -e "${GREEN}Happy automating! 🚀${NC}"
