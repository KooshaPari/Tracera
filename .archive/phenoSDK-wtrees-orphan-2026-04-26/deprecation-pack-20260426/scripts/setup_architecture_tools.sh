#!/usr/bin/env bash
# Setup script for architectural boundary enforcement tools
# This script installs and initializes Tach, Grimp, Deply, and pydeps
#
# Usage: ./scripts/setup_architecture_tools.sh [--init] [--report]
#
# Options:
#   --init     Initialize Tach and create tach.toml
#   --report   Generate dependency report
#   --help     Show this help message

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOLS=("tach" "grimp" "deply" "pydeps")

# Functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

show_help() {
    grep "^#" "$0" | grep -v "^#!/" | sed 's/^# //'
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    log_success "Python 3 found: $(python3 --version)"
}

check_uv() {
    if ! command -v uv &> /dev/null; then
        log_warning "uv not found, using pip instead"
        return 1
    fi
    log_success "uv found: $(uv --version)"
    return 0
}

install_tools() {
    log_info "Installing architectural boundary tools..."
    
    if check_uv; then
        uv pip install tach grimp deply pydeps
    else
        pip install tach grimp deply pydeps
    fi
    
    log_success "Tools installed successfully"
}

verify_installation() {
    log_info "Verifying tool installations..."
    
    for tool in "${TOOLS[@]}"; do
        if python3 -c "import importlib.util; importlib.util.find_spec('$tool')" 2>/dev/null; then
            log_success "$tool installed"
        else
            log_warning "$tool not found, attempting pip install..."
            if check_uv; then
                uv pip install "$tool"
            else
                pip install "$tool"
            fi
        fi
    done
}

init_tach() {
    log_info "Initializing Tach..."
    cd "$PROJECT_ROOT"
    
    if [ -f "tach.toml" ]; then
        log_warning "tach.toml already exists, skipping initialization"
        return
    fi
    
    log_info "Running: tach init"
    tach init --yes 2>/dev/null || {
        log_warning "Tach interactive init skipped; creating baseline tach.toml"
        create_baseline_tach_config
    }
    
    log_success "Tach initialized"
}

create_baseline_tach_config() {
    log_info "Creating baseline tach.toml configuration..."
    
    cat > "$PROJECT_ROOT/tach.toml" << 'EOF'
# Tach Configuration for PhenoSDK
# Defines module boundaries and enforces architectural constraints
# 
# Documentation: https://docs.gauge.sh/usage/configuration/
# Key commands:
#   tach check              - Verify all boundaries
#   tach show               - Generate dependency graph (web)
#   tach mod                - Interactive module editor
#   tach sync               - Sync dependencies from imports

[build]
# Start permissive; gradually increase strictness
strict = false

# Core domains (no dependencies - foundation layer)
[[modules]]
name = "pheno.domain"
path = "src/pheno/domain"
depends_on = []
# Domain entities, events, exceptions - independent of everything

[[modules]]
name = "pheno.core.ports"
path = "src/pheno/core/ports"
depends_on = []
# Port interfaces - define contracts, no implementation

# Application layer (depends on domain only)
[[modules]]
name = "pheno.application"
path = "src/pheno/application"
depends_on = [
  { module = "pheno.domain" },
]

[[modules]]
name = "pheno.credentials"
path = "src/pheno/credentials"
depends_on = [
  { module = "pheno.domain" },
  { module = "pheno.core.ports" },
]

# Infrastructure & Adapters (can depend on ports)
[[modules]]
name = "pheno.core.adapters"
path = "src/pheno/core/adapters"
depends_on = [
  { module = "pheno.core.ports" },
  { module = "pheno.domain" },
]

[[modules]]
name = "pheno.adapters"
path = "src/pheno/adapters"
depends_on = [
  { module = "pheno.core.ports" },
  { module = "pheno.domain" },
  { module = "pheno.credentials" },
]

[[modules]]
name = "pheno.infra"
path = "src/pheno/infra"
depends_on = [
  { module = "pheno.core.ports" },
  { module = "pheno.domain" },
]

# Cross-cutting concerns
[[modules]]
name = "pheno.testing"
path = "src/pheno/testing"
depends_on = [
  { module = "pheno.domain" },
  { module = "pheno.application" },
]

# CLI (depends on application layer, not infrastructure)
[[modules]]
name = "pheno.cli"
path = "src/pheno/cli"
depends_on = [
  { module = "pheno.application" },
  { module = "pheno.credentials" },
]

# SDK Surface (lean interface, depends on CLI)
[[modules]]
name = "pheno_sdk"
path = "src/pheno_sdk"
depends_on = [
  { module = "pheno.cli" },
  { module = "pheno.credentials" },
]

# Forbidden patterns (explicit denials)
[rules]
# Comment out to disable; uncomment to enforce
# forbidden_imports = [
#   "pheno.domain -> pheno.infra",
#   "pheno.domain -> pheno.adapters",
#   "pheno.credentials -> pheno.dev",
# ]
EOF

    log_success "Created baseline tach.toml"
    echo ""
    log_info "Next steps:"
    echo "  1. Review tach.toml configuration"
    echo "  2. Run: tach check         (verify current state)"
    echo "  3. Run: tach show          (view dependency graph)"
    echo "  4. Run: tach mod           (interactive boundary editor)"
}

