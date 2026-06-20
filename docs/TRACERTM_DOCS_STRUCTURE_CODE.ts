// TraceRTM MASSIVE Documentation Structure
// Copy this into the DOCS_STRUCTURE constant in docs-site/app/docs/[[...slug]]/page.tsx

export const DOCS_STRUCTURE_MASSIVE = {
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
          'macos': { title: 'Install on macOS', path: '01-macos' },
          'linux': { title: 'Install on Linux', path: '02-linux' },
          'windows': { title: 'Install on Windows', path: '03-windows' },
          'docker': { title: 'Install with Docker', path: '04-docker' },
          'binary': { title: 'Binary Installation', path: '05-binary' },
          'source': { title: 'Build from Source', path: '06-source' },
        },
      },
      'quick-start': { title: 'Quick Start Guide', path: '02-quick-start' },
      'system-requirements': {
        title: 'System Requirements',
        path: '03-system-requirements',
        children: {
          'hardware': { title: 'Hardware Requirements', path: '01-hardware' },
          'software': { title: 'Software Dependencies', path: '02-software' },
          'network': { title: 'Network Requirements', path: '03-network' },
        },
      },
      'core-concepts': {
        title: 'Core Concepts',
        path: '04-core-concepts',
        children: {
          'traceability': { title: 'What is Traceability?', path: '01-traceability' },
          'artifacts': { title: 'Understanding Artifacts', path: '02-artifacts' },
          'relationships': { title: 'Artifact Relationships', path: '03-relationships' },
          'workflows': { title: 'Workflow Basics', path: '04-workflows' },
          'projects': { title: 'Projects & Organization', path: '05-projects' },
        },
      },
      'first-project': {
        title: 'First Project Tutorial',
        path: '05-first-project',
        children: {
          'create-project': { title: 'Creating a Project', path: '01-create-project' },
          'add-artifacts': { title: 'Adding Artifacts', path: '02-add-artifacts' },
          'link-artifacts': { title: 'Linking Artifacts', path: '03-link-artifacts' },
          'run-queries': { title: 'Running Queries', path: '04-run-queries' },
        },
      },
      'basic-workflow': { title: 'Basic Workflow', path: '06-basic-workflow' },
      'advanced-workflow': {
        title: 'Advanced Workflow',
        path: '07-advanced-workflow',
        children: {
          'batch-operations': { title: 'Batch Operations', path: '01-batch-operations' },
          'automation': { title: 'Workflow Automation', path: '02-automation' },
          'custom-workflows': { title: 'Custom Workflows', path: '03-custom-workflows' },
        },
      },
      'configuration': {
        title: 'Configuration Guide',
        path: '08-configuration',
        children: {
          'config-file': { title: 'Configuration File', path: '01-config-file' },
          'environment-vars': { title: 'Environment Variables', path: '02-environment-vars' },
          'profiles': { title: 'Profiles', path: '03-profiles' },
        },
      },
      'environment-setup': {
        title: 'Environment Setup',
        path: '09-environment-setup',
        children: {
          'database': { title: 'Database Setup', path: '01-database' },
          'search': { title: 'Search Engine Setup', path: '02-search' },
          'cache': { title: 'Cache Setup', path: '03-cache' },
        },
      },
      'troubleshooting': {
        title: 'Troubleshooting Installation',
        path: '10-troubleshooting',
        children: {
          'common-errors': { title: 'Common Installation Errors', path: '01-common-errors' },
          'connection-issues': { title: 'Connection Issues', path: '02-connection-issues' },
          'permission-issues': { title: 'Permission Issues', path: '03-permission-issues' },
        },
      },
      'migration': {
        title: 'Migration from v1.x',
        path: '11-migration',
        children: {
          'breaking-changes': { title: 'Breaking Changes', path: '01-breaking-changes' },
          'migration-steps': { title: 'Migration Steps', path: '02-migration-steps' },
          'data-migration': { title: 'Data Migration', path: '03-data-migration' },
        },
      },
      'faq': { title: 'FAQ', path: '12-faq' },
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
              'overview': { title: 'Traceability Overview', path: '01-overview' },
              'best-practices': { title: 'Best Practices', path: '02-best-practices' },
              'patterns': { title: 'Traceability Patterns', path: '03-patterns' },
              'anti-patterns': { title: 'Anti-patterns', path: '04-anti-patterns' },
            },
          },
          'traceability-matrix': {
            title: 'Traceability Matrix',
            path: '02-traceability-matrix',
            children: {
              'creating': { title: 'Creating Matrices', path: '01-creating' },
              'managing': { title: 'Managing Matrices', path: '02-managing' },
              'exporting': { title: 'Exporting Matrices', path: '03-exporting' },
              'visualizing': { title: 'Visualizing Matrices', path: '04-visualizing' },
            },
          },
          'requirements': {
            title: 'Requirements',
            path: '03-requirements',
            children: {
              'types': { title: 'Requirement Types', path: '01-types' },
              'states': { title: 'Requirement States', path: '02-states' },
              'attributes': { title: 'Requirement Attributes', path: '03-attributes' },
              'templates': { title: 'Requirement Templates', path: '04-templates' },
              'baselines': { title: 'Baselines', path: '05-baselines' },
            },
          },
          'workflows': {
            title: 'Workflows',
            path: '04-workflows',
            children: {
              'states': { title: 'Workflow States', path: '01-states' },
              'transitions': { title: 'State Transitions', path: '02-transitions' },
              'automation': { title: 'Workflow Automation', path: '03-automation' },
              'custom': { title: 'Custom Workflows', path: '04-custom' },
            },
          },
          'artifacts': {
            title: 'Artifacts',
            path: '05-artifacts',
            children: {
              'types': { title: 'Artifact Types', path: '01-types' },
              'versioning': { title: 'Artifact Versioning', path: '02-versioning' },
              'templates': { title: 'Artifact Templates', path: '03-templates' },
              'management': { title: 'Artifact Management', path: '04-management' },
            },
          },
          'relationships': {
            title: 'Relationships',
            path: '06-relationships',
            children: {
              'types': { title: 'Relationship Types', path: '01-types' },
              'directionality': { title: 'Directionality', path: '02-directionality' },
              'rules': { title: 'Relationship Rules', path: '03-rules' },
              'validation': { title: 'Link Validation', path: '04-validation' },
            },
          },
          'impact-analysis': {
            title: 'Impact Analysis',
            path: '07-impact-analysis',
            children: {
              'forward': { title: 'Forward Tracing', path: '01-forward' },
              'backward': { title: 'Backward Tracing', path: '02-backward' },
              'change-impact': { title: 'Change Impact Analysis', path: '03-change-impact' },
            },
          },
          'versioning': {
            title: 'Versioning',
            path: '08-versioning',
            children: {
              'strategies': { title: 'Versioning Strategies', path: '01-strategies' },
              'branching': { title: 'Branching', path: '02-branching' },
              'merging': { title: 'Merging', path: '03-merging' },
              'history': { title: 'Version History', path: '04-history' },
            },
          },
          'baselines': {
            title: 'Baselines',
            path: '09-baselines',
            children: {
              'creating': { title: 'Creating Baselines', path: '01-creating' },
              'comparing': { title: 'Comparing Baselines', path: '02-comparing' },
              'restoring': { title: 'Restoring Baselines', path: '03-restoring' },
            },
          },
          'compliance': {
            title: 'Compliance',
            path: '10-compliance',
            children: {
              'standards': { title: 'Compliance Standards', path: '01-standards' },
              'auditing': { title: 'Auditing', path: '02-auditing' },
              'reports': { title: 'Compliance Reports', path: '03-reports' },
            },
          },
          'custom-fields': {
            title: 'Custom Fields',
            path: '11-custom-fields',
            children: {
              'creating': { title: 'Creating Custom Fields', path: '01-creating' },
              'types': { title: 'Field Types', path: '02-types' },
              'validation': { title: 'Field Validation', path: '03-validation' },
            },
          },
          'templates': {
            title: 'Templates',
            path: '12-templates',
            children: {
              'item-templates': { title: 'Item Templates', path: '01-item-templates' },
              'workflow-templates': { title: 'Workflow Templates', path: '02-workflow-templates' },
            },
          },
          'permissions': {
            title: 'Permissions',
            path: '13-permissions',
            children: {
              'users': { title: 'User Management', path: '01-users' },
              'roles': { title: 'Roles', path: '02-roles' },
              'teams': { title: 'Teams', path: '03-teams' },
              'access-control': { title: 'Access Control', path: '04-access-control' },
            },
          },
          'notifications': {
            title: 'Notifications',
            path: '14-notifications',
            children: {
              'email': { title: 'Email Notifications', path: '01-email' },
              'webhooks': { title: 'Webhook Notifications', path: '02-webhooks' },
              'integrations': { title: 'Integration Notifications', path: '03-integrations' },
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
              'overview': { title: 'CLI Overview', path: '01-overview' },
              'global-flags': { title: 'Global Flags', path: '02-global-flags' },
              'configuration': { title: 'CLI Configuration', path: '03-configuration' },
              'aliases': { title: 'Command Aliases', path: '04-aliases' },
            },
          },
          'web-ui': {
            title: 'Web UI Guide',
            path: '02-web-ui',
            children: {
              'overview': { title: 'UI Overview', path: '01-overview' },
              'navigation': { title: 'Navigation', path: '02-navigation' },
              'keyboard-shortcuts': { title: 'Keyboard Shortcuts', path: '03-keyboard-shortcuts' },
            },
          },
          'dashboard': {
            title: 'Dashboard',
            path: '03-dashboard',
            children: {
              'overview': { title: 'Dashboard Overview', path: '01-overview' },
              'widgets': { title: 'Dashboard Widgets', path: '02-widgets' },
              'customization': { title: 'Customization', path: '03-customization' },
            },
          },
          'item-management': {
            title: 'Item Management',
            path: '04-item-management',
            children: {
              'creating': { title: 'Creating Items', path: '01-creating' },
              'editing': { title: 'Editing Items', path: '02-editing' },
              'bulk-operations': { title: 'Bulk Operations', path: '03-bulk-operations' },
            },
          },
          'link-management': {
            title: 'Link Management',
            path: '05-link-management',
            children: {
              'creating': { title: 'Creating Links', path: '01-creating' },
              'visualizing': { title: 'Visualizing Links', path: '02-visualizing' },
              'managing': { title: 'Managing Links', path: '03-managing' },
            },
          },
          'search': {
            title: 'Search Guide',
            path: '06-search',
            children: {
              'basic': { title: 'Basic Search', path: '01-basic' },
              'advanced': { title: 'Advanced Search', path: '02-advanced' },
              'saved-searches': { title: 'Saved Searches', path: '03-saved-searches' },
            },
          },
          'reports': {
            title: 'Reports',
            path: '07-reports',
            children: {
              'built-in': { title: 'Built-in Reports', path: '01-built-in' },
              'custom': { title: 'Custom Reports', path: '02-custom' },
              'scheduling': { title: 'Report Scheduling', path: '03-scheduling' },
              'export': { title: 'Report Export', path: '04-export' },
            },
          },
          'import-export': {
            title: 'Import/Export',
            path: '08-import-export',
            children: {
              'formats': { title: 'Supported Formats', path: '01-formats' },
              'tools': { title: 'Import/Export Tools', path: '02-tools' },
              'automation': { title: 'Automation', path: '03-automation' },
            },
          },
          'integrations': {
            title: 'Integrations',
            path: '09-integrations',
            children: {
              'jira': { title: 'Jira Integration', path: '01-jira' },
              'github': { title: 'GitHub Integration', path: '02-github' },
              'gitlab': { title: 'GitLab Integration', path: '03-gitlab' },
              'azure-devops': { title: 'Azure DevOps Integration', path: '04-azure-devops' },
            },
          },
          'cicd': {
            title: 'CI/CD Integration',
            path: '10-cicd',
            children: {
              'jenkins': { title: 'Jenkins Integration', path: '01-jenkins' },
              'github-actions': { title: 'GitHub Actions', path: '02-github-actions' },
              'gitlab-ci': { title: 'GitLab CI', path: '03-gitlab-ci' },
            },
          },
          'performance': {
            title: 'Performance Tuning',
            path: '11-performance',
            children: {
              'database': { title: 'Database Tuning', path: '01-database' },
              'search': { title: 'Search Optimization', path: '02-search' },
              'caching': { title: 'Caching Strategies', path: '03-caching' },
            },
          },
          'security': {
            title: 'Security Guide',
            path: '12-security',
            children: {
              'authentication': { title: 'Authentication', path: '01-authentication' },
              'authorization': { title: 'Authorization', path: '02-authorization' },
              'audit': { title: 'Security Audit', path: '03-audit' },
            },
          },
          'migration': {
            title: 'Migration Guide',
            path: '13-migration',
            children: {
              'versions': { title: 'Version Migration', path: '01-versions' },
              'tools': { title: 'Migration Tools', path: '02-tools' },
              'best-practices': { title: 'Migration Best Practices', path: '03-best-practices' },
            },
          },
          'backup-restore': {
            title: 'Backup & Restore',
            path: '14-backup-restore',
            children: {
              'strategies': { title: 'Backup Strategies', path: '01-strategies' },
              'tools': { title: 'Backup Tools', path: '02-tools' },
              'automation': { title: 'Automated Backups', path: '03-automation' },
            },
          },
        },
      },
      'examples': {
        title: 'Examples',
        path: '03-examples',
        children: {
          'hello-world': { title: 'Hello World', path: '01-hello-world' },
          'basic-workflow': { title: 'Basic Workflow Example', path: '02-basic-workflow' },
          'advanced-queries': {
            title: 'Advanced Query Examples',
            path: '03-advanced-queries',
            children: {
              'filtering': { title: 'Complex Filtering', path: '01-filtering' },
              'aggregation': { title: 'Aggregation Queries', path: '02-aggregation' },
              'graph-queries': { title: 'Graph Queries', path: '03-graph-queries' },
            },
          },
          'integration-examples': {
            title: 'Integration Examples',
            path: '04-integration-examples',
            children: {
              'jira-sync': { title: 'Jira Sync Example', path: '01-jira-sync' },
              'github-hooks': { title: 'GitHub Webhooks', path: '02-github-hooks' },
              'gitlab-pipeline': { title: 'GitLab Pipeline', path: '03-gitlab-pipeline' },
            },
          },
          'cicd-pipeline': {
            title: 'CI/CD Pipeline Examples',
            path: '05-cicd-pipeline',
            children: {
              'jenkins': { title: 'Jenkins Pipeline', path: '01-jenkins' },
              'github-actions': { title: 'GitHub Actions Workflow', path: '02-github-actions' },
              'gitlab-ci': { title: 'GitLab CI Example', path: '03-gitlab-ci' },
            },
          },
          'multi-project': {
            title: 'Multi-Project Setup',
            path: '06-multi-project',
            children: {
              'organization': { title: 'Project Organization', path: '01-organization' },
              'shared-artifacts': { title: 'Shared Artifacts', path: '02-shared-artifacts' },
            },
          },
          'multi-team': {
            title: 'Multi-Team Collaboration',
            path: '07-multi-team',
            children: {
              'permissions': { title: 'Team Permissions', path: '01-permissions' },
              'workflows': { title: 'Team Workflows', path: '02-workflows' },
            },
          },
          'compliance-tracking': {
            title: 'Compliance Tracking Examples',
            path: '08-compliance-tracking',
            children: {
              'iso-27001': { title: 'ISO 27001 Example', path: '01-iso-27001' },
              'fda-21-cfr': { title: 'FDA 21 CFR Part 11', path: '02-fda-21-cfr' },
            },
          },
          'real-world': {
            title: 'Real-World Scenarios',
            path: '09-real-world',
            children: {
              'automotive': { title: 'Automotive Industry', path: '01-automotive' },
              'aerospace': { title: 'Aerospace & Defense', path: '02-aerospace' },
              'medical': { title: 'Medical Devices', path: '03-medical' },
              'fintech': { title: 'Financial Technology', path: '04-fintech' },
            },
          },
          'enterprise-setup': {
            title: 'Enterprise Setup Examples',
            path: '10-enterprise-setup',
            children: {
              'multi-site': { title: 'Multi-Site Deployment', path: '01-multi-site' },
              'high-availability': { title: 'High Availability Setup', path: '02-high-availability' },
            },
          },
        },
      },
      'use-cases': {
        title: 'Use Cases',
        path: '04-use-cases',
        children: {
          'software-development': {
            title: 'Software Development',
            path: '01-software-development',
            children: {
              'agile': { title: 'Agile Development', path: '01-agile' },
              'waterfall': { title: 'Waterfall Projects', path: '02-waterfall' },
              'devops': { title: 'DevOps', path: '03-devops' },
            },
          },
          'aerospace-defense': {
            title: 'Aerospace & Defense',
            path: '02-aerospace-defense',
            children: {
              'do-178c': { title: 'DO-178C Compliance', path: '01-do-178c' },
              'mil-std': { title: 'MIL-STD Requirements', path: '02-mil-std' },
            },
          },
          'automotive': {
            title: 'Automotive',
            path: '03-automotive',
            children: {
              'iso-26262': { title: 'ISO 26262 Safety', path: '01-iso-26262' },
              'aspice': { title: 'ASPICE Compliance', path: '02-aspice' },
            },
          },
          'medical-devices': {
            title: 'Medical Devices',
            path: '04-medical-devices',
            children: {
              'iec-62304': { title: 'IEC 62304', path: '01-iec-62304' },
              'fda-validation': { title: 'FDA Validation', path: '02-fda-validation' },
            },
          },
          'pharmaceuticals': {
            title: 'Pharmaceuticals',
            path: '05-pharmaceuticals',
            children: {
              'gxp-compliance': { title: 'GxP Compliance', path: '01-gxp-compliance' },
              'validation': { title: 'System Validation', path: '02-validation' },
            },
          },
          'manufacturing': {
            title: 'Manufacturing',
            path: '06-manufacturing',
            children: {
              'quality-management': { title: 'Quality Management', path: '01-quality-management' },
              'supply-chain': { title: 'Supply Chain', path: '02-supply-chain' },
            },
          },
          'financial-services': {
            title: 'Financial Services',
            path: '07-financial-services',
            children: {
              'sox-compliance': { title: 'SOX Compliance', path: '01-sox-compliance' },
              'risk-management': { title: 'Risk Management', path: '02-risk-management' },
            },
          },
          'government': {
            title: 'Government',
            path: '08-government',
            children: {
              'fisma': { title: 'FISMA Compliance', path: '01-fisma' },
              'fedramp': { title: 'FedRAMP Requirements', path: '02-fedramp' },
            },
          },
          'telecommunications': {
            title: 'Telecommunications',
            path: '09-telecommunications',
            children: {
              'network-management': { title: 'Network Management', path: '01-network-management' },
              'compliance': { title: 'Telecom Compliance', path: '02-compliance' },
            },
          },
        },
      },
    },
  },
}

// Continue in next part...
