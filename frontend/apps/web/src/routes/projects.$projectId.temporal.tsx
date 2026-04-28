import type { Dispatch, SetStateAction } from 'react';

import { createFileRoute, useParams } from '@tanstack/react-router';
import { useCallback, useEffect, useState } from 'react';

import type { Branch, Version } from '@/components/temporal/TemporalNavigator';
import type { Milestone, Sprint } from '@tracertm/types';

import { ProgressDashboard } from '@/components/temporal/ProgressDashboard';
import { TemporalNavigator } from '@/components/temporal/TemporalNavigator';
import { logger } from '@/lib/logger';
import { requireAuth } from '@/lib/route-guards';

type TemporalTab = 'navigator' | 'progress';

interface TemporalTabsProps {
  activeTab: TemporalTab;
  onNavigatorClick: () => void;
  onProgressClick: () => void;
}

interface TemporalContentProps {
  activeTab: TemporalTab;
  branches: Branch[];
  versions: Version[];
  milestones: Milestone[];
  sprints: Sprint[];
  isLoading: boolean;
  projectId: string;
  currentBranchId: string;
  currentVersionId: string;
  onBranchChange: (branchId: string) => void;
  onVersionChange: (versionId: string) => void;
  onMilestoneClick: (milestoneId: string) => void;
  onSprintClick: (sprintId: string) => void;
}

interface TemporalDataState {
  branches: Branch[];
  versions: Version[];
  milestones: Milestone[];
  sprints: Sprint[];
  currentBranchId: string;
  currentVersionId: string;
  isLoading: boolean;
  setCurrentBranchId: Dispatch<SetStateAction<string>>;
  setCurrentVersionId: Dispatch<SetStateAction<string>>;
}

// Mock branch data factory
const createMockBranches = (): Branch[] => [
  {
    createdAt: new Date(),
    id: 'main',
    mergeRequestCount: 0,
    name: 'Main',
    status: 'active',
    updatedAt: new Date(),
  },
];

// Mock version data factory
const createMockVersions = (branchId: string): Version[] => [
  {
    branchId,
    id: 'v1',
    status: 'published',
    timestamp: new Date(),
    title: 'Version 1.0',
  },
];

const getTabClassName = (activeTab: TemporalTab, tab: TemporalTab): string => {
  const baseClassName = 'px-4 py-2 font-medium transition-colors';
  if (activeTab === tab) {
    return `${baseClassName} border-b-2 border-primary text-primary`;
  }
  return `${baseClassName} text-muted-foreground hover:text-foreground`;
};

const TemporalHeader = (): JSX.Element => (
  <div className='flex items-center justify-between'>
    <div>
      <h1 className='text-3xl font-bold tracking-tight'>Temporal Navigation</h1>
      <p className='text-muted-foreground'>Version and branch management with progress tracking</p>
    </div>
  </div>
);

const TemporalTabs = ({
  activeTab,
  onNavigatorClick,
  onProgressClick,
}: TemporalTabsProps): JSX.Element => (
  <div className='flex gap-2 border-b'>
    <button
      type='button'
      onClick={onNavigatorClick}
      className={getTabClassName(activeTab, 'navigator')}
    >
      Version Navigator
    </button>
    <button
      type='button'
      onClick={onProgressClick}
      className={getTabClassName(activeTab, 'progress')}
    >
      Progress Dashboard
    </button>
  </div>
);

const TemporalContent = ({
  activeTab,
  branches,
  versions,
  milestones,
  sprints,
  isLoading,
  projectId,
  currentBranchId,
  currentVersionId,
  onBranchChange,
  onVersionChange,
  onMilestoneClick,
  onSprintClick,
}: TemporalContentProps): JSX.Element => {
  if (activeTab === 'navigator') {
    return (
      <TemporalNavigator
        projectId={projectId}
        currentBranchId={currentBranchId}
        currentVersionId={currentVersionId}
        branches={branches}
        versions={versions}
        isLoading={isLoading}
        onBranchChange={onBranchChange}
        onVersionChange={onVersionChange}
      />
    );
  }

  return (
    <ProgressDashboard
      projectId={projectId}
      milestones={milestones}
      sprints={sprints}
      isLoading={isLoading}
      onMilestoneClick={onMilestoneClick}
      onSprintClick={onSprintClick}
    />
  );
};

