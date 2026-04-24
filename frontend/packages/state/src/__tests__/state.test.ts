import { afterEach, describe, expect, it } from 'vitest';

import type { Agent, Item, Link, Project } from '@tracertm/types';

import { actions, appState$, currentProject$, currentView$, isOnline$ } from '../state';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeProject(overrides: Partial<Project> = {}): Project {
  return {
    id: 'proj-1',
    name: 'Test Project',
    description: 'A test project',
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-01-01T00:00:00Z',
    ...overrides,
  };
}

function makeItem(overrides: Partial<Item> = {}): Item {
  return {
    id: 'item-1',
    projectId: 'proj-1',
    view: 'FEATURE',
    type: 'requirement',
    title: 'Test Item',
    status: 'ACTIVE',
    priority: 'MEDIUM',
    version: 1,
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-01-01T00:00:00Z',
    ...overrides,
  } as Item;
}

function makeLink(overrides: Partial<Link> = {}): Link {
  return {
    id: 'link-1',
    projectId: 'proj-1',
    sourceId: 'item-1',
    targetId: 'item-2',
    type: 'TRACES_TO',
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-01-01T00:00:00Z',
    version: 1,
    ...overrides,
  } as Link;
}

function makeAgent(overrides: Partial<Agent> = {}): Agent {
  return {
    id: 'agent-1',
    name: 'Test Agent',
    type: 'analyzer',
    status: 'active',
    lastSeen: '2025-01-01T00:00:00Z',
    ...overrides,
  };
}

/** Reset the entire observable tree back to its initial defaults. */
function resetState(): void {
  appState$.set({
    currentProject: null,
    items: {},
    links: [],
    agents: [],
    ui: {
      currentView: 'FEATURE',
      isDarkMode: false,
      searchQuery: '',
      selectedItemId: null,
      sidebarOpen: true,
    },
    sync: {
      isOnline: true,
      lastSyncedAt: null,
      pendingMutations: 0,
    },
  });
}

// Reset after every test so tests are fully isolated.
afterEach(() => {
  resetState();
});

// ---------------------------------------------------------------------------
// 1. Initial state
// ---------------------------------------------------------------------------

describe('appState$ initial state', () => {
  it('has null currentProject', () => {
    expect(appState$.currentProject.get()).toBeNull();
  });

  it('has empty items record', () => {
    expect(appState$.items.get()).toEqual({});
  });

  it('has empty links array', () => {
    expect(appState$.links.get()).toEqual([]);
  });

  it('has empty agents array', () => {
    expect(appState$.agents.get()).toEqual([]);
  });

  it('has correct default UI state', () => {
    const ui = appState$.ui.get();
    expect(ui.currentView).toBe('FEATURE');
    expect(ui.isDarkMode).toBeFalsy();
    expect(ui.searchQuery).toBe('');
    expect(ui.selectedItemId).toBeNull();
    expect(ui.sidebarOpen).toBeTruthy();
  });

  it('has correct default sync state', () => {
    const sync = appState$.sync.get();
    expect(sync.isOnline).toBeTruthy();
    expect(sync.lastSyncedAt).toBeNull();
    expect(sync.pendingMutations).toBe(0);
  });
});

// ---------------------------------------------------------------------------
// 2. Selectors
// ---------------------------------------------------------------------------

describe('selectors', () => {
  it('currentProject$ reflects appState$.currentProject', () => {
    expect(currentProject$.get()).toBeNull();
    const project = makeProject();
    appState$.currentProject.set(project);
    expect(currentProject$.get()).toEqual(project);
  });

  it('currentView$ reflects appState$.ui.currentView', () => {
    expect(currentView$.get()).toBe('FEATURE');
    appState$.ui.currentView.set('CODE');
    expect(currentView$.get()).toBe('CODE');
  });

  it('isOnline$ reflects appState$.sync.isOnline', () => {
    expect(isOnline$.get()).toBeTruthy();
    appState$.sync.isOnline.set(false);
    expect(isOnline$.get()).toBeFalsy();
  });

  it('selectors update when actions mutate state', () => {
    actions.setProject(makeProject({ id: 'sel-proj' }));
    expect(currentProject$.get()?.id).toBe('sel-proj');

    actions.setView('DATABASE');
    expect(currentView$.get()).toBe('DATABASE');

    actions.setOnline(false);
    expect(isOnline$.get()).toBeFalsy();
  });
});

