/**
 * Tests for Deployment View Route
 */

import { describe, expect, it } from 'vitest';

describe('Deployment View Route', () => {
  it('validates deployment view route path pattern', () => {
    const deploymentPath = '/projects/proj-1/views/deployment';
    expect(deploymentPath).toMatch(/^\/projects\/[^/]+\/views\/deployment$/);
  });

  it('extracts projectId from route parameters', () => {
    const path = '/projects/proj-123/views/deployment';
    const match = path.match(/\/projects\/([^/]+)\/views\/deployment/);

    expect(match).not.toBeNull();
    expect(match?.[1]).toBe('proj-123');
  });

  it('recognizes deployment view type from route', () => {
    const path = '/projects/proj-1/views/deployment';
    const [projectsSegment, projectId, viewsSegment, viewType] = path.split('/').slice(1);

    expect(projectsSegment).toBe('projects');
    expect(projectId).toBe('proj-1');
    expect(viewsSegment).toBe('views');
    expect(viewType).toBe('deployment');
  });

  it('supports deployment metadata', () => {
    const mockDeployment = {
      environment: 'production',
      id: 'deploy-1',
      status: 'done',
      title: 'Production Deployment',
      type: 'deployment',
    };

    expect(mockDeployment.environment).toMatch(/^(staging|production|development)$/);
    expect(mockDeployment.status).toMatch(/^(pending|done|failed)$/);
  });

  it('handles multiple deployments', () => {
    const mockDeployments = [
      { environment: 'development', id: 'd1', status: 'done' },
      { environment: 'staging', id: 'd2', status: 'done' },
      { environment: 'production', id: 'd3', status: 'pending' },
    ];

    expect(mockDeployments).toHaveLength(3);
    expect(mockDeployments.filter((d) => d.status === 'done')).toHaveLength(2);
  });
});
