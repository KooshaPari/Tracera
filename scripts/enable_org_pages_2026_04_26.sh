#!/usr/bin/env bash
# enable_org_pages_2026_04_26.sh
#
# Enable GitHub Pages for 5 product repos with Cloudflare CNAMEs but no Pages
# origin (origin 404 -> CF 530 error chain).
#
# Source audit: org_pages_status_2026_04_26_late.md (commit d954227f6d)
#
# WHAT THIS SCRIPT DOES:
#   * Verifies each repo has a Pages-deploy workflow on main.
#   * EMITS (commented-out) `gh api` calls to flip Pages source to "workflow".
#   * Verifies CF endpoint after enable (decommented).
#
# WHY COMMENTED OUT:
#   Enabling Pages is a user decision (build minutes, billing, branch source).
#   This script is a runbook -- review per-repo, uncomment, then execute.
#
# USAGE:
#   bash scripts/enable_org_pages_2026_04_26.sh check    # workflow audit only
#   # Then manually uncomment the `gh api ... -X POST` lines for repos you
#   # want to enable, and re-run with `enable`.
#   bash scripts/enable_org_pages_2026_04_26.sh enable
#   bash scripts/enable_org_pages_2026_04_26.sh verify   # curl CF endpoints

set -euo pipefail

OWNER="KooshaPari"
MODE="${1:-check}"

# repo : workflow_file : build_path : cf_host
REPOS=(
  "FocalPoint:docs.yml:./docs-site/.vitepress/dist:focalpoint.kooshapari.com"
  "PolicyStack:pages-deploy.yml:docs/.vitepress/dist:policystack.kooshapari.com"
  "Tokn:docs.yml:docs/.vitepress/dist/:tokn.kooshapari.com"
  "HeliosLab:deploy-docs.yml:./docs/.vitepress/dist:helioslab.kooshapari.com"
  "KDesktopVirt:NONE:NONE:kdesktopvirt.kooshapari.com"
)

check_workflow() {
  local repo="$1" wf="$2"
  if [[ "$wf" == "NONE" ]]; then
    echo "  [GAP] $repo: NO Pages-deploy workflow exists. Scaffold required before enable."
    return 1
  fi
  if [[ -f "$repo/.github/workflows/$wf" ]]; then
    echo "  [OK]  $repo: workflow $wf present"
    return 0
  fi
  echo "  [MISS] $repo: expected $repo/.github/workflows/$wf -- not found"
  return 1
}

cmd_check() {
  echo "== Workflow audit =="
  for entry in "${REPOS[@]}"; do
    IFS=: read -r repo wf path host <<<"$entry"
    check_workflow "$repo" "$wf" || true
  done
}

cmd_enable() {
  echo "== Enable Pages (workflow source) =="
  echo "All gh api calls below are COMMENTED. Uncomment per-repo to apply."
  echo ""

  # FocalPoint -- has docs.yml on main, builds ./docs-site/.vitepress/dist
  # gh api repos/${OWNER}/FocalPoint/pages -X POST \
  #   -F build_type=workflow \
  #   -f source[branch]=main -f source[path]=/

  # PolicyStack -- has pages-deploy.yml on main, builds docs/.vitepress/dist
  # gh api repos/${OWNER}/PolicyStack/pages -X POST \
  #   -F build_type=workflow \
  #   -f source[branch]=main -f source[path]=/

  # Tokn -- has docs.yml on main, builds docs/.vitepress/dist/
  # gh api repos/${OWNER}/Tokn/pages -X POST \
  #   -F build_type=workflow \
  #   -f source[branch]=main -f source[path]=/

  # HeliosLab -- has deploy-docs.yml on main, builds ./docs/.vitepress/dist
  # NOTE: deploy-docs.yml uses peaceiris/actions-gh-pages (gh-pages branch),
  # not actions/deploy-pages. Choose ONE:
  #   (a) Set source to gh-pages branch (legacy mode):
  # gh api repos/${OWNER}/HeliosLab/pages -X POST \
  #   -f source[branch]=gh-pages -f source[path]=/
  #   (b) Migrate workflow to actions/deploy-pages first, then:
  # gh api repos/${OWNER}/HeliosLab/pages -X POST \
  #   -F build_type=workflow -f source[branch]=main -f source[path]=/

  # KDesktopVirt -- NO Pages-deploy workflow exists.
  # Action required BEFORE enabling Pages:
  #   1. Add VitePress config + docs/package.json (currently raw .md only).
  #   2. Scaffold .github/workflows/deploy-pages.yml (template:
  #      thegent/templates/vitepress-full/.github/workflows/).
  #   3. Then run:
  # gh api repos/${OWNER}/KDesktopVirt/pages -X POST \
  #   -F build_type=workflow -f source[branch]=main -f source[path]=/

  echo "Done (no-op until uncommented)."
}

cmd_verify() {
  echo "== Cloudflare endpoint verification =="
  for entry in "${REPOS[@]}"; do
    IFS=: read -r repo wf path host <<<"$entry"
    code=$(curl -sI -o /dev/null -w "%{http_code}" "https://$host" || echo "ERR")
    echo "  $host -> HTTP $code"
  done
}

case "$MODE" in
  check) cmd_check ;;
  enable) cmd_enable ;;
  verify) cmd_verify ;;
  *) echo "usage: $0 {check|enable|verify}"; exit 2 ;;
esac

# -----------------------------------------------------------------------------
# RELATED: Tracera + heliosApp CF proxy fix (different failure mode)
# -----------------------------------------------------------------------------
# These two repos have HEALTHY Pages origins but BROKEN Cloudflare proxy
# (origin 200 / 301, CF returns 530 or wrong host).
# Fix path is NOT this script -- it lives in Cloudflare:
#
#   * Tracera: tracera.kooshapari.com
#       - Verify CNAME target = kooshapari.github.io (not <repo>.github.io
#         unless custom domain set in repo Pages settings)
#       - In repo Pages settings, set Custom domain = tracera.kooshapari.com
#         and tick "Enforce HTTPS".
#       - In CF DNS, ensure proxy=Proxied, SSL/TLS mode = Full (not Flexible).
#
#   * heliosApp: helios.kooshapari.com (or heliosapp.kooshapari.com -- confirm)
#       - Same procedure; verify the GH Pages custom domain matches the CF host.
#
# Audit reference: org_pages_status_2026_04_26_late.md "proxy-broken" cohort.