// ---------------------------------------------------------------------------
// 3. actions.selectItem
// ---------------------------------------------------------------------------

describe('actions.selectItem', () => {
  it('sets selectedItemId to a string', () => {
    actions.selectItem('item-42');
    expect(appState$.ui.selectedItemId.get()).toBe('item-42');
  });

  it('clears selectedItemId when passed null', () => {
    actions.selectItem('item-42');
    actions.selectItem(null);
    expect(appState$.ui.selectedItemId.get()).toBeNull();
  });

  it('overwrites a previous selection', () => {
    actions.selectItem('item-1');
    actions.selectItem('item-2');
    expect(appState$.ui.selectedItemId.get()).toBe('item-2');
  });
});

// ---------------------------------------------------------------------------
// 4. actions.setOnline
// ---------------------------------------------------------------------------

describe('actions.setOnline', () => {
  it('sets online to false', () => {
    actions.setOnline(false);
    expect(appState$.sync.isOnline.get()).toBeFalsy();
  });

  it('sets online back to true', () => {
    actions.setOnline(false);
    actions.setOnline(true);
    expect(appState$.sync.isOnline.get()).toBeTruthy();
  });

  it('is idempotent when setting the same value', () => {
    actions.setOnline(true);
    expect(appState$.sync.isOnline.get()).toBeTruthy();
  });
});

// ---------------------------------------------------------------------------
// 5. actions.setProject
// ---------------------------------------------------------------------------

describe('actions.setProject', () => {
  it('sets the current project', () => {
    const project = makeProject();
    actions.setProject(project);
    expect(appState$.currentProject.get()).toEqual(project);
  });

  it('replaces a previous project', () => {
    actions.setProject(makeProject({ id: 'proj-a' }));
    actions.setProject(makeProject({ id: 'proj-b', name: 'Second' }));
    expect(appState$.currentProject.get()?.id).toBe('proj-b');
    expect(appState$.currentProject.get()?.name).toBe('Second');
  });

  it('preserves project metadata', () => {
    const project = makeProject({ metadata: { key: 'value', nested: { a: 1 } } });
    actions.setProject(project);
    expect(appState$.currentProject.get()?.metadata).toEqual({ key: 'value', nested: { a: 1 } });
  });
});

// ---------------------------------------------------------------------------
// 6. actions.setView
// ---------------------------------------------------------------------------

describe('actions.setView', () => {
  it('changes the current view', () => {
    actions.setView('CODE');
    expect(appState$.ui.currentView.get()).toBe('CODE');
  });

  it('accepts arbitrary view strings', () => {
    actions.setView('CUSTOM_VIEW');
    expect(appState$.ui.currentView.get()).toBe('CUSTOM_VIEW');
  });

  it('can set view to empty string', () => {
    actions.setView('');
    expect(appState$.ui.currentView.get()).toBe('');
  });
});

// ---------------------------------------------------------------------------
// 7. actions.toggleDarkMode
// ---------------------------------------------------------------------------

describe('actions.toggleDarkMode', () => {
  it('toggles from false to true', () => {
    expect(appState$.ui.isDarkMode.get()).toBeFalsy();
    actions.toggleDarkMode();
    expect(appState$.ui.isDarkMode.get()).toBeTruthy();
  });

  it('toggles from true back to false', () => {
    actions.toggleDarkMode();
    actions.toggleDarkMode();
    expect(appState$.ui.isDarkMode.get()).toBeFalsy();
  });

  it('round-trips correctly over multiple toggles', () => {
    for (let i = 0; i < 5; i++) {
      actions.toggleDarkMode();
    }
    // 5 toggles from false => true
    expect(appState$.ui.isDarkMode.get()).toBeTruthy();
  });
});

// ---------------------------------------------------------------------------
// 8. actions.toggleSidebar
// ---------------------------------------------------------------------------

