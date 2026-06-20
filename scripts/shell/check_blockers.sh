#!/bin/bash
################################################################################
# Blocker SLA Checker
#
# Monitors active blockers for SLA violations
# Runs every 30 minutes via GitHub Actions or as cron job
# Outputs violations and triggers escalation if needed
#
# Usage:
#   bash scripts/check_blockers.sh
#   # Run manually to check current status
#
#   # In GitHub Actions (.github/workflows/escalation-monitor.yml):
#   - name: Check blocker SLAs
#     run: bash scripts/check_blockers.sh
#
# Exit codes:
#   0 = All blockers within SLA
#   1 = One or more blockers past SLA
################################################################################

set -e

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STANDUP_LOG="${PROJECT_DIR}/DAILY_STANDUP_LOG.md"
ESCALATION_LOG="${PROJECT_DIR}/.escalation_log"
VIOLATIONS_FILE="${PROJECT_DIR}/.blocker_violations"

# SLA thresholds (in minutes)
TIER1_SLA=120      # 2 hours
TIER2_SLA=240      # 4 hours
TIER3_SLA=480      # 8 hours

# Tracking
VIOLATIONS=0
CURRENT_TIME=$(date +%s)
TODAY=$(date +%Y-%m-%d)

################################################################################
# Utility Functions
################################################################################

print_header() {
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║ Blocker SLA Checker - $(date +'%Y-%m-%d %H:%M:%S')"
    echo "╚════════════════════════════════════════════════════════════════╝"
}

print_info() {
    echo "[INFO] $1"
}

print_warning() {
    echo "[WARNING] $1"
}

print_error() {
    echo "[ERROR] $1"
}

print_violation() {
    echo "🚨 [VIOLATION] $1"
}

get_timestamp_seconds() {
    # Convert "HH:MM, Date" format to seconds since epoch
    local time_str="$1"
    local date_str="$2"

    # Simple conversion (assumes today's date if not specified)
    if [[ -z "$date_str" ]]; then
        date_str=$(date +%Y-%m-%d)
    fi

    # Parse HH:MM format
    local hour=$(echo "$time_str" | cut -d: -f1)
    local minute=$(echo "$time_str" | cut -d: -f2 | cut -d, -f1)

    # Convert to seconds
    date -d "${date_str} ${hour}:${minute}:00" +%s 2>/dev/null || echo 0
}

minutes_elapsed() {
    local start_seconds=$1
    local current_seconds=$2

    if [[ $start_seconds -eq 0 ]]; then
        echo 0
    else
        echo $(((current_seconds - start_seconds) / 60))
    fi
}

check_sla_status() {
    local tier=$1
    local elapsed_minutes=$2

    case $tier in
        1)
            if [[ $elapsed_minutes -gt $TIER1_SLA ]]; then
                echo "VIOLATED"
            else
                echo "OK"
            fi
            ;;
        2)
            if [[ $elapsed_minutes -gt $TIER2_SLA ]]; then
                echo "VIOLATED"
            else
                echo "OK"
            fi
            ;;
        3)
            if [[ $elapsed_minutes -gt $TIER3_SLA ]]; then
                echo "VIOLATED"
            else
                echo "OK"
            fi
            ;;
        *)
            echo "UNKNOWN"
            ;;
    esac
}

################################################################################
# Main Logic
################################################################################

