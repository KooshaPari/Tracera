// Frontend Database Seeder - Seed Mock Data
// Linked to: All frontend tests

import { FrontendSeedData, Item, Link, Agent, User, Project } from '../seeds/frontend-seeds';

export interface MockDatabase {
  items: Map<string, Item>;
  links: Map<string, Link>;
  agents: Map<string, Agent>;
  users: Map<string, User>;
  projects: Map<string, Project>;
}

export class FrontendDatabaseSeeder {
  constructor(private db: MockDatabase) {}

  // ============================================================================
  // ITEM SEEDING
  // ============================================================================

  async seedItems(count: number = 20, overrides: Partial<Item> = {}): Promise<Item[]> {
    const items = FrontendSeedData.generateItems(count, overrides);
    for (const item of items) {
      this.db.items.set(item.id, item);
    }
    return items;
  }

  async seedItemsByType(type: Item['type'], count: number = 5): Promise<Item[]> {
    const items = FrontendSeedData.generateItemsByType(type, count);
    for (const item of items) {
      this.db.items.set(item.id, item);
    }
    return items;
  }

  async seedItemsByStatus(status: Item['status'], count: number = 5): Promise<Item[]> {
    const items = FrontendSeedData.generateItemsByStatus(status, count);
    for (const item of items) {
      this.db.items.set(item.id, item);
    }
    return items;
  }

  async seedItemsByPriority(priority: Item['priority'], count: number = 5): Promise<Item[]> {
    const items = FrontendSeedData.generateItemsByPriority(priority, count);
    for (const item of items) {
      this.db.items.set(item.id, item);
    }
    return items;
  }

  // ============================================================================
  // LINK SEEDING
  // ============================================================================

  async seedLinks(count: number = 10): Promise<Link[]> {
    const items = Array.from(this.db.items.values());
    const links: Link[] = [];
    
    for (let i = 0; i < count && i < items.length - 1; i++) {
      const link = FrontendSeedData.generateLink(items[i].id, items[i + 1].id);
      this.db.links.set(link.id, link);
      links.push(link);
    }
    
    return links;
  }

  async seedLinksByType(type: Link['type'], count: number = 5): Promise<Link[]> {
    const items = Array.from(this.db.items.values());
    const links: Link[] = [];
    
    for (let i = 0; i < count && i < items.length - 1; i++) {
      const link = FrontendSeedData.generateLinksByType(type, items[i].id, items[i + 1].id, 1)[0];
      this.db.links.set(link.id, link);
      links.push(link);
    }
    
    return links;
  }

  // ============================================================================
  // AGENT SEEDING
  // ============================================================================

  async seedAgents(count: number = 3): Promise<Agent[]> {
    const agents = FrontendSeedData.generateAgents(count);
    for (const agent of agents) {
      this.db.agents.set(agent.id, agent);
    }
    return agents;
  }

  async seedAgentsByStatus(status: Agent['status'], count: number = 3): Promise<Agent[]> {
    const agents = FrontendSeedData.generateAgentsByStatus(status, count);
    for (const agent of agents) {
      this.db.agents.set(agent.id, agent);
    }
    return agents;
  }

  // ============================================================================
  // USER SEEDING
  // ============================================================================

  async seedUsers(count: number = 5): Promise<User[]> {
    const users = FrontendSeedData.generateUsers(count);
    for (const user of users) {
      this.db.users.set(user.id, user);
    }
    return users;
  }

  async seedUsersByRole(role: User['role'], count: number = 3): Promise<User[]> {
    const users = FrontendSeedData.generateUsersByRole(role, count);
    for (const user of users) {
      this.db.users.set(user.id, user);
    }
    return users;
  }

  // ============================================================================
  // PROJECT SEEDING
  // ============================================================================

  async seedProject(overrides: Partial<Project> = {}): Promise<Project> {
    const project = FrontendSeedData.generateProject(overrides);
    this.db.projects.set(project.id, project);
    return project;
  }