describe('actions.toggleSidebar', () => {
  it('toggles from true (default) to false', () => {
    expect(appState$.ui.sidebarOpen.get()).toBeTruthy();
    actions.toggleSidebar();
    expect(appState$.ui.sidebarOpen.get()).toBeFalsy();
  });

  it('toggles back to true', () => {
    actions.toggleSidebar();
    actions.toggleSidebar();
    expect(appState$.ui.sidebarOpen.get()).toBeTruthy();
  });
});

// ---------------------------------------------------------------------------
// 9. Direct observable mutations (items, links, agents, sync)
// ---------------------------------------------------------------------------

describe('direct observable mutations', () => {
  it('can set items for a specific view', () => {
    const items = [makeItem({ id: 'i1' }), makeItem({ id: 'i2' })];
    appState$.items.set({ FEATURE: items });
    expect(appState$.items.get()).toEqual({ FEATURE: items });
  });

  it('can add items for multiple views', () => {
    appState$.items.set({
      FEATURE: [makeItem({ id: 'f1', view: 'FEATURE' })],
      CODE: [makeItem({ id: 'c1', view: 'CODE' })],
    });
    const all = appState$.items.get();
    expect(Object.keys(all)).toHaveLength(2);
    expect(all['FEATURE']).toHaveLength(1);
    expect(all['CODE']).toHaveLength(1);
  });

  it('can set links array', () => {
    const links = [makeLink({ id: 'l1' }), makeLink({ id: 'l2' })];
    appState$.links.set(links);
    expect(appState$.links.get()).toHaveLength(2);
    expect(appState$.links.get()[0].id).toBe('l1');
  });

  it('can set agents array', () => {
    const agents = [makeAgent({ id: 'a1' }), makeAgent({ id: 'a2', status: 'idle' })];
    appState$.agents.set(agents);
    expect(appState$.agents.get()).toHaveLength(2);
    expect(appState$.agents.get()[1].status).toBe('idle');
  });

  it('can update lastSyncedAt', () => {
    const ts = '2025-06-15T12:00:00Z';
    appState$.sync.lastSyncedAt.set(ts);
    expect(appState$.sync.lastSyncedAt.get()).toBe(ts);
  });

  it('can increment pendingMutations', () => {
    appState$.sync.pendingMutations.set(3);
    expect(appState$.sync.pendingMutations.get()).toBe(3);
  });

  it('can update searchQuery', () => {
    appState$.ui.searchQuery.set('hello world');
    expect(appState$.ui.searchQuery.get()).toBe('hello world');
  });
});

// ---------------------------------------------------------------------------
// 10. Edge cases and boundary conditions
// ---------------------------------------------------------------------------

describe('edge cases', () => {
  it('handles setting empty items record', () => {
    appState$.items.set({ FEATURE: [makeItem()] });
    appState$.items.set({});
    expect(appState$.items.get()).toEqual({});
  });

  it('handles setting empty links array', () => {
    appState$.links.set([makeLink()]);
    appState$.links.set([]);
    expect(appState$.links.get()).toEqual([]);
  });

  it('handles setting empty agents array', () => {
    appState$.agents.set([makeAgent()]);
    appState$.agents.set([]);
    expect(appState$.agents.get()).toEqual([]);
  });

  it('handles rapid sequential action calls', () => {
    for (let i = 0; i < 100; i++) {
      actions.selectItem(`item-${i}`);
    }
    expect(appState$.ui.selectedItemId.get()).toBe('item-99');
  });

  it('handles setting project after clearing', () => {
    const project = makeProject();
    actions.setProject(project);
    appState$.currentProject.set(null);
    expect(appState$.currentProject.get()).toBeNull();
    actions.setProject(makeProject({ id: 'proj-new' }));
    expect(appState$.currentProject.get()?.id).toBe('proj-new');
  });

  it('multiple toggleDarkMode calls converge to expected value', () => {
    // Even number of toggles -> back to false
    actions.toggleDarkMode();
    actions.toggleDarkMode();
    actions.toggleDarkMode();
    actions.toggleDarkMode();
    expect(appState$.ui.isDarkMode.get()).toBeFalsy();
  });

  it('multiple toggleSidebar calls converge to expected value', () => {
    // Default is true; odd toggles -> false
    actions.toggleSidebar();
    actions.toggleSidebar();
    actions.toggleSidebar();
    expect(appState$.ui.sidebarOpen.get()).toBeFalsy();
  });

  it('does not cross-contaminate UI and sync state', () => {
    actions.setOnline(false);
    actions.toggleDarkMode();
    expect(appState$.sync.isOnline.get()).toBeFalsy();
    expect(appState$.ui.isDarkMode.get()).toBeTruthy();
    // Other UI fields remain unchanged
    expect(appState$.ui.sidebarOpen.get()).toBeTruthy();
    expect(appState$.ui.currentView.get()).toBe('FEATURE');
  });

  it('full state set overwrites all fields atomically', () => {
    actions.setProject(makeProject());
    actions.setView('CODE');
    actions.selectItem('item-xyz');
    appState$.sync.pendingMutations.set(5);

    resetState();

    expect(appState$.currentProject.get()).toBeNull();
    expect(appState$.ui.currentView.get()).toBe('FEATURE');
    expect(appState$.ui.selectedItemId.get()).toBeNull();
    expect(appState$.sync.pendingMutations.get()).toBe(0);
  });
});

