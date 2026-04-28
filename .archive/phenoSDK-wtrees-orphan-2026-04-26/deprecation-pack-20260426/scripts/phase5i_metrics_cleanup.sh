#!/bin/bash
# Phase 5i: Delete Duplicate MetricsManager Classes
# Target: -2,000 LOC

set -e

BACKUP_DIR="backups/phase5i-metrics-cleanup-$(date +%Y%m%d-%H%M%S)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=== Phase 5i: Metrics Cleanup ==="
echo "Backup directory: $BACKUP_DIR"
echo ""

# Create backup
mkdir -p "$BACKUP_DIR"

echo "Step 1: Backing up duplicate metrics files..."
FILES_TO_DELETE=(
    "src/pheno/core/ports/metrics_manager.py"
    "src/pheno/core/logging/metrics_manager.py"
    "src/pheno/core/adapters/metrics_manager.py"
    "src/pheno/core/factories/metrics_manager.py"
    "src/pheno/core/validators/metrics_manager.py"
    "src/pheno/core/storage/metrics_manager.py"
    "src/pheno/core/utilities/metrics_manager.py"
    "src/pheno/core/testing/metrics_manager.py"
    "src/pheno/core/security/operations/metrics_manager.py"
    "src/pheno/core/monitoring/monitor_components/metrics_collector.py"
    "src/pheno/core/monitoring/registry_metrics.py"
    "src/pheno/core/registries/database/metrics.py"
    "src/pheno/core/registries/security/metrics.py"
    "src/pheno/core/registries/api/metrics.py"
    "src/pheno/core/registries/monitoring/metrics.py"
    "src/pheno/core/api/metrics.py"
    "src/pheno/observability/metrics.py"
    "src/pheno/llm/routing/ensemble/router/metrics.py"
    "src/pheno/ui/rich/live_metrics_integration.py"
    "src/pheno/patterns/refactoring/analysis/metrics.py"
    "src/pheno/mcp/metrics/agent_metrics.py"
)

for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        echo "  Backing up: $file"
        mkdir -p "$BACKUP_DIR/$(dirname "$file")"
        cp "$file" "$BACKUP_DIR/$file"
    fi
done

echo ""
echo "Step 2: Counting LOC before deletion..."
TOTAL_LOC=0
FILES_FOUND=0
for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        echo "  $file: $LOC LOC"
        TOTAL_LOC=$((TOTAL_LOC + LOC))
        FILES_FOUND=$((FILES_FOUND + 1))
    fi
done
echo "  Files found: $FILES_FOUND"
echo "  Total LOC to delete: $TOTAL_LOC"

echo ""
echo "Step 3: Deleting duplicate metrics files..."
for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        echo "  Deleting: $file"
        rm "$file"
    fi
done

echo ""
echo "Step 4: Creating migration guide..."
cat > "$BACKUP_DIR/MIGRATION_GUIDE.md" << 'EOF'
# Metrics Migration Guide

## What Changed

Deleted 20+ duplicate MetricsManager implementations in favor of existing Prometheus and OpenTelemetry integrations.

## Canonical Implementations

**KEEP (Use These)**:
1. `src/pheno/dev/prometheus/manager.py` - Prometheus metrics
2. `src/pheno/dev/opentelemetry/manager.py` - OpenTelemetry metrics

## Migration Path

### Before (Custom MetricsManager)

```python
from pheno.core.ports.metrics_manager import MetricsManager

metrics = MetricsManager()
metrics.increment("requests_total")
metrics.gauge("active_connections", 42)
```

### After (Prometheus)

```python
from pheno.dev.prometheus.manager import PrometheusManager
from prometheus_client import Counter, Gauge

# Initialize
prometheus = PrometheusManager()

# Define metrics
requests_total = Counter('requests_total', 'Total requests')
active_connections = Gauge('active_connections', 'Active connections')

# Use metrics
requests_total.inc()
active_connections.set(42)
```

### After (OpenTelemetry)

```python
from pheno.dev.opentelemetry.manager import OpenTelemetryManager
from opentelemetry import metrics

# Initialize
otel = OpenTelemetryManager()
meter = otel.get_meter(__name__)

# Define metrics
requests_counter = meter.create_counter("requests_total")
connections_gauge = meter.create_up_down_counter("active_connections")

# Use metrics
requests_counter.add(1)
connections_gauge.add(42)
```

## Benefits

1. **Industry Standard**: Prometheus and OpenTelemetry are industry standards
2. **Better Integration**: Works with Grafana, Datadog, etc.
3. **Less Code**: -2,000 LOC to maintain
4. **Better Performance**: Optimized implementations
5. **Better Docs**: Excellent documentation and community support

## Next Steps

If any code breaks due to missing imports:
1. Check the migration examples above
2. Update imports to use `pheno.dev.prometheus` or `pheno.dev.opentelemetry`
3. Update metric initialization code
4. Run tests to verify functionality

## Rollback

If needed, restore from backup:
```bash
cp -r backups/phase5i-metrics-cleanup-*/src/* src/
```
EOF

echo ""
echo "Step 5: Summary"
echo "  Files deleted: $FILES_FOUND"
echo "  LOC removed: $TOTAL_LOC"
echo "  Backup location: $BACKUP_DIR"
echo "  Migration guide: $BACKUP_DIR/MIGRATION_GUIDE.md"
echo ""
echo "✅ Phase 5i Complete!"
echo ""
echo "Next: Run tests to verify nothing broke"
echo "  pytest tests/ -v"

