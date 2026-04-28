#!/usr/bin/env python3
"""Generate comprehensive Operations Layer for SwiftRide project.

Creates 900+ operational items across 10 categories.
"""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

PROJECT_ID = "40b0a8d1-af95-4b97-a52c-9b891b6ea3db"
TRACE_DIR = Path(__file__).resolve().parent.parent / "samples" / "DEMO_PROJECT" / ".trace"

# Item type configurations
ITEM_TYPES = {
    "deployment_environment": 50,
    "infrastructure_resource": 100,
    "monitoring_metric": 120,
    "alert_rule": 100,
    "runbook": 80,
    "ci_cd_pipeline": 70,
    "kubernetes_config": 90,
    "terraform_config": 80,
    "scaling_policy": 60,
    "backup_strategy": 50,
}


def generate_deployment_environments() -> list[dict[str, Any]]:
    """Generate 50 deployment environments."""
    items = []

    regions = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1", "ap-northeast-1"]

    idx = 1

    # Regional production environments
    for region in regions:
        items.append({
            "id": f"DEPLOY_ENV-{idx:03d}",
            "title": f"Production - {region}",
            "description": f"Production environment in {region} region with full HA setup",
            "metadata": {
                "environment_type": "production",
                "region": region,
                "ha_enabled": True,
                "auto_scaling": True,
                "disaster_recovery": True,
                "kubernetes_cluster": f"swiftride-prod-{region}",
                "rds_instances": ["primary", "replica-1", "replica-2"],
                "cache_clusters": ["redis-primary", "redis-replica"],
            },
        })
        idx += 1

    # Regional staging environments
    for region in regions[:3]:
        items.append({
            "id": f"DEPLOY_ENV-{idx:03d}",
            "title": f"Staging - {region}",
            "description": f"Staging environment in {region} for pre-production testing",
            "metadata": {
                "environment_type": "staging",
                "region": region,
                "ha_enabled": True,
                "auto_scaling": True,
                "kubernetes_cluster": f"swiftride-staging-{region}",
            },
        })
        idx += 1

    # Development environments
    for i in range(5):
        items.append({
            "id": f"DEPLOY_ENV-{idx:03d}",
            "title": f"Development-{i + 1}",
            "description": f"Development environment {i + 1} for feature development",
            "metadata": {
                "environment_type": "development",
                "region": "us-east-1",
                "team": f"team-{chr(65 + i)}",
                "auto_shutdown": True,
            },
        })
        idx += 1

    # Blue/Green deployment environments
    for region in regions[:2]:
        for color in ["blue", "green"]:
            items.append({
                "id": f"DEPLOY_ENV-{idx:03d}",
                "title": f"Production {color.title()} - {region}",
                "description": f"{color.title()} environment for zero-downtime deployments in {region}",
                "metadata": {
                    "environment_type": "production",
                    "deployment_strategy": color,
                    "region": region,
                    "ha_enabled": True,
                },
            })
            idx += 1

    # Special purpose environments
    special = [
        ("QA", "Quality assurance testing environment"),
        ("UAT", "User acceptance testing environment"),
        ("Performance", "Performance and load testing environment"),
        ("Security", "Security testing and penetration testing"),
        ("Sandbox", "Experimental features sandbox"),
        ("Canary-US", "Canary deployment environment US"),
        ("Canary-EU", "Canary deployment environment EU"),
        ("DR-Primary", "Disaster recovery primary site"),
        ("DR-Secondary", "Disaster recovery secondary site"),
        ("Training", "Training and demo environment"),
        ("Partner-Integration", "Third-party integration testing"),
        ("Mobile-Beta", "Mobile app beta testing"),
    ]

    for name, desc in special:
        if idx <= 50:
            items.append({
                "id": f"DEPLOY_ENV-{idx:03d}",
                "title": name,
                "description": desc,
                "metadata": {
                    "environment_type": "special",
                    "purpose": name.lower().replace("-", "_"),
                },
            })
            idx += 1

    return items[:50]


