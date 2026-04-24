/**
 * Mock data descriptions and code snippets
 */

export const codeSnippets = {
  python: [
    `def authenticate_user(email: str, password: str) -> User:
    """Authenticate user with email and password."""
    user = db.session.query(User).filter_by(email=email).first()
    if user and bcrypt.checkpw(password.encode(), user.password_hash):
        return user
    raise AuthenticationError("Invalid credentials")`,
    `class ProjectService:
    def __init__(self, db_session):
        self.db = db_session

    def create_project(self, name: str, description: str) -> Project:
        project = Project(name=name, description=description)
        self.db.add(project)
        self.db.commit()
        return project`,
    `@app.route('/api/v1/items', methods=['POST'])
def create_item():
    data = request.get_json()
    item = Item(**data)
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201`,
  ],
  typescript: [
    `export async function fetchItems(projectId?: string): Promise<Item[]> {
  const params = new URLSearchParams();
  if (projectId) params.set('project_id', projectId);
  const res = await fetch(\`\${API_URL}/api/v1/items?\${params}\`);
  if (!res.ok) throw new Error('Failed to fetch items');
  return res.json();
}`,
    `export function useItems(filters: ItemFilters = {}) {
  return useQuery({
    queryKey: ['items', filters],
    queryFn: () => fetchItems(filters.projectId),
  });
}`,
    `interface Item {
  id: string;
  project_id: string;
  type: ItemType;
  title: string;
  status: ItemStatus;
  priority?: ItemPriority;
}`,
  ],
  javascript: [
    `const express = require('express');
const router = express.Router();

router.post('/api/v1/items', async (req, res) => {
  try {
    const item = await Item.create(req.body);
    res.status(201).json(item);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});`,
  ],
  sql: [
    `CREATE TABLE items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(id),
  type VARCHAR(50) NOT NULL,
  title VARCHAR(255) NOT NULL,
  status VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);`,
    `CREATE INDEX idx_items_project_id ON items(project_id);
CREATE INDEX idx_items_type ON items(type);
CREATE INDEX idx_items_status ON items(status);`,
  ],
};

export const descriptions = {
  requirement: [
    // Functional Requirements
    'Users must be able to authenticate using email, password, and OAuth2 providers',
    'The system shall support multi-factor authentication with TOTP and SMS',
    'All API endpoints must return consistent error responses with descriptive messages',
    'Data must be encrypted at rest (AES-256) and in transit (TLS 1.3)',
    'The application must support real-time notifications via WebSocket',
    'Users must be able to manage projects with role-based access control (RBAC)',
    'The system shall maintain audit logs for all critical operations',
    'Requirements must support version control with change tracking',
    'The system shall provide search capabilities across all data types',
    'Users must be able to export data in multiple formats (JSON, CSV, PDF)',
    'The system shall support concurrent editing with conflict resolution',
    'Real-time collaboration features must sync within 500ms',
    'The system must handle up to 10,000 concurrent users',
    'API rate limiting must prevent abuse while maintaining performance',
    'All data must be backed up automatically with point-in-time recovery',
  ],
  feature: [
    // User-facing Features
    'User authentication with JWT tokens and refresh token rotation',
    'Project management dashboard with real-time team collaboration',
    'Multi-view traceability matrix visualization and filtering',
    'Advanced full-text search with AI-powered recommendations',
    'Automated report generation and export functionality',
    'Impact analysis visualization with dependency graphs',
    'Requirements lifecycle management with workflow automation',
    'Custom fields and metadata for flexible data modeling',
    'Bulk operations for efficient data management',
    'Mobile-responsive UI with progressive enhancement',
    'Dark mode and theme customization',
    'Notification center with customizable alerts',
    'File attachment and version management',
    'Comments and discussion threads on items',
    'Change history and rollback capabilities',
    'Relationship mapping and impact propagation',
    'Risk assessment and coverage metrics',
    'Compliance reporting for standards (ISO, SOC2)',
    'Integration with GitHub, Jira, and Azure DevOps',
    'Custom webhooks for external integrations',
  ],
  code: [
    // Implementation Details
    'Authentication service with OAuth2, JWT, and MFA support',
    'Database models for projects, items, links, and users',
    'REST API controllers with request/response validation',
    'GraphQL resolvers for efficient data fetching',
    'WebSocket handlers for real-time synchronization',
    'Search indexing and query optimization layer',
    'File storage service with versioning and deduplication',
    'Notification service with email, SMS, and push support',
    'Audit logging middleware and event streaming',
    'Rate limiting and throttling middleware',
    'Data encryption utilities and key management',
    'Error handling and exception mapping',
    'Caching layer with Redis integration',
    'Database migration management system',
    'Scheduled job handlers for background tasks',
    'Batch processing for bulk operations',
    'Data validation and sanitization utilities',
    'API client libraries for external integrations',
    'Mock data generators for testing',
    'Monitoring and metrics collection instrumentation',
  ],
  test: [
    // Testing Coverage
    'Unit tests for authentication service (login, logout, MFA)',
    'Integration tests for API endpoints (CRUD operations)',
    'E2E tests for complete user workflows',
    'Performance tests for database queries and API latency',
    'Security tests for authentication and authorization',
    'Load testing for 10,000 concurrent users',
    'Contract tests for API consumers',
    'Visual regression tests for UI components',
    'Accessibility tests for WCAG 2.1 compliance',
    'Data migration tests for schema changes',
    'Error recovery and resilience tests',
    'Concurrency and race condition tests',
    'Rate limiting and quota tests',
    'Backup and restore verification tests',
    'Security scanning for OWASP Top 10',
  ],
  api: [
    // API Endpoints
    'POST /api/v1/auth/login - User authentication',
    'POST /api/v1/auth/mfa - Multi-factor authentication',
    'GET /api/v1/projects - List user projects',
    'POST /api/v1/projects - Create new project',
    'GET /api/v1/items - Query items with filters',
    'POST /api/v1/items - Create new item',
    'PUT /api/v1/items/{id} - Update item',
    'DELETE /api/v1/items/{id} - Delete item',
    'GET /api/v1/items/{id}/history - Item change history',
    'POST /api/v1/links - Create traceability link',
    'DELETE /api/v1/links/{id} - Remove link',
    'GET /api/v1/search - Full-text search',
    'POST /api/v1/reports/generate - Generate report',
    'GET /api/v1/analytics/metrics - Project metrics',
    'POST /api/v1/integrations/github/sync - Sync with GitHub',
    'WebSocket /ws/projects/{id}/sync - Real-time collaboration',
  ],
  database: [
    // Database Schema
    'PostgreSQL table: users (id, email, password_hash, created_at)',
    'PostgreSQL table: projects (id, name, description, owner_id)',
    'PostgreSQL table: items (id, project_id, type, title, status, priority)',
    'PostgreSQL table: links (id, source_id, target_id, type, created_at)',
    'PostgreSQL table: audit_logs (id, user_id, action, entity_type, entity_id)',
    'Index: idx_items_project_id for query optimization',
    'Index: idx_items_status_priority for filtering',
    'Index: idx_audit_logs_user_id for audit trails',
    'Full-text search index on items.title and items.description',
    'Partitioning strategy for large audit tables',
    'Backup script with automated daily snapshots',
    'Data archival policy for historical data',
    'Replication configuration for high availability',
  ],
};
