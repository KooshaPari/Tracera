# Mock Data Seeding - Finalized Shapes (COMPREHENSIVE)

**Date**: 2025-11-22  
**Version**: 1.0 (MOCK DATA SEEDING)  
**Status**: APPROVED

---

## 🌱 **MOCK DATA SEEDING STRATEGY**

### Purpose
Provide consistent, realistic mock data for all test variations (Mock-Mock, Mock-Live, Live-Mock, Live-Live)

### Benefits
- ✅ Consistent test data across all tests
- ✅ Realistic data shapes matching production
- ✅ Easy to seed and reset between tests
- ✅ Supports all test variations
- ✅ Enables deterministic testing
- ✅ Reduces test flakiness

---

## 📊 **DATA SHAPES (FINALIZED)**

### Item Shape
```typescript
interface Item {
  id: string;                    // UUID v4
  projectId: string;             // UUID v4
  title: string;                 // 1-255 chars
  type: ItemType;                // REQUIREMENT | DESIGN | IMPLEMENTATION | TEST | DEPLOYMENT | DOCUMENTATION | RESEARCH | SPIKE
  description: string;           // 0-5000 chars, markdown
  status: ItemStatus;            // DRAFT | ACTIVE | IN_PROGRESS | COMPLETED | ARCHIVED
  priority: Priority;            // LOW | MEDIUM | HIGH | CRITICAL
  tags: string[];                // 0-20 tags
  assignees: string[];           // User IDs
  estimatedEffort?: number;      // Story points (1-13)
  actualEffort?: number;         // Story points
  dueDate?: Date;                // ISO 8601
  completedDate?: Date;          // ISO 8601
  metadata: Record<string, any>; // Custom metadata
  createdBy: string;             // User ID
  createdAt: Date;               // ISO 8601
  updatedBy: string;             // User ID
  updatedAt: Date;               // ISO 8601
  deletedAt?: Date;              // Soft delete
}
```

### Link Shape
```typescript
interface Link {
  id: string;                    // UUID v4
  projectId: string;             // UUID v4
  type: LinkType;                // DEPENDS_ON | BLOCKS | RELATES_TO | DUPLICATES | PARENT_OF | CHILD_OF
  sourceId: string;              // Item ID
  targetId: string;              // Item ID
  description: string;           // 0-1000 chars
  metadata: Record<string, any>; // Custom metadata
  createdBy: string;             // User ID
  createdAt: Date;               // ISO 8601
  updatedBy: string;             // User ID
  updatedAt: Date;               // ISO 8601
}
```

### Agent Shape
```typescript
interface Agent {
  id: string;                    // UUID v4
  name: string;                  // 1-255 chars
  status: AgentStatus;           // ONLINE | OFFLINE | BUSY | ERROR
  capabilities: string[];        // READ | WRITE | EXECUTE | TEST | DEPLOY
  currentItemId?: string;        // Item ID
  itemsCompleted: number;        // Count
  itemsFailed: number;           // Count
  successRate: number;           // 0-100%
  averageTime: number;           // Milliseconds
  metadata: Record<string, any>; // Custom metadata
  registeredAt: Date;            // ISO 8601
  lastSeenAt: Date;              // ISO 8601
}
```

### User Shape
```typescript
interface User {
  id: string;                    // UUID v4
  email: string;                 // Valid email
  name: string;                  // 1-255 chars
  role: UserRole;                // ADMIN | MANAGER | USER | VIEWER
  permissions: string[];         // Fine-grained permissions
  avatar?: string;               // URL
  metadata: Record<string, any>; // Custom metadata
  createdAt: Date;               // ISO 8601
  updatedAt: Date;               // ISO 8601
  lastLoginAt?: Date;            // ISO 8601
}
```

### Project Shape
```typescript
interface Project {
  id: string;                    // UUID v4
  name: string;                  // 1-255 chars
  description: string;           // 0-5000 chars
  status: ProjectStatus;         // PLANNING | ACTIVE | COMPLETED | ARCHIVED
  owner: string;                 // User ID
  members: string[];             // User IDs
  itemCount: number;             // Count
  linkCount: number;             // Count
  metadata: Record<string, any>; // Custom metadata
  createdAt: Date;               // ISO 8601
  updatedAt: Date;               // ISO 8601
}
```