// ---------------------------------------------------------------------------
// 11. Composite / integration-style scenarios
// ---------------------------------------------------------------------------

describe('composite state scenarios', () => {
  it('simulates a complete user session flow', () => {
    // User logs in and a project is selected
    const project = makeProject({ id: 'session-proj', name: 'Session Project' });
    actions.setProject(project);
    expect(currentProject$.get()?.name).toBe('Session Project');

    // User navigates to code view
    actions.setView('CODE');
    expect(currentView$.get()).toBe('CODE');

    // Items loaded for that view
    const items = [
      makeItem({ id: 'code-1', view: 'CODE', title: 'Module A' }),
      makeItem({ id: 'code-2', view: 'CODE', title: 'Module B' }),
    ];
    appState$.items.set({ CODE: items });

    // User selects an item
    actions.selectItem('code-1');
    expect(appState$.ui.selectedItemId.get()).toBe('code-1');

    // User toggles dark mode
    actions.toggleDarkMode();
    expect(appState$.ui.isDarkMode.get()).toBeTruthy();

    // User goes offline
    actions.setOnline(false);
    expect(isOnline$.get()).toBeFalsy();
    appState$.sync.pendingMutations.set(2);

    // User comes back online and mutations are synced
    actions.setOnline(true);
    appState$.sync.pendingMutations.set(0);
    appState$.sync.lastSyncedAt.set('2025-06-15T13:00:00Z');

    expect(isOnline$.get()).toBeTruthy();
    expect(appState$.sync.pendingMutations.get()).toBe(0);
    expect(appState$.sync.lastSyncedAt.get()).toBe('2025-06-15T13:00:00Z');
  });

  it('simulates agents being added and removed', () => {
    const agent1 = makeAgent({ id: 'a1', name: 'Analyzer', status: 'active' });
    const agent2 = makeAgent({ id: 'a2', name: 'Linker', status: 'idle' });
    appState$.agents.set([agent1, agent2]);
    expect(appState$.agents.get()).toHaveLength(2);

    // Remove one agent
    appState$.agents.set([agent1]);
    expect(appState$.agents.get()).toHaveLength(1);
    expect(appState$.agents.get()[0].name).toBe('Analyzer');
  });

  it('simulates links being established between items', () => {
    const link1 = makeLink({ id: 'lnk-1', sourceId: 'item-a', targetId: 'item-b' });
    const link2 = makeLink({ id: 'lnk-2', sourceId: 'item-b', targetId: 'item-c' });
    appState$.links.set([link1, link2]);

    expect(appState$.links.get()).toHaveLength(2);
    expect(appState$.links.get()[0].sourceId).toBe('item-a');
    expect(appState$.links.get()[1].targetId).toBe('item-c');
  });
});