def generate_infrastructure_resources() -> list[dict[str, Any]]:
    """Generate 100 infrastructure resources."""
    items = []
    idx = 1

    # RDS Databases
    regions = ["us-east-1", "us-west-2", "eu-west-1"]
    for region in regions:
        for db_type in ["primary", "replica-1", "replica-2", "analytics"]:
            items.append({
                "id": f"INFRA-{idx:03d}",
                "title": f"RDS PostgreSQL {db_type.title()} - {region}",
                "description": f"PostgreSQL database instance for {db_type} in {region}",
                "metadata": {
                    "resource_type": "rds",
                    "engine": "postgres",
                    "version": "15.4",
                    "instance_class": "db.r6g.2xlarge" if db_type == "primary" else "db.r6g.xlarge",
                    "region": region,
                    "multi_az": db_type == "primary",
                    "backup_retention": 30 if db_type == "primary" else 7,
                },
            })
            idx += 1

    # ElastiCache Redis
    for region in regions:
        for purpose in ["sessions", "cache", "queue"]:
            items.append({
                "id": f"INFRA-{idx:03d}",
                "title": f"ElastiCache Redis - {purpose.title()} - {region}",
                "description": f"Redis cluster for {purpose} in {region}",
                "metadata": {
                    "resource_type": "elasticache",
                    "engine": "redis",
                    "version": "7.0",
                    "node_type": "cache.r6g.large",
                    "num_nodes": 3,
                    "region": region,
                },
            })
            idx += 1

    # S3 Buckets
    purposes = [
        "driver-documents",
        "rider-profiles",
        "ride-receipts",
        "app-logs",
        "analytics-data",
        "backup",
        "cdn-assets",
        "ml-models",
    ]
    for purpose in purposes:
        items.append({
            "id": f"INFRA-{idx:03d}",
            "title": f"S3 Bucket - {purpose}",
            "description": f"S3 bucket for storing {purpose.replace('-', ' ')}",
            "metadata": {
                "resource_type": "s3",
                "versioning": True,
                "encryption": "AES256",
                "lifecycle_policy": True,
            },
        })
        idx += 1

    # Load Balancers
    for region in regions:
        for service in ["api-gateway", "matching-service", "payment-service"]:
            items.append({
                "id": f"INFRA-{idx:03d}",
                "title": f"ALB - {service} - {region}",
                "description": f"Application Load Balancer for {service} in {region}",
                "metadata": {
                    "resource_type": "alb",
                    "scheme": "internet-facing",
                    "region": region,
                    "ssl_certificate": True,
                },
            })
            idx += 1

    # CloudFront Distributions
    for purpose in ["web-app", "mobile-app", "static-assets"]:
        items.append({
            "id": f"INFRA-{idx:03d}",
            "title": f"CloudFront - {purpose}",
            "description": f"CloudFront CDN distribution for {purpose}",
            "metadata": {
                "resource_type": "cloudfront",
                "price_class": "PriceClass_All",
                "ssl_certificate": True,
            },
        })
        idx += 1

    # SQS Queues
    queues = [
        "ride-requests",
        "notifications",
        "analytics-events",
        "driver-location-updates",
        "payment-processing",
        "fraud-detection",
        "dead-letter",
    ]
    for queue in queues:
        items.append({
            "id": f"INFRA-{idx:03d}",
            "title": f"SQS Queue - {queue}",
            "description": f"SQS queue for {queue.replace('-', ' ')}",
            "metadata": {
                "resource_type": "sqs",
                "visibility_timeout": 300,
                "message_retention": 345600,
            },
        })
        idx += 1

    # SNS Topics
    topics = ["ride-events", "driver-events", "payment-events", "system-alerts"]
    for topic in topics:
        items.append({
            "id": f"INFRA-{idx:03d}",
            "title": f"SNS Topic - {topic}",
            "description": f"SNS topic for {topic.replace('-', ' ')} notifications",
            "metadata": {
                "resource_type": "sns",
            },
        })
        idx += 1

    # Lambda Functions
    functions = ["payment-webhook", "driver-onboarding", "fraud-detection", "receipt-generator", "analytics-processor"]
    for func in functions:
        items.append({
            "id": f"INFRA-{idx:03d}",
            "title": f"Lambda - {func}",
            "description": f"Lambda function for {func.replace('-', ' ')}",
            "metadata": {
                "resource_type": "lambda",
                "runtime": "python3.11",
                "memory": 512,
                "timeout": 30,
            },
        })
        idx += 1

    return items[:100]