---

## 🌱 **SEED DATA GENERATORS**

### Frontend Seed Data (TypeScript)

```typescript
// tests/seeds/frontend-seeds.ts

import { faker } from '@faker-js/faker';

export class FrontendSeedData {
  // ============================================================================
  // ITEM SEEDS
  // ============================================================================

  static generateItem(overrides: Partial<Item> = {}): Item {
    return {
      id: faker.string.uuid(),
      projectId: faker.string.uuid(),
      title: faker.lorem.sentence(),
      type: faker.helpers.arrayElement(['REQUIREMENT', 'DESIGN', 'IMPLEMENTATION', 'TEST']),
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
      createdAt: faker.date.past(),
      updatedBy: faker.string.uuid(),
      updatedAt: faker.date.recent(),
      ...overrides,
    };
  }

  static generateItems(count: number, overrides: Partial<Item> = {}): Item[] {
    return Array.from({ length: count }, () => this.generateItem(overrides));
  }

  // ============================================================================
  // LINK SEEDS
  // ============================================================================

  static generateLink(sourceId: string, targetId: string, overrides: Partial<Link> = {}): Link {
    return {
      id: faker.string.uuid(),
      projectId: faker.string.uuid(),
      type: faker.helpers.arrayElement(['DEPENDS_ON', 'BLOCKS', 'RELATES_TO']),
      sourceId,
      targetId,
      description: faker.lorem.sentence(),
      metadata: {},
      createdBy: faker.string.uuid(),
      createdAt: faker.date.past(),
      updatedBy: faker.string.uuid(),
      updatedAt: faker.date.recent(),
      ...overrides,
    };
  }

  static generateLinks(count: number, sourceId: string, targetId: string): Link[] {
    return Array.from({ length: count }, () => this.generateLink(sourceId, targetId));
  }

  // ============================================================================
  // AGENT SEEDS
  // ============================================================================

  static generateAgent(overrides: Partial<Agent> = {}): Agent {
    return {
      id: faker.string.uuid(),
      name: faker.person.fullName(),
      status: faker.helpers.arrayElement(['ONLINE', 'OFFLINE', 'BUSY']),
      capabilities: faker.helpers.multiple(() => faker.helpers.arrayElement(['READ', 'WRITE', 'EXECUTE']), { count: 3 }),
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

  // ============================================================================
  // PROJECT SEEDS
  // ============================================================================

  static generateProject(overrides: Partial<Project> = {}): Project {
    return {
      id: faker.string.uuid(),
      name: faker.company.name(),
      description: faker.lorem.paragraphs(2),
      status: faker.helpers.arrayElement(['PLANNING', 'ACTIVE', 'COMPLETED']),
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
}
```

### Backend Seed Data (Go)

