#!/bin/bash

# Feature Flag Management CLI
# Usage: ./feature_flags.sh [get|set|enable|disable|list] <flag_name> [value]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env.integration ]; then
    export $(cat .env.integration | grep -v '^#' | grep REDIS_URL | xargs)
elif [ -f .env ]; then
    export $(cat .env | grep -v '^#' | grep REDIS_URL | xargs)
fi

if [ -z "$REDIS_URL" ]; then
    echo -e "${RED}Error: REDIS_URL not set${NC}"
    echo "Please set REDIS_URL in .env or .env.integration"
    exit 1
fi

ACTION=$1
FLAG=$2
VALUE=$3

FLAG_PREFIX="feature:flag:"

# Function to show usage
show_usage() {
    echo "Feature Flag Management CLI"
    echo ""
    echo "Usage:"
    echo "  ./feature_flags.sh get <flag_name>      - Get flag value"
    echo "  ./feature_flags.sh set <flag_name> <value>  - Set flag to 'true' or 'false'"
    echo "  ./feature_flags.sh enable <flag_name>   - Enable flag (set to 'true')"
    echo "  ./feature_flags.sh disable <flag_name>  - Disable flag (set to 'false')"
    echo "  ./feature_flags.sh list                 - List all feature flags"
    echo "  ./feature_flags.sh init                 - Initialize default flags"
    echo ""
    echo "Common Flags:"
    echo "  - nats_events              - Enable NATS event publishing"
    echo "  - cross_backend_calls      - Enable HTTP delegation"
    echo "  - shared_cache             - Enable Redis-compatible cache"
    echo "  - python_spec_analytics    - Use Python spec analytics service"
    echo "  - go_graph_analysis        - Use Go graph analysis service"
    echo "  - enhanced_logging         - Enable enhanced logging"
    echo "  - metrics_collection       - Enable metrics collection"
    echo "  - distributed_tracing      - Enable distributed tracing"
    echo ""
}

# Function to get flag
get_flag() {
    local flag_name=$1
    local result=$(redis-cli -u "$REDIS_URL" GET "${FLAG_PREFIX}${flag_name}" 2>&1)

    if [ $? -ne 0 ]; then
        echo -e "${RED}Error connecting to Redis-compatible cache${NC}"
        return 1
    fi

    if [ "$result" = "(nil)" ] || [ -z "$result" ]; then
        echo -e "${YELLOW}Flag '$flag_name' not set${NC}"
    else
        if [ "$result" = "true" ]; then
            echo -e "${GREEN}$flag_name: enabled${NC}"
        else
            echo -e "${BLUE}$flag_name: disabled${NC}"
        fi
    fi
}

# Function to set flag
set_flag() {
    local flag_name=$1
    local value=$2

    if [ "$value" != "true" ] && [ "$value" != "false" ]; then
        echo -e "${RED}Error: Value must be 'true' or 'false'${NC}"
        return 1
    fi

    redis-cli -u "$REDIS_URL" SET "${FLAG_PREFIX}${flag_name}" "$value" > /dev/null 2>&1

    if [ $? -eq 0 ]; then
        if [ "$value" = "true" ]; then
            echo -e "${GREEN}✓ Enabled flag '$flag_name'${NC}"
        else
            echo -e "${BLUE}✓ Disabled flag '$flag_name'${NC}"
        fi
    else
        echo -e "${RED}Error setting flag${NC}"
        return 1
    fi
}

# Function to list all flags
list_flags() {
    echo "Feature Flags:"
    echo "----------------------------------------------------------------------"

    local keys
    keys=$(redis-cli -u "$REDIS_URL" --scan --pattern "${FLAG_PREFIX}*" 2>&1)

    if [ $? -ne 0 ]; then
        echo -e "${RED}Error connecting to Redis-compatible cache${NC}"
        return 1
    fi

    if [ -z "$keys" ]; then
        echo -e "${YELLOW}No feature flags set${NC}"
        return 0
    fi

    # Process each key
    while IFS= read -r key; do
        if [ ! -z "$key" ]; then
            local flag_name=${key#$FLAG_PREFIX}
            local value=$(redis-cli -u "$REDIS_URL" GET "$key" 2>&1)

            if [ "$value" = "true" ]; then
                echo -e "  ${GREEN}✓${NC} $flag_name"
            else
                echo -e "  ${BLUE}✗${NC} $flag_name"
            fi
        fi
    done <<< "$keys"
}

# Function to initialize default flags
init_flags() {
    echo "Initializing default feature flags..."
    echo ""

    declare -A defaults=(
        ["nats_events"]="true"
        ["cross_backend_calls"]="true"
        ["shared_cache"]="true"
        ["python_spec_analytics"]="true"
        ["go_graph_analysis"]="true"
        ["enhanced_logging"]="false"
        ["metrics_collection"]="true"
        ["distributed_tracing"]="true"
    )

    for flag in "${!defaults[@]}"; do
        # Check if flag exists
        local existing=$(redis-cli -u "$REDIS_URL" GET "${FLAG_PREFIX}${flag}" 2>&1)

        if [ "$existing" = "(nil)" ] || [ -z "$existing" ]; then
            # Flag doesn't exist, set default
            set_flag "$flag" "${defaults[$flag]}"
        else
            echo -e "${YELLOW}⚠ Flag '$flag' already exists, skipping${NC}"
        fi
    done

    echo ""
    echo -e "${GREEN}Default flags initialized${NC}"
}

# Main command processing
case "$ACTION" in
    get)
        if [ -z "$FLAG" ]; then
            echo -e "${RED}Error: Flag name required${NC}"
            show_usage
            exit 1
        fi
        get_flag "$FLAG"
        ;;
    set)
        if [ -z "$FLAG" ] || [ -z "$VALUE" ]; then
            echo -e "${RED}Error: Flag name and value required${NC}"
            show_usage
            exit 1
        fi
        set_flag "$FLAG" "$VALUE"
        ;;
    enable)
        if [ -z "$FLAG" ]; then
            echo -e "${RED}Error: Flag name required${NC}"
            show_usage
            exit 1
        fi
        set_flag "$FLAG" "true"
        ;;
    disable)
        if [ -z "$FLAG" ]; then
            echo -e "${RED}Error: Flag name required${NC}"
            show_usage
            exit 1
        fi
        set_flag "$FLAG" "false"
        ;;
    list)
        list_flags
        ;;
    init)
        init_flags
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        echo -e "${RED}Error: Invalid action '$ACTION'${NC}"
        echo ""
        show_usage
        exit 1
        ;;
esac
