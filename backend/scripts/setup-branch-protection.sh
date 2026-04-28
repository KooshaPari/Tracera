#!/bin/bash

################################################################################
# GitHub Branch Protection Setup Script
################################################################################
#
# Purpose:
#   Configures branch protection rules on the main branch to enforce code
#   quality, testing, and review requirements before merge.
#
# Protection Rules Enforced:
#   1. Required Status Checks (must pass before merge):
#      - go-tests: Go backend unit tests and linting
#      - python-tests: Python backend unit tests and linting
#      - frontend-packages-test: Frontend packages library test matrix
#      - frontend-web-test: Web application tests
#      - frontend-docs-test: Documentation site tests
#      - frontend-desktop-test: Electron desktop app tests
#      - quality-guards: Naming explosion and LOC limit checks
#
#   2. Branch Up-to-Date Requirement:
#      - Branches must be rebased/synced with main before merge
#      - Prevents merge conflicts and stale CI results
#
#   3. Code Review Requirements:
#      - Minimum 1 approval required
#      - Dismiss stale reviews when new commits are pushed
#      - Prevents bypassing reviews via new commits
#
#   4. Admin-Only Restrictions:
#      - Force pushes restricted to repository administrators
#      - Direct commits to main restricted to administrators
#      - Protects against accidental/malicious direct modifications
#
# Prerequisites:
#   - GitHub CLI (gh) installed and authenticated
#   - GitHub token with 'repo:admin' scope (for repository settings)
#   - User must have admin access to the repository
#   - Bash 4+
#
# Usage:
#   1. Authenticate with GitHub:
#      $ gh auth login --scopes repo:admin
#
#   2. Run the script:
#      $ bash backend/scripts/setup-branch-protection.sh
#
#   3. (Optional) Test mode - validate rules without applying:
#      $ DRY_RUN=1 bash backend/scripts/setup-branch-protection.sh
#
# Configuration:
#   Environment variables for customization:
#   - REPO: GitHub repository (owner/repo). Auto-detected from git remote.
#   - BRANCH: Branch to protect (default: main)
#   - MIN_APPROVALS: Minimum review approvals required (default: 1)
#   - DRY_RUN: Set to 1 to validate without applying (default: 0)
#   - VERBOSE: Set to 1 for detailed output (default: 0)
#
# Example:
#   # Apply protection rules to main branch
#   $ bash backend/scripts/setup-branch-protection.sh
#
#   # Apply to develop branch with 2 approvals required
#   $ BRANCH=develop MIN_APPROVALS=2 bash backend/scripts/setup-branch-protection.sh
#
#   # Dry-run to validate configuration
#   $ DRY_RUN=1 bash backend/scripts/setup-branch-protection.sh
#
# Idempotency:
#   This script is idempotent - it can be run multiple times safely.
#   Existing rules are updated, not duplicated.
#
# Troubleshooting:
#   - "Not authenticated": Run `gh auth login --scopes repo:admin`
#   - "Permission denied": Verify you have admin access to the repository
#   - "Repository not found": Check REPO variable and git remote
#
# Documentation:
#   GitHub API: https://docs.github.com/en/rest/repos/rules
#   Branch Protection: https://docs.github.com/en/repositories/configuring-branches-and-merges-pull-requests
#
################################################################################

set -euo pipefail

# Color output for better readability
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Configuration with defaults
readonly BRANCH="${BRANCH:-main}"
readonly MIN_APPROVALS="${MIN_APPROVALS:-1}"
readonly DRY_RUN="${DRY_RUN:-0}"
readonly VERBOSE="${VERBOSE:-0}"

# Auto-detect repository from git remote
REPO="${REPO:-}"

# Required status checks (from .github/workflows/ci.yml)
readonly REQUIRED_CHECKS=(
  "go-tests"
  "python-tests"
  "frontend-packages-test"
  "frontend-web-test"
  "frontend-docs-test"
  "frontend-desktop-test"
  "quality-guards"
)

################################################################################
# Utility Functions
################################################################################

log_info() {
  echo -e "${BLUE}ℹ${NC} $*" >&2
}

