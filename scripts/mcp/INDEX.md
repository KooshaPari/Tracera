# BMM MCP Server - Documentation Index

Complete guide to the BMM MCP server and CLI implementation.

## 📚 Documentation Files

### 🚀 Getting Started

1. **[SETUP.md](./SETUP.md)** - Start here!
   - Prerequisites and installation
   - Step-by-step setup guide
   - Configuration for Claude Desktop, Cursor, custom clients
   - Testing procedures
   - Troubleshooting
   - **Best for:** First-time setup

### 📖 Complete Guide

2. **[README.md](./README.md)** - Full documentation
   - All features explained
   - MCP server capabilities
   - CLI commands reference
   - Usage examples
   - Advanced features
   - **Best for:** Understanding all capabilities

### 🏗️ Technical Details

3. **[DESIGN.md](./DESIGN.md)** - Architecture and design
   - Why MCP over custom CLI
   - FastMCP features analysis
   - Architecture design
   - Integration with factory models
   - CLI enhancement strategy
   - **Best for:** Developers and architects

### 📊 Summary

4. **[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)** - What was built
   - Complete deliverables list
   - Key innovations
   - Feature comparison (old vs new)
   - Usage examples
   - FastMCP 3.0.0b1 features showcase
   - **Best for:** Project stakeholders and quick overview

## 🎯 Quick Navigation

### By User Type

**New User:**
1. Read [SETUP.md](./SETUP.md)
2. Run setup steps
3. Test with `python3 scripts/mcp/bmm_cli.py status`
4. Try `python3 scripts/mcp/bmm_cli.py --help`

**Experienced User:**
1. Check [README.md](./README.md) for advanced options
2. Configure Claude Desktop
3. Explore resources and prompts
4. Use parallel execution

**Developer:**
1. Review [DESIGN.md](./DESIGN.md)
2. Understand MCP architecture
3. Check [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)
4. Extend with custom tools/resources

**Project Manager:**
1. Read [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)
2. Review feature comparison
3. Check migration path
4. Plan rollout

### By Task

**Installing:**
→ [SETUP.md - Installation](./SETUP.md#installation)

**Configuring Claude Desktop:**
→ [SETUP.md - For Claude Desktop](./SETUP.md#for-claude-desktop)

**Using CLI:**
→ [README.md - CLI Commands](./README.md#-cli-commands)

**Understanding MCP Features:**
→ [DESIGN.md - FastMCP Features](./DESIGN.md#fastmcp-features-analysis)

**Troubleshooting:**
→ [SETUP.md - Troubleshooting](./SETUP.md#troubleshooting)

**Extending:**
→ [README.md - Advanced Usage](./README.md#-advanced-usage)

## 📁 File Structure

```
scripts/mcp/
├── bmm_server.py                    # MCP server (604 lines)
├── bmm_cli.py                       # CLI with Typer + Rich (322 lines)
├── INDEX.md                         # This file
├── README.md                        # Complete documentation
├── SETUP.md                         # Setup guide
├── DESIGN.md                        # Architecture document
├── IMPLEMENTATION_SUMMARY.md        # Summary and comparison
└── claude_desktop_config.json       # Claude Desktop configuration
```

## 🎓 Learning Path

### Beginner Path (30 minutes)

1. **Read:** [SETUP.md](./SETUP.md) (10 min)
2. **Install:** Follow setup steps (10 min)
3. **Test:** Run `bmm status` (5 min)
4. **Explore:** Try `bmm --help` (5 min)

### Intermediate Path (1 hour)

1. **Review:** [README.md](./README.md) (20 min)
2. **Configure:** Set up Claude Desktop (15 min)
3. **Practice:** Run workflows with CLI (15 min)
4. **Experiment:** Try resources and prompts (10 min)

### Advanced Path (2 hours)

1. **Study:** [DESIGN.md](./DESIGN.md) (30 min)
2. **Understand:** MCP features and architecture (30 min)
3. **Analyze:** [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) (20 min)
4. **Plan:** Custom extensions or integrations (40 min)

## 🔍 Common Questions

### "Where do I start?"
→ [SETUP.md](./SETUP.md)

### "How does it work?"
→ [DESIGN.md - Architecture](./DESIGN.md#architecture-design)

### "What can it do?"
→ [README.md - Features](./README.md#-features)

### "How do I use the CLI?"
→ [README.md - CLI Commands](./README.md#-cli-commands)

### "How do I configure Claude Desktop?"
→ [SETUP.md - For Claude Desktop](./SETUP.md#for-claude-desktop)

### "What's different from bmm-auto.py?"
→ [IMPLEMENTATION_SUMMARY.md - Feature Comparison](./IMPLEMENTATION_SUMMARY.md#-feature-comparison)

### "How do I extend it?"
→ [README.md - Advanced Usage](./README.md#-advanced-usage)

### "What if something breaks?"
→ [SETUP.md - Troubleshooting](./SETUP.md#troubleshooting)

## 📋 Cheat Sheet

### Essential Commands

```bash
# Setup
chmod +x scripts/mcp/bmm_server.py scripts/mcp/bmm_cli.py

# Initialize
python3 scripts/mcp/bmm_cli.py init

# Check status
python3 scripts/mcp/bmm_cli.py status

# Run next workflow
python3 scripts/mcp/bmm_cli.py next

# Run specific workflow
python3 scripts/mcp/bmm_cli.py run <workflow-id>

# Run phase
python3 scripts/mcp/bmm_cli.py run --phase <0|1|2|3>

# Run phase in parallel
python3 scripts/mcp/bmm_cli.py run --phase <0|1|2|3> --parallel

# List resources
python3 scripts/mcp/bmm_cli.py resources

# Read resource
python3 scripts/mcp/bmm_cli.py read bmm://workflow-status

# List tools
python3 scripts/mcp/bmm_cli.py tools

# Get help
python3 scripts/mcp/bmm_cli.py --help
```

### MCP Resources

```
bmm://workflow-status      # Current workflow status (YAML)
bmm://project-config       # BMM configuration
bmm://next-workflow        # Next pending workflow
bmm://progress-summary     # Human-readable progress
```

### MCP Tools

```
init_project               # Initialize BMM project
run_workflow               # Execute specific workflow
run_phase                  # Execute entire phase
get_status                 # Get workflow status
```

## 🔗 External Resources

- **FastMCP Documentation:** https://gofastmcp.com/
- **MCP Specification:** https://modelcontextprotocol.io/
- **Typer Documentation:** https://typer.tiangolo.com/
- **Rich Documentation:** https://rich.readthedocs.io/

## 📞 Support

For help:
1. Check this INDEX for relevant documentation
2. Review the specific guide for your task
3. Check troubleshooting sections
4. Consult FastMCP documentation

## 🎉 Quick Wins

**5 minutes:**
- Install and test CLI
- Check workflow status

**15 minutes:**
- Configure Claude Desktop
- Run first workflow

**30 minutes:**
- Explore all CLI commands
- Test resources and prompts

**1 hour:**
- Run complete phase
- Understand MCP architecture

---

**Start here:** [SETUP.md](./SETUP.md) 🚀

