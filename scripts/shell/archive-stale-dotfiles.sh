#!/usr/bin/env bash
set -euo pipefail
mkdir -p ARCHIVE/coordination-2026-06
git mv .CHECKPOINT_* ARCHIVE/coordination-2026-06/ 2>/dev/null || true
git mv .AWAITING_TEAM_LEAD_CLARIFICATION.txt ARCHIVE/coordination-2026-06/ 2>/dev/null || true
git mv .COORDINATOR_* ARCHIVE/coordination-2026-06/ 2>/dev/null || true
git mv .checkpoint-* ARCHIVE/coordination-2026-06/ 2>/dev/null || true
git mv .checkpoint*_* ARCHIVE/coordination-2026-06/ 2>/dev/null || true
git mv .BLOCKER_FIX_INSTRUCTIONS.md ARCHIVE/coordination-2026-06/ 2>/dev/null || true
echo "Archived stale coordination files. Review with: git status"
