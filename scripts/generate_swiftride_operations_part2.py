#!/usr/bin/env python3
"""
Generate remaining Operations Layer items for SwiftRide (Part 2).
Creates alert rules, runbooks, CI/CD pipelines, K8s configs, terraform, scaling policies, and backup strategies.
"""

import os
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

PROJECT_ID = "40b0a8d1-af95-4b97-a52c-9b891b6ea3db"
TRACE_DIR = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/DEMO_PROJECT/.trace")


def generate_alert_rules() -> List[Dict[str, Any]]:
    """Generate 100 alert rules."""
    items = []
    idx = 1

    # Critical alerts - Payment
    critical_payment_alerts = [
        ("payment_failures_exceed_5_percent", "Payment failure rate exceeds 5%", "critical",
         "payment_failure_rate > 5", "PagerDuty + Slack #incidents"),
        ("payment_gateway_down", "Payment gateway unreachable", "critical",
         "payment_gateway_latency > 30000 OR payment_gateway_errors > 10", "PagerDuty + SMS"),
        ("fraud_detection_high_risk", "High number of fraud attempts detected", "critical",
         "fraud_detection_rate > 10", "Security Team + PagerDuty"),
        ("refund_spike", "Abnormal spike in refund requests", "critical",
         "refund_rate > 20", "Finance Team + Slack"),
    ]

    for name, desc, severity, condition, notification in critical_payment_alerts:
        items.append({
            "id": f"ALERT-{idx:03d}",
            "title": name.replace("_", " ").title(),
            "description": desc,
            "metadata": {
                "severity": severity,
                "condition": condition,
                "notification_channels": notification,
                "category": "payment",
                "evaluation_period": "5m",
                "datapoints_to_alarm": 2,
            }
        })
        idx += 1

    # Critical alerts - Matching Service
    critical_matching_alerts = [
        ("no_available_drivers", "No drivers available in region", "critical",
         "active_drivers < 5", "Operations Team + PagerDuty"),
        ("matching_service_down", "Driver matching service unavailable", "critical",
         "matching_service_latency > 10000 OR errors > 50", "PagerDuty + Slack #oncall"),
        ("high_ride_rejection_rate", "Drivers rejecting >30% of requests", "critical",
         "driver_rejection_rate > 30", "Operations + Product"),
        ("matching_timeout_spike", "Matching timeouts exceeding threshold", "critical",
         "matching_timeouts > 20", "Engineering Team"),
    ]

    for name, desc, severity, condition, notification in critical_matching_alerts:
        items.append({
            "id": f"ALERT-{idx:03d}",
            "title": name.replace("_", " ").title(),
            "description": desc,
            "metadata": {
                "severity": severity,
                "condition": condition,
                "notification_channels": notification,
                "category": "matching",
                "evaluation_period": "3m",
            }
        })
        idx += 1

    # Critical alerts - Infrastructure
    critical_infra_alerts = [
        ("database_primary_down", "Primary database unreachable", "critical",
         "database_connections == 0", "DBA Team + PagerDuty"),
        ("database_replica_lag", "Database replica lag >60 seconds", "critical",
         "replica_lag_seconds > 60", "DBA Team"),
        ("redis_cluster_down", "Redis cluster unavailable", "critical",
         "redis_available_nodes < 2", "Platform Team + PagerDuty"),
        ("api_gateway_5xx_errors", "API Gateway 5xx error rate >5%", "critical",
         "api_5xx_error_rate > 5", "Platform + PagerDuty"),
    ]

    for name, desc, severity, condition, notification in critical_infra_alerts:
        items.append({
            "id": f"ALERT-{idx:03d}",
            "title": name.replace("_", " ").title(),
            "description": desc,
            "metadata": {
                "severity": severity,
                "condition": condition,
                "notification_channels": notification,
                "category": "infrastructure",
                "evaluation_period": "2m",
            }
        })
        idx += 1

    # Warning alerts - Performance
    warning_alerts = [
        ("high_latency_api_gateway", "API Gateway latency >500ms", "warning",
         "api_gateway_latency > 500", "Slack #performance"),
        ("high_latency_matching_service", "Matching service latency >2s", "warning",
         "matching_service_latency > 2000", "Slack #performance"),
        ("cache_hit_rate_low", "Cache hit rate below 80%", "warning",
         "redis_cache_hit_rate < 80", "Platform Team"),
        ("database_slow_queries", "High number of slow queries", "warning",
         "database_slow_queries > 50", "DBA Team + Slack"),
        ("high_cpu_utilization", "Service CPU usage >75%", "warning",
         "cpu_utilization > 75", "Platform Team"),
        ("high_memory_utilization", "Service memory usage >80%", "warning",
         "memory_utilization > 80", "Platform Team"),
        ("pod_restart_rate_high", "Kubernetes pods restarting frequently", "warning",
         "pod_restart_count > 5", "DevOps Team"),
    ]

    for name, desc, severity, condition, notification in warning_alerts:
        items.append({
            "id": f"ALERT-{idx:03d}",
            "title": name.replace("_", " ").title(),
            "description": desc,
            "metadata": {
                "severity": severity,
                "condition": condition,
                "notification_channels": notification,
                "category": "performance",
                "evaluation_period": "10m",
            }
        })
        idx += 1

    # Business metrics alerts
    business_alerts = [
        ("low_driver_supply", "Driver supply below demand", "warning",
         "active_drivers / active_riders < 0.3", "Operations Team"),
        ("high_cancellation_rate", "Ride cancellation rate >15%", "warning",
         "ride_cancellation_rate > 15", "Product + Operations"),
        ("customer_satisfaction_low", "Customer satisfaction below 4.5", "warning",
         "customer_satisfaction_score < 4.5", "Customer Success"),
        ("revenue_drop", "Revenue decreased >20% hour-over-hour", "critical",
         "revenue_per_hour_change < -20", "Finance + Leadership"),
        ("surge_pricing_active", "Surge pricing multiplier >2.0", "info",
         "surge_pricing_multiplier > 2.0", "Operations Dashboard"),
    ]

    for name, desc, severity, condition, notification in business_alerts:
        items.append({
            "id": f"ALERT-{idx:03d}",
            "title": name.replace("_", " ").title(),
            "description": desc,
            "metadata": {
                "severity": severity,
                "condition": condition,
                "notification_channels": notification,
                "category": "business",
                "evaluation_period": "15m",
            }
        })
        idx += 1

    # Security alerts
    security_alerts = [
        ("account_takeover_attempts", "Multiple failed login attempts", "critical",
         "failed_login_attempts > 100", "Security Team + PagerDuty"),
        ("ddos_attack_detected", "Potential DDoS attack in progress", "critical",
         "request_rate > 10000", "Security + Platform"),
        ("unauthorized_access_attempts", "Unauthorized API access attempts", "warning",
         "unauthorized_requests > 50", "Security Team"),
        ("data_breach_suspected", "Suspicious data access pattern", "critical",
         "bulk_data_access_detected == true", "Security + Legal + Leadership"),
    ]

    for name, desc, severity, condition, notification in security_alerts:
        items.append({
            "id": f"ALERT-{idx:03d}",
            "title": name.replace("_", " ").title(),
            "description": desc,
            "metadata": {
                "severity": severity,
                "condition": condition,
                "notification_channels": notification,
                "category": "security",
                "evaluation_period": "5m",
            }
        })
        idx += 1

    # SLA alerts
    sla_alerts = [
        ("sla_availability_breach", "API availability below 99.9%", "critical",
         "api_availability < 99.9", "Leadership + Operations"),
        ("sla_latency_breach", "P95 latency exceeds SLA", "critical",
         "p95_response_time > 1000", "Engineering + Product"),
        ("sla_error_rate_breach", "Error rate exceeds 1%", "critical",
         "api_error_rate > 1", "Engineering Team"),
    ]

    for name, desc, severity, condition, notification in sla_alerts:
        items.append({
            "id": f"ALERT-{idx:03d}",
            "title": name.replace("_", " ").title(),
            "description": desc,
            "metadata": {
                "severity": severity,
                "condition": condition,
                "notification_channels": notification,
                "category": "sla",
                "evaluation_period": "5m",
            }
        })
        idx += 1

    # Additional infrastructure alerts
    additional_infra = [
        ("s3_bucket_permission_change", "S3 bucket permissions modified", "warning"),
        ("rds_storage_low", "RDS storage utilization >85%", "warning"),
        ("elasticache_eviction_high", "High cache eviction rate", "warning"),
        ("sqs_queue_depth_high", "SQS queue depth >1000", "warning"),
        ("lambda_errors_high", "Lambda function error rate >5%", "warning"),
        ("cloudfront_4xx_errors", "CloudFront 4xx error spike", "info"),
        ("alb_unhealthy_targets", "Load balancer unhealthy target count >0", "warning"),
        ("vpc_flow_logs_stopped", "VPC flow logs not being delivered", "warning"),
        ("iam_policy_change", "IAM policy modified", "warning"),
        ("security_group_change", "Security group rules changed", "warning"),
    ]

    for name, desc, severity in additional_infra:
        items.append({
            "id": f"ALERT-{idx:03d}",
            "title": name.replace("_", " ").title(),
            "description": desc,
            "metadata": {
                "severity": severity,
                "category": "infrastructure",
                "notification_channels": "Slack #infrastructure",
                "evaluation_period": "5m",
            }
        })
        idx += 1

    # Cost alerts
    cost_alerts = [
        ("aws_cost_spike", "Daily AWS cost increased >30%", "warning",
         "aws_daily_cost_change > 30", "Finance + Engineering"),
        ("rds_cost_high", "RDS costs exceeding budget", "warning",
         "rds_monthly_cost > budget_threshold", "Finance Team"),
        ("data_transfer_cost_high", "High data transfer costs", "warning",
         "data_transfer_cost > 1000", "Platform Team"),
    ]

    for name, desc, severity, condition, notification in cost_alerts:
        items.append({
            "id": f"ALERT-{idx:03d}",
            "title": name.replace("_", " ").title(),
            "description": desc,
            "metadata": {
                "severity": severity,
                "condition": condition,
                "notification_channels": notification,
                "category": "cost",
                "evaluation_period": "1h",
            }
        })
        idx += 1

    return items[:100]


