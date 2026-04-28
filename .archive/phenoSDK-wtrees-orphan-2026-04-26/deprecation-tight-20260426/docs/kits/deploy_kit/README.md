# Deployment Kit Documentation

## Overview

The Deployment Kit provides comprehensive multi-cloud deployment automation for modern applications, supporting Vercel, AWS, Google Cloud, Azure, and other platforms with a unified interface.

## Key Features

- **Multi-Cloud Support**: Deploy to Vercel, AWS Lambda/ECS, GCP Cloud Run, Azure Functions
- **Zero-Downtime Deployments**: Blue-green and canary deployment strategies
- **Health Checks**: Automated health monitoring and rollback triggers
- **Configuration Management**: Environment-specific configs with secret handling
- **CI/CD Integration**: GitHub Actions, GitLab CI, Jenkins support
- **Infrastructure as Code**: Terraform and CloudFormation abstractions

## Quick Start

```python
from pheno.deployment import DeploymentManager, Platform

# Initialize deployment manager
deployer = DeploymentManager()

# Deploy to Vercel
await deployer.deploy(
    platform=Platform.VERCEL,
    project="my-app",
    environment="production",
    config={
        "regions": ["iad1", "sfo1"],
        "functions": {
            "api/*": {"maxDuration": 30}
        },
        "env": {
            "DATABASE_URL": "@database-url-secret"
        }
    }
)

# Deploy to AWS Lambda
await deployer.deploy(
    platform=Platform.AWS_LAMBDA,
    function_name="my-function",
    runtime="python3.11",
    handler="main.handler",
    memory=512,
    timeout=30
)
```

## Platform-Specific Features

### Vercel Deployment

```python
from pheno.deployment.platforms import VercelDeployer

vercel = VercelDeployer(token="vercel_token")

# Deploy with custom domains
deployment = await vercel.deploy(
    project="my-app",
    domains=["app.example.com", "www.app.example.com"],
    build_env={"NODE_ENV": "production"},
    functions_config={
        "api/endpoint": {
            "maxDuration": 60,
            "memory": 3008
        }
    }
)

# Monitor deployment
status = await vercel.get_deployment_status(deployment.id)
if status == "ready":
    print(f"Deployed to: {deployment.url}")
```

### AWS Deployment

```python
from pheno.deployment.platforms import AWSDeployer

aws = AWSDeployer(
    region="us-east-1",
    access_key_id="key",
    secret_access_key="secret"
)

# Deploy Lambda function
lambda_deployment = await aws.deploy_lambda(
    function_name="data-processor",
    code_uri="s3://bucket/code.zip",
    environment_variables={
        "STAGE": "production"
    },
    vpc_config={
        "SubnetIds": ["subnet-1", "subnet-2"],
        "SecurityGroupIds": ["sg-1"]
    }
)

# Deploy to ECS
ecs_deployment = await aws.deploy_ecs(
    cluster="production",
    service="api-service",
    task_definition="api-task:latest",
    desired_count=3
)
```

## Health Monitoring

```python
from pheno.deployment.checks import HealthCheck

health = HealthCheck(
    endpoints=[
        "https://api.example.com/health",
        "https://app.example.com/"
    ],
    interval=30,
    timeout=10,
    retries=3
)

# Start monitoring
await health.start_monitoring()

# Get status
status = await health.get_status()
for endpoint in status:
    print(f"{endpoint.url}: {endpoint.status} ({endpoint.response_time}ms)")
```

## Rollback Support

```python
# Automatic rollback on failure
deployment = await deployer.deploy(
    platform=Platform.VERCEL,
    project="my-app",
    rollback_on_failure=True,
    health_check_url="https://app.example.com/health",
    health_check_timeout=60
)

# Manual rollback
await deployer.rollback(deployment.id)
```

## Configuration Examples

```yaml
# deploy.yaml
deployments:
  production:
    platform: vercel
    project: my-app-prod
    regions: [iad1, sfo1, lhr1]
    env:
      NODE_ENV: production
      API_URL: https://api.example.com

  staging:
    platform: aws_lambda
    function: my-app-staging
    runtime: python3.11
    memory: 256
    timeout: 15
```

## Performance

- **3x faster deployments** with parallel operations
- **Zero-downtime** with blue-green deployments
- **Automatic rollback** within 30 seconds of failure
- **Multi-region** deployments in under 2 minutes

---

*Full documentation: [Deploy Kit Guide](https://your-org.github.io/pheno-sdk/kits/deploy)*