main() {
    print_header

    if [[ ! -f "$STANDUP_LOG" ]]; then
        print_error "Standup log not found: $STANDUP_LOG"
        return 1
    fi

    print_info "Scanning for active blockers..."

    # Clear violations file
    > "$VIOLATIONS_FILE"

    # Extract all BLOCKER entries from standup log
    # Pattern: BLOCKER: [description]
    #          - Category: [category]
    #          - Reported: [time], [date]
    #          - Tier: [1|2|3]
    #          - Owner: [name]

    local blocker_count=0
    local violations_count=0

    while IFS= read -r line; do
        if [[ "$line" =~ ^BLOCKER:\ (.+)$ ]]; then
            ((blocker_count++))
            local blocker_title="${BASH_REMATCH[1]}"
            local category=""
            local reported_time=""
            local reported_date=""
            local tier=1
            local owner=""

            print_info "Processing: $blocker_title"

            # Read next 5 lines for blocker details
            for i in {1..5}; do
                read -r detail_line || break

                if [[ "$detail_line" =~ Category:\ (.+) ]]; then
                    category="${BASH_REMATCH[1]}"
                elif [[ "$detail_line" =~ Reported:\ ([0-9:]+),?\ ?([0-9-]*) ]]; then
                    reported_time="${BASH_REMATCH[1]}"
                    reported_date="${BASH_REMATCH[2]}"
                elif [[ "$detail_line" =~ Tier:\ ([0-9]) ]]; then
                    tier="${BASH_REMATCH[1]}"
                elif [[ "$detail_line" =~ Owner:\ (.+) ]]; then
                    owner="${BASH_REMATCH[1]}"
                fi
            done

            # Validate required fields
            if [[ -z "$reported_time" ]]; then
                print_warning "Blocker missing 'Reported' field: $blocker_title"
                continue
            fi

            # Calculate elapsed time
            local start_seconds=$(get_timestamp_seconds "$reported_time" "$reported_date")
            if [[ $start_seconds -eq 0 ]]; then
                print_warning "Could not parse timestamp for: $blocker_title"
                continue
            fi

            local elapsed=$(minutes_elapsed "$start_seconds" "$CURRENT_TIME")

            # Get SLA threshold for this tier
            local sla_threshold
            case $tier in
                1) sla_threshold=$TIER1_SLA ;;
                2) sla_threshold=$TIER2_SLA ;;
                3) sla_threshold=$TIER3_SLA ;;
                *) sla_threshold=999999 ;;
            esac

            # Check SLA status
            local sla_status=$(check_sla_status "$tier" "$elapsed")

            # Format output
            echo ""
            echo "  Title: $blocker_title"
            echo "  Category: $category"
            echo "  Tier: $tier"
            echo "  Owner: $owner"
            echo "  Reported: $reported_time $reported_date"
            echo "  Elapsed: ${elapsed}m / SLA: ${sla_threshold}m"
            echo "  Status: $sla_status"

            # Record violations
            if [[ "$sla_status" == "VIOLATED" ]]; then
                ((violations_count++))
                ((VIOLATIONS++))

                print_violation "$blocker_title (Tier $tier, elapsed ${elapsed}m > ${sla_threshold}m)"

                # Log violation
                echo "$(date -Iseconds): BLOCKER '$blocker_title' (Tier $tier) elapsed ${elapsed}m, SLA ${sla_threshold}m" >> "$VIOLATIONS_FILE"

                # Recommend escalation
                local new_tier=$((tier + 1))
                if [[ $new_tier -le 4 ]]; then
                    print_warning "RECOMMEND: Escalate to Tier $new_tier"
                    echo "ESCALATE_TO_TIER: $new_tier" >> "$VIOLATIONS_FILE"
                else
                    print_error "CRITICAL: Blocker exceeds Tier 3 SLA - IMMEDIATE ACTION REQUIRED"
                    echo "CRITICAL: Blocker at max tier" >> "$VIOLATIONS_FILE"
                fi
            fi
        fi
    done < "$STANDUP_LOG"

    # Summary
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║ Summary"
    echo "╠════════════════════════════════════════════════════════════════╣"
    echo "║ Blockers Found:    $blocker_count"
    echo "║ Violations:        $violations_count"
    echo "║ Status:            $([ $violations_count -eq 0 ] && echo 'ALL OK ✓' || echo 'VIOLATIONS FOUND ✗')"
    echo "╚════════════════════════════════════════════════════════════════╝"

    print_info "Violations log: $VIOLATIONS_FILE"

    # Generate GitHub Actions summary if in CI
    if [[ -n "$GITHUB_STEP_SUMMARY" ]]; then
        echo "## Blocker SLA Check - $(date +'%Y-%m-%d %H:%M:%S')" >> "$GITHUB_STEP_SUMMARY"
        echo "" >> "$GITHUB_STEP_SUMMARY"
        echo "| Metric | Value |" >> "$GITHUB_STEP_SUMMARY"
        echo "|--------|-------|" >> "$GITHUB_STEP_SUMMARY"
        echo "| Blockers Found | $blocker_count |" >> "$GITHUB_STEP_SUMMARY"
        echo "| SLA Violations | $violations_count |" >> "$GITHUB_STEP_SUMMARY"
        echo "| Status | $([ $violations_count -eq 0 ] && echo '✓ OK' || echo '✗ VIOLATIONS') |" >> "$GITHUB_STEP_SUMMARY"
    fi

    # Return appropriate exit code
    if [[ $VIOLATIONS -gt 0 ]]; then
        print_error "One or more blockers exceeded SLA"
        return 1
    else
        print_info "All blockers within SLA"
        return 0
    fi
}

################################################################################
# Execution
################################################################################

main "$@"
exit $?