```go
// tests/seeds/backend_seeds.go

package seeds

import (
	"github.com/brianvoe/gofakeit/v6"
	"time"
)

type BackendSeedData struct{}

// ============================================================================
// ITEM SEEDS
// ============================================================================

func (s *BackendSeedData) GenerateItem(overrides map[string]interface{}) *Item {
	item := &Item{
		ID:        gofakeit.UUID(),
		ProjectID: gofakeit.UUID(),
		Title:     gofakeit.Sentence(5),
		Type:      "REQUIREMENT",
		Description: gofakeit.Paragraph(2, 5, 10, " "),
		Status:    "DRAFT",
		Priority:  "MEDIUM",
		Tags:      []string{},
		Assignees: []string{},
		CreatedBy: gofakeit.UUID(),
		CreatedAt: time.Now().Add(-time.Hour * 24),
		UpdatedBy: gofakeit.UUID(),
		UpdatedAt: time.Now(),
	}

	// Apply overrides
	if title, ok := overrides["title"].(string); ok {
		item.Title = title
	}
	if itemType, ok := overrides["type"].(string); ok {
		item.Type = itemType
	}

	return item
}

func (s *BackendSeedData) GenerateItems(count int, overrides map[string]interface{}) []*Item {
	items := make([]*Item, count)
	for i := 0; i < count; i++ {
		items[i] = s.GenerateItem(overrides)
	}
	return items
}

// ============================================================================
// LINK SEEDS
// ============================================================================

func (s *BackendSeedData) GenerateLink(sourceID, targetID string, overrides map[string]interface{}) *Link {
	link := &Link{
		ID:        gofakeit.UUID(),
		ProjectID: gofakeit.UUID(),
		Type:      "DEPENDS_ON",
		SourceID:  sourceID,
		TargetID:  targetID,
		Description: gofakeit.Sentence(5),
		CreatedBy: gofakeit.UUID(),
		CreatedAt: time.Now().Add(-time.Hour * 24),
		UpdatedBy: gofakeit.UUID(),
		UpdatedAt: time.Now(),
	}

	// Apply overrides
	if linkType, ok := overrides["type"].(string); ok {
		link.Type = linkType
	}

	return link
}

func (s *BackendSeedData) GenerateLinks(count int, sourceID, targetID string) []*Link {
	links := make([]*Link, count)
	for i := 0; i < count; i++ {
		links[i] = s.GenerateLink(sourceID, targetID, map[string]interface{}{})
	}
	return links
}

// ============================================================================
// AGENT SEEDS
// ============================================================================

func (s *BackendSeedData) GenerateAgent(overrides map[string]interface{}) *Agent {
	agent := &Agent{
		ID:             gofakeit.UUID(),
		Name:           gofakeit.Name(),
		Status:         "ONLINE",
		Capabilities:   []string{"READ", "WRITE", "EXECUTE"},
		ItemsCompleted: gofakeit.Number(0, 100),
		ItemsFailed:    gofakeit.Number(0, 10),
		SuccessRate:    float64(gofakeit.Number(80, 100)),
		AverageTime:    int64(gofakeit.Number(100, 10000)),
		RegisteredAt:   time.Now().Add(-time.Hour * 24 * 30),
		LastSeenAt:     time.Now(),
	}

	// Apply overrides
	if name, ok := overrides["name"].(string); ok {
		agent.Name = name
	}

	return agent
}

func (s *BackendSeedData) GenerateAgents(count int) []*Agent {
	agents := make([]*Agent, count)
	for i := 0; i < count; i++ {
		agents[i] = s.GenerateAgent(map[string]interface{}{})
	}
	return agents
}

// ============================================================================
// USER SEEDS
// ============================================================================

func (s *BackendSeedData) GenerateUser(overrides map[string]interface{}) *User {
	user := &User{
		ID:    gofakeit.UUID(),
		Email: gofakeit.Email(),
		Name:  gofakeit.Name(),
		Role:  "USER",
		Permissions: []string{"READ", "WRITE"},
		CreatedAt: time.Now().Add(-time.Hour * 24 * 30),
		UpdatedAt: time.Now(),
	}

	// Apply overrides
	if email, ok := overrides["email"].(string); ok {
		user.Email = email
	}

	return user
}

func (s *BackendSeedData) GenerateUsers(count int) []*User {
	users := make([]*User, count)
	for i := 0; i < count; i++ {
		users[i] = s.GenerateUser(map[string]interface{}{})
	}
	return users
}

// ============================================================================
// PROJECT SEEDS
// ============================================================================

func (s *BackendSeedData) GenerateProject(overrides map[string]interface{}) *Project {
	project := &Project{
		ID:        gofakeit.UUID(),
		Name:      gofakeit.Company(),
		Description: gofakeit.Paragraph(2, 5, 10, " "),
		Status:    "ACTIVE",
		Owner:     gofakeit.UUID(),
		Members:   []string{},
		ItemCount: gofakeit.Number(0, 100),
		LinkCount: gofakeit.Number(0, 50),
		CreatedAt: time.Now().Add(-time.Hour * 24 * 30),
		UpdatedAt: time.Now(),
	}

	// Apply overrides
	if name, ok := overrides["name"].(string); ok {
		project.Name = name
	}

	return project
}

func (s *BackendSeedData) GenerateProjects(count int) []*Project {
	projects := make([]*Project, count)
	for i := 0; i < count; i++ {
		projects[i] = s.GenerateProject(map[string]interface{}{})
	}
	return projects
}

// ============================================================================
// BATCH SEEDS
// ============================================================================

func (s *BackendSeedData) GenerateCompleteProject() map[string]interface{} {
	project := s.GenerateProject(map[string]interface{}{})
	users := s.GenerateUsers(5)
	items := s.GenerateItems(20, map[string]interface{}{"projectId": project.ID})
	
	links := make([]*Link, 10)
	for i := 0; i < 10; i++ {
		links[i] = s.GenerateLink(items[i].ID, items[i+1].ID, map[string]interface{}{})
	}
	
	agents := s.GenerateAgents(3)

	return map[string]interface{}{
		"project": project,
		"users":   users,
		"items":   items,
		"links":   links,
		"agents":  agents,
	}
}
```

