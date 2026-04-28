/**
 * Expanded Documentation Structure Template
 *
 * This file contains a massively expanded structure template for TraceRTM documentation.
 * Use this as a reference to expand the DOCS_STRUCTURE in structure.ts to 750+ pages.
 */

export const EXPANDED_STRUCTURE = {
  'getting-started': {
    title: 'Getting Started',
    description: 'Get up and running with TraceRTM in minutes',
    path: '00-getting-started',
    icon: 'Rocket',
    children: {
      'installation': {
        title: 'Installation',
        path: '01-installation',
        children: {
          'windows': { title: 'Windows Installation', path: '01-windows' },
          'macos': { title: 'macOS Installation', path: '02-macos' },
          'linux': { title: 'Linux Installation', path: '03-linux' },
          'docker': { title: 'Docker Installation', path: '04-docker' },
          'kubernetes': { title: 'Kubernetes Installation', path: '05-kubernetes' },
          'cloud': {
            title: 'Cloud Installation',
            path: '06-cloud',
            children: {
              'aws': { title: 'AWS Deployment', path: '01-aws' },
              'azure': { title: 'Azure Deployment', path: '02-azure' },
              'gcp': { title: 'GCP Deployment', path: '03-gcp' },
              'vercel': { title: 'Vercel Deployment', path: '04-vercel' },
              'netlify': { title: 'Netlify Deployment', path: '05-netlify' },
            },
          },
          'troubleshooting': { title: 'Installation Troubleshooting', path: '07-troubleshooting' },
        },
      },
      'quick-start': {
        title: 'Quick Start',
        path: '02-quick-start',
        children: {
          '5-minute-tutorial': { title: '5-Minute Tutorial', path: '01-5-minute-tutorial' },
          'video-guides': { title: 'Video Guides', path: '02-video-guides' },
          'interactive-demo': { title: 'Interactive Demo', path: '03-interactive-demo' },
        },
      },
      'system-requirements': {
        title: 'System Requirements',
        path: '03-system-requirements',
        children: {
          'hardware': { title: 'Hardware Requirements', path: '01-hardware' },
          'software': { title: 'Software Requirements', path: '02-software' },
          'network': { title: 'Network Requirements', path: '03-network' },
          'browser': { title: 'Browser Compatibility', path: '04-browser' },
        },
      },
      'core-concepts': {
        title: 'Core Concepts',
        path: '04-core-concepts',
        children: {
          'architecture': { title: 'Architecture Overview', path: '01-architecture' },
          'data-model': { title: 'Data Model', path: '02-data-model' },
          'workflows': { title: 'Workflow Concepts', path: '03-workflows' },
          'permissions': { title: 'Permissions Model', path: '04-permissions' },
          'terminology': { title: 'Terminology', path: '05-terminology' },
        },
      },
      'first-project': {
        title: 'First Project',
        path: '05-first-project',
        children: {
          'project-setup': { title: 'Project Setup', path: '01-project-setup' },
          'requirements': { title: 'Creating Requirements', path: '02-requirements' },
          'test-cases': { title: 'Creating Test Cases', path: '03-test-cases' },
          'traceability': { title: 'Establishing Traceability', path: '04-traceability' },
          'reports': { title: 'Generating Reports', path: '05-reports' },
        },
      },
      'basic-workflow': {
        title: 'Basic Workflow',
        path: '06-basic-workflow',
        children: {
          'daily-workflow': { title: 'Daily Workflow', path: '01-daily-workflow' },
          'team-collaboration': { title: 'Team Collaboration', path: '02-team-collaboration' },
          'version-control': { title: 'Version Control Integration', path: '03-version-control' },
        },
      },
      'faq': { title: 'FAQ', path: '07-faq' },
    },
  },
  'wiki': {
    title: 'Wiki',
    description: 'Knowledge base and guides',
    path: '01-wiki',
    icon: 'BookOpen',
    children: {
      'concepts': {
        title: 'Concepts',
        path: '01-concepts',
        children: {
          'traceability': {
            title: 'Traceability',
            path: '01-traceability',
            children: {
              'what-is-traceability': { title: 'What is Traceability?', path: '01-what-is' },
              'types': { title: 'Types of Traceability', path: '02-types' },
              'benefits': { title: 'Benefits', path: '03-benefits' },
              'best-practices': { title: 'Best Practices', path: '04-best-practices' },
              'standards': { title: 'Industry Standards', path: '05-standards' },
              'compliance': { title: 'Compliance Requirements', path: '06-compliance' },
            },
          },
          'workflows': {
            title: 'Workflows',
            path: '02-workflows',
            children: {
              'agile': { title: 'Agile Workflows', path: '01-agile' },
              'waterfall': { title: 'Waterfall Workflows', path: '02-waterfall' },
              'hybrid': { title: 'Hybrid Workflows', path: '03-hybrid' },
              'custom': { title: 'Custom Workflows', path: '04-custom' },
              'automation': { title: 'Workflow Automation', path: '05-automation' },
            },
          },
          'artifacts': {
            title: 'Artifacts',
            path: '03-artifacts',
            children: {
              'requirements': { title: 'Requirements', path: '01-requirements' },
              'design': { title: 'Design Documents', path: '02-design' },
              'test-cases': { title: 'Test Cases', path: '03-test-cases' },
              'code': { title: 'Code Artifacts', path: '04-code' },
              'documentation': { title: 'Documentation', path: '05-documentation' },
              'custom': { title: 'Custom Artifacts', path: '06-custom' },
            },
          },
          'relationships': {
            title: 'Relationships',
            path: '04-relationships',
            children: {
              'types': { title: 'Relationship Types', path: '01-types' },
              'mapping': { title: 'Relationship Mapping', path: '02-mapping' },
              'visualization': { title: 'Visualization', path: '03-visualization' },
              'impact-analysis': { title: 'Impact Analysis', path: '04-impact-analysis' },
            },
          },
          'metadata': {
            title: 'Metadata',
            path: '05-metadata',
            children: {
              'standard-fields': { title: 'Standard Fields', path: '01-standard-fields' },
              'custom-fields': { title: 'Custom Fields', path: '02-custom-fields' },
              'validation': { title: 'Validation Rules', path: '03-validation' },
              'search': { title: 'Search and Filter', path: '04-search' },
            },
          },
          'versioning': {
            title: 'Versioning',
            path: '06-versioning',
            children: {
              'strategies': { title: 'Versioning Strategies', path: '01-strategies' },
              'branching': { title: 'Branching Model', path: '02-branching' },
              'merging': { title: 'Merging Changes', path: '03-merging' },
              'history': { title: 'Change History', path: '04-history' },
              'rollback': { title: 'Rollback Procedures', path: '05-rollback' },
            },
          },
          'compliance': {
            title: 'Compliance',
            path: '07-compliance',
            children: {
              'iso-26262': { title: 'ISO 26262', path: '01-iso-26262' },
              'do-178c': { title: 'DO-178C', path: '02-do-178c' },
              'iec-62304': { title: 'IEC 62304', path: '03-iec-62304' },
              'gdpr': { title: 'GDPR Compliance', path: '04-gdpr' },
              'soc2': { title: 'SOC 2', path: '05-soc2' },
              'hipaa': { title: 'HIPAA', path: '06-hipaa' },
            },
          },
          'security': {
            title: 'Security',
            path: '08-security',
            children: {
              'authentication': { title: 'Authentication', path: '01-authentication' },
              'authorization': { title: 'Authorization', path: '02-authorization' },
              'encryption': { title: 'Encryption', path: '03-encryption' },
              'audit-logs': { title: 'Audit Logs', path: '04-audit-logs' },
              'best-practices': { title: 'Security Best Practices', path: '05-best-practices' },
            },
          },
          'performance': {
            title: 'Performance',
            path: '09-performance',
            children: {
              'optimization': { title: 'Optimization Techniques', path: '01-optimization' },
              'caching': { title: 'Caching Strategies', path: '02-caching' },
              'scaling': { title: 'Scaling', path: '03-scaling' },
              'monitoring': { title: 'Performance Monitoring', path: '04-monitoring' },
            },
          },
          'integrations': {
            title: 'Integrations',
            path: '10-integrations',
            children: {
              'jira': { title: 'Jira Integration', path: '01-jira' },
              'github': { title: 'GitHub Integration', path: '02-github' },
              'gitlab': { title: 'GitLab Integration', path: '03-gitlab' },
              'jenkins': { title: 'Jenkins Integration', path: '04-jenkins' },
              'slack': { title: 'Slack Integration', path: '05-slack' },
              'teams': { title: 'Microsoft Teams', path: '06-teams' },
              'custom': { title: 'Custom Integrations', path: '07-custom' },
            },
          },
        },
      },
      'guides': {
        title: 'Guides',
        path: '02-guides',
        children: {
          'cli-guide': {
            title: 'CLI Guide',
            path: '01-cli-guide',
            children: {
              'installation': { title: 'CLI Installation', path: '01-installation' },
              'configuration': { title: 'Configuration', path: '02-configuration' },
              'commands': {
                title: 'Commands',
                path: '03-commands',
                children: {
                  'init': { title: 'init Command', path: '01-init' },
                  'create': { title: 'create Command', path: '02-create' },
                  'update': { title: 'update Command', path: '03-update' },
                  'delete': { title: 'delete Command', path: '04-delete' },
                  'link': { title: 'link Command', path: '05-link' },
                  'unlink': { title: 'unlink Command', path: '06-unlink' },
                  'query': { title: 'query Command', path: '07-query' },
                  'report': { title: 'report Command', path: '08-report' },
                  'export': { title: 'export Command', path: '09-export' },
                  'import': { title: 'import Command', path: '10-import' },
                  'sync': { title: 'sync Command', path: '11-sync' },
                  'validate': { title: 'validate Command', path: '12-validate' },
                },
              },
              'scripting': { title: 'Scripting and Automation', path: '04-scripting' },
              'plugins': { title: 'CLI Plugins', path: '05-plugins' },
            },
          },
          'web-ui-guide': {
            title: 'Web UI Guide',
            path: '02-web-ui-guide',
            children: {
              'dashboard': { title: 'Dashboard Overview', path: '01-dashboard' },
              'navigation': { title: 'Navigation', path: '02-navigation' },
              'projects': { title: 'Managing Projects', path: '03-projects' },
              'artifacts': { title: 'Managing Artifacts', path: '04-artifacts' },
              'relationships': { title: 'Relationship Views', path: '05-relationships' },
              'reports': { title: 'Report Generation', path: '06-reports' },
              'search': { title: 'Search and Filters', path: '07-search' },
              'settings': { title: 'Settings', path: '08-settings' },
              'keyboard-shortcuts': { title: 'Keyboard Shortcuts', path: '09-keyboard-shortcuts' },
            },
          },
          'troubleshooting': {
            title: 'Troubleshooting',
            path: '03-troubleshooting',
            children: {
              'common-issues': { title: 'Common Issues', path: '01-common-issues' },
              'error-messages': { title: 'Error Messages', path: '02-error-messages' },
              'performance': { title: 'Performance Issues', path: '03-performance' },
              'connectivity': { title: 'Connectivity Problems', path: '04-connectivity' },
              'data-issues': { title: 'Data Issues', path: '05-data-issues' },
              'logs': { title: 'Log Analysis', path: '06-logs' },
            },
          },
          'performance-tuning': {
            title: 'Performance Tuning',
            path: '04-performance-tuning',
            children: {
              'database': { title: 'Database Optimization', path: '01-database' },
              'caching': { title: 'Caching Configuration', path: '02-caching' },
              'query-optimization': { title: 'Query Optimization', path: '03-query-optimization' },
              'resource-limits': { title: 'Resource Limits', path: '04-resource-limits' },
              'monitoring': { title: 'Performance Monitoring', path: '05-monitoring' },
            },
          },
          'security': {
            title: 'Security',
            path: '05-security',
            children: {
              'authentication': { title: 'Authentication Setup', path: '01-authentication' },
              'authorization': { title: 'Authorization Rules', path: '02-authorization' },
              'rbac': { title: 'Role-Based Access Control', path: '03-rbac' },
              'sso': { title: 'Single Sign-On', path: '04-sso' },
              'api-security': { title: 'API Security', path: '05-api-security' },
              'data-encryption': { title: 'Data Encryption', path: '06-data-encryption' },
              'security-audit': { title: 'Security Auditing', path: '07-security-audit' },
            },
          },
          'migration-guide': {
            title: 'Migration Guide',
            path: '06-migration-guide',
            children: {
              'from-doors': { title: 'From IBM DOORS', path: '01-from-doors' },
              'from-jama': { title: 'From Jama Connect', path: '02-from-jama' },
              'from-polarion': { title: 'From Polarion', path: '03-from-polarion' },
              'from-excel': { title: 'From Excel', path: '04-from-excel' },
              'data-mapping': { title: 'Data Mapping', path: '05-data-mapping' },
              'validation': { title: 'Migration Validation', path: '06-validation' },
            },
          },
          'backup-restore': {
            title: 'Backup & Restore',
            path: '07-backup-restore',
            children: {
              'backup-strategies': { title: 'Backup Strategies', path: '01-backup-strategies' },
              'automated-backups': { title: 'Automated Backups', path: '02-automated-backups' },
              'restore-procedures': { title: 'Restore Procedures', path: '03-restore-procedures' },
              'disaster-recovery': { title: 'Disaster Recovery', path: '04-disaster-recovery' },
            },
          },
        },
      },
      'tutorials': {
        title: 'Tutorials',
        path: '03-tutorials',
        children: {
          'beginner': {
            title: 'Beginner Tutorials',
            path: '01-beginner',
            children: {
              'your-first-requirement': { title: 'Your First Requirement', path: '01-first-requirement' },
              'creating-test-cases': { title: 'Creating Test Cases', path: '02-creating-tests' },
              'linking-artifacts': { title: 'Linking Artifacts', path: '03-linking' },
              'generating-reports': { title: 'Generating Reports', path: '04-reports' },
            },
          },
          'intermediate': {
            title: 'Intermediate Tutorials',
            path: '02-intermediate',
            children: {
              'custom-workflows': { title: 'Custom Workflows', path: '01-custom-workflows' },
              'advanced-queries': { title: 'Advanced Queries', path: '02-advanced-queries' },
              'automation': { title: 'Automation Scripts', path: '03-automation' },
              'integrations': { title: 'Third-Party Integrations', path: '04-integrations' },
            },
          },
          'advanced': {
            title: 'Advanced Tutorials',
            path: '03-advanced',
            children: {
              'custom-plugins': { title: 'Building Custom Plugins', path: '01-custom-plugins' },
              'api-development': { title: 'API Development', path: '02-api-development' },
              'performance-optimization': { title: 'Performance Optimization', path: '03-performance' },
              'enterprise-deployment': { title: 'Enterprise Deployment', path: '04-enterprise' },
            },
          },
        },
      },
      'best-practices': {
        title: 'Best Practices',
        path: '04-best-practices',
        children: {
          'requirement-writing': { title: 'Requirement Writing', path: '01-requirement-writing' },
          'test-management': { title: 'Test Management', path: '02-test-management' },
          'traceability': { title: 'Traceability Management', path: '03-traceability' },
          'team-collaboration': { title: 'Team Collaboration', path: '04-team-collaboration' },
          'documentation': { title: 'Documentation', path: '05-documentation' },
          'version-control': { title: 'Version Control', path: '06-version-control' },
        },
      },
    },
  },
  'api-reference': {
    title: 'API Reference',
    description: 'Complete API documentation',
    path: '02-api-reference',
    icon: 'Zap',
    children: {
      'authentication': {
        title: 'Authentication',
        path: '01-authentication',
        children: {
          'jwt': { title: 'JWT Authentication', path: '01-jwt' },
          'oauth': { title: 'OAuth 2.0', path: '02-oauth' },
          'api-keys': { title: 'API Keys', path: '03-api-keys' },
          'sso': { title: 'Single Sign-On', path: '04-sso' },
        },
      },
      'rest-api': {
        title: 'REST API',
        path: '02-rest-api',
        children: {
          'overview': { title: 'REST API Overview', path: '01-overview' },
          'endpoints': {
            title: 'Endpoints',
            path: '02-endpoints',
            children: {
              'projects': { title: 'Projects API', path: '01-projects' },
              'requirements': { title: 'Requirements API', path: '02-requirements' },
              'tests': { title: 'Tests API', path: '03-tests' },
              'relationships': { title: 'Relationships API', path: '04-relationships' },
              'reports': { title: 'Reports API', path: '05-reports' },
              'users': { title: 'Users API', path: '06-users' },
              'teams': { title: 'Teams API', path: '07-teams' },
              'workflows': { title: 'Workflows API', path: '08-workflows' },
              'webhooks': { title: 'Webhooks API', path: '09-webhooks' },
            },
          },
          'pagination': { title: 'Pagination', path: '03-pagination' },
          'filtering': { title: 'Filtering', path: '04-filtering' },
          'sorting': { title: 'Sorting', path: '05-sorting' },
          'rate-limiting': { title: 'Rate Limiting', path: '06-rate-limiting' },
          'errors': { title: 'Error Handling', path: '07-errors' },
        },
      },
      'graphql-api': {
        title: 'GraphQL API',
        path: '03-graphql-api',
        children: {
          'overview': { title: 'GraphQL Overview', path: '01-overview' },
          'schema': { title: 'Schema Reference', path: '02-schema' },
          'queries': { title: 'Queries', path: '03-queries' },
          'mutations': { title: 'Mutations', path: '04-mutations' },
          'subscriptions': { title: 'Subscriptions', path: '05-subscriptions' },
        },
      },
      'cli': {
        title: 'CLI',
        path: '04-cli',
        children: {
          'overview': { title: 'CLI Overview', path: '01-overview' },
          'commands': { title: 'Command Reference', path: '02-commands' },
          'configuration': { title: 'Configuration', path: '03-configuration' },
          'plugins': { title: 'Plugin System', path: '04-plugins' },
        },
      },
      'sdk': {
        title: 'SDKs',
        path: '05-sdk',
        children: {
          'javascript': { title: 'JavaScript SDK', path: '01-javascript' },
          'typescript': { title: 'TypeScript SDK', path: '02-typescript' },
          'python': { title: 'Python SDK', path: '03-python' },
          'java': { title: 'Java SDK', path: '04-java' },
          'csharp': { title: 'C# SDK', path: '05-csharp' },
          'go': { title: 'Go SDK', path: '06-go' },
        },
      },
      'webhooks': {
        title: 'Webhooks',
        path: '06-webhooks',
        children: {
          'overview': { title: 'Webhooks Overview', path: '01-overview' },
          'events': { title: 'Event Types', path: '02-events' },
          'security': { title: 'Webhook Security', path: '03-security' },
          'retry-logic': { title: 'Retry Logic', path: '04-retry-logic' },
        },
      },
    },
  },
  'development': {
    title: 'Development',
    description: 'Internal development guides',
    path: '03-development',
    icon: 'Wrench',
    children: {
      'architecture': {
        title: 'Architecture',
        path: '01-architecture',
        children: {
          'overview': { title: 'Architecture Overview', path: '01-overview' },
          'frontend': { title: 'Frontend Architecture', path: '02-frontend' },
          'backend': { title: 'Backend Architecture', path: '03-backend' },
          'database': { title: 'Database Design', path: '04-database' },
          'infrastructure': { title: 'Infrastructure', path: '05-infrastructure' },
          'security': { title: 'Security Architecture', path: '06-security' },
        },
      },
      'setup': {
        title: 'Setup',
        path: '02-setup',
        children: {
          'local-development': { title: 'Local Development Setup', path: '01-local-development' },
          'docker': { title: 'Docker Setup', path: '02-docker' },
          'dependencies': { title: 'Dependencies', path: '03-dependencies' },
          'environment': { title: 'Environment Variables', path: '04-environment' },
          'ide-setup': { title: 'IDE Setup', path: '05-ide-setup' },
        },
      },
      'contributing': {
        title: 'Contributing',
        path: '03-contributing',
        children: {
          'guidelines': { title: 'Contribution Guidelines', path: '01-guidelines' },
          'code-style': { title: 'Code Style', path: '02-code-style' },
          'testing': { title: 'Testing Standards', path: '03-testing' },
          'documentation': { title: 'Documentation Standards', path: '04-documentation' },
          'pull-requests': { title: 'Pull Request Process', path: '05-pull-requests' },
          'code-review': { title: 'Code Review', path: '06-code-review' },
        },
      },
      'internals': {
        title: 'Internals',
        path: '04-internals',
        children: {
          'data-flow': { title: 'Data Flow', path: '01-data-flow' },
          'state-management': { title: 'State Management', path: '02-state-management' },
          'caching': { title: 'Caching Layer', path: '03-caching' },
          'queuing': { title: 'Job Queuing', path: '04-queuing' },
          'search': { title: 'Search System', path: '05-search' },
          'graph-engine': { title: 'Graph Engine', path: '06-graph-engine' },
        },
      },
      'testing': {
        title: 'Testing',
        path: '05-testing',
        children: {
          'unit-tests': { title: 'Unit Testing', path: '01-unit-tests' },
          'integration-tests': { title: 'Integration Testing', path: '02-integration-tests' },
          'e2e-tests': { title: 'E2E Testing', path: '03-e2e-tests' },
          'api-tests': { title: 'API Testing', path: '04-api-tests' },
          'performance-tests': { title: 'Performance Testing', path: '05-performance-tests' },
        },
      },
      'deployment': {
        title: 'Deployment',
        path: '06-deployment',
        children: {
          'ci-cd': { title: 'CI/CD Pipeline', path: '01-ci-cd' },
          'docker': { title: 'Docker Deployment', path: '02-docker' },
          'kubernetes': { title: 'Kubernetes Deployment', path: '03-kubernetes' },
          'monitoring': { title: 'Monitoring Setup', path: '04-monitoring' },
          'logging': { title: 'Logging Configuration', path: '05-logging' },
        },
      },
    },
  },
  'changelog': {
    title: 'Changelog',
    description: 'Version history and updates',
    path: '04-changelog',
    icon: 'RotateCcw',
    children: {
      'v1-0-0': { title: 'v1.0.0', path: '01-v1-0-0' },
      'v0-9-0': { title: 'v0.9.0', path: '02-v0-9-0' },
      'v0-8-0': { title: 'v0.8.0', path: '03-v0-8-0' },
      'v0-7-0': { title: 'v0.7.0', path: '04-v0-7-0' },
      'v0-6-0': { title: 'v0.6.0', path: '05-v0-6-0' },
      'v0-5-0': { title: 'v0.5.0', path: '06-v0-5-0' },
    },
  },
  'use-cases': {
    title: 'Use Cases',
    description: 'Real-world use cases and examples',
    path: '05-use-cases',
    icon: 'Briefcase',
    children: {
      'automotive': {
        title: 'Automotive',
        path: '01-automotive',
        children: {
          'iso-26262': { title: 'ISO 26262 Compliance', path: '01-iso-26262' },
          'safety-critical': { title: 'Safety-Critical Systems', path: '02-safety-critical' },
          'adas': { title: 'ADAS Development', path: '03-adas' },
        },
      },
      'aerospace': {
        title: 'Aerospace',
        path: '02-aerospace',
        children: {
          'do-178c': { title: 'DO-178C Compliance', path: '01-do-178c' },
          'systems-engineering': { title: 'Systems Engineering', path: '02-systems-engineering' },
        },
      },
      'medical': {
        title: 'Medical Devices',
        path: '03-medical',
        children: {
          'iec-62304': { title: 'IEC 62304 Compliance', path: '01-iec-62304' },
          'fda-validation': { title: 'FDA Validation', path: '02-fda-validation' },
        },
      },
      'software': {
        title: 'Software Development',
        path: '04-software',
        children: {
          'agile': { title: 'Agile Development', path: '01-agile' },
          'devops': { title: 'DevOps Integration', path: '02-devops' },
          'ci-cd': { title: 'CI/CD Pipelines', path: '03-ci-cd' },
        },
      },
    },
  },
  'enterprise': {
    title: 'Enterprise',
    description: 'Enterprise features and deployment',
    path: '06-enterprise',
    icon: 'Building',
    children: {
      'administration': {
        title: 'Administration',
        path: '01-administration',
        children: {
          'user-management': { title: 'User Management', path: '01-user-management' },
          'team-management': { title: 'Team Management', path: '02-team-management' },
          'permissions': { title: 'Permissions', path: '03-permissions' },
          'audit-logs': { title: 'Audit Logs', path: '04-audit-logs' },
        },
      },
      'deployment': {
        title: 'Deployment',
        path: '02-deployment',
        children: {
          'on-premises': { title: 'On-Premises Deployment', path: '01-on-premises' },
          'cloud': { title: 'Cloud Deployment', path: '02-cloud' },
          'hybrid': { title: 'Hybrid Deployment', path: '03-hybrid' },
          'high-availability': { title: 'High Availability', path: '04-high-availability' },
        },
      },
      'security': {
        title: 'Security',
        path: '03-security',
        children: {
          'sso': { title: 'Single Sign-On', path: '01-sso' },
          'saml': { title: 'SAML Integration', path: '02-saml' },
          'ldap': { title: 'LDAP Integration', path: '03-ldap' },
          'compliance': { title: 'Compliance Features', path: '04-compliance' },
        },
      },
    },
  },
}

// Calculate total pages
export function countPages(structure: any): number {
  let count = 0
  for (const [_, value] of Object.entries(structure)) {
    if (typeof value !== 'object' || !value) continue
    count++
    const item = value as any
    if (item.children) {
      count += countPages(item.children)
    }
  }
  return count
}

console.log(`Total pages in expanded structure: ${countPages(EXPANDED_STRUCTURE)}`)
