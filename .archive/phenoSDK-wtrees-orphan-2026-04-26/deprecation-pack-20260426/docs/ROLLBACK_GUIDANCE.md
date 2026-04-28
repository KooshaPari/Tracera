# Rollback Guidance

**Version**: 2.0.0
**Date**: 2025-10-12
**Purpose**: Comprehensive rollback procedures for pheno-sdk v2.0.0 migration

---

## Overview

This document provides detailed rollback procedures for reverting from pheno-sdk v2.0.0 back to v1.x in case of critical issues during migration. The rollback process is designed to be safe, systematic, and reversible.

---

## When to Rollback

### Critical Issues Requiring Rollback

- **Authentication Failures**: OAuth2 flows not working, token validation errors
- **Service Infrastructure Issues**: Services not starting, orchestration failures
- **Proxy Gateway Problems**: Request routing failures, health check issues
- **Performance Degradation**: Significant performance regression
- **Security Vulnerabilities**: Critical security issues discovered
- **Data Loss**: Any data corruption or loss during migration

### Non-Critical Issues (Do Not Rollback)

- **Minor UI Issues**: Cosmetic problems, minor display issues
- **Documentation Gaps**: Missing documentation, unclear instructions
- **Feature Requests**: Missing features that can be added later
- **Minor Performance Issues**: Small performance regressions

---

## Pre-Rollback Checklist

### 1. Assess Current State

- [ ] Document current issues and their severity
- [ ] Identify affected components and services
- [ ] Check system health and performance metrics
- [ ] Verify data integrity and consistency
- [ ] Review error logs and monitoring data

### 2. Prepare Rollback Environment

- [ ] Ensure v1.x packages are available
- [ ] Verify rollback scripts are functional
- [ ] Check database backup availability
- [ ] Confirm configuration backups exist
- [ ] Test rollback procedures in staging

### 3. Notify Stakeholders

- [ ] Inform development team
- [ ] Notify operations team
- [ ] Update status page if applicable
- [ ] Communicate with users if necessary
- [ ] Document rollback decision and rationale

---

## Rollback Procedures

### 1. Code Rollback

#### Revert to Previous Version

```bash
# Stop all services
sudo systemctl stop pheno-services

# Revert to v1.x
git checkout v1.9.0
git checkout -b rollback-v1.9.0

# Install v1.x dependencies
pip install -r requirements-v1.txt

# Verify installation
python -c "import pheno; print(pheno.__version__)"
```

#### Restore Old Configuration

```bash
# Restore configuration files
cp config/authkit-client.yaml.backup config/
cp config/service-config.yaml.backup config/
cp config/proxy-config.yaml.backup config/

# Remove new configuration
rm config/pheno-config.yaml

# Verify configuration
python scripts/validate_config.py --config config/
```

### 2. Database Rollback

#### Schema Rollback

```bash
# Run database rollback migrations
python scripts/rollback/db_rollback.py --version 1.9.0

# Verify schema
python scripts/validate_db_schema.py --version 1.9.0
```

#### Data Restoration

```bash
# Restore from backup if needed
pg_restore -d pheno_db backup_v1.9.0.dump

# Verify data integrity
python scripts/validate_data_integrity.py
```

### 3. Service Rollback

#### Restart Services

```bash
# Start services with old configuration
sudo systemctl start pheno-services

# Verify service status
sudo systemctl status pheno-services

# Check service health
curl http://localhost:8000/health
curl http://localhost:9100/health
```

#### Validate Functionality

```bash
# Run health checks
python scripts/health_check.py --all

# Test authentication
python scripts/test_auth.py --provider authkit

# Test service orchestration
python scripts/test_services.py --all
```

---

## Automated Rollback Scripts

### 1. Full Rollback Script

```bash
#!/bin/bash
# scripts/rollback/full_rollback.sh

set -e

echo "Starting full rollback to v1.9.0..."

# Stop services
echo "Stopping services..."
sudo systemctl stop pheno-services

# Revert code
echo "Reverting code..."
git checkout v1.9.0
git checkout -b rollback-v1.9.0

# Install dependencies
echo "Installing v1.x dependencies..."
pip install -r requirements-v1.txt

# Restore configuration
echo "Restoring configuration..."
cp config/*.backup config/
rm -f config/pheno-config.yaml

# Rollback database
echo "Rolling back database..."
python scripts/rollback/db_rollback.py --version 1.9.0

# Start services
echo "Starting services..."
sudo systemctl start pheno-services

# Validate
echo "Validating rollback..."
python scripts/validate_rollback.py

echo "Rollback completed successfully!"
```

### 2. Partial Rollback Script

```bash
#!/bin/bash
# scripts/rollback/partial_rollback.sh

set -e

COMPONENT=$1

case $COMPONENT in
    "auth")
        echo "Rolling back authentication..."
        python scripts/rollback/auth_rollback.py
        ;;
    "services")
        echo "Rolling back service infrastructure..."
        python scripts/rollback/services_rollback.py
        ;;
    "proxy")
        echo "Rolling back proxy gateway..."
        python scripts/rollback/proxy_rollback.py
        ;;
    *)
        echo "Unknown component: $COMPONENT"
        exit 1
        ;;
esac

echo "Partial rollback completed for $COMPONENT"
```

