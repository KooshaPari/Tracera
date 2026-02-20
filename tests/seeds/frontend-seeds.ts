// Frontend Mock Data Seeds - Finalized Shapes
// Linked to: All frontend tests

import { faker } from '@faker-js/faker';

// ============================================================================
// TYPE DEFINITIONS (Finalized Shapes)
// ============================================================================

export interface Item {
  id: string;
  projectId: string;
  title: string;
  type: 'REQUIREMENT' | 'DESIGN' | 'IMPLEMENTATION' | 'TEST' | 'DEPLOYMENT' | 'DOCUMENTATION' | 'RESEARCH' | 'SPIKE';
  description: string;
  status: 'DRAFT' | 'ACTIVE' | 'IN_PROGRESS' | 'COMPLETED' | 'ARCHIVED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  tags: string[];
  assignees: string[];
  estimatedEffort?: number;
  actualEffort?: number;
  dueDate?: Date;
  completedDate?: Date;
  metadata: Record<string, any>;
  createdBy: string;
  createdAt: Date;
  updatedBy: string;
  updatedAt: Date;
  deletedAt?: Date;
}

export interface Link {
  id: string;
  projectId: string;
  type: 'DEPENDS_ON' | 'BLOCKS' | 'RELATES_TO' | 'DUPLICATES' | 'PARENT_OF' | 'CHILD_OF';
  sourceId: string;
  targetId: string;
  description: string;
  metadata: Record<string, any>;
  createdBy: string;
  createdAt: Date;
  updatedBy: string;
  updatedAt: Date;
}

export interface Agent {
  id: string;
  name: string;
  status: 'ONLINE' | 'OFFLINE' | 'BUSY' | 'ERROR';
  capabilities: string[];
  currentItemId?: string;
  itemsCompleted: number;
  itemsFailed: number;
  successRate: number;
  averageTime: number;
  metadata: Record<string, any>;
  registeredAt: Date;
  lastSeenAt: Date;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'ADMIN' | 'MANAGER' | 'USER' | 'VIEWER';
  permissions: string[];
  avatar?: string;
  metadata: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
  lastLoginAt?: Date;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  status: 'PLANNING' | 'ACTIVE' | 'COMPLETED' | 'ARCHIVED';
  owner: string;
  members: string[];
  itemCount: number;
  linkCount: number;
  metadata: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

// ============================================================================
// SEED DATA GENERATORS
// ============================================================================

export class FrontendSeedData {
  // ============================================================================
  // ITEM SEEDS
  // ============================================================================

