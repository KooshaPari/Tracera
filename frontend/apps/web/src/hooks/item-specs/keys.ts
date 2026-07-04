import type {
  DefectSeverity,
  DefectStatus,
  EpicStatus,
  TaskStatus,
  TestType,
  UserStoryStatus,
} from './types';

const itemSpecKeys = {
  all: ['item-specs'] as const,
  requirements: (projectId: string) => [...itemSpecKeys.all, 'requirements', projectId] as const,
  requirement: (projectId: string, specId: string) =>
    [...itemSpecKeys.requirements(projectId), specId] as const,
  requirementByItem: (projectId: string, itemId: string) =>
    [...itemSpecKeys.requirements(projectId), 'by-item', itemId] as const,
  unverifiedRequirements: (projectId: string) =>
    [...itemSpecKeys.requirements(projectId), 'unverified'] as const,
  highRiskRequirements: (projectId: string) =>
    [...itemSpecKeys.requirements(projectId), 'high-risk'] as const,

  // Test specs
  tests: (projectId: string) => [...itemSpecKeys.all, 'tests', projectId] as const,
  test: (projectId: string, specId: string) => [...itemSpecKeys.tests(projectId), specId] as const,
  testByItem: (projectId: string, itemId: string) =>
    [...itemSpecKeys.tests(projectId), 'by-item', itemId] as const,
  flakyTests: (projectId: string) => [...itemSpecKeys.tests(projectId), 'flaky'] as const,
  testsByType: (projectId: string, type: TestType) =>
    [...itemSpecKeys.tests(projectId), 'by-type', type] as const,
  testHealthReport: (projectId: string) =>
    [...itemSpecKeys.tests(projectId), 'health-report'] as const,
  quarantinedTests: (projectId: string) =>
    [...itemSpecKeys.tests(projectId), 'quarantined'] as const,

  // Epic specs
  epics: (projectId: string) => [...itemSpecKeys.all, 'epics', projectId] as const,
  epic: (projectId: string, specId: string) => [...itemSpecKeys.epics(projectId), specId] as const,
  epicByItem: (projectId: string, itemId: string) =>
    [...itemSpecKeys.epics(projectId), 'by-item', itemId] as const,
  epicsByStatus: (projectId: string, status: EpicStatus) =>
    [...itemSpecKeys.epics(projectId), 'by-status', status] as const,

  // User story specs
  userStories: (projectId: string) => [...itemSpecKeys.all, 'user-stories', projectId] as const,
  userStory: (projectId: string, specId: string) =>
    [...itemSpecKeys.userStories(projectId), specId] as const,
  userStoryByItem: (projectId: string, itemId: string) =>
    [...itemSpecKeys.userStories(projectId), 'by-item', itemId] as const,
  userStoriesByEpic: (projectId: string, epicId: string) =>
    [...itemSpecKeys.userStories(projectId), 'by-epic', epicId] as const,
  userStoriesByStatus: (projectId: string, status: UserStoryStatus) =>
    [...itemSpecKeys.userStories(projectId), 'by-status', status] as const,

  // Task specs
  tasks: (projectId: string) => [...itemSpecKeys.all, 'tasks', projectId] as const,
  task: (projectId: string, specId: string) => [...itemSpecKeys.tasks(projectId), specId] as const,
  taskByItem: (projectId: string, itemId: string) =>
    [...itemSpecKeys.tasks(projectId), 'by-item', itemId] as const,
  tasksByStory: (projectId: string, storyId: string) =>
    [...itemSpecKeys.tasks(projectId), 'by-story', storyId] as const,
  tasksByStatus: (projectId: string, status: TaskStatus) =>
    [...itemSpecKeys.tasks(projectId), 'by-status', status] as const,

  // Defect specs
  defects: (projectId: string) => [...itemSpecKeys.all, 'defects', projectId] as const,
  defect: (projectId: string, specId: string) =>
    [...itemSpecKeys.defects(projectId), specId] as const,
  defectByItem: (projectId: string, itemId: string) =>
    [...itemSpecKeys.defects(projectId), 'by-item', itemId] as const,
  defectsBySeverity: (projectId: string, severity: DefectSeverity) =>
    [...itemSpecKeys.defects(projectId), 'by-severity', severity] as const,
  defectsByStatus: (projectId: string, status: DefectStatus) =>
    [...itemSpecKeys.defects(projectId), 'by-status', status] as const,

  // Summary/stats
  stats: (projectId: string) => [...itemSpecKeys.all, 'stats', projectId] as const,
};

export { itemSpecKeys };