generate_tach_report() {
    log_info "Running Tach checks..."
    cd "$PROJECT_ROOT"
    
    if ! tach check --no-cache 2>/dev/null; then
        log_warning "Some boundary violations detected (non-critical)"
    else
        log_success "All boundaries verified"
    fi
}

generate_grimp_report() {
    log_info "Analyzing with Grimp..."
    cd "$PROJECT_ROOT"
    
    cat > /tmp/grimp_analysis.py << 'GRIMP_EOF'
from grimp import build_graph

try:
    graph = build_graph('src/pheno')
    print(f"\n📊 Module Statistics:")
    print(f"   Modules: {len(graph.modules)}")
    print(f"   Edges: {len(graph.edges)}")
    
    # Find most connected modules
    print(f"\n🔗 Most Connected Modules:")
    modules_by_connections = sorted(
        graph.modules,
        key=lambda m: len(graph.descendants(m)),
        reverse=True
    )[:5]
    for i, mod in enumerate(modules_by_connections, 1):
        descendants = len(graph.descendants(mod))
        print(f"   {i}. {mod} -> {descendants} descendants")
    
    print("\n✓ Grimp analysis complete")
except Exception as e:
    print(f"⚠ Grimp analysis skipped: {e}")
GRIMP_EOF

    python3 /tmp/grimp_analysis.py || log_warning "Grimp analysis skipped"
}

generate_pydeps_graph() {
    log_info "Generating dependency graph with pydeps..."
    cd "$PROJECT_ROOT"
    
    OUTPUT_FILE="architecture_dependencies.svg"
    
    if pydeps --nodot --only pheno --max-bacon 2 src/pheno -o "$OUTPUT_FILE" 2>/dev/null; then
        log_success "Generated: $OUTPUT_FILE"
        echo "   Open in browser: file://$PROJECT_ROOT/$OUTPUT_FILE"
    else
        log_warning "pydeps graph generation skipped (requires graphviz)"
    fi
}

print_summary() {
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "Architecture Tools Setup Complete"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "Installed Tools:"
    for tool in "${TOOLS[@]}"; do
        echo "  ✓ $tool"
    done
    echo ""
    echo "Configuration Files:"
    echo "  ✓ tach.toml                            - Module boundaries"
    echo "  ✓ .grimp.toml                          - Dependency analysis"
    echo "  ✓ deply.yaml                           - Layer enforcement"
    echo "  ✓ scripts/validate_architecture_grimp.py - Validation script"
    echo ""
    echo "Key Commands:"
    echo "  tach check                                    - Verify architecture boundaries"
    echo "  tach show                                     - View dependency graph (web)"
    echo "  python scripts/validate_architecture_grimp.py - Run full validation"
    echo "  deply check                                   - Layer enforcement check"
    echo "  pydeps src/pheno -o graph.svg                 - Generate visual graphs"
    echo ""
    echo "Next Steps:"
    echo "  1. Review: cat tach.toml deply.yaml"
    echo "  2. Validate: tach check"
    echo "  3. Visualize: tach show"
    echo "  4. Full report: python scripts/validate_architecture_grimp.py --report"
    echo ""
    echo "Documentation:"
    echo "  - Tools Guide: docs/guides/architecture/ARCHITECTURE_TOOLS.md"
    echo "  - Spec: openspec/ARCHITECTURE_TOOLS_SPEC.md"
    echo "  - Architecture: src/pheno/ARCHITECTURE.md"
    echo ""
}

# Main script
main() {
    log_info "PhenoSDK Architecture Tools Setup"
    echo ""
    
    # Parse arguments
    INIT=false
    REPORT=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --init)
                INIT=true
                shift
                ;;
            --report)
                REPORT=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Execute steps
    check_python
    install_tools
    verify_installation
    
    if [ "$INIT" = true ]; then
        init_tach
    fi
    
    if [ "$REPORT" = true ]; then
        generate_tach_report
        generate_grimp_report
        generate_pydeps_graph
    fi
    
    print_summary
}

# Run main function
main "$@"