---

## 🗄️ **DATABASE SEEDING**

### Frontend Database Seeding

```typescript
// tests/setup/frontend-db-seed.ts

import { FrontendSeedData } from '../seeds/frontend-seeds';

export class FrontendDatabaseSeeder {
  constructor(private db: MockDatabase) {}

  async seedItems(count: number = 20): Promise<Item[]> {
    const items = FrontendSeedData.generateItems(count);
    for (const item of items) {
      this.db.items.set(item.id, item);
    }
    return items;
  }

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

  async seedAgents(count: number = 3): Promise<Agent[]> {
    const agents = FrontendSeedData.generateAgents(count);
    for (const agent of agents) {
      this.db.agents.set(agent.id, agent);
    }
    return agents;
  }

  async seedUsers(count: number = 5): Promise<User[]> {
    const users = FrontendSeedData.generateUsers(count);
    for (const user of users) {
      this.db.users.set(user.id, user);
    }
    return users;
  }

  async seedProject(): Promise<{
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

  async clear(): Promise<void> {
    this.db.items.clear();
    this.db.links.clear();
    this.db.agents.clear();
    this.db.users.clear();
    this.db.projects.clear();
  }
}
```

### Backend Database Seeding

```go
// tests/setup/backend_db_seed.go

package setup

import (
	"testing"
	"github.com/stretchr/testify/require"
)

type BackendDatabaseSeeder struct {
	db *TestDatabase
	t  *testing.T
}

func NewBackendDatabaseSeeder(db *TestDatabase, t *testing.T) *BackendDatabaseSeeder {
	return &BackendDatabaseSeeder{db: db, t: t}
}

func (s *BackendDatabaseSeeder) SeedItems(count int) []*Item {
	seeder := &BackendSeedData{}
	items := seeder.GenerateItems(count, map[string]interface{}{})
	
	for _, item := range items {
		err := s.db.InsertItem(item)
		require.NoError(s.t, err)
	}
	
	return items
}

func (s *BackendDatabaseSeeder) SeedLinks(count int, sourceID, targetID string) []*Link {
	seeder := &BackendSeedData{}
	links := seeder.GenerateLinks(count, sourceID, targetID)
	
	for _, link := range links {
		err := s.db.InsertLink(link)
		require.NoError(s.t, err)
	}
	
	return links
}

func (s *BackendDatabaseSeeder) SeedAgents(count int) []*Agent {
	seeder := &BackendSeedData{}
	agents := seeder.GenerateAgents(count)
	
	for _, agent := range agents {
		err := s.db.InsertAgent(agent)
		require.NoError(s.t, err)
	}
	
	return agents
}

func (s *BackendDatabaseSeeder) SeedUsers(count int) []*User {
	seeder := &BackendSeedData{}
	users := seeder.GenerateUsers(count)
	
	for _, user := range users {
		err := s.db.InsertUser(user)
		require.NoError(s.t, err)
	}
	
	return users
}

func (s *BackendDatabaseSeeder) SeedCompleteProject() map[string]interface{} {
	seeder := &BackendSeedData{}
	data := seeder.GenerateCompleteProject()
	
	project := data["project"].(*Project)
	users := data["users"].([]*User)
	items := data["items"].([]*Item)
	links := data["links"].([]*Link)
	agents := data["agents"].([]*Agent)
	
	// Seed all data
	err := s.db.InsertProject(project)
	require.NoError(s.t, err)
	
	for _, user := range users {
		err := s.db.InsertUser(user)
		require.NoError(s.t, err)
	}
	
	for _, item := range items {
		err := s.db.InsertItem(item)
		require.NoError(s.t, err)
	}
	
	for _, link := range links {
		err := s.db.InsertLink(link)
		require.NoError(s.t, err)
	}
	
	for _, agent := range agents {
		err := s.db.InsertAgent(agent)
		require.NoError(s.t, err)
	}
	
	return data
}

func (s *BackendDatabaseSeeder) Clear() error {
	return s.db.Clear()
}
```