### 3. Validation Script

```python
#!/usr/bin/env python3
# scripts/rollback/validate_rollback.py

import sys
import subprocess
import requests
import json

def check_services():
    """Check if all services are running."""
    services = [
        ("pheno-api", "http://localhost:8000/health"),
        ("pheno-proxy", "http://localhost:9100/health"),
        ("pheno-auth", "http://localhost:8001/health"),
    ]

    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} is healthy")
            else:
                print(f"❌ {name} returned {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ {name} is not responding: {e}")
            return False

    return True

def check_authentication():
    """Test authentication functionality."""
    try:
        # Test OAuth2 flow
        result = subprocess.run([
            "python", "scripts/test_auth.py", "--provider", "authkit"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Authentication is working")
            return True
        else:
            print(f"❌ Authentication test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        return False

def check_database():
    """Check database connectivity and schema."""
    try:
        result = subprocess.run([
            "python", "scripts/validate_db_schema.py", "--version", "1.9.0"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Database schema is correct")
            return True
        else:
            print(f"❌ Database validation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Database validation error: {e}")
        return False

def main():
    """Main validation function."""
    print("Validating rollback...")

    checks = [
        ("Services", check_services),
        ("Authentication", check_authentication),
        ("Database", check_database),
    ]

    all_passed = True
    for name, check_func in checks:
        print(f"\nChecking {name}...")
        if not check_func():
            all_passed = False

    if all_passed:
        print("\n✅ All rollback validations passed!")
        sys.exit(0)
    else:
        print("\n❌ Some rollback validations failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## Component-Specific Rollback

### Authentication Rollback

#### 1. Revert Auth Configuration

```bash
# Restore old auth configuration
cp config/authkit-client.yaml.backup config/
rm config/pheno-config.yaml

# Update environment variables
export AUTHKIT_CLIENT_ID=${OLD_AUTHKIT_CLIENT_ID}
export AUTHKIT_CLIENT_SECRET=${OLD_AUTHKIT_CLIENT_SECRET}
unset AUTH_CLIENT_ID
unset AUTH_CLIENT_SECRET
```

#### 2. Revert Auth Code

```python
# Revert to old auth imports
from authkit_client import AuthKitClient
from some_other_auth import CustomProvider

# Restore old auth initialization
authkit = AuthKitClient(config)
custom_auth = CustomProvider(settings)
```

#### 3. Validate Auth Rollback

```bash
# Test OAuth2 flows
python scripts/test_auth.py --provider authkit
python scripts/test_auth.py --provider custom

# Test token validation
python scripts/test_tokens.py --all
```

### Service Infrastructure Rollback

#### 1. Revert Service Configuration

```bash
# Restore old service configuration
cp config/service-config.yaml.backup config/

# Update environment variables
export SERVICE_PORT=${OLD_SERVICE_PORT}
export ORCHESTRATOR_PORT=${OLD_ORCHESTRATOR_PORT}
unset SERVICE_PREFERRED_PORT
unset FALLBACK_PORT
```

#### 2. Revert Service Code

```python
# Revert to old service imports
from service_manager import ServiceManager
from orchestrator import Orchestrator

# Restore old service initialization
service_mgr = ServiceManager()
orchestrator = Orchestrator()
```

#### 3. Validate Service Rollback

```bash
# Test service startup
python scripts/test_services.py --start

# Test service orchestration
python scripts/test_orchestration.py --all

# Test health monitoring
python scripts/test_health.py --all
```

### Proxy Gateway Rollback

#### 1. Revert Proxy Configuration

```bash
# Restore old proxy configuration
cp config/proxy-config.yaml.backup config/

# Update environment variables
export PROXY_PORT=${OLD_PROXY_PORT}
unset FALLBACK_PORT
```

#### 2. Revert Proxy Code

```python
# Revert to old proxy imports
from pheno.infra.proxy_gateway import ProxyServer
from gateway import Gateway

# Restore old proxy initialization
proxy = ProxyServer(port=9100)
gateway = Gateway()
```

#### 3. Validate Proxy Rollback

```bash
# Test proxy routing
python scripts/test_proxy.py --routing

# Test health monitoring
python scripts/test_proxy.py --health

# Test fallback handling
python scripts/test_proxy.py --fallback
```

---

## Data Migration Rollback

### Database Rollback

#### 1. Schema Rollback

```sql
-- Rollback authentication schema
DROP TABLE IF EXISTS auth_tokens_v2;
DROP TABLE IF EXISTS auth_sessions_v2;
DROP TABLE IF EXISTS auth_providers_v2;