def generate_runbooks() -> List[Dict[str, Any]]:
    """Generate 80 runbooks."""
    items = []
    idx = 1

    runbooks_data = [
        # Database runbooks
        ("Database Failover Procedure", "Step-by-step guide for failing over to RDS replica", "database", "critical"),
        ("Database Backup Restoration", "How to restore database from backup", "database", "critical"),
        ("Database Performance Tuning", "Optimize slow queries and indexes", "database", "maintenance"),
        ("Database Connection Pool Reset", "Reset connection pools during connection issues", "database", "incident"),
        ("Database Replica Lag Investigation", "Diagnose and fix replica lag", "database", "incident"),

        # Scaling runbooks
        ("Scale Up During Peak Hours", "Increase capacity for expected traffic surge", "scaling", "operational"),
        ("Emergency Scale Up", "Rapid scaling during unexpected load", "scaling", "critical"),
        ("Scale Down Off-Peak", "Reduce capacity to optimize costs", "scaling", "operational"),
        ("Auto-Scaling Group Adjustment", "Modify ASG settings", "scaling", "maintenance"),

        # Incident response
        ("Payment Processor Outage Response", "Handle third-party payment gateway downtime", "incident", "critical"),
        ("API Gateway Failure Recovery", "Restore API Gateway service", "incident", "critical"),
        ("DDoS Attack Mitigation", "Steps to mitigate DDoS attacks", "security", "critical"),
        ("Data Breach Response", "Incident response for potential data breach", "security", "critical"),
        ("Service Degradation Investigation", "Diagnose performance degradation", "incident", "high"),

        # Deployment runbooks
        ("Blue-Green Deployment", "Execute zero-downtime blue-green deployment", "deployment", "operational"),
        ("Canary Deployment", "Gradual rollout with canary deployment", "deployment", "operational"),
        ("Rollback Procedure", "Rollback failed deployment", "deployment", "critical"),
        ("Database Migration During Deployment", "Run database migrations safely", "deployment", "high"),
        ("Feature Flag Rollout", "Enable feature flags progressively", "deployment", "operational"),

        # Monitoring and alerting
        ("Alert Fatigue Reduction", "Tune alert thresholds to reduce noise", "monitoring", "maintenance"),
        ("Dashboard Creation", "Create new monitoring dashboard", "monitoring", "operational"),
        ("Log Aggregation Setup", "Configure log shipping to central system", "monitoring", "operational"),
        ("Metric Collection Setup", "Add new application metrics", "monitoring", "operational"),

        # Security
        ("SSL Certificate Renewal", "Renew SSL/TLS certificates", "security", "maintenance"),
        ("Access Key Rotation", "Rotate AWS access keys", "security", "maintenance"),
        ("Security Patch Deployment", "Deploy critical security patches", "security", "critical"),
        ("Audit Log Investigation", "Investigate security audit logs", "security", "operational"),

        # Backup and recovery
        ("S3 Bucket Restoration", "Restore deleted S3 objects", "backup", "incident"),
        ("Point-in-Time Recovery", "Restore database to specific timestamp", "backup", "critical"),
        ("Disaster Recovery Drill", "Test disaster recovery procedures", "backup", "maintenance"),
        ("Cross-Region Backup Verification", "Verify backup replication", "backup", "operational"),

        # Performance
        ("Cache Warming", "Pre-populate cache after deployment", "performance", "operational"),
        ("CDN Cache Invalidation", "Invalidate CloudFront cache", "performance", "operational"),
        ("Query Performance Investigation", "Diagnose slow database queries", "performance", "operational"),
        ("Memory Leak Investigation", "Identify and fix memory leaks", "performance", "incident"),

        # Network
        ("VPN Connection Troubleshooting", "Fix VPN connectivity issues", "network", "operational"),
        ("DNS Configuration Update", "Update Route53 DNS records", "network", "operational"),
        ("Load Balancer Health Check", "Configure ALB health checks", "network", "operational"),
        ("Network Connectivity Troubleshooting", "Diagnose network issues", "network", "incident"),

        # Kubernetes
        ("Pod Restart Investigation", "Investigate frequent pod restarts", "kubernetes", "incident"),
        ("Kubernetes Node Drain", "Safely drain node for maintenance", "kubernetes", "maintenance"),
        ("Horizontal Pod Autoscaling", "Configure HPA for service", "kubernetes", "operational"),
        ("Kubernetes Secret Rotation", "Rotate Kubernetes secrets", "kubernetes", "security"),
        ("Service Mesh Configuration", "Configure Istio service mesh", "kubernetes", "operational"),

        # Application-specific
        ("Driver Matching Algorithm Tuning", "Optimize driver-rider matching", "application", "operational"),
        ("Surge Pricing Adjustment", "Manual surge pricing override", "application", "operational"),
        ("Fraud Detection Rule Update", "Update fraud detection rules", "application", "operational"),
        ("Payment Gateway Switching", "Switch to backup payment processor", "application", "critical"),
        ("Notification System Recovery", "Restore notification service", "application", "incident"),

        # Cost optimization
        ("Reserved Instance Planning", "Plan and purchase RIs", "cost", "operational"),
        ("Unused Resource Cleanup", "Identify and remove unused resources", "cost", "maintenance"),
        ("S3 Lifecycle Policy Setup", "Configure S3 object lifecycle", "cost", "operational"),
        ("CloudWatch Log Retention", "Adjust log retention policies", "cost", "maintenance"),

        # Compliance
        ("GDPR Data Export", "Export user data per GDPR request", "compliance", "operational"),
        ("GDPR Data Deletion", "Delete user data per GDPR request", "compliance", "operational"),
        ("Compliance Audit Preparation", "Prepare for compliance audit", "compliance", "operational"),
        ("PCI DSS Compliance Check", "Verify PCI DSS compliance", "compliance", "operational"),

        # Additional operational runbooks
        ("API Rate Limit Adjustment", "Modify API rate limiting", "api", "operational"),
        ("Webhook Endpoint Verification", "Verify webhook endpoints", "integration", "operational"),
        ("Third-Party Integration Health Check", "Test external integrations", "integration", "operational"),
        ("Mobile App Release Coordination", "Coordinate mobile app deployment", "deployment", "operational"),
        ("A/B Test Configuration", "Set up A/B test", "experimentation", "operational"),
        ("Customer Support Escalation", "Escalate critical customer issues", "support", "high"),
        ("On-Call Handoff Procedure", "Transfer on-call responsibilities", "operational", "operational"),
        ("Incident Postmortem Process", "Conduct incident postmortem", "process", "operational"),
        ("Chaos Engineering Exercise", "Run chaos engineering test", "testing", "operational"),
        ("Load Testing Execution", "Execute load test", "testing", "operational"),
        ("Capacity Planning Review", "Review and update capacity plans", "planning", "operational"),
        ("SLA Review Meeting", "Quarterly SLA review process", "process", "operational"),
        ("Architecture Decision Record", "Document architectural decision", "process", "operational"),
        ("Service Deprecation Plan", "Plan service deprecation", "planning", "operational"),
        ("New Region Launch", "Launch service in new region", "expansion", "high"),
        ("Partner API Onboarding", "Onboard new API partner", "integration", "operational"),
        ("Machine Learning Model Deployment", "Deploy new ML model", "ml", "operational"),
        ("Data Pipeline Failure Recovery", "Recover failed data pipeline", "data", "incident"),
        ("Analytics Dashboard Update", "Update business analytics dashboard", "analytics", "operational"),
    ]

    for title, description, category, priority in runbooks_data:
        items.append({
            "id": f"RUNBOOK-{idx:03d}",
            "title": title,
            "description": description,
            "metadata": {
                "category": category,
                "priority": priority,
                "last_updated": datetime.now().isoformat(),
                "owner_team": f"{category}-team",
                "estimated_duration": "30-60 minutes",
                "prerequisites": ["Access to AWS console", "kubectl access", "PagerDuty access"],
                "related_alerts": [],
            }
        })
        idx += 1

    return items[:80]


