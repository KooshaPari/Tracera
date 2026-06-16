# Check existence of modified files on integration/consolidate
$files = @(
  ".github/workflows/chromatic.yml",
  ".github/workflows/test-validation.yml",
  "backend/internal/handlers/binder.go",
  "backend/internal/services/integration_test_setup.go",
  "backend/internal/services/integration_tests.go",
  "backend/tests/coordination_test.go",
  "backend/tests/integration/comprehensive_scenarios_integration_test.go",
  "backend/tests/integration/cross_package_integration_test.go",
  "backend/tests/integration/event_test.go",
  "backend/tests/integration/external_services_integration_test.go",
  "backend/tests/integration/integration_common_test.go",
  "backend/tests/integration_test.go",
  "backend/tests/item_handler_test.go",
  "backend/tests/link_handler_test.go",
  "backend/tests/progress_metrics_test.go",
  "backend/tests/security_test.go",
  "backend/tests/service_performance_test.go",
  "backend/tests/validation_smoke_test.go",
  "backend/tests/validation_test.go"
)

foreach ($f in $files) {
  $result = git show "integration/consolidate:`"$f`"" 2>&1 | Select-Object -First 1
  if ($result -match "fatal:") {
    Write-Host "DELETED in consolidate: $f"
  } else {
    Write-Host "EXISTS in consolidate:  $f"
  }
}

# Also check the two "Added" files to confirm they are new
Write-Host "`n--- New files (Added) on feature branch ---"
foreach ($f in @("backend/tests/api_setup_test.go", "backend/tests/integration_setup_test.go")) {
  $result = git show "integration/consolidate:`"$f`"" 2>&1 | Select-Object -First 1
  if ($result -match "fatal:") {
    Write-Host "NOT on consolidate (new file): $f"
  } else {
    Write-Host "EXISTS on consolidate:       $f"
  }
}
