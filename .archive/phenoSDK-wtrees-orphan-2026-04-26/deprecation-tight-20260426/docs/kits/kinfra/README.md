# Kinfra Documentation

## Overview

Kinfra (K Infrastructure) provides infrastructure as code management and orchestration capabilities, with abstractions over Terraform, Pulumi, and CloudFormation.

## Key Features

- **Multi-Tool Support**: Terraform, Pulumi, CloudFormation abstractions
- **State Management**: Centralized infrastructure state tracking
- **Resource Provisioning**: Declarative cloud resource management
- **Cost Optimization**: Cloud cost analysis and recommendations
- **Security Scanning**: Infrastructure security validation
- **Drift Detection**: Identify configuration drift

## Quick Start

```python
from pheno.infra.kinfra import InfraManager

# Initialize infrastructure manager
infra = InfraManager(
    backend="terraform",  # or "pulumi", "cloudformation"
    state_backend="s3",
    state_bucket="terraform-state"
)

# Define infrastructure
infrastructure = {
    "vpc": {
        "type": "aws_vpc",
        "cidr": "10.0.0.0/16",
        "enable_dns": True
    },
    "database": {
        "type": "aws_rds_instance",
        "engine": "postgres",
        "instance_class": "db.t3.micro",
        "allocated_storage": 20
    },
    "app_servers": {
        "type": "aws_instance",
        "count": 3,
        "instance_type": "t3.medium",
        "ami": "ami-12345678"
    }
}

# Apply infrastructure
result = await infra.apply(infrastructure)
print(f"Created {result.resources_created} resources")
```

## Terraform Abstraction

```python
from pheno.infra.kinfra import TerraformProvider

tf = TerraformProvider(
    working_dir="/infrastructure",
    auto_approve=False
)

# Initialize Terraform
await tf.init()

# Plan changes
plan = await tf.plan()
print(f"Will create: {plan.to_create}")
print(f"Will modify: {plan.to_modify}")
print(f"Will destroy: {plan.to_destroy}")

# Apply with approval
if await tf.confirm("Apply changes?"):
    await tf.apply()

# Get outputs
outputs = await tf.get_outputs()
print(f"Load balancer URL: {outputs['lb_url']}")
```

## Cost Optimization

```python
from pheno.infra.kinfra import CostOptimizer

optimizer = CostOptimizer()

# Analyze current costs
analysis = await optimizer.analyze_costs()
print(f"Current monthly cost: ${analysis.current_cost}")
print(f"Projected monthly cost: ${analysis.projected_cost}")

# Get recommendations
recommendations = await optimizer.get_recommendations()
for rec in recommendations:
    print(f"{rec.resource}: {rec.suggestion} (saves ${rec.monthly_savings})")

# Apply optimizations
if recommendations:
    await optimizer.apply_recommendations(recommendations)
```

## Security Scanning

```python
from pheno.infra.kinfra import SecurityScanner

scanner = SecurityScanner()

# Scan infrastructure
issues = await scanner.scan_infrastructure()

for issue in issues:
    print(f"{issue.severity}: {issue.resource}")
    print(f"  Issue: {issue.description}")
    print(f"  Fix: {issue.remediation}")

# Auto-remediate critical issues
critical = [i for i in issues if i.severity == "CRITICAL"]
await scanner.auto_remediate(critical)
```

## State Management

```python
# Import existing resources
await infra.import_resource(
    "aws_instance.app",
    "i-1234567890abcdef0"
)

# Lock state for operations
async with infra.state_lock():
    await infra.apply(changes)

# Backup and restore state
backup = await infra.backup_state()
await infra.restore_state(backup)
```

## Drift Detection

```python
# Check for drift
drift = await infra.detect_drift()

if drift.has_drift:
    print("Configuration drift detected:")
    for resource in drift.drifted_resources:
        print(f"  {resource.name}: {resource.drift_details}")

    # Reconcile drift
    await infra.reconcile_drift(drift)
```

## Multi-Cloud Support

```python
# AWS infrastructure
aws_infra = InfraManager(provider="aws", region="us-east-1")
await aws_infra.apply(aws_resources)

# GCP infrastructure
gcp_infra = InfraManager(provider="gcp", project="my-project")
await gcp_infra.apply(gcp_resources)

# Azure infrastructure
azure_infra = InfraManager(provider="azure", subscription="sub-123")
await azure_infra.apply(azure_resources)
```

---

*Full documentation: [Kinfra Guide](https://your-org.github.io/pheno-sdk/kits/kinfra)*