def save_items_as_markdown(items: List[Dict[str, Any]], item_type: str):
    """Save items as individual markdown files."""
    type_dir = TRACE_DIR / f"{item_type}s"
    type_dir.mkdir(exist_ok=True)

    for item in items:
        file_path = type_dir / f"{item['id']}.md"

        content = f"""---
id: {item['id']}
type: {item_type}
title: {item['title']}
status: active
created_at: {datetime.now().isoformat()}
---

# {item['title']}

## Description
{item['description']}

## Metadata
```yaml
{yaml.dump(item['metadata'], default_flow_style=False)}
```

## Links
- Related Services: (to be linked)
- Related Incidents: (to be linked)
- Related Features: (to be linked)
"""

        with open(file_path, 'w') as f:
            f.write(content)

    print(f"✓ Created {len(items)} {item_type} items in {type_dir}")


def main():
    print("Generating SwiftRide Operations Layer (Part 2)...\n")

    # Generate alert rules
    print("Generating alert rules...")
    alerts = generate_alert_rules()
    save_items_as_markdown(alerts, "alert_rule")

    # Generate runbooks
    print("Generating runbooks...")
    runbooks = generate_runbooks()
    save_items_as_markdown(runbooks, "runbook")

    print(f"\n✓ Part 2 Complete: {len(alerts) + len(runbooks)} items created")
    print("\nNext: Run part 3 for CI/CD, Kubernetes, Terraform, Scaling, and Backup items")


if __name__ == "__main__":
    main()