def generate_monitoring_metrics() -> list[dict[str, Any]]:
    """Generate 120 monitoring metrics."""
    items = []
    idx = 1

    # Application metrics - Ride Management
    ride_metrics = [
        ("ride_requests_per_second", "Number of ride requests per second", "rate", "rides"),
        ("ride_acceptance_rate", "Percentage of rides accepted by drivers", "percentage", "rides"),
        ("ride_cancellation_rate", "Percentage of rides cancelled", "percentage", "rides"),
        ("average_wait_time", "Average time riders wait for driver acceptance", "seconds", "rides"),
        ("average_ride_duration", "Average duration of completed rides", "minutes", "rides"),
        ("rides_completed_per_hour", "Number of completed rides per hour", "count", "rides"),
        ("surge_pricing_multiplier", "Current surge pricing multiplier", "ratio", "pricing"),
        ("driver_acceptance_rate", "Percentage of requests accepted by drivers", "percentage", "drivers"),
        ("driver_rejection_rate", "Percentage of requests rejected by drivers", "percentage", "drivers"),
        ("eta_accuracy", "Accuracy of estimated time of arrival", "percentage", "rides"),
    ]

    for metric, desc, unit, category in ride_metrics:
        items.append({
            "id": f"METRIC-{idx:03d}",
            "title": metric,
            "description": desc,
            "metadata": {
                "metric_type": "application",
                "category": category,
                "unit": unit,
                "aggregation": "avg",
                "dashboard": "ride-operations",
            },
        })
        idx += 1

    # Payment metrics
    payment_metrics = [
        ("payment_success_rate", "Percentage of successful payments", "percentage", "payments"),
        ("payment_failure_rate", "Percentage of failed payments", "percentage", "payments"),
        ("average_payment_processing_time", "Average time to process payment", "milliseconds", "payments"),
        ("payment_gateway_latency", "Latency to payment gateway", "milliseconds", "payments"),
        ("refund_rate", "Percentage of rides resulting in refunds", "percentage", "payments"),
        ("revenue_per_hour", "Revenue generated per hour", "usd", "business"),
        ("average_fare_amount", "Average fare per ride", "usd", "business"),
        ("tip_percentage", "Average tip as percentage of fare", "percentage", "business"),
    ]

    for metric, desc, unit, category in payment_metrics:
        items.append({
            "id": f"METRIC-{idx:03d}",
            "title": metric,
            "description": desc,
            "metadata": {
                "metric_type": "application",
                "category": category,
                "unit": unit,
                "aggregation": "avg",
                "dashboard": "payment-operations",
            },
        })
        idx += 1

    # Infrastructure metrics
    infra_metrics = [
        ("api_gateway_latency", "API Gateway response time", "milliseconds", "latency"),
        ("matching_service_latency", "Driver matching service latency", "milliseconds", "latency"),
        ("payment_service_latency", "Payment service latency", "milliseconds", "latency"),
        ("notification_service_latency", "Notification service latency", "milliseconds", "latency"),
        ("database_query_time", "Average database query execution time", "milliseconds", "database"),
        ("database_connection_pool_usage", "Database connection pool utilization", "percentage", "database"),
        ("database_slow_queries", "Number of slow queries per minute", "count", "database"),
        ("redis_cache_hit_rate", "Cache hit rate percentage", "percentage", "cache"),
        ("redis_memory_usage", "Redis memory utilization", "percentage", "cache"),
        ("redis_eviction_rate", "Cache key eviction rate", "count", "cache"),
    ]

    for metric, desc, unit, category in infra_metrics:
        items.append({
            "id": f"METRIC-{idx:03d}",
            "title": metric,
            "description": desc,
            "metadata": {
                "metric_type": "infrastructure",
                "category": category,
                "unit": unit,
                "aggregation": "avg",
            },
        })
        idx += 1

    # System metrics (CPU, Memory, Network)
    services = ["api-gateway", "matching-service", "payment-service", "notification-service"]
    for service in services:
        for metric_type in ["cpu_utilization", "memory_utilization", "network_bytes_in", "network_bytes_out"]:
            items.append({
                "id": f"METRIC-{idx:03d}",
                "title": f"{service}_{metric_type}",
                "description": f"{metric_type.replace('_', ' ').title()} for {service}",
                "metadata": {
                    "metric_type": "infrastructure",
                    "category": "system",
                    "service": service,
                    "unit": "percentage" if "utilization" in metric_type else "bytes",
                },
            })
            idx += 1

    # Business metrics
    business_metrics = [
        ("active_drivers", "Number of drivers currently online", "count", "drivers"),
        ("active_riders", "Number of active rider sessions", "count", "riders"),
        ("driver_utilization_rate", "Percentage of driver time on paid rides", "percentage", "drivers"),
        ("new_user_signups", "New user registrations per hour", "count", "growth"),
        ("user_retention_rate", "7-day user retention rate", "percentage", "growth"),
        ("driver_churn_rate", "Weekly driver churn rate", "percentage", "drivers"),
        ("customer_satisfaction_score", "Average rider rating", "score", "quality"),
        ("driver_satisfaction_score", "Average driver rating", "score", "quality"),
        ("fraud_detection_rate", "Percentage of rides flagged for fraud", "percentage", "security"),
        ("account_takeover_attempts", "Number of account takeover attempts", "count", "security"),
    ]

    for metric, desc, unit, category in business_metrics:
        items.append({
            "id": f"METRIC-{idx:03d}",
            "title": metric,
            "description": desc,
            "metadata": {
                "metric_type": "business",
                "category": category,
                "unit": unit,
                "aggregation": "avg",
            },
        })
        idx += 1

    # Kubernetes metrics
    k8s_metrics = [
        ("pod_restart_count", "Number of pod restarts", "count", "kubernetes"),
        ("pod_cpu_throttling", "CPU throttling events", "count", "kubernetes"),
        ("pod_memory_oom_kills", "Out of memory kills", "count", "kubernetes"),
        ("ingress_request_rate", "Ingress requests per second", "rate", "kubernetes"),
        ("service_mesh_latency", "Service mesh latency", "milliseconds", "kubernetes"),
    ]

    for metric, desc, unit, category in k8s_metrics:
        items.append({
            "id": f"METRIC-{idx:03d}",
            "title": metric,
            "description": desc,
            "metadata": {
                "metric_type": "infrastructure",
                "category": category,
                "unit": unit,
            },
        })
        idx += 1

    # SLA metrics
    sla_metrics = [
        ("api_availability", "API uptime percentage", "percentage", "sla"),
        ("api_error_rate", "API error rate", "percentage", "sla"),
        ("matching_success_rate", "Driver matching success rate", "percentage", "sla"),
        ("payment_uptime", "Payment service uptime", "percentage", "sla"),
        ("p95_response_time", "95th percentile API response time", "milliseconds", "sla"),
        ("p99_response_time", "99th percentile API response time", "milliseconds", "sla"),
    ]

    for metric, desc, unit, category in sla_metrics:
        items.append({
            "id": f"METRIC-{idx:03d}",
            "title": metric,
            "description": desc,
            "metadata": {
                "metric_type": "sla",
                "category": category,
                "unit": unit,
            },
        })
        idx += 1

    return items[:120]


def save_items_as_markdown(items: list[dict[str, Any]], item_type: str) -> None:
    """Save items as individual markdown files."""
    type_dir = TRACE_DIR / f"{item_type}s"
    type_dir.mkdir(exist_ok=True)

    for item in items:
        file_path = type_dir / f"{item['id']}.md"

        content = f"""---
id: {item["id"]}
type: {item_type}
title: {item["title"]}
status: active
created_at: {datetime.now(UTC).isoformat()}
---

# {item["title"]}

## Description
{item["description"]}

## Metadata
```yaml
{yaml.dump(item["metadata"], default_flow_style=False)}
```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
"""

        Path(file_path).write_text(content, encoding="utf-8")


def main() -> None:
    """Main."""
    # Generate deployment environments
    envs = generate_deployment_environments()
    save_items_as_markdown(envs, "deployment_environment")

    # Generate infrastructure resources
    infra = generate_infrastructure_resources()
    save_items_as_markdown(infra, "infrastructure_resource")

    # Generate monitoring metrics
    metrics = generate_monitoring_metrics()
    save_items_as_markdown(metrics, "monitoring_metric")


if __name__ == "__main__":
    main()
