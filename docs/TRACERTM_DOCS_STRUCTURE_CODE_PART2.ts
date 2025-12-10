// TraceRTM MASSIVE Documentation Structure - Part 2
// API Reference, Development, and Changelog sections

export const DOCS_STRUCTURE_PART2 = {
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
          'api-keys': {
            title: 'API Keys',
            path: '01-api-keys',
            children: {
              'overview': { title: 'API Keys Overview', path: '01-overview' },
              'management': { title: 'Key Management', path: '02-management' },
              'rotation': { title: 'Key Rotation', path: '03-rotation' },
              'scopes': { title: 'Key Scopes', path: '04-scopes' },
            },
          },
          'oauth': {
            title: 'OAuth 2.0',
            path: '02-oauth',
            children: {
              'flows': { title: 'OAuth Flows', path: '01-flows' },
              'clients': { title: 'OAuth Clients', path: '02-clients' },
              'tokens': { title: 'Access Tokens', path: '03-tokens' },
            },
          },
          'jwt': {
            title: 'JWT',
            path: '03-jwt',
            children: {
              'claims': { title: 'JWT Claims', path: '01-claims' },
              'validation': { title: 'Token Validation', path: '02-validation' },
              'refresh': { title: 'Token Refresh', path: '03-refresh' },
            },
          },
          'saml': {
            title: 'SAML 2.0',
            path: '04-saml',
            children: {
              'configuration': { title: 'SAML Configuration', path: '01-configuration' },
              'federation': { title: 'Identity Federation', path: '02-federation' },
            },
          },
          'ldap': {
            title: 'LDAP/Active Directory',
            path: '05-ldap',
            children: {
              'configuration': { title: 'LDAP Configuration', path: '01-configuration' },
              'sync': { title: 'User Synchronization', path: '02-sync' },
            },
          },
          'mfa': { title: 'Multi-Factor Authentication', path: '06-mfa' },
          'sessions': { title: 'Session Management', path: '07-sessions' },
          'sso': { title: 'SSO Configuration', path: '08-sso' },
        },
      },
      'rest-api': {
        title: 'REST API',
        path: '02-rest-api',
        children: {
          'overview': {
            title: 'Overview & Getting Started',
            path: '00-overview',
            children: {
              'introduction': { title: 'API Introduction', path: '01-introduction' },
              'authentication': { title: 'Quick Authentication', path: '02-authentication' },
              'first-request': { title: 'First API Request', path: '03-first-request' },
            },
          },
          'base-url': { title: 'Base URL & Versioning', path: '00a-base-url' },
          'projects': {
            title: 'Projects API',
            path: '01-projects',
            children: {
              'list': { title: 'List Projects', path: '01-list' },
              'get': { title: 'Get Project', path: '02-get' },
              'create': { title: 'Create Project', path: '03-create' },
              'update': { title: 'Update Project', path: '04-update' },
              'delete': { title: 'Delete Project', path: '05-delete' },
              'search': { title: 'Search Projects', path: '06-search' },
              'settings': { title: 'Project Settings', path: '07-settings' },
            },
          },
          'items': {
            title: 'Items API',
            path: '02-items',
            children: {
              'list': { title: 'List Items', path: '01-list' },
              'get': { title: 'Get Item', path: '02-get' },
              'create': { title: 'Create Item', path: '03-create' },
              'update': { title: 'Update Item', path: '04-update' },
              'delete': { title: 'Delete Item', path: '05-delete' },
              'bulk': { title: 'Bulk Operations', path: '06-bulk' },
              'search': { title: 'Search Items', path: '07-search' },
              'history': { title: 'Item History', path: '08-history' },
            },
          },
          'links': {
            title: 'Links API',
            path: '03-links',
            children: {
              'create': { title: 'Create Link', path: '01-create' },
              'delete': { title: 'Delete Link', path: '02-delete' },
              'query': { title: 'Query Links', path: '03-query' },
              'validation': { title: 'Link Validation', path: '04-validation' },
            },
          },
          'workflows': {
            title: 'Workflows API',
            path: '04-workflows',
            children: {
              'states': { title: 'Workflow States', path: '01-states' },
              'transitions': { title: 'State Transitions', path: '02-transitions' },
              'automation': { title: 'Workflow Automation', path: '03-automation' },
            },
          },
          'search': {
            title: 'Search API',
            path: '05-search',
            children: {
              'basic': { title: 'Basic Search', path: '01-basic' },
              'advanced': { title: 'Advanced Search', path: '02-advanced' },
              'filters': { title: 'Search Filters', path: '03-filters' },
              'facets': { title: 'Search Facets', path: '04-facets' },
            },
          },
          'reports': {
            title: 'Reports API',
            path: '06-reports',
            children: {
              'generate': { title: 'Generate Reports', path: '01-generate' },
              'schedule': { title: 'Schedule Reports', path: '02-schedule' },
              'export': { title: 'Export Reports', path: '03-export' },
            },
          },
          'users': {
            title: 'Users API',
            path: '07-users',
            children: {
              'crud': { title: 'User CRUD', path: '01-crud' },
              'roles': { title: 'User Roles', path: '02-roles' },
              'permissions': { title: 'User Permissions', path: '03-permissions' },
            },
          },
          'teams': {
            title: 'Teams API',
            path: '08-teams',
            children: {
              'crud': { title: 'Team CRUD', path: '01-crud' },
              'members': { title: 'Team Members', path: '02-members' },
              'permissions': { title: 'Team Permissions', path: '03-permissions' },
            },
          },
          'webhooks': {
            title: 'Webhooks API',
            path: '09-webhooks',
            children: {
              'register': { title: 'Register Webhooks', path: '01-register' },
              'manage': { title: 'Manage Webhooks', path: '02-manage' },
              'events': { title: 'Webhook Events', path: '03-events' },
            },
          },
          'batch': {
            title: 'Batch Operations',
            path: '10-batch',
            children: {
              'create': { title: 'Bulk Create', path: '01-create' },
              'update': { title: 'Bulk Update', path: '02-update' },
              'delete': { title: 'Bulk Delete', path: '03-delete' },
            },
          },
          'rate-limiting': {
            title: 'Rate Limiting',
            path: '11-rate-limiting',
            children: {
              'quotas': { title: 'Rate Quotas', path: '01-quotas' },
              'headers': { title: 'Rate Limit Headers', path: '02-headers' },
              'throttling': { title: 'Request Throttling', path: '03-throttling' },
            },
          },
          'pagination': {
            title: 'Pagination',
            path: '12-pagination',
            children: {
              'cursor': { title: 'Cursor Pagination', path: '01-cursor' },
              'offset': { title: 'Offset Pagination', path: '02-offset' },
              'performance': { title: 'Pagination Performance', path: '03-performance' },
            },
          },
          'filtering': {
            title: 'Filtering',
            path: '13-filtering',
            children: {
              'operators': { title: 'Filter Operators', path: '01-operators' },
              'expressions': { title: 'Filter Expressions', path: '02-expressions' },
              'complex': { title: 'Complex Queries', path: '03-complex' },
            },
          },
          'sorting': {
            title: 'Sorting',
            path: '14-sorting',
            children: {
              'fields': { title: 'Sort Fields', path: '01-fields' },
              'multi-sort': { title: 'Multi-field Sort', path: '02-multi-sort' },
              'performance': { title: 'Sort Performance', path: '03-performance' },
            },
          },
          'field-selection': {
            title: 'Field Selection',
            path: '15-field-selection',
            children: {
              'sparse-fieldsets': { title: 'Sparse Fieldsets', path: '01-sparse-fieldsets' },
              'performance': { title: 'Performance Benefits', path: '02-performance' },
            },
          },
          'errors': {
            title: 'Error Handling',
            path: '16-errors',
            children: {
              'codes': { title: 'Error Codes', path: '01-codes' },
              'messages': { title: 'Error Messages', path: '02-messages' },
              'debugging': { title: 'Debugging Errors', path: '03-debugging' },
            },
          },
          'versioning': {
            title: 'API Versioning',
            path: '17-versioning',
            children: {
              'strategy': { title: 'Versioning Strategy', path: '01-strategy' },
              'deprecation': { title: 'Deprecation Policy', path: '02-deprecation' },
            },
          },
          'changelog': {
            title: 'API Changelog',
            path: '18-changelog',
            children: {
              'v3': { title: 'v3 Changes', path: '01-v3' },
              'v2': { title: 'v2 Changes', path: '02-v2' },
              'migration': { title: 'Migration Guides', path: '03-migration' },
            },
          },
        },
      },
      'graphql-api': {
        title: 'GraphQL API',
        path: '03-graphql-api',
        children: {
          'overview': { title: 'GraphQL Overview', path: '01-overview' },
          'schema': {
            title: 'Schema',
            path: '02-schema',
            children: {
              'types': { title: 'Types', path: '01-types' },
              'interfaces': { title: 'Interfaces', path: '02-interfaces' },
              'unions': { title: 'Unions', path: '03-unions' },
            },
          },
          'queries': {
            title: 'Queries',
            path: '03-queries',
            children: {
              'basic': { title: 'Basic Queries', path: '01-basic' },
              'advanced': { title: 'Advanced Queries', path: '02-advanced' },
              'fragments': { title: 'Fragments', path: '03-fragments' },
            },
          },
          'mutations': {
            title: 'Mutations',
            path: '04-mutations',
            children: {
              'create': { title: 'Create Mutations', path: '01-create' },
              'update': { title: 'Update Mutations', path: '02-update' },
              'delete': { title: 'Delete Mutations', path: '03-delete' },
            },
          },
          'subscriptions': {
            title: 'Subscriptions',
            path: '05-subscriptions',
            children: {
              'real-time': { title: 'Real-time Updates', path: '01-real-time' },
              'events': { title: 'Event Subscriptions', path: '02-events' },
            },
          },
          'pagination': { title: 'Pagination', path: '06-pagination' },
          'errors': { title: 'Error Handling', path: '07-errors' },
          'best-practices': { title: 'Best Practices', path: '08-best-practices' },
        },
      },
      'cli': {
        title: 'CLI',
        path: '04-cli',
        children: {
          'installation': {
            title: 'Installation',
            path: '01-installation',
            children: {
              'macos': { title: 'Install on macOS', path: '01-macos' },
              'linux': { title: 'Install on Linux', path: '02-linux' },
              'windows': { title: 'Install on Windows', path: '03-windows' },
            },
          },
          'configuration': {
            title: 'Configuration',
            path: '02-configuration',
            children: {
              'files': { title: 'Config Files', path: '01-files' },
              'environment': { title: 'Environment Variables', path: '02-environment' },
              'profiles': { title: 'Profiles', path: '03-profiles' },
            },
          },
          'project-commands': { title: 'Project Commands', path: '03-project-commands' },
          'item-commands': { title: 'Item Commands', path: '04-item-commands' },
          'link-commands': { title: 'Link Commands', path: '05-link-commands' },
          'workflow-commands': { title: 'Workflow Commands', path: '06-workflow-commands' },
          'search-commands': { title: 'Search Commands', path: '07-search-commands' },
          'report-commands': { title: 'Report Commands', path: '08-report-commands' },
          'import-export': { title: 'Import/Export Commands', path: '09-import-export' },
          'user-management': { title: 'User Management', path: '10-user-management' },
          'scripting': {
            title: 'Scripting & Automation',
            path: '11-scripting',
            children: {
              'bash': { title: 'Bash Scripting', path: '01-bash' },
              'powershell': { title: 'PowerShell Scripting', path: '02-powershell' },
              'python': { title: 'Python Scripting', path: '03-python' },
            },
          },
          'plugins': {
            title: 'Plugins',
            path: '12-plugins',
            children: {
              'development': { title: 'Plugin Development', path: '01-development' },
              'marketplace': { title: 'Plugin Marketplace', path: '02-marketplace' },
            },
          },
          'troubleshooting': {
            title: 'Troubleshooting',
            path: '13-troubleshooting',
            children: {
              'common-errors': { title: 'Common Errors', path: '01-common-errors' },
              'debug-mode': { title: 'Debug Mode', path: '02-debug-mode' },
            },
          },
        },
      },
      'sdks': {
        title: 'SDKs',
        path: '05-sdks',
        children: {
          'python': {
            title: 'Python SDK',
            path: '01-python',
            children: {
              'installation': { title: 'Installation & Setup', path: '01-installation' },
              'quickstart': { title: 'Quick Start', path: '02-quickstart' },
              'authentication': { title: 'Authentication', path: '03-authentication' },
              'configuration': { title: 'Configuration', path: '04-configuration' },
              'projects': { title: 'Projects API', path: '05-projects' },
              'items': { title: 'Items API', path: '06-items' },
              'links': { title: 'Links API', path: '07-links' },
              'workflows': { title: 'Workflows API', path: '08-workflows' },
              'search': { title: 'Search API', path: '09-search' },
              'async': { title: 'Async/Concurrency', path: '10-async' },
              'error-handling': { title: 'Error Handling', path: '11-error-handling' },
              'testing': { title: 'Testing & Mocking', path: '12-testing' },
              'best-practices': { title: 'Best Practices', path: '13-best-practices' },
              'migration': { title: 'Migration Guide', path: '14-migration' },
            },
          },
          'javascript': {
            title: 'JavaScript/TypeScript SDK',
            path: '02-javascript',
            children: {
              'installation': { title: 'Installation & Setup', path: '01-installation' },
              'quickstart': { title: 'Quick Start', path: '02-quickstart' },
              'authentication': { title: 'Authentication', path: '03-authentication' },
              'configuration': { title: 'Configuration', path: '04-configuration' },
              'projects': { title: 'Projects API', path: '05-projects' },
              'items': { title: 'Items API', path: '06-items' },
              'links': { title: 'Links API', path: '07-links' },
              'workflows': { title: 'Workflows API', path: '08-workflows' },
              'search': { title: 'Search API', path: '09-search' },
              'async': { title: 'Async/Promises', path: '10-async' },
              'error-handling': { title: 'Error Handling', path: '11-error-handling' },
              'testing': { title: 'Testing & Mocking', path: '12-testing' },
              'best-practices': { title: 'Best Practices', path: '13-best-practices' },
              'migration': { title: 'Migration Guide', path: '14-migration' },
            },
          },
          'go': {
            title: 'Go SDK',
            path: '03-go',
            children: {
              'installation': { title: 'Installation & Setup', path: '01-installation' },
              'quickstart': { title: 'Quick Start', path: '02-quickstart' },
              'authentication': { title: 'Authentication', path: '03-authentication' },
              'configuration': { title: 'Configuration', path: '04-configuration' },
              'projects': { title: 'Projects API', path: '05-projects' },
              'items': { title: 'Items API', path: '06-items' },
              'links': { title: 'Links API', path: '07-links' },
              'workflows': { title: 'Workflows API', path: '08-workflows' },
              'search': { title: 'Search API', path: '09-search' },
              'concurrency': { title: 'Concurrency Patterns', path: '10-concurrency' },
              'error-handling': { title: 'Error Handling', path: '11-error-handling' },
              'testing': { title: 'Testing & Mocking', path: '12-testing' },
              'best-practices': { title: 'Best Practices', path: '13-best-practices' },
              'migration': { title: 'Migration Guide', path: '14-migration' },
            },
          },
          'java': {
            title: 'Java SDK',
            path: '04-java',
            children: {
              'installation': { title: 'Installation & Setup', path: '01-installation' },
              'quickstart': { title: 'Quick Start', path: '02-quickstart' },
              'authentication': { title: 'Authentication', path: '03-authentication' },
              'configuration': { title: 'Configuration', path: '04-configuration' },
              'projects': { title: 'Projects API', path: '05-projects' },
              'items': { title: 'Items API', path: '06-items' },
              'links': { title: 'Links API', path: '07-links' },
              'workflows': { title: 'Workflows API', path: '08-workflows' },
              'search': { title: 'Search API', path: '09-search' },
              'async': { title: 'Async/Concurrency', path: '10-async' },
              'error-handling': { title: 'Error Handling', path: '11-error-handling' },
              'testing': { title: 'Testing & Mocking', path: '12-testing' },
              'best-practices': { title: 'Best Practices', path: '13-best-practices' },
              'migration': { title: 'Migration Guide', path: '14-migration' },
            },
          },
          'dotnet': {
            title: '.NET SDK',
            path: '05-dotnet',
            children: {
              'installation': { title: 'Installation & Setup', path: '01-installation' },
              'quickstart': { title: 'Quick Start', path: '02-quickstart' },
              'authentication': { title: 'Authentication', path: '03-authentication' },
              'configuration': { title: 'Configuration', path: '04-configuration' },
              'projects': { title: 'Projects API', path: '05-projects' },
              'items': { title: 'Items API', path: '06-items' },
              'links': { title: 'Links API', path: '07-links' },
              'workflows': { title: 'Workflows API', path: '08-workflows' },
              'search': { title: 'Search API', path: '09-search' },
              'async': { title: 'Async/Await', path: '10-async' },
              'error-handling': { title: 'Error Handling', path: '11-error-handling' },
              'testing': { title: 'Testing & Mocking', path: '12-testing' },
              'best-practices': { title: 'Best Practices', path: '13-best-practices' },
              'migration': { title: 'Migration Guide', path: '14-migration' },
            },
          },
          'ruby': {
            title: 'Ruby SDK',
            path: '06-ruby',
            children: {
              'installation': { title: 'Installation & Setup', path: '01-installation' },
              'quickstart': { title: 'Quick Start', path: '02-quickstart' },
              'authentication': { title: 'Authentication', path: '03-authentication' },
              'configuration': { title: 'Configuration', path: '04-configuration' },
              'projects': { title: 'Projects API', path: '05-projects' },
              'items': { title: 'Items API', path: '06-items' },
              'links': { title: 'Links API', path: '07-links' },
              'workflows': { title: 'Workflows API', path: '08-workflows' },
              'search': { title: 'Search API', path: '09-search' },
              'async': { title: 'Async Patterns', path: '10-async' },
              'error-handling': { title: 'Error Handling', path: '11-error-handling' },
              'testing': { title: 'Testing & Mocking', path: '12-testing' },
              'best-practices': { title: 'Best Practices', path: '13-best-practices' },
              'migration': { title: 'Migration Guide', path: '14-migration' },
            },
          },
        },
      },
    },
  },
}

// Continue in Part 3 for Development and Changelog...
