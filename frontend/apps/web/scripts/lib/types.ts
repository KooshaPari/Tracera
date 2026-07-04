/**
 * Type definitions for mock data generation
 */

export type ItemType =
  | 'requirement'
  | 'feature'
  | 'code'
  | 'test'
  | 'api'
  | 'database'
  | 'wireframe'
  | 'documentation'
  | 'deployment';

export type ItemStatus = 'pending' | 'in_progress' | 'completed' | 'blocked';
export type ItemPriority = 'low' | 'medium' | 'high' | 'critical';
export type LinkType = 'implements' | 'tests' | 'depends_on' | 'relates_to';
export type ProjectDomain =
  | 'backend'
  | 'frontend'
  | 'mobile'
  | 'devops'
  | 'data'
  | 'ai'
  | 'fullstack';

export interface CreateItemInput {
  project_id: string;
  type: ItemType;
  title: string;
  description?: string;
  status?: ItemStatus;
  priority?: ItemPriority;
  parent_id?: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
}

export interface ProjectConfig {
  name: string;
  description: string;
  domain: ProjectDomain;
  itemCounts: {
    requirements: number;
    features: number;
    code: number;
    tests: number;
    api: number;
    database: number;
    wireframe: number;
    documentation: number;
    deployment: number;
  };
}

export interface ItemsByType {
  requirement: any[];
  feature: any[];
  code: any[];
  test: any[];
  api: any[];
  database: any[];
  wireframe: any[];
  documentation: any[];
  deployment: any[];
}
