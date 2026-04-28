/**
 * Project configurations for mock data generation
 */

import type { ProjectConfig } from './types';

export const PROJECTS: ProjectConfig[] = [
  {
    name: 'TraceRTM Core Platform',
    description:
      'Enterprise requirements traceability and impact analysis system with real-time collaboration',
    domain: 'fullstack',
    itemCounts: {
      requirements: 200,
      features: 300,
      code: 400,
      tests: 300,
      api: 150,
      database: 150,
      wireframe: 100,
      documentation: 100,
      deployment: 50,
    },
  },
  {
    name: 'React Native Mobile Client',
    description: 'Cross-platform mobile application for TraceRTM with offline-first architecture',
    domain: 'mobile',
    itemCounts: {
      requirements: 120,
      features: 180,
      code: 250,
      tests: 200,
      api: 80,
      database: 60,
      wireframe: 150,
      documentation: 60,
      deployment: 40,
    },
  },
  {
    name: 'Data Analytics & Insights Engine',
    description: 'Real-time analytics, reporting, and predictive insights for project metrics',
    domain: 'data',
    itemCounts: {
      requirements: 150,
      features: 200,
      code: 300,
      tests: 250,
      api: 120,
      database: 200,
      wireframe: 50,
      documentation: 80,
      deployment: 40,
    },
  },
  {
    name: 'Infrastructure & DevOps',
    description: 'Kubernetes-based deployment, monitoring, and infrastructure-as-code automation',
    domain: 'devops',
    itemCounts: {
      requirements: 100,
      features: 150,
      code: 250,
      tests: 200,
      api: 80,
      database: 80,
      wireframe: 20,
      documentation: 100,
      deployment: 100,
    },
  },
  {
    name: 'AI-Powered Recommendations',
    description:
      'Machine learning models for intelligent requirement suggestions and anomaly detection',
    domain: 'ai',
    itemCounts: {
      requirements: 120,
      features: 150,
      code: 280,
      tests: 220,
      api: 100,
      database: 140,
      wireframe: 30,
      documentation: 70,
      deployment: 35,
    },
  },
  {
    name: 'Frontend Web Application v2',
    description:
      'Next-generation React + TypeScript web interface with advanced data visualization',
    domain: 'frontend',
    itemCounts: {
      requirements: 180,
      features: 250,
      code: 350,
      tests: 280,
      api: 100,
      database: 50,
      wireframe: 200,
      documentation: 90,
      deployment: 40,
    },
  },
  {
    name: 'Backend API Gateway',
    description:
      'GraphQL and REST API gateway with advanced caching, rate limiting, and authentication',
    domain: 'backend',
    itemCounts: {
      requirements: 130,
      features: 170,
      code: 300,
      tests: 250,
      api: 200,
      database: 120,
      wireframe: 10,
      documentation: 80,
      deployment: 50,
    },
  },
  {
    name: 'Integration Platform',
    description:
      'Multi-vendor integrations with Jira, GitHub, Azure DevOps, and enterprise systems',
    domain: 'backend',
    itemCounts: {
      requirements: 110,
      features: 140,
      code: 220,
      tests: 180,
      api: 150,
      database: 90,
      wireframe: 15,
      documentation: 70,
      deployment: 30,
    },
  },
];

export function getTotalItemCount(): number {
  return PROJECTS.reduce(
    (sum, p) => sum + Object.values(p.itemCounts).reduce((a, b) => a + b, 0),
    0,
  );
}

export function getProjectStats() {
  return PROJECTS.map((p) => ({
    name: p.name,
    domain: p.domain,
    items: Object.values(p.itemCounts).reduce((a, b) => a + b, 0),
  }));
}
