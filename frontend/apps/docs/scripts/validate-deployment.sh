#!/bin/bash
set -e

# Validate deployment of documentation site
# Usage: ./validate-deployment.sh [url]

URL="${1:-https://docs.tracertm.com}"

BOLD="\033[1m"
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
NC="\033[0m"

print_header() {
  echo -e "${BOLD}====================================================${NC}"
  echo -e "${BOLD}  TraceRTM Documentation Deployment Validation${NC}"
  echo -e "${BOLD}====================================================${NC}\n"
  echo -e "${BOLD}Target URL:${NC} $URL\n"
}

print_success() {
  echo -e "${GREEN}✓${NC} $1"
}

print_error() {
  echo -e "${RED}✗${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}⚠${NC} $1"
}

ERRORS=0

check_url() {
  local path=$1
  local name=$2
  local expected_code=${3:-200}

  echo -n "Checking $name... "

  response=$(curl -s -o /dev/null -w "%{http_code}" "$URL$path" 2>/dev/null)

  if [ "$response" = "$expected_code" ]; then
    print_success "$name is accessible (HTTP $response)"
    return 0
  else
    print_error "$name returned HTTP $response (expected $expected_code)"
    ERRORS=$((ERRORS + 1))
    return 1
  fi
}

check_content() {
  local path=$1
  local name=$2
  local search_string=$3

  echo -n "Checking $name content... "

  content=$(curl -s "$URL$path" 2>/dev/null)

  if echo "$content" | grep -q "$search_string"; then
    print_success "$name contains expected content"
    return 0
  else
    print_error "$name does not contain expected content"
    ERRORS=$((ERRORS + 1))
    return 1
  fi
}

check_ssl() {
  echo -n "Checking SSL certificate... "

  if curl -s -I "$URL" 2>&1 | grep -q "SSL certificate"; then
    print_success "SSL certificate is valid"
    return 0
  else
    # If it's HTTPS and we got a response, SSL is probably fine
    if [[ "$URL" == https://* ]]; then
      response=$(curl -s -o /dev/null -w "%{http_code}" "$URL" 2>/dev/null)
      if [ "$response" = "200" ] || [ "$response" = "308" ]; then
        print_success "SSL is working (HTTPS accessible)"
        return 0
      fi
    fi
    print_warning "Could not verify SSL certificate"
    return 1
  fi
}

check_response_time() {
  local path=$1
  local max_time=${2:-2}

  echo -n "Checking response time for $path... "

  time=$(curl -s -o /dev/null -w "%{time_total}" "$URL$path" 2>/dev/null)
  time_ms=$(echo "$time * 1000" | bc)

  if (( $(echo "$time <= $max_time" | bc -l) )); then
    print_success "Response time: ${time_ms}ms (under ${max_time}s)"
    return 0
  else
    print_warning "Response time: ${time_ms}ms (over ${max_time}s threshold)"
    return 1
  fi
}

main() {
  print_header

  echo -e "${BOLD}Basic Accessibility Checks${NC}\n"
  check_url "/" "Homepage"
  check_url "/docs" "Documentation" "200"
  check_url "/api-reference" "API Reference"
  echo ""

  echo -e "${BOLD}API Endpoint Checks${NC}\n"
  check_url "/api/openapi.json" "OpenAPI JSON spec"
  check_url "/api/openapi.yaml" "OpenAPI YAML spec"
  echo ""

  echo -e "${BOLD}Content Validation${NC}\n"
  check_content "/" "Homepage" "TraceRTM"
  check_content "/api/openapi.json" "OpenAPI spec" "openapi"
  echo ""

  echo -e "${BOLD}Security Checks${NC}\n"
  check_ssl
  echo ""

  echo -e "${BOLD}Performance Checks${NC}\n"
  check_response_time "/" 2
  check_response_time "/api/openapi.json" 1
  echo ""

  echo -e "${BOLD}Header Checks${NC}\n"
  echo -n "Checking security headers... "
  headers=$(curl -s -I "$URL" 2>/dev/null)

  if echo "$headers" | grep -q "X-Content-Type-Options: nosniff"; then
    print_success "Security headers present"
  else
    print_warning "Some security headers may be missing"
  fi
  echo ""

  # Summary
  echo -e "${BOLD}====================================================${NC}"
  if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}${BOLD}✓ All checks passed!${NC}"
    echo -e "${BOLD}====================================================${NC}"
    exit 0
  else
    echo -e "${RED}${BOLD}✗ $ERRORS check(s) failed${NC}"
    echo -e "${BOLD}====================================================${NC}"
    exit 1
  fi
}

main
