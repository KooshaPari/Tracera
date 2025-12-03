// TraceRTM MASSIVE Documentation Structure - Part 3
// Development and Changelog sections

export const DOCS_STRUCTURE_PART3 = {
  'development': {
    title: 'Development',
    description: 'Development setup and internals',
    path: '03-development',
    icon: 'Wrench',
    children: {
      'architecture': {
        title: 'Architecture',
        path: '01-architecture',
        children: {
          'system-design': {
            title: 'System Design Overview',
            path: '01-system-design',
            children: {
              'overview': { title: 'Architecture Overview', path: '01-overview' },
              'principles': { title: 'Design Principles', path: '02-principles' },
            },
          },
          'microservices': { title: 'Microservices Architecture', path: '02-microservices' },
          'data-flow': { title: 'Data Flow', path: '03-data-flow' },
          'request-flow': { title: 'Request Flow', path: '04-request-flow' },
          'component-design': { title: 'Component Design', path: '05-component-design' },
          'database-schema': {
            title: 'Database Schema',
            path: '06-database-schema',
            children: {
              'postgresql': { title: 'PostgreSQL Schema', path: '01-postgresql' },
              'neo4j': { title: 'Neo4j Graph Schema', path: '02-neo4j' },
            },
          },
          'caching': { title: 'Caching Strategy', path: '07-caching' },
          'search': { title: 'Search Architecture', path: '08-search' },
          'event-driven': { title: 'Event-Driven Architecture', path: '09-event-driven' },
          'api-gateway': { title: 'API Gateway', path: '10-api-gateway' },
          'service-mesh': { title: 'Service Mesh', path: '11-service-mesh' },
          'performance': { title: 'Performance & Scalability', path: '12-performance' },
          'security': { title: 'Security Architecture', path: '13-security' },
        },
      },
      'setup': {
        title: 'Setup',
        path: '02-setup',
        children: {
          'prerequisites': { title: 'Prerequisites', path: '01-prerequisites' },
          'local-development': {
            title: 'Local Development',
            path: '02-local-development',
            children: {
              'macos': { title: 'macOS Setup', path: '01-macos' },
              'linux': { title: 'Linux Setup', path: '02-linux' },
              'windows': { title: 'Windows Setup', path: '03-windows' },
            },
          },
          'docker': { title: 'Docker Setup', path: '03-docker' },
          'kubernetes': { title: 'Kubernetes Setup', path: '04-kubernetes' },
          'database': {
            title: 'Database Setup',
            path: '05-database',
            children: {
              'postgresql': { title: 'PostgreSQL Setup', path: '01-postgresql' },
              'neo4j': { title: 'Neo4j Setup', path: '02-neo4j' },
              'redis': { title: 'Redis Setup', path: '03-redis' },
            },
          },
          'search': {
            title: 'Search Setup',
            path: '06-search',
            children: {
              'elasticsearch': { title: 'Elasticsearch Setup', path: '01-elasticsearch' },
              'meilisearch': { title: 'Meilisearch Setup', path: '02-meilisearch' },
            },
          },
          'environment': { title: 'Environment Configuration', path: '07-environment' },
          'ide': { title: 'IDE Setup', path: '08-ide' },
          'verification': { title: 'First Run & Verification', path: '09-verification' },
        },
      },
      'contributing': {
        title: 'Contributing',
        path: '03-contributing',
        children: {
          'getting-started': { title: 'Getting Started', path: '01-getting-started' },
          'code-style': {
            title: 'Code Style Guides',
            path: '02-code-style',
            children: {
              'go': { title: 'Go Style Guide', path: '01-go' },
              'typescript': { title: 'TypeScript Style', path: '02-typescript' },
              'python': { title: 'Python Style', path: '03-python' },
            },
          },
          'commit-conventions': { title: 'Commit Conventions', path: '03-commit-conventions' },
          'pull-requests': {
            title: 'Pull Request Process',
            path: '04-pull-requests',
            children: {
              'process': { title: 'PR Process', path: '01-process' },
              'review': { title: 'Code Review Guidelines', path: '02-review' },
            },
          },
          'testing': { title: 'Testing Standards', path: '05-testing' },
          'documentation': { title: 'Documentation Standards', path: '06-documentation' },
          'release': { title: 'Release Process', path: '07-release' },
        },
      },
      'internals': {
        title: 'Internals',
        path: '04-internals',
        children: {
          'backend': { title: 'Backend Architecture', path: '01-backend' },
          'frontend': { title: 'Frontend Architecture', path: '02-frontend' },
          'database': { title: 'Database Layer', path: '03-database' },
          'search': { title: 'Search Layer', path: '04-search' },
          'cache': { title: 'Caching Layer', path: '05-cache' },
          'queue': { title: 'Queue System', path: '06-queue' },
          'events': { title: 'Event System', path: '07-events' },
          'authentication': { title: 'Authentication System', path: '08-authentication' },
          'authorization': { title: 'Authorization System', path: '09-authorization' },
          'api': { title: 'API Layer', path: '10-api' },
          'service-communication': { title: 'Service Communication', path: '11-service-communication' },
        },
      },
      'testing': {
        title: 'Testing',
        path: '05-testing',
        children: {
          'unit': { title: 'Unit Testing', path: '01-unit' },
          'integration': { title: 'Integration Testing', path: '02-integration' },
          'e2e': { title: 'E2E Testing', path: '03-e2e' },
          'performance': { title: 'Performance Testing', path: '04-performance' },
          'security': { title: 'Security Testing', path: '05-security' },
          'coverage': { title: 'Test Coverage', path: '06-coverage' },
          'ci-cd': { title: 'CI/CD for Testing', path: '07-ci-cd' },
          'test-data': { title: 'Test Data Management', path: '08-test-data' },
        },
      },
      'deployment': {
        title: 'Deployment',
        path: '06-deployment',
        children: {
          'docker': {
            title: 'Docker Deployment',
            path: '01-docker',
            children: {
              'overview': { title: 'Docker Overview', path: '01-overview' },
              'compose': { title: 'Docker Compose', path: '02-compose' },
            },
          },
          'kubernetes': {
            title: 'Kubernetes Deployment',
            path: '02-kubernetes',
            children: {
              'manifests': { title: 'K8s Manifests', path: '01-manifests' },
              'helm': { title: 'Helm Charts', path: '02-helm' },
            },
          },
          'aws': { title: 'AWS Deployment', path: '03-aws' },
          'gcp': { title: 'GCP Deployment', path: '04-gcp' },
          'azure': { title: 'Azure Deployment', path: '05-azure' },
          'on-premises': { title: 'On-Premises Deployment', path: '06-on-premises' },
          'high-availability': { title: 'High Availability Setup', path: '07-high-availability' },
          'disaster-recovery': { title: 'Disaster Recovery', path: '08-disaster-recovery' },
          'monitoring': {
            title: 'Monitoring & Alerting',
            path: '09-monitoring',
            children: {
              'prometheus': { title: 'Prometheus', path: '01-prometheus' },
              'grafana': { title: 'Grafana', path: '02-grafana' },
            },
          },
          'logging': { title: 'Logging & Observability', path: '10-logging' },
          'scaling': { title: 'Scaling Strategies', path: '11-scaling' },
          'security': { title: 'Security Hardening', path: '12-security' },
        },
      },
    },
  },
  'changelog': {
    title: 'Changelog',
    description: 'Release notes and updates',
    path: '04-changelog',
    icon: 'RotateCcw',
    children: {
      'v3-0': {
        title: 'v3.0',
        path: '01-v3.0',
        children: {
          'overview': { title: 'v3.0 Overview', path: '01-overview' },
          'features': { title: 'New Features', path: '02-features' },
          'breaking': { title: 'Breaking Changes', path: '03-breaking' },
          'migration': { title: 'Migration Guide', path: '04-migration' },
        },
      },
      'v2-5': {
        title: 'v2.5',
        path: '02-v2.5',
        children: {
          'overview': { title: 'v2.5 Overview', path: '01-overview' },
          'features': { title: 'New Features', path: '02-features' },
          'fixes': { title: 'Bug Fixes', path: '03-fixes' },
        },
      },
      'v2-0': {
        title: 'v2.0',
        path: '03-v2.0',
        children: {
          'overview': { title: 'v2.0 Overview', path: '01-overview' },
          'features': { title: 'New Features', path: '02-features' },
          'breaking': { title: 'Breaking Changes', path: '03-breaking' },
          'migration': { title: 'Migration Guide', path: '04-migration' },
        },
      },
      'v1-5': {
        title: 'v1.5',
        path: '04-v1.5',
        children: {
          'overview': { title: 'v1.5 Overview', path: '01-overview' },
          'features': { title: 'New Features', path: '02-features' },
        },
      },
      'v1-0': {
        title: 'v1.0',
        path: '05-v1.0',
        children: {
          'overview': { title: 'v1.0 Overview', path: '01-overview' },
          'initial': { title: 'Initial Release', path: '02-initial' },
        },
      },
      'migration-guides': {
        title: 'Migration Guides',
        path: '06-migration-guides',
        children: {
          'v2-to-v3': { title: 'v2 to v3 Migration', path: '01-v2-to-v3' },
          'v1-to-v2': { title: 'v1 to v2 Migration', path: '02-v1-to-v2' },
        },
      },
    },
  },
}

// NOTE: To use this structure, merge DOCS_STRUCTURE_MASSIVE, DOCS_STRUCTURE_PART2, and DOCS_STRUCTURE_PART3
// into a single object and replace the existing DOCS_STRUCTURE in page.tsx