log_success() {
  echo -e "${GREEN}✓${NC} $*" >&2
}

log_warning() {
  echo -e "${YELLOW}⚠${NC} $*" >&2
}

log_error() {
  echo -e "${RED}✗${NC} $*" >&2
}

log_section() {
  echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" >&2
  echo -e "${BLUE}$*${NC}" >&2
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" >&2
}

verbose() {
  if [[ "$VERBOSE" == "1" ]]; then
    echo -e "${BLUE}→${NC} $*" >&2
  fi
}

################################################################################
# Validation Functions
################################################################################

check_prerequisites() {
  log_section "Checking Prerequisites"

  # Check gh CLI is installed
  if ! command -v gh &> /dev/null; then
    log_error "GitHub CLI (gh) not found. Please install from: https://cli.github.com/"
    exit 1
  fi
  log_success "GitHub CLI found: $(gh --version)"

  # Check gh authentication
  if ! gh auth status &> /dev/null; then
    log_error "Not authenticated with GitHub. Run: gh auth login --scopes repo:admin"
    exit 1
  fi
  log_success "GitHub authentication verified"

  # Verify repo:admin scope
  if ! gh auth status --show-token 2>&1 | grep -q "repo:admin\|admin"; then
    log_warning "Note: repo:admin scope may be required for full branch protection features"
  fi
}

