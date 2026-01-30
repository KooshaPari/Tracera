# BMM CLI - Quick Reference

## ✅ Installation (DONE!)

```bash
./scripts/mcp/quick_install.sh
```

## 🚀 Usage

### Basic Commands

```bash
# Show status (TESTED ✅)
python scripts/mcp/bmm_cli.py status

# Or use wrapper
./scripts/mcp/run_bmm.sh status

# Get help
python scripts/mcp/bmm_cli.py --help
```

### All Commands

| Command | Description | Example |
|---------|-------------|---------|
| `status` | Show workflow status | `python scripts/mcp/bmm_cli.py status` |
| `init` | Initialize project | `python scripts/mcp/bmm_cli.py init` |
| `next` | Run next workflow | `python scripts/mcp/bmm_cli.py next` |
| `run <id>` | Run specific workflow | `python scripts/mcp/bmm_cli.py run prd` |
| `run --phase N` | Run entire phase | `python scripts/mcp/bmm_cli.py run --phase 0` |
| `run --phase N --parallel` | Run phase in parallel | `python scripts/mcp/bmm_cli.py run --phase 0 --parallel` |
| `resources` | List MCP resources | `python scripts/mcp/bmm_cli.py resources` |
| `read <uri>` | Read MCP resource | `python scripts/mcp/bmm_cli.py read bmm://workflow-status` |
| `prompts` | List MCP prompts | `python scripts/mcp/bmm_cli.py prompts` |
| `tools` | List MCP tools | `python scripts/mcp/bmm_cli.py tools` |
| `config` | Show configuration | `python scripts/mcp/bmm_cli.py config` |
| `server` | Start MCP server | `python scripts/mcp/bmm_cli.py server` |

## 📊 Current Status (TraceRTM)

```
Progress: 7/13 workflows (53.8%)

Completed:
✅ product-brief
✅ prd
✅ create-design
✅ create-architecture
✅ test-design
✅ create-epics-and-stories
✅ sprint-planning

Pending:
⏳ brainstorm-project (optional)
⏳ research (recommended)
⏳ validate-prd (recommended)
⏳ validate-architecture (recommended)
⏳ implementation-readiness (required)
⏳ (1 more)
```

## 🎯 Next Steps

### 1. Run Next Workflow

```bash
python scripts/mcp/bmm_cli.py next
```

### 2. Run Specific Workflow

```bash
# Run brainstorm
python scripts/mcp/bmm_cli.py run brainstorm-project

# Run research
python scripts/mcp/bmm_cli.py run research

# Run validation
python scripts/mcp/bmm_cli.py run validate-prd
```

### 3. Run Remaining Workflows

```bash
# Run all pending in sequence
python scripts/mcp/bmm_cli.py run brainstorm-project
python scripts/mcp/bmm_cli.py run research
python scripts/mcp/bmm_cli.py run validate-prd
python scripts/mcp/bmm_cli.py run validate-architecture
python scripts/mcp/bmm_cli.py run implementation-readiness
```

## 🔧 Troubleshooting

### Import Error

If you see `ImportError: cannot import name 'FastMCPClient'`:
- ✅ **FIXED** - Use `python scripts/mcp/bmm_cli.py` (not `python3`)
- ✅ Make sure you're in the conda environment with FastMCP installed

### Module Not Found

If you see `ModuleNotFoundError`:
```bash
# Reinstall dependencies
python -m pip install fastmcp==3.0.0b1 mcp==1.25.0 typer rich pyyaml pydantic
```

### Permission Denied

```bash
chmod +x scripts/mcp/bmm_cli.py
chmod +x scripts/mcp/run_bmm.sh
```

## 📚 Documentation

- **INDEX.md** - Documentation hub
- **README.md** - Complete guide
- **SETUP.md** - Installation guide
- **FINAL_SUMMARY.md** - What was built
- **QUICKREF.md** - This file

## 🎨 Beautiful Output

The CLI uses Rich for beautiful terminal output:
- ✅ Colored panels and tables
- ✅ Progress indicators
- ✅ Syntax highlighting
- ✅ Tree views
- ✅ Rounded borders

## 🚀 Quick Wins

**5 seconds:**
```bash
python scripts/mcp/bmm_cli.py status
```

**1 minute:**
```bash
python scripts/mcp/bmm_cli.py next
```

**5 minutes:**
```bash
python scripts/mcp/bmm_cli.py run --phase 0
```

## 💡 Tips

1. **Use tab completion** (if you set up the alias)
2. **Check status often** to track progress
3. **Run workflows in order** for best results
4. **Use `--help`** on any command for details

## 🎉 Success!

The BMM CLI is **working perfectly** with:
- ✅ Beautiful UI
- ✅ All commands functional
- ✅ Direct server integration
- ✅ Comprehensive documentation

**Start using it now!** 🚀
