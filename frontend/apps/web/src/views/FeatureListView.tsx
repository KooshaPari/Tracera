import { useNavigate, useSearch } from '@tanstack/react-router';
import {
  BookOpen,
  CheckCircle2,
  Filter,
  ListTodo,
  Plus,
  Search,
  TrendingUp,
  XCircle,
} from 'lucide-react';
import { useMemo, useState } from 'react';
import { toast } from 'sonner';

import type { Feature, FeatureStatus } from '@tracertm/types';

import { FeatureCard } from '@/components/specifications/bdd/FeatureCard';
import { useFeatures } from '@/hooks/useSpecifications';
import {
  Button,
  Card,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Skeleton,
} from '@tracertm/ui';

interface FeatureListViewProps {
  projectId: string;
}

export const FeatureListView = ({ projectId }: FeatureListViewProps) => {
  const navigate = useNavigate();
  const searchParams = useSearch({ strict: false });

  const { data: featuresData, isLoading } = useFeatures({ projectId });
  const features = featuresData?.features ?? [];

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<FeatureStatus | 'all'>(
    (searchParams?.status as FeatureStatus) || 'all',
  );

  const [newName, setNewName] = useState('');
  const [newStatus, setNewStatus] = useState<FeatureStatus>('draft');
  const [newDescription, setNewDescription] = useState('');

  const filteredFeatures = useMemo(
    () =>
      features.filter((feature: Feature) => {
        const matchesStatus = statusFilter === 'all' || feature.status === statusFilter;
        const matchesQuery =
          feature.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          feature.featureNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
          (feature.description?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false);

        return matchesStatus && matchesQuery;
      }),
    [features, statusFilter, searchQuery],
  );

  const statusCounts = useMemo(
    () => ({
      active: features.filter((f: Feature) => f.status === 'active').length,
      all: features.length,
      archived: features.filter((f: Feature) => f.status === 'archived').length,
      deprecated: features.filter((f: Feature) => f.status === 'deprecated').length,
      draft: features.filter((f: Feature) => f.status === 'draft').length,
    }),
    [features],
  );

  const overallPassRate = useMemo(() => {
    if (features.length === 0) {
      return '0';
    }
    const totalScenarios = features.reduce(
      (sum: number, f: Feature) => sum + (f.scenarioCount || 0),
      0,
    );
    const passedScenarios = features.reduce(
      (sum: number, f: Feature) => sum + (f.passedScenarios || 0),
      0,
    );
    return totalScenarios > 0 ? ((passedScenarios / totalScenarios) * 100).toFixed(1) : '0';
  }, [features]);

  const scenarioSummary = useMemo(() => {
    const summary = {
      failed: features.reduce((sum: number, f: Feature) => sum + (f.failedScenarios || 0), 0),
      passed: features.reduce((sum: number, f: Feature) => sum + (f.passedScenarios || 0), 0),
      pending: features.reduce((sum: number, f: Feature) => sum + (f.pendingScenarios || 0), 0),
      total: features.reduce((sum: number, f: Feature) => sum + (f.scenarioCount || 0), 0),
    };
    return summary;
  }, [features]);

  const handleCreate = async () => {
    if (!newName.trim()) {
      toast.error('Feature name is required');
      return;
    }
    try {
      // API call would go here
      toast.success('Feature created successfully');
      setNewName('');
      setNewDescription('');
      setNewStatus('draft');
      setShowCreateModal(false);
    } catch {
      toast.error('Failed to create feature');
    }
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const handleStatusFilterChange = (v: string) => {
    setStatusFilter(v as FeatureStatus | 'all');
  };

  const handleFeatureClick = (feature: Feature) => {
    navigate({
      params: { featureId: feature.id, projectId },
      to: '/projects/$projectId/features/$featureId',
    });
  };

  const handleNewStatusChange = (v: string) => {
    setNewStatus(v as FeatureStatus);
  };

  const handleCloseModal = () => {
    setShowCreateModal(false);
  };

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNewName(e.target.value);
  };

  const handleDescriptionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setNewDescription(e.target.value);
  };

  if (isLoading) {
    return (
      <div className='animate-pulse space-y-8 p-6'>
        <Skeleton className='h-10 w-48' />
        <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Skeleton key={i} className='h-40 rounded-xl' />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className='animate-in fade-in mx-auto max-w-[1600px] space-y-8 p-6 pb-20 duration-500'>
      {/* Header */}
      <div className='flex flex-col justify-between gap-4 md:flex-row md:items-center'>
        <div>
          <h1 className='text-2xl font-black tracking-tight uppercase'>BDD Features</h1>
          <p className='text-muted-foreground text-sm font-medium'>
            Manage Gherkin features and test scenarios.
          </p>
        </div>
        <Button
          size='sm'
          onClick={() => {
            setShowCreateModal(true);
          }}
          className='shadow-primary/20 gap-2 rounded-xl shadow-lg'
        >
          <Plus className='h-4 w-4' /> New Feature
        </Button>
      </div>

      {/* Scenario Summary */}
      <div className='grid gap-4 md:grid-cols-5'>
        <Card className='border-none bg-gradient-to-br from-blue-50 to-blue-100/50 dark:from-blue-950/20 dark:to-blue-900/20'>
          <div className='space-y-2 p-4'>
            <div className='flex items-center justify-between'>
              <span className='text-muted-foreground text-xs font-medium'>Total Scenarios</span>
              <BookOpen className='h-4 w-4 text-blue-600' />
            </div>
            <div className='text-2xl font-bold'>{scenarioSummary.total}</div>
          </div>
        </Card>

        <Card className='border-none bg-gradient-to-br from-green-50 to-green-100/50 dark:from-green-950/20 dark:to-green-900/20'>
          <div className='space-y-2 p-4'>
            <div className='flex items-center justify-between'>
              <span className='text-muted-foreground text-xs font-medium'>Passing</span>
              <CheckCircle2 className='h-4 w-4 text-green-600' />
            </div>
            <div className='text-2xl font-bold'>{scenarioSummary.passed}</div>
          </div>
        </Card>

        <Card className='border-none bg-gradient-to-br from-red-50 to-red-100/50 dark:from-red-950/20 dark:to-red-900/20'>
          <div className='space-y-2 p-4'>
            <div className='flex items-center justify-between'>
              <span className='text-muted-foreground text-xs font-medium'>Failing</span>
              <XCircle className='h-4 w-4 text-red-600' />
            </div>
            <div className='text-2xl font-bold'>{scenarioSummary.failed}</div>
          </div>
        </Card>

        <Card className='border-none bg-gradient-to-br from-yellow-50 to-yellow-100/50 dark:from-yellow-950/20 dark:to-yellow-900/20'>
          <div className='space-y-2 p-4'>
            <div className='flex items-center justify-between'>
              <span className='text-muted-foreground text-xs font-medium'>Pending</span>
              <ListTodo className='h-4 w-4 text-yellow-600' />
            </div>
            <div className='text-2xl font-bold'>{scenarioSummary.pending}</div>
          </div>
        </Card>

        <Card className='border-none bg-gradient-to-br from-purple-50 to-purple-100/50 dark:from-purple-950/20 dark:to-purple-900/20'>
          <div className='space-y-2 p-4'>
            <div className='flex items-center justify-between'>
              <span className='text-muted-foreground text-xs font-medium'>Pass Rate</span>
              <TrendingUp className='h-4 w-4 text-purple-600' />
            </div>
            <div className='text-2xl font-bold'>{overallPassRate}%</div>
          </div>
        </Card>
      </div>

      {/* Filters Bar */}
      <Card className='bg-muted/30 flex flex-wrap items-center gap-3 rounded-2xl border-none p-3'>
        <div className='relative min-w-[250px] flex-1'>
          <Search className='text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2' />
          <Input
            placeholder='Search by name or feature number...'
            className='h-10 border-none bg-transparent pl-10 focus-visible:ring-0'
            value={searchQuery}
            onChange={handleSearchChange}
          />
        </div>

        <div className='bg-border/50 hidden h-6 w-px md:block' />

        <Select value={statusFilter} onValueChange={handleStatusFilterChange}>
          <SelectTrigger className='hover:bg-background/50 h-10 w-[140px] border-none bg-transparent'>
            <div className='flex items-center gap-2'>
              <Filter className='text-muted-foreground h-3.5 w-3.5' />
              <SelectValue placeholder='Status' />
            </div>
          </SelectTrigger>
          <SelectContent>
            <SelectItem value='all'>All ({statusCounts.all})</SelectItem>
            <SelectItem value='draft'>Draft ({statusCounts.draft})</SelectItem>
            <SelectItem value='active'>Active ({statusCounts.active})</SelectItem>
            <SelectItem value='deprecated'>Deprecated ({statusCounts.deprecated})</SelectItem>
            <SelectItem value='archived'>Archived ({statusCounts.archived})</SelectItem>
          </SelectContent>
        </Select>
      </Card>

      {/* Features Grid */}
      {filteredFeatures.length > 0 ? (
        <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
          {filteredFeatures.map((feature: Feature) => (
            <button
              key={feature.id}
              onClick={() => {
                handleFeatureClick(feature);
              }}
              className='text-left'
            >
              <FeatureCard feature={feature} />
            </button>
          ))}
        </div>
      ) : (
        <Card className='bg-muted/20 border-none py-12'>
          <div className='text-muted-foreground/40 flex flex-col items-center justify-center'>
            <BookOpen className='mb-4 h-12 w-12' />
            <p className='text-sm font-medium'>No features found</p>
            <p className='text-muted-foreground/50 text-xs'>
              {searchQuery || statusFilter !== 'all'
                ? 'Try adjusting your filters'
                : 'Create your first feature to get started'}
            </p>
          </div>
        </Card>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className='fixed inset-0 z-50 flex items-center justify-center'>
          <div className='fixed inset-0 bg-black/50 backdrop-blur-sm' onClick={handleCloseModal} />
          <div
            className='bg-background relative w-full max-w-2xl rounded-xl border p-6 shadow-2xl'
            role='dialog'
            aria-modal='true'
            aria-labelledby='create-feature-title'
          >
            <div className='mb-6 flex items-center justify-between'>
              <h2 id='create-feature-title' className='text-lg font-semibold'>
                Create New Feature
              </h2>
              <button
                type='button'
                onClick={handleCloseModal}
                aria-label='Close dialog'
                className='hover:bg-accent rounded-lg p-1'
              >
                ✕
              </button>
            </div>

            <div className='space-y-4'>
              <div>
                <label className='mb-1 block text-sm font-medium'>Feature Name</label>
                <Input
                  value={newName}
                  onChange={handleNameChange}
                  placeholder='e.g., User Authentication'
                  className='h-10'
                />
              </div>

              <div>
                <label className='mb-1 block text-sm font-medium'>Status</label>
                <Select value={newStatus} onValueChange={handleNewStatusChange}>
                  <SelectTrigger className='h-10'>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value='draft'>Draft</SelectItem>
                    <SelectItem value='active'>Active</SelectItem>
                    <SelectItem value='deprecated'>Deprecated</SelectItem>
                    <SelectItem value='archived'>Archived</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className='mb-1 block text-sm font-medium'>Description</label>
                <textarea
                  value={newDescription}
                  onChange={handleDescriptionChange}
                  placeholder='Describe the feature in business terms...'
                  className='border-input bg-background h-24 w-full rounded-lg border px-3 py-2'
                />
              </div>

              <div className='flex justify-end gap-2 pt-4'>
                <Button variant='ghost' onClick={handleCloseModal}>
                  Cancel
                </Button>
                <Button onClick={handleCreate} disabled={!newName.trim()}>
                  Create Feature
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