-- Restore old schema
CREATE TABLE auth_tokens (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    token TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Restore indexes
CREATE INDEX idx_auth_tokens_user_id ON auth_tokens(user_id);
CREATE INDEX idx_auth_tokens_expires_at ON auth_tokens(expires_at);
```

#### 2. Data Migration

```python
# scripts/rollback/migrate_data_back.py

import psycopg2
import json

def migrate_auth_data():
    """Migrate auth data back to v1.x format."""
    conn = psycopg2.connect("postgresql://user:pass@localhost/pheno_db")
    cur = conn.cursor()

    # Migrate tokens
    cur.execute("""
        INSERT INTO auth_tokens (user_id, token, expires_at, created_at)
        SELECT
            user_id,
            access_token,
            expires_at,
            created_at
        FROM auth_tokens_v2
        WHERE token_type = 'access'
    """)

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    migrate_auth_data()
```

### Configuration Rollback

#### 1. Restore Old Configuration

```bash
# Restore all configuration files
cp config/*.backup config/

# Remove new configuration
rm config/pheno-config.yaml

# Restore environment variables
cp .env.v1.backup .env
```

#### 2. Validate Configuration

```bash
# Validate old configuration
python scripts/validate_config.py --config config/authkit-client.yaml
python scripts/validate_config.py --config config/service-config.yaml
python scripts/validate_config.py --config config/proxy-config.yaml
```

---

## Monitoring and Validation

### Health Checks

#### 1. Service Health

```bash
# Check all services
curl http://localhost:8000/health
curl http://localhost:9100/health
curl http://localhost:8001/health

# Check service status
sudo systemctl status pheno-services
```

#### 2. Authentication Health

```bash
# Test OAuth2 flows
python scripts/test_auth.py --provider authkit
python scripts/test_auth.py --provider custom

# Test token validation
python scripts/test_tokens.py --all
```

#### 3. Database Health

```bash
# Check database connectivity
python scripts/check_db.py

# Validate schema
python scripts/validate_db_schema.py --version 1.9.0

# Check data integrity
python scripts/validate_data_integrity.py
```

### Performance Monitoring

#### 1. Response Times

```bash
# Monitor API response times
python scripts/monitor_performance.py --duration 300

# Check service latency
python scripts/check_latency.py --all
```

#### 2. Resource Usage

```bash
# Monitor CPU and memory
python scripts/monitor_resources.py --duration 300

# Check disk usage
df -h
```

---

## Troubleshooting Rollback Issues

### Common Issues

#### 1. Service Won't Start

```bash
# Check service logs
sudo journalctl -u pheno-services -f

# Check configuration
python scripts/validate_config.py --all

# Restart services
sudo systemctl restart pheno-services
```

#### 2. Database Connection Issues

```bash
# Check database status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U pheno_user -d pheno_db -c "SELECT 1"

# Restore database backup if needed
pg_restore -d pheno_db backup_v1.9.0.dump
```

#### 3. Authentication Issues

```bash
# Check auth service logs
sudo journalctl -u pheno-auth -f

# Test auth configuration
python scripts/test_auth.py --debug

# Restore auth configuration
cp config/authkit-client.yaml.backup config/
```

### Recovery Procedures

#### 1. Complete System Recovery

```bash
# Stop all services
sudo systemctl stop pheno-services

# Restore from full backup
tar -xzf backup_v1.9.0_full.tar.gz -C /

# Restart services
sudo systemctl start pheno-services

# Validate everything
python scripts/validate_rollback.py
```

#### 2. Partial Recovery

```bash
# Identify failed components
python scripts/diagnose_issues.py

# Rollback specific components
python scripts/rollback/partial_rollback.sh auth
python scripts/rollback/partial_rollback.sh services
python scripts/rollback/partial_rollback.sh proxy
```

---

## Post-Rollback Procedures

### 1. Validation

- [ ] Run full test suite
- [ ] Validate all integrations
- [ ] Check performance metrics
- [ ] Verify data integrity
- [ ] Test all user workflows

### 2. Monitoring

- [ ] Set up monitoring alerts
- [ ] Monitor error rates
- [ ] Track performance metrics
- [ ] Watch for regressions
- [ ] Document any issues

### 3. Documentation

- [ ] Document rollback decision
- [ ] Record lessons learned
- [ ] Update runbooks
- [ ] Plan future migration
- [ ] Communicate status

---

## Prevention Strategies

### 1. Staging Validation

- Always test rollback procedures in staging
- Validate all components before production
- Run full test suite before migration
- Monitor performance and stability

### 2. Backup Strategy

- Maintain complete system backups
- Keep configuration backups
- Document all changes
- Test backup restoration

### 3. Gradual Migration

- Migrate components incrementally
- Monitor each step carefully
- Have rollback points ready
- Validate after each step

---

## Support and Escalation

### Internal Support

- **Development Team**: For code-related issues
- **Operations Team**: For infrastructure issues
- **Database Team**: For data-related issues
- **Security Team**: For security concerns

### External Support

- **GitHub Issues**: [github.com/pheno-sdk/issues](https://github.com/pheno-sdk/issues)
- **Discord**: [discord.gg/pheno-sdk](https://discord.gg/pheno-sdk)
- **Documentation**: [docs.pheno-sdk.com](https://docs.pheno-sdk.com)

### Emergency Contacts

- **On-Call Engineer**: +1-555-0123
- **Team Lead**: +1-555-0124
- **Manager**: +1-555-0125

---

**Last Updated**: 2025-10-12
**Version**: 2.0.0
**Next Review**: 2025-11-12
