# Production Operations Documentation Index

Complete guide to production deployment, operations, and troubleshooting for TracerTM.

## Table of Contents

- [Overview](#overview)
- [Documentation Structure](#documentation-structure)
- [Quick Start for Production](#quick-start-for-production)
- [By Role](#by-role)
- [By Task](#by-task)
- [Related Documentation](#related-documentation)

---

## Overview

This index provides a central navigation point for all production operations documentation. Whether you're deploying for the first time, troubleshooting an issue, or managing day-to-day operations, start here.

### Documentation Hierarchy

```
Production Operations
├── PRODUCTION_DEPLOYMENT.md      (Setup & Initial Deployment)
├── ENVIRONMENT_CONFIGURATION.md  (All Environment Variables)
├── OPERATIONS_RUNBOOK.md         (Daily Operations & Incidents)
└── TROUBLESHOOTING.md            (Problem Solving)
```

---

## Documentation Structure

### 1. Production Deployment Guide

**File**: [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)

**Use When**: Setting up a new production environment or deploying updates.

**Covers**:
- System requirements and prerequisites
- Production vs development differences
- SSL/TLS setup with Let's Encrypt and Caddy
- Docker Compose deployment
- Security hardening
- Monitoring setup (Prometheus & Grafana)
- Backup and disaster recovery
- Post-deployment verification

**Key Sections**:
- Environment Configuration
- SSL/TLS Setup (Option 1: Let's Encrypt, Option 2: Caddy)
- Service Deployment Steps
- Security Hardening Checklist
- Monitoring Configuration
- Backup Procedures

---

### 2. Environment Configuration Guide

**File**: [ENVIRONMENT_CONFIGURATION.md](ENVIRONMENT_CONFIGURATION.md)

**Use When**: Configuring services, updating environment variables, or troubleshooting configuration issues.

**Covers**:
- Complete reference for all environment variables
- Required vs optional variables
- Development vs production configurations
- Secret management strategies
- Configuration validation

**Key Sections**:
- Database Configuration (PostgreSQL, Neo4j)
- Cache and Message Broker (Redis, NATS)
- Authentication (WorkOS, JWT)
- External Integrations (GitHub, Temporal)
- Embeddings and AI (VoyageAI, OpenRouter)
- Security Configuration
- Feature Flags

**Quick Reference Tables**:
- By Service
- By Environment (Dev vs Prod)
- Secret Management Options

---

### 3. Operations Runbook

**File**: [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md)

**Use When**: Performing daily operations, responding to incidents, or managing production services.

**Covers**:
- Service monitoring procedures
- Common operational tasks
- Incident response workflows
- Scaling procedures
- Performance tuning
- Log management
- Database maintenance

**Key Sections**:
- Service Management Commands
- Health Check Monitoring
- Incident Response by Severity (P0-P3)
- Common Incident Scenarios
- Scaling Procedures (Horizontal & Vertical)
- Performance Tuning
- Database Maintenance Schedule
- On-Call Procedures

**Emergency Procedures**:
- Database connection pool exhausted
- Out of memory (OOM)
- Disk full
- SSL certificate expired

---

### 4. Troubleshooting Guide

**File**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Use When**: Something is broken or not working as expected.

**Covers**:
- Service startup issues
- Connection problems
- Performance degradation
- Authentication failures
- Database issues
- Cache and message broker problems
- API errors
- Frontend issues

**Key Sections**:
- Service Won't Start (Port conflicts, missing env vars, permissions)
- Connection Issues (Database, Redis, NATS)
- Performance Problems (CPU, memory, slow queries)
- Authentication Issues (WorkOS, JWT, sessions)
- Database Issues (Locks, migrations, disk space)
- Log Analysis Techniques
- Debug Mode Activation
- Emergency Procedures

**Diagnostic Tools**:
- Health check scripts
- Log filtering and analysis
- Docker debugging
- Network troubleshooting

---

## Quick Start for Production

### First-Time Deployment

**Timeline**: ~2-4 hours

1. **Prerequisites** (30 min)
   - Read: [PRODUCTION_DEPLOYMENT.md § Prerequisites](PRODUCTION_DEPLOYMENT.md#prerequisites)
   - Provision server (4 cores, 8GB RAM, 50GB SSD)
   - Install Docker and Docker Compose
   - Configure DNS

2. **Environment Setup** (30 min)
   - Read: [ENVIRONMENT_CONFIGURATION.md § Production Environment](ENVIRONMENT_CONFIGURATION.md#production-environment)
   - Create `/etc/tracertm/.env`
   - Generate secrets (JWT, passwords)
   - Configure WorkOS

3. **SSL/TLS Setup** (30 min)
   - Read: [PRODUCTION_DEPLOYMENT.md § SSL/TLS Setup](PRODUCTION_DEPLOYMENT.md#ssltls-setup)
   - Option 1: Let's Encrypt (manual)
   - Option 2: Caddy (automatic)

4. **Deploy Services** (30 min)
   - Read: [PRODUCTION_DEPLOYMENT.md § Service Deployment](PRODUCTION_DEPLOYMENT.md#service-deployment)
   - Clone repository
   - Build Docker images
   - Start services
   - Verify deployment

5. **Security Hardening** (30 min)
   - Read: [PRODUCTION_DEPLOYMENT.md § Security Hardening](PRODUCTION_DEPLOYMENT.md#security-hardening)
   - Configure firewall (UFW)
   - Set resource limits
   - Harden database
   - Configure rate limiting

6. **Monitoring & Backups** (30 min)
   - Read: [PRODUCTION_DEPLOYMENT.md § Monitoring Setup](PRODUCTION_DEPLOYMENT.md#monitoring-setup)
   - Configure Prometheus
   - Set up Grafana dashboards
   - Schedule database backups
   - Test disaster recovery

### Daily Operations

**Morning Checklist** (5-10 min):

1. Run health check:
   ```bash
   /opt/tracertm/scripts/health-check.sh tracertm.example.com
   ```

2. Review metrics in Grafana:
   - https://tracertm.example.com:3000

3. Check for alerts in Prometheus:
   - https://tracertm.example.com:9090

4. Review error logs:
   ```bash
   docker compose logs --since 24h | grep ERROR
   ```

**Reference**: [OPERATIONS_RUNBOOK.md § Service Monitoring](OPERATIONS_RUNBOOK.md#service-monitoring)

### Incident Response

**When Something Breaks**:

1. **Assess Severity**
   - Read: [OPERATIONS_RUNBOOK.md § Incident Severity Levels](OPERATIONS_RUNBOOK.md#incident-severity-levels)
   - P0 (Critical): Immediate response
   - P1 (High): < 15 min
   - P2 (Medium): < 1 hour
   - P3 (Low): < 4 hours

2. **Initial Diagnosis**
   - Read: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
   - Check service status: `docker compose ps`
   - View recent logs: `docker compose logs --tail=100`
   - Check resources: `docker stats --no-stream`

3. **Consult Runbook**
   - Read: [OPERATIONS_RUNBOOK.md § Common Incident Scenarios](OPERATIONS_RUNBOOK.md#common-incident-scenarios)
   - Find matching scenario
   - Follow resolution steps

4. **If Not Resolved**
   - Read: [TROUBLESHOOTING.md § Getting Help](TROUBLESHOOTING.md#getting-help)
   - Gather diagnostic information
   - Escalate per on-call procedures

---

## By Role

### DevOps Engineer / SRE

**Your Documentation**:

1. **Primary**: [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)
   - Know this inside out for deployments

2. **Daily**: [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md)
   - Your go-to for daily operations

3. **Reference**: [ENVIRONMENT_CONFIGURATION.md](ENVIRONMENT_CONFIGURATION.md)
   - For configuration changes

4. **Emergency**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
   - Keep this bookmarked

**Key Tasks**:
- Deploy new versions
- Monitor service health
- Respond to incidents
- Perform backups
- Scale services
- Optimize performance

### Backend Developer

**Your Documentation**:

1. **Configuration**: [ENVIRONMENT_CONFIGURATION.md](ENVIRONMENT_CONFIGURATION.md)
   - Understand all service configuration

2. **Debugging**: [TROUBLESHOOTING.md § Debug Mode Activation](TROUBLESHOOTING.md#debug-mode-activation)
   - Enable debug logging
   - Analyze logs

3. **Reference**: [OPERATIONS_RUNBOOK.md § Log Management](OPERATIONS_RUNBOOK.md#log-management)
   - Log analysis techniques

**Key Tasks**:
- Debug production issues
- Optimize database queries
- Configure new services
- Update environment variables

### Security Engineer

**Your Documentation**:

1. **Security**: [PRODUCTION_DEPLOYMENT.md § Security Hardening](PRODUCTION_DEPLOYMENT.md#security-hardening)
   - Firewall configuration
   - Container security
   - Database security

2. **Secrets**: [ENVIRONMENT_CONFIGURATION.md § Secret Management](ENVIRONMENT_CONFIGURATION.md#secret-management)
   - Vault, Docker secrets

3. **Monitoring**: [OPERATIONS_RUNBOOK.md § Service Monitoring](OPERATIONS_RUNBOOK.md#service-monitoring)
   - Security metrics

**Key Tasks**:
- Security audits
- Secret rotation
- Access control
- Vulnerability management

### On-Call Engineer

**Your Documentation**:

1. **Runbook**: [OPERATIONS_RUNBOOK.md § Incident Response](OPERATIONS_RUNBOOK.md#incident-response)
   - Incident workflow
   - Common scenarios

2. **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
   - Quick problem solving

3. **Emergency**: [OPERATIONS_RUNBOOK.md § On-Call Procedures](OPERATIONS_RUNBOOK.md#on-call-procedures)
   - Escalation path
   - Contact list

**Keep Handy**:
- Health check script
- Emergency rollback procedure
- Incident report template

---

## By Task

### Configuration Tasks

| Task | Documentation | Section |
|------|---------------|---------|
| Add environment variable | [ENVIRONMENT_CONFIGURATION.md](ENVIRONMENT_CONFIGURATION.md) | Relevant service section |
| Update database connection | [ENVIRONMENT_CONFIGURATION.md](ENVIRONMENT_CONFIGURATION.md) | Database Configuration |
| Configure WorkOS | [ENVIRONMENT_CONFIGURATION.md](ENVIRONMENT_CONFIGURATION.md) | Authentication |
| Set up embeddings | [ENVIRONMENT_CONFIGURATION.md](ENVIRONMENT_CONFIGURATION.md) | Embeddings and AI |
| Validate configuration | [ENVIRONMENT_CONFIGURATION.md](ENVIRONMENT_CONFIGURATION.md) | Configuration Validation |

### Deployment Tasks

| Task | Documentation | Section |
|------|---------------|---------|
| Initial deployment | [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) | Service Deployment |
| Set up SSL | [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) | SSL/TLS Setup |
| Configure monitoring | [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) | Monitoring Setup |
| Set up backups | [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) | Backup and Disaster Recovery |
| Deploy update | [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md) | Update Application Code |

### Operational Tasks

| Task | Documentation | Section |
|------|---------------|---------|
| Restart service | [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md) | Service Management |
| View logs | [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md) | Common Operational Tasks |
| Scale service | [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md) | Scaling Procedures |
| Tune performance | [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md) | Performance Tuning |
| Database maintenance | [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md) | Database Maintenance |

### Troubleshooting Tasks

| Task | Documentation | Section |
|------|---------------|---------|
| Service won't start | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Service Won't Start |
| Connection issues | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Connection Issues |
| Performance problems | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Performance Problems |
| Authentication fails | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Authentication Issues |
| Database problems | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Database Issues |
| Analyze logs | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Log Analysis Techniques |

### Emergency Tasks

| Task | Documentation | Section |
|------|---------------|---------|
| Respond to incident | [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md) | Incident Response |
| Emergency rollback | [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md) | Common Incident Scenarios |
| Database recovery | [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) | Disaster Recovery Plan |
| Complete reset | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Emergency Procedures |

---

## Related Documentation

### Architecture and Design

- [System Architecture](/docs/02-architecture/core-architecture.md)
- [Infrastructure Design](/docs/02-architecture/infrastructure.md)
- [Data Flow](/docs/02-architecture/data-flow.md)

### Development

- [Developer Guide](/docs/04-guides/developer-guide.md)
- [Quick Start](/docs/01-getting-started/quick-start.md)
- [API Reference](/docs/06-api-reference/api-documentation.md)

### Planning and History

- [Implementation Plan](/docs/03-planning/implementation-plan.md)
- [Sprint Plan](/docs/03-planning/sprint-plan.md)
- [Phase Reports](/docs/07-reports/README.md)

### Reference

- [Quick Reference](/docs/08-reference/quick-reference.md)
- [Glossary](/docs/08-reference/glossary.md)
- [FAQ](/docs/08-reference/faq.md)

---

## Document Cross-References

### Internal Links

Each document references the others for related information:

**PRODUCTION_DEPLOYMENT.md** references:
- OPERATIONS_RUNBOOK.md (for ongoing operations)
- TROUBLESHOOTING.md (for deployment issues)
- ENVIRONMENT_CONFIGURATION.md (for configuration details)

**ENVIRONMENT_CONFIGURATION.md** references:
- PRODUCTION_DEPLOYMENT.md (for deployment context)
- OPERATIONS_RUNBOOK.md (for runtime configuration)
- TROUBLESHOOTING.md (for configuration issues)

**OPERATIONS_RUNBOOK.md** references:
- PRODUCTION_DEPLOYMENT.md (for initial setup)
- ENVIRONMENT_CONFIGURATION.md (for configuration)
- TROUBLESHOOTING.md (for problem solving)

**TROUBLESHOOTING.md** references:
- OPERATIONS_RUNBOOK.md (for operational procedures)
- ENVIRONMENT_CONFIGURATION.md (for configuration fixes)
- PRODUCTION_DEPLOYMENT.md (for deployment context)

---

## Quick Reference Cards

### Health Check Script

```bash
/opt/tracertm/scripts/health-check.sh tracertm.example.com
```

**Reference**: [PRODUCTION_DEPLOYMENT.md § Post-Deployment Verification](PRODUCTION_DEPLOYMENT.md#post-deployment-verification)

### Service Management

```bash
# View status
docker compose ps

# View logs
docker compose logs -f [service_name]

# Restart service
docker compose restart [service_name]

# Update service
git pull && docker compose build && docker compose up -d
```

**Reference**: [OPERATIONS_RUNBOOK.md § Service Management](OPERATIONS_RUNBOOK.md#service-management)

### Emergency Commands

```bash
# Emergency restart
docker compose down && docker compose up -d

# Emergency rollback
cd /opt/tracertm && git checkout backup-LATEST && docker compose up -d --build

# Database restore
cat /backup/tracertm_LATEST.dump.gz | gunzip | \
  docker compose exec -T postgres pg_restore -U tracertm -d tracertm -c
```

**Reference**: [TROUBLESHOOTING.md § Emergency Procedures](TROUBLESHOOTING.md#emergency-procedures)

---

## Document Maintenance

### Update Schedule

- **Monthly**: Review and update metrics thresholds
- **Quarterly**: Verify all procedures with test incidents
- **After Major Release**: Update deployment procedures
- **After Incidents**: Add new scenarios to troubleshooting

### Contributing

Found an issue or have an improvement? See [Contributing Guide](/docs/01-getting-started/contributing.md).

---

## Support

For issues not covered in this documentation:

1. Check [FAQ](/docs/08-reference/faq.md)
2. Search existing [GitHub Issues](https://github.com/your-org/tracertm/issues)
3. Create a new issue with diagnostic information

**Diagnostic Information to Include**:
- Service status: `docker compose ps`
- Recent logs: `docker compose logs --tail=200`
- Environment (sanitized): `cat .env | sed 's/=.*/=***/'`

---

**Last Updated**: January 2026
**Version**: 1.0.0
**Maintained By**: Platform Engineering Team