  static generateItem(overrides: Partial<Item> = {}): Item {
    const now = new Date();
    const pastDate = new Date(now.getTime() - 24 * 60 * 60 * 1000);

    return {
      id: faker.string.uuid(),
      projectId: faker.string.uuid(),
      title: faker.lorem.sentence(),
      type: faker.helpers.arrayElement(['REQUIREMENT', 'DESIGN', 'IMPLEMENTATION', 'TEST', 'DEPLOYMENT', 'DOCUMENTATION', 'RESEARCH', 'SPIKE']),
      description: faker.lorem.paragraphs(2),
      status: faker.helpers.arrayElement(['DRAFT', 'ACTIVE', 'IN_PROGRESS', 'COMPLETED']),
      priority: faker.helpers.arrayElement(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
      tags: faker.helpers.multiple(() => faker.lorem.word(), { count: { min: 0, max: 5 } }),
      assignees: faker.helpers.multiple(() => faker.string.uuid(), { count: { min: 0, max: 3 } }),
      estimatedEffort: faker.number.int({ min: 1, max: 13 }),
      actualEffort: faker.number.int({ min: 1, max: 13 }),
      dueDate: faker.date.future(),
      metadata: {},
      createdBy: faker.string.uuid(),
      createdAt: pastDate,
      updatedBy: faker.string.uuid(),
      updatedAt: now,
      ...overrides,
    };
  }

  static generateItems(count: number, overrides: Partial<Item> = {}): Item[] {
    return Array.from({ length: count }, () => this.generateItem(overrides));
  }

  static generateItemsByType(type: Item['type'], count: number = 5): Item[] {
    return this.generateItems(count, { type });
  }

  static generateItemsByStatus(status: Item['status'], count: number = 5): Item[] {
    return this.generateItems(count, { status });
  }

  static generateItemsByPriority(priority: Item['priority'], count: number = 5): Item[] {
    return this.generateItems(count, { priority });
  }

  // ============================================================================
  // LINK SEEDS
  // ============================================================================

  static generateLink(sourceId: string, targetId: string, overrides: Partial<Link> = {}): Link {
    const now = new Date();
    const pastDate = new Date(now.getTime() - 24 * 60 * 60 * 1000);

    return {
      id: faker.string.uuid(),
      projectId: faker.string.uuid(),
      type: faker.helpers.arrayElement(['DEPENDS_ON', 'BLOCKS', 'RELATES_TO', 'DUPLICATES', 'PARENT_OF', 'CHILD_OF']),
      sourceId,
      targetId,
      description: faker.lorem.sentence(),
      metadata: {},
      createdBy: faker.string.uuid(),
      createdAt: pastDate,
      updatedBy: faker.string.uuid(),
      updatedAt: now,
      ...overrides,
    };
  }

  static generateLinks(count: number, sourceId: string, targetId: string): Link[] {
    return Array.from({ length: count }, () => this.generateLink(sourceId, targetId));
  }

  static generateLinksByType(type: Link['type'], sourceId: string, targetId: string, count: number = 5): Link[] {
    return Array.from({ length: count }, () => this.generateLink(sourceId, targetId, { type }));
  }

  // ============================================================================
  // AGENT SEEDS
  // ============================================================================

  static generateAgent(overrides: Partial<Agent> = {}): Agent {
    return {
      id: faker.string.uuid(),
      name: faker.person.fullName(),
      status: faker.helpers.arrayElement(['ONLINE', 'OFFLINE', 'BUSY', 'ERROR']),
      capabilities: faker.helpers.multiple(() => faker.helpers.arrayElement(['READ', 'WRITE', 'EXECUTE', 'TEST', 'DEPLOY']), { count: 3 }),
      itemsCompleted: faker.number.int({ min: 0, max: 100 }),
      itemsFailed: faker.number.int({ min: 0, max: 10 }),
      successRate: faker.number.float({ min: 0, max: 100, precision: 0.01 }),
      averageTime: faker.number.int({ min: 100, max: 10000 }),
      metadata: {},
      registeredAt: faker.date.past(),
      lastSeenAt: faker.date.recent(),
      ...overrides,
    };
  }

  static generateAgents(count: number): Agent[] {
    return Array.from({ length: count }, () => this.generateAgent());
  }

  static generateAgentsByStatus(status: Agent['status'], count: number = 3): Agent[] {
    return this.generateAgents(count).map(agent => ({ ...agent, status }));
  }

  // ============================================================================
  // USER SEEDS
  // ============================================================================

  static generateUser(overrides: Partial<User> = {}): User {
    return {
      id: faker.string.uuid(),
      email: faker.internet.email(),
      name: faker.person.fullName(),
      role: faker.helpers.arrayElement(['ADMIN', 'MANAGER', 'USER', 'VIEWER']),
      permissions: ['READ', 'WRITE'],
      avatar: faker.image.avatar(),
      metadata: {},
      createdAt: faker.date.past(),
      updatedAt: faker.date.recent(),
      lastLoginAt: faker.date.recent(),
      ...overrides,
    };
  }

  static generateUsers(count: number): User[] {
    return Array.from({ length: count }, () => this.generateUser());
  }

  static generateUsersByRole(role: User['role'], count: number = 3): User[] {
    return this.generateUsers(count).map(user => ({ ...user, role }));
  }

  // ============================================================================
  // PROJECT SEEDS
  // ============================================================================

  static generateProject(overrides: Partial<Project> = {}): Project {
    return {
      id: faker.string.uuid(),
      name: faker.company.name(),
      description: faker.lorem.paragraphs(2),
      status: faker.helpers.arrayElement(['PLANNING', 'ACTIVE', 'COMPLETED', 'ARCHIVED']),
      owner: faker.string.uuid(),
      members: faker.helpers.multiple(() => faker.string.uuid(), { count: { min: 1, max: 10 } }),
      itemCount: faker.number.int({ min: 0, max: 100 }),
      linkCount: faker.number.int({ min: 0, max: 50 }),
      metadata: {},
      createdAt: faker.date.past(),
      updatedAt: faker.date.recent(),
      ...overrides,
    };
  }

  static generateProjects(count: number): Project[] {
    return Array.from({ length: count }, () => this.generateProject());
  }

  // ============================================================================
  // BATCH SEEDS
  // ============================================================================

  static generateCompleteProject(): {
    project: Project;
    users: User[];
    items: Item[];
    links: Link[];
    agents: Agent[];
  } {
    const project = this.generateProject();
    const users = this.generateUsers(5);
    const items = this.generateItems(20, { projectId: project.id });
    const links = Array.from({ length: 10 }, (_, i) => 
      this.generateLink(items[i].id, items[i + 1].id, { projectId: project.id })
    );
    const agents = this.generateAgents(3);

    return { project, users, items, links, agents };
  }

  static generateCompleteProjects(count: number): Array<{
    project: Project;
    users: User[];
    items: Item[];
    links: Link[];
    agents: Agent[];
  }> {
    return Array.from({ length: count }, () => this.generateCompleteProject());
  }

  // ============================================================================
  // REALISTIC SCENARIOS
  // ============================================================================

  static generateBackendProject(): {
    project: Project;
    users: User[];
    items: Item[];
    links: Link[];
  } {
    const project = this.generateProject({ name: 'Backend API Development' });
    const users = this.generateUsers(3);
    
    const items = [
      this.generateItem({ projectId: project.id, type: 'REQUIREMENT', title: 'Design API Schema' }),
      this.generateItem({ projectId: project.id, type: 'IMPLEMENTATION', title: 'Implement REST Endpoints' }),
      this.generateItem({ projectId: project.id, type: 'TEST', title: 'Write API Tests' }),
      this.generateItem({ projectId: project.id, type: 'DEPLOYMENT', title: 'Deploy to Production' }),
    ];

    const links = [
      this.generateLink(items[0].id, items[1].id, { type: 'DEPENDS_ON' }),
      this.generateLink(items[1].id, items[2].id, { type: 'DEPENDS_ON' }),
      this.generateLink(items[2].id, items[3].id, { type: 'DEPENDS_ON' }),
    ];

    return { project, users, items, links };
  }

  static generateFrontendProject(): {
    project: Project;
    users: User[];
    items: Item[];
    links: Link[];
  } {
    const project = this.generateProject({ name: 'Frontend UI Development' });
    const users = this.generateUsers(3);
    
    const items = [
      this.generateItem({ projectId: project.id, type: 'DESIGN', title: 'Design UI Mockups' }),
      this.generateItem({ projectId: project.id, type: 'IMPLEMENTATION', title: 'Implement React Components' }),
      this.generateItem({ projectId: project.id, type: 'TEST', title: 'Write Component Tests' }),
      this.generateItem({ projectId: project.id, type: 'DEPLOYMENT', title: 'Deploy to Vercel' }),
    ];

    const links = [
      this.generateLink(items[0].id, items[1].id, { type: 'DEPENDS_ON' }),
      this.generateLink(items[1].id, items[2].id, { type: 'DEPENDS_ON' }),
      this.generateLink(items[2].id, items[3].id, { type: 'DEPENDS_ON' }),
    ];

    return { project, users, items, links };
  }
}