---

## 🧪 **USING SEEDED DATA IN TESTS**

### Frontend Unit Test Example

```typescript
// tests/frontend/features/FR-1.1-CreateItem.mock-live.test.tsx

describe('FR-1.1: Create Item - Mock API, Real Database', () => {
  let seeder: FrontendDatabaseSeeder;
  let db: MockDatabase;

  beforeEach(async () => {
    db = new MockDatabase();
    seeder = new FrontendDatabaseSeeder(db);
    
    // Seed initial data
    await seeder.seedItems(10);
    await seeder.seedUsers(5);
  });

  afterEach(async () => {
    await seeder.clear();
  });

  test('should create item and link to existing items', async () => {
    // Get seeded items
    const existingItems = Array.from(db.items.values());
    
    // Create new item
    const newItem = FrontendSeedData.generateItem({
      projectId: existingItems[0].projectId,
    });
    
    // Verify it can be linked
    const link = FrontendSeedData.generateLink(existingItems[0].id, newItem.id);
    
    expect(link.sourceId).toBe(existingItems[0].id);
    expect(link.targetId).toBe(newItem.id);
  });
});
```

### Backend Integration Test Example

```go
// tests/backend/api/FR-1.1-CreateItem.live-mock.test.go

func TestCreateItem_WithSeededData(t *testing.T) {
  db := setupTestDatabase(t)
  defer db.Close()
  
  seeder := NewBackendDatabaseSeeder(db, t)
  
  // Seed initial data
  items := seeder.SeedItems(10)
  users := seeder.SeedUsers(5)
  
  // Create service
  service := NewItemService(db)
  
  // Create new item
  newItem := &Item{
    Title:     "New Item",
    Type:      "REQUIREMENT",
    ProjectID: items[0].ProjectID,
    CreatedBy: users[0].ID,
  }
  
  result, err := service.Create(newItem)
  
  assert.NoError(t, err)
  assert.NotEmpty(t, result.ID)
  assert.Equal(t, "New Item", result.Title)
}
```

---

## 📊 **SEED DATA STATISTICS**

### Data Volume
- **Items**: 20+ per project
- **Links**: 10+ per project
- **Agents**: 3+ per project
- **Users**: 5+ per project
- **Projects**: 1+ per test suite

### Data Variety
- **Item Types**: 8 types
- **Item Statuses**: 4 statuses
- **Priorities**: 4 priorities
- **Link Types**: 6 types
- **User Roles**: 4 roles
- **Agent Statuses**: 4 statuses

### Data Realism
- ✅ Realistic names (faker.js / gofakeit)
- ✅ Realistic emails
- ✅ Realistic descriptions
- ✅ Realistic timestamps
- ✅ Realistic relationships
- ✅ Realistic counts

---

## 🎯 **SEEDING STRATEGIES**

### Strategy 1: Minimal Seeding
```typescript
// Seed only what's needed for the test
beforeEach(async () => {
  await seeder.seedItems(1);
  await seeder.seedUsers(1);
});
```

### Strategy 2: Standard Seeding
```typescript
// Seed typical project data
beforeEach(async () => {
  await seeder.seedProject();
});
```

### Strategy 3: Comprehensive Seeding
```typescript
// Seed all data types
beforeEach(async () => {
  await seeder.seedItems(50);
  await seeder.seedLinks(25);
  await seeder.seedAgents(10);
  await seeder.seedUsers(20);
});
```

---

## ✅ **BENEFITS OF MOCK DATA SEEDING**

✅ **Consistency**: Same data across all tests  
✅ **Realism**: Data matches production shapes  
✅ **Determinism**: Predictable test results  
✅ **Isolation**: Each test starts fresh  
✅ **Speed**: No need to create data in each test  
✅ **Maintainability**: Easy to update seed data  
✅ **Scalability**: Easy to seed large datasets  
✅ **Flexibility**: Easy to customize per test  