const useTemporalData = (projectId: string): TemporalDataState => {
  const [branches, setBranches] = useState<Branch[]>([]);
  const [versions, setVersions] = useState<Version[]>([]);
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [sprints, setSprints] = useState<Sprint[]>([]);
  const [currentBranchId, setCurrentBranchId] = useState<string>('');
  const [currentVersionId, setCurrentVersionId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    try {
      // NOTE: Replace with actual API calls when backend endpoints are wired.
      const mockBranches = createMockBranches();
      const [firstBranch] = mockBranches;
      let firstBranchId = '';
      if (firstBranch) {
        firstBranchId = firstBranch.id;
      }
      const mockVersions = createMockVersions(firstBranchId);
      const [firstVersion] = mockVersions;
      let firstVersionId = '';
      if (firstVersion) {
        firstVersionId = firstVersion.id;
      }

      setBranches(mockBranches);
      setVersions(mockVersions);
      setMilestones([]);
      setSprints([]);
      setCurrentBranchId(firstBranchId);
      setCurrentVersionId(firstVersionId);
    } catch (error) {
      logger.error('Failed to load temporal data:', error);
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  return {
    branches,
    currentBranchId,
    currentVersionId,
    isLoading,
    milestones,
    setCurrentBranchId,
    setCurrentVersionId,
    sprints,
    versions,
  };
};

/**
 * Temporal Navigation View
 * Provides version/branch navigation and progress tracking
 */
const TemporalView = (): JSX.Element => {
  const { projectId } = useParams({ from: '/projects/$projectId/temporal' });
  const [activeTab, setActiveTab] = useState<TemporalTab>('navigator');
  const {
    branches,
    currentBranchId,
    currentVersionId,
    isLoading,
    milestones,
    setCurrentBranchId,
    setCurrentVersionId,
    sprints,
    versions,
  } = useTemporalData(projectId);

  const handleBranchChange = useCallback(
    (branchId: string): void => {
      setCurrentBranchId(branchId);
      const firstVersion = versions.find((version) => version.branchId === branchId);
      if (firstVersion) {
        setCurrentVersionId(firstVersion.id);
      }
    },
    [setCurrentBranchId, setCurrentVersionId, versions],
  );

  const handleVersionChange = useCallback(
    (versionId: string): void => {
      setCurrentVersionId(versionId);
    },
    [setCurrentVersionId],
  );

  const handleMilestoneClick = useCallback((milestoneId: string): void => {
    logger.info('Milestone clicked:', milestoneId);
  }, []);

  const handleSprintClick = useCallback((sprintId: string): void => {
    logger.info('Sprint clicked:', sprintId);
  }, []);

  const handleNavigatorTabClick = useCallback((): void => {
    setActiveTab('navigator');
  }, []);

  const handleProgressTabClick = useCallback((): void => {
    setActiveTab('progress');
  }, []);

  return (
    <div className='flex-1 space-y-6 p-6'>
      <TemporalHeader />

      <TemporalTabs
        activeTab={activeTab}
        onNavigatorClick={handleNavigatorTabClick}
        onProgressClick={handleProgressTabClick}
      />

      <div className='space-y-6'>
        <TemporalContent
          activeTab={activeTab}
          branches={branches}
          versions={versions}
          milestones={milestones}
          sprints={sprints}
          isLoading={isLoading}
          projectId={projectId}
          currentBranchId={currentBranchId}
          currentVersionId={currentVersionId}
          onBranchChange={handleBranchChange}
          onVersionChange={handleVersionChange}
          onMilestoneClick={handleMilestoneClick}
          onSprintClick={handleSprintClick}
        />
      </div>
    </div>
  );
};

const TEMPORAL_VIEW = TemporalView;

const Route = createFileRoute('/projects/$projectId/temporal')({
  beforeLoad: async () => {
    await requireAuth();
  },
  component: TemporalView,
  loader: () => ({}),
});

export { Route, TEMPORAL_VIEW, TemporalView };
