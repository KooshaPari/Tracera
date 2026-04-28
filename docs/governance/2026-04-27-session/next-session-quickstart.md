# Next-Session Quickstart (continuing 2026-04-27 work)

## Load context fast
1. Read `MEMORY.md` for index
2. Read `feedback_only_parent_claude.md` + `feedback_never_idle_never_hold.md` (mandates)
3. Read `repos/docs/governance/2026-04-27-session/turn-summary.md` for what was just done
4. Read `repos/docs/governance/2026-04-27-session/residuals-tracker.md` for open work

## First commands to run
```bash
# Check disk + omniroute
df -h /
curl -sf http://localhost:20128/v1/models -o /dev/null && echo "omniroute UP"

# Check GH rate limit
gh api rate_limit --jq '.resources.core.remaining'

# Org alert state
for r in $(gh repo list KooshaPari --limit 100 --no-archived --json name --jq '.[].name'); do
  c=$(gh api repos/KooshaPari/$r/dependabot/alerts --paginate --jq '[.[] | select(.state=="open")] | length' 2>/dev/null)
  if [[ "$c" =~ ^[0-9]+$ ]] && [ "$c" -gt 0 ]; then echo "$r:$c"; fi
done | sort -t: -k2 -n -r | head -15

# PR queue
gh search prs --owner KooshaPari --state open --limit 100 --json url,isDraft,author \
  --jq '.[] | select(.isDraft==false and (.author.login | startswith("app/dependabot") | not)) | .url'
```

## Top priorities (residuals from 2026-04-27)
1. **PhenoProject 30 npm overrides** — manual peerDep walkthrough; complex
2. **HexaKit 18 rust transitives** — `cargo update --precise` per residual; cookbook in `hexakit-residuals-cookbook.md`
3. **heliosCLI 18 mixed** — uuid peerDep blocker; needs manifest edit
4. **pheno 19** — submodule URL config fix as separate small PR
5. **CRIT verification** — verify org-wide CRIT count is now 0 post-session merges

## Worker tiers usable
- `dispatch-worker --tier minimax-direct` — fast, paid (low cost)
- `dispatch-worker --tier kimi-direct` — routes to gpt-oss-120b free
- `dispatch-worker --tier freetier` — minimax 2.5 free
- BROKEN: codex-mini (no openai creds), gemini (404)

## Reusable scripts available
- `repos/docs/scripts/lockfile-regen/lockfile_regen_v2.sh <repo> <alerts> [suffix]`
- `repos/docs/scripts/lockfile-regen/branch_cleanup_wide.sh <repo>`

## DO NOT
- Use `Agent` tool with claude general-purpose subagent (FORBIDDEN per regime)
- End a turn with "holding for wakeup" — always dispatch
- Revert these governance docs without user instruction