  async seedProjects(count: number = 3): Promise<Project[]> {
    const projects = FrontendSeedData.generateProjects(count);
    for (const project of projects) {
      this.db.projects.set(project.id, project);
    }
    return projects;
  }

  // ============================================================================
  // COMPLETE PROJECT SEEDING
  // ============================================================================

  async seedCompleteProject(): Promise<{
    project: Project;
    users: User[];
    items: Item[];
    links: Link[];
    agents: Agent[];
  }> {
    const { project, users, items, links, agents } = FrontendSeedData.generateCompleteProject();
    
    // Seed all data
    this.db.projects.set(project.id, project);
    for (const user of users) this.db.users.set(user.id, user);
    for (const item of items) this.db.items.set(item.id, item);
    for (const link of links) this.db.links.set(link.id, link);
    for (const agent of agents) this.db.agents.set(agent.id, agent);
    
    return { project, users, items, links, agents };
  }

  async seedCompleteProjects(count: number = 3): Promise<Array<{
    project: Project;
    users: User[];
    items: Item[];
    links: Link[];
    agents: Agent[];
  }>> {
    const projects = FrontendSeedData.generateCompleteProjects(count);
    
    for (const { project, users, items, links, agents } of projects) {
      this.db.projects.set(project.id, project);
      for (const user of users) this.db.users.set(user.id, user);
      for (const item of items) this.db.items.set(item.id, item);
      for (const link of links) this.db.links.set(link.id, link);
      for (const agent of agents) this.db.agents.set(agent.id, agent);
    }
    
    return projects;
  }

  // ============================================================================
  // REALISTIC SCENARIOS
  // ============================================================================

  async seedBackendProject(): Promise<{
    project: Project;
    users: User[];
    items: Item[];
    links: Link[];
  }> {
    const { project, users, items, links } = FrontendSeedData.generateBackendProject();
    
    this.db.projects.set(project.id, project);
    for (const user of users) this.db.users.set(user.id, user);
    for (const item of items) this.db.items.set(item.id, item);
    for (const link of links) this.db.links.set(link.id, link);
    
    return { project, users, items, links };
  }

  async seedFrontendProject(): Promise<{
    project: Project;
    users: User[];
    items: Item[];
    links: Link[];
  }> {
    const { project, users, items, links } = FrontendSeedData.generateFrontendProject();
    
    this.db.projects.set(project.id, project);
    for (const user of users) this.db.users.set(user.id, user);
    for (const item of items) this.db.items.set(item.id, item);
    for (const link of links) this.db.links.set(link.id, link);
    
    return { project, users, items, links };
  }

  // ============================================================================
  // UTILITY METHODS
  // ============================================================================

  async clear(): Promise<void> {
    this.db.items.clear();
    this.db.links.clear();
    this.db.agents.clear();
    this.db.users.clear();
    this.db.projects.clear();
  }

  async getStats(): Promise<{
    itemCount: number;
    linkCount: number;
    agentCount: number;
    userCount: number;
    projectCount: number;
  }> {
    return {
      itemCount: this.db.items.size,
      linkCount: this.db.links.size,
      agentCount: this.db.agents.size,
      userCount: this.db.users.size,
      projectCount: this.db.projects.size,
    };
  }

  async getItemsByProject(projectId: string): Promise<Item[]> {
    return Array.from(this.db.items.values()).filter(item => item.projectId === projectId);
  }

  async getLinksByProject(projectId: string): Promise<Link[]> {
    return Array.from(this.db.links.values()).filter(link => link.projectId === projectId);
  }

  async getProjectMembers(projectId: string): Promise<User[]> {
    const project = this.db.projects.get(projectId);
    if (!project) return [];
    
    return Array.from(this.db.users.values()).filter(user => project.members.includes(user.id));
  }

  async getItemAssignees(itemId: string): Promise<User[]> {
    const item = this.db.items.get(itemId);
    if (!item) return [];
    
    return Array.from(this.db.users.values()).filter(user => item.assignees.includes(user.id));
  }
}