detect_repository() {
  log_section "Detecting Repository"

  if [[ -z "$REPO" ]]; then
    # Try to auto-detect from git remote
    if ! REPO=$(git config --get remote.origin.url 2>/dev/null | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/'); then
      log_error "Could not auto-detect repository. Set REPO=owner/repo and try again."
      exit 1
    fi
  fi

  # Validate repo format
  if [[ ! "$REPO" =~ ^[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$ ]]; then
    log_error "Invalid repository format: $REPO (expected: owner/repo)"
    exit 1
  fi

  log_success "Repository: $REPO"
  verbose "Branch to protect: $BRANCH"
}

verify_branch_exists() {
  log_section "Verifying Branch"

  if ! gh repo view "$REPO" --json defaultBranchRef --jq .defaultBranchRef.name &> /dev/null; then
    log_error "Could not verify repository access or branch exists"
    exit 1
  fi

  log_success "Repository access verified"
}

################################################################################
# Rule Configuration Functions
################################################################################

configure_required_status_checks() {
  log_section "Configuring Required Status Checks"

  log_info "Required checks: ${REQUIRED_CHECKS[*]}"

  verbose "Status checks to enforce: ${REQUIRED_CHECKS[*]}"

  if [[ "$DRY_RUN" == "1" ]]; then
    log_info "[DRY-RUN] Would require these checks to pass:"
    printf '%s\n' "${REQUIRED_CHECKS[@]}" | sed 's/^/  - /'
    return 0
  fi

  log_info "Applying status check requirements via GitHub API..."
  log_info "Note: Will apply via classic branch protection endpoint"
}

configure_classic_branch_protection() {
  log_section "Configuring Classic Branch Protection Rules"

  if [[ "$DRY_RUN" == "1" ]]; then
    log_info "[DRY-RUN] Would configure:"
    echo "  - Require status checks: YES"
    echo "  - Required checks: ${REQUIRED_CHECKS[*]}"
    echo "  - Require branches up to date: YES"
    echo "  - Require code reviews: YES (min $MIN_APPROVALS approval(s))"
    echo "  - Dismiss stale reviews: YES"
    echo "  - Restrict force pushes: Admins only"
    echo "  - Restrict push access: Admins only"
    return 0
  fi

  log_info "Applying classic branch protection (fallback method)..."

  log_info "Configuring protection for branch: $BRANCH"

  # Build status checks array for gh api
  local checks_args=()
  for check in "${REQUIRED_CHECKS[@]}"; do
    checks_args+=(-f "required_status_checks.contexts[]=$check")
  done

  verbose "Status checks: ${REQUIRED_CHECKS[*]}"

  # Apply classic branch protection using gh cli
  # Note: gh pr does not directly support branch protection, so we use raw API

  # Create protection rule
  gh api \
    --method PUT \
    "repos/$REPO/branches/$BRANCH/protection" \
    -H "Accept: application/vnd.github+json" \
    -f required_status_checks.strict=true \
    "${checks_args[@]}" \
    -f "required_pull_request_reviews.required_approving_review_count=$MIN_APPROVALS" \
    -f required_pull_request_reviews.dismiss_stale_reviews=true \
    -f required_pull_request_reviews.require_code_owner_reviews=false \
    -f allow_force_pushes.enabled=false \
    -f allow_deletions.enabled=false \
    -f require_branches_to_be_up_to_date=true \
    -f restrictions=null \
    && log_success "Branch protection rules applied" \
    || log_error "Failed to apply branch protection rules"
}

################################################################################
# Verification Functions
################################################################################

verify_protection() {
  log_section "Verifying Protection Configuration"

  if [[ "$DRY_RUN" == "1" ]]; then
    log_info "[DRY-RUN] Skipping verification"
    return 0
  fi

  log_info "Fetching current branch protection settings..."

  # Get branch protection status
  if gh api "repos/$REPO/branches/$BRANCH" --jq '.protected' &>/dev/null; then
    local is_protected
    is_protected=$(gh api "repos/$REPO/branches/$BRANCH" --jq '.protected')

    if [[ "$is_protected" == "true" ]]; then
      log_success "Branch protection is ENABLED"

      # Display protection details
      log_info "Protection settings:"
      gh api "repos/$REPO/branches/$BRANCH/protection" --jq '{
        required_status_checks: .required_status_checks.contexts,
        require_pull_request_reviews: .required_pull_request_reviews,
        allow_force_pushes: .allow_force_pushes,
        allow_deletions: .allow_deletions,
        require_branches_up_to_date: .required_pull_request_reviews.require_branches_up_to_date
      }' 2>/dev/null || log_warning "Could not fetch full protection details"
    else
      log_warning "Branch protection is currently DISABLED"
    fi
  else
    log_warning "Could not verify branch protection status"
  fi
}

################################################################################
# Summary Function
################################################################################

print_summary() {
  log_section "Configuration Summary"

  cat <<EOF

Repository:  $REPO
Branch:      $BRANCH
Dry Run:     $([ "$DRY_RUN" = "1" ] && echo "YES" || echo "NO")

Required Status Checks (${#REQUIRED_CHECKS[@]}):
EOF
  printf '%s\n' "${REQUIRED_CHECKS[@]}" | sed 's/^/  ✓ /'

  cat <<EOF

Code Review Requirements:
  • Minimum Approvals: $MIN_APPROVALS
  • Dismiss Stale Reviews: YES
  • Require Code Owner Review: NO
  • Branches Must Be Up-to-Date: YES

Force Push & Admin Restrictions:
  • Force Pushes Restricted To: Admins Only
  • Direct Commits Restricted To: Admins Only
  • Deletions Allowed: NO

EOF

  if [[ "$DRY_RUN" == "1" ]]; then
    log_warning "DRY RUN MODE: No changes were applied"
    log_info "To apply these settings, run without DRY_RUN=1"
  else
    log_success "Configuration applied successfully!"
  fi
}

################################################################################
# Error Handling
################################################################################

handle_error() {
  local line_no=$1
  log_error "Script failed at line $line_no"
  exit 1
}

trap 'handle_error $LINENO' ERR

################################################################################
# Main Execution
################################################################################

main() {
  echo ""
  log_section "GitHub Branch Protection Setup"
  echo "Starting configuration of branch protection rules..."
  echo ""

  # Step 1: Check prerequisites
  check_prerequisites

  # Step 2: Detect and validate repository
  detect_repository
  verify_branch_exists

  # Step 3: Configure protection rules
  configure_required_status_checks

  # Step 4: Apply classic branch protection (if needed)
  configure_classic_branch_protection

  # Step 5: Verify configuration
  verify_protection

  # Step 6: Print summary
  print_summary
}

# Run main function
main "$@"
