#!/bin/bash
set -e

echo "Starting load tests..."

# Ensure backends are running
if ! curl -f http://localhost/health > /dev/null 2>&1; then
    echo "ERROR: Backends not running. Start with docker-compose up"
    exit 1
fi

# Create results directory
mkdir -p load-test-results

# Run tests
echo "1/6: Go Items CRUD..."
k6 run --out json=load-test-results/go-items.json load-tests/go-items.js

echo "2/6: Go Graph Operations..."
k6 run --out json=load-test-results/go-graph.json load-tests/go-graph.js

echo "3/6: Python Spec Analytics..."
k6 run --out json=load-test-results/python-specs.json load-tests/python-specs.js

echo "4/6: Python AI Streaming..."
k6 run --out json=load-test-results/python-ai.json load-tests/python-ai.js

echo "5/6: WebSocket Connections..."
k6 run --out json=load-test-results/websocket.json load-tests/websocket.js

echo "6/6: End-to-End Scenario..."
k6 run --out json=load-test-results/e2e-scenario.json load-tests/e2e-scenario.js

# Generate report
echo "Generating report..."
python3 scripts/generate_load_test_report.py load-test-results/

echo "Load tests complete! See load-test-results/report.html"
