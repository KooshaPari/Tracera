import { useNavigate, useParams } from '@tanstack/react-router';
import { format } from 'date-fns';
import { useMemo, useState } from 'react';

import type { Scenario, ScenarioActivity } from '@tracertm/types';

import {
  useFeatures,
  useProjectScenarioActivities,
  useProjectScenarios,
  useScenarioActivities,
} from '@/hooks/useSpecifications';
import {
  Card,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui';

export function ScenarioActivityView() {
  const params = useParams({ strict: false });
  const _navigate = useNavigate();
  const projectId = params.projectId ?? '';
  const [statusFilter, setStatusFilter] = useState('all');
  const { data: scenariosData } = useProjectScenarios(
    projectId,
    statusFilter === 'all' ? undefined : statusFilter,
  );
  const { data: featuresData } = useFeatures({ projectId });
  const scenarios = scenariosData?.scenarios ?? [];
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedScenarioId, setSelectedScenarioId] = useState('');
  const [sortOrder, setSortOrder] = useState<'recent' | 'oldest'>('recent');
  const [collapsedGroups, setCollapsedGroups] = useState<Set<string>>(() => new Set());
  const [page, setPage] = useState(1);
  const pageSize = 10;
  const { data: activities } = useScenarioActivities(selectedScenarioId);
  const [streamPage, setStreamPage] = useState(1);
  const [streamEventType, setStreamEventType] = useState('all');
  const [streamRange, setStreamRange] = useState('30d');
  const streamPageSize = 12;

  const streamSince = useMemo(() => {
    if (streamRange === 'all') {
      return;
    }
    const now = new Date();
    const days =
      streamRange === '24h' ? 1 : streamRange === '7d' ? 7 : streamRange === '30d' ? 30 : 90;
    const since = new Date(now.getTime() - days * 24 * 60 * 60 * 1000);
    return since.toISOString();
  }, [streamRange]);

  const { data: projectActivityData } = useProjectScenarioActivities(projectId, {
    limit: streamPageSize,
    offset: (streamPage - 1) * streamPageSize,
    ...(streamEventType !== 'all' ? { eventType: streamEventType } : {}),
    ...(streamSince ? { since: streamSince } : {}),
  });
  const projectActivities = Array.isArray(projectActivityData) ? projectActivityData : [];
  const projectActivityTotal = projectActivities.length;
  const featureMap = useMemo(() => {
    const map = new Map<string, string>();
    for (const feature of featuresData?.features ?? []) {
      map.set(feature.id, `${feature.featureNumber} · ${feature.name}`);
    }
    return map;
  }, [featuresData]);

  const filteredScenarios = useMemo(() => {
    const query = searchQuery.toLowerCase();
    return scenarios.filter(
      (scenario: Scenario) =>
        scenario.title.toLowerCase().includes(query) ||
        scenario.scenarioNumber.toLowerCase().includes(query),
    );
  }, [scenarios, searchQuery]);

  const groupedScenarios = useMemo(() => {
    const groups = new Map<string, Scenario[]>();
    for (const scenario of filteredScenarios) {
      const key = scenario.featureId || 'unknown';
      const list = groups.get(key) ?? [];
      list.push(scenario);
      groups.set(key, list);
    }
    return [...groups.entries()].toSorted((a, b) => {
      const aLabel = featureMap.get(a[0]) ?? a[0];
      const bLabel = featureMap.get(b[0]) ?? b[0];
      return aLabel.localeCompare(bLabel);
    });
  }, [filteredScenarios, featureMap]);

  const activitiesList = activities?.activities ?? [];
  const sortedActivities = useMemo(() => {
    if (activitiesList.length === 0) {
      return [];
    }
    const sorted = [...activitiesList].toSorted((a, b) => {
      const aTime = a.createdAt ? new Date(a.createdAt).getTime() : 0;
      const bTime = b.createdAt ? new Date(b.createdAt).getTime() : 0;
      return sortOrder === 'recent' ? bTime - aTime : aTime - bTime;
    });
    return sorted;
  }, [activitiesList, sortOrder]);

  const totalPages = Math.max(1, Math.ceil(sortedActivities.length / pageSize));
  const pagedActivities = sortedActivities.slice((page - 1) * pageSize, page * pageSize);

  return (
    <div className='space-y-6 p-6'>
      <div>
        <h1 className='text-2xl font-bold'>Scenario Activity</h1>
        <p className='text-muted-foreground'>
          Review scenario execution and update history across this project.
        </p>
      </div>

      <Card className='bg-card/50 space-y-4 border-none p-4'>
        <div className='flex flex-col gap-3 md:flex-row'>
          <Input
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
            }}
            placeholder='Search scenarios…'
            className='md:w-80'
          />
          <Select
            value={selectedScenarioId}
            onValueChange={(value) => {
              setSelectedScenarioId(value);
            }}
          >
            <SelectTrigger className='md:w-[360px]'>
              <SelectValue placeholder='Select a scenario' />
            </SelectTrigger>
            <SelectContent>
              {filteredScenarios.map((scenario) => (
                <SelectItem key={scenario.id} value={scenario.id}>
                  {scenario.scenarioNumber} · {scenario.title}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select
            value={statusFilter}
            onValueChange={(value) => {
              setStatusFilter(value);
            }}
          >
            <SelectTrigger className='md:w-[160px]'>
              <SelectValue placeholder='Status' />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value='all'>All status</SelectItem>
              <SelectItem value='draft'>Draft</SelectItem>
              <SelectItem value='review'>Review</SelectItem>
              <SelectItem value='approved'>Approved</SelectItem>
              <SelectItem value='automated'>Automated</SelectItem>
              <SelectItem value='deprecated'>Deprecated</SelectItem>
              <SelectItem value='pending'>Pending</SelectItem>
              <SelectItem value='passing'>Passing</SelectItem>
              <SelectItem value='failing'>Failing</SelectItem>
              <SelectItem value='skipped'>Skipped</SelectItem>
            </SelectContent>
          </Select>
          <Select
            value={sortOrder}
            onValueChange={(v) => {
              setSortOrder(v as any);
            }}
          >
            <SelectTrigger className='md:w-[160px]'>
              <SelectValue placeholder='Sort' />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value='recent'>Most recent</SelectItem>
              <SelectItem value='oldest'>Oldest first</SelectItem>
            </SelectContent>
          </Select>
          {selectedScenarioId && (
            <button className='text-primary text-sm' onClick={() => {}}>
              Open scenario
            </button>
          )}
        </div>

        {groupedScenarios.length > 0 && (
          <div className='space-y-4'>
            {groupedScenarios.map(([featureId, group]) => (
              <div key={featureId} className='space-y-2'>
                <button
                  className='text-muted-foreground flex items-center gap-2 text-left text-xs font-semibold tracking-wide uppercase'
                  onClick={() => {
                    setCollapsedGroups((prev) => {
                      const next = new Set(prev);
                      if (next.has(featureId)) {
                        next.delete(featureId);
                      } else {
                        next.add(featureId);
                      }
                      return next;
                    });
                  }}
                >
                  <span>{featureMap.get(featureId) ?? `Feature ${featureId}`}</span>
                  <span className='text-[10px]'>
                    {collapsedGroups.has(featureId) ? 'Show' : 'Hide'}
                  </span>
                </button>
                {!collapsedGroups.has(featureId) && (
                  <div className='grid gap-2 md:grid-cols-2'>
                    {group.slice(0, 6).map((scenario) => (
                      <button
                        key={scenario.id}
                        className={`rounded-lg border px-3 py-2 text-left text-sm transition-colors ${
                          selectedScenarioId === scenario.id
                            ? 'border-primary/50 bg-primary/5'
                            : 'border-border/50 hover:bg-muted/40'
                        }`}
                        onClick={() => {
                          setSelectedScenarioId(scenario.id);
                        }}
                      >
                        <div className='text-foreground font-medium'>
                          {scenario.scenarioNumber} · {scenario.title}
                        </div>
                        <div className='text-muted-foreground text-xs'>{scenario.status}</div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        <div className='text-muted-foreground space-y-3 text-sm'>
          {pagedActivities.length > 0 ? (
            pagedActivities.map((activity) => (
              <div
                key={activity.id}
                className='border-border/50 flex items-center justify-between border-b pb-2 last:border-0'
              >
                <div>
                  <div className='text-foreground font-medium'>{activity.activityType}</div>
                  <div className='text-muted-foreground text-xs'>
                    {activity.description ?? 'Scenario updated'}
                  </div>
                </div>
                <div className='text-muted-foreground text-xs'>
                  {activity.createdAt
                    ? format(new Date(activity.createdAt), 'MMM d, yyyy HH:mm')
                    : '—'}
                </div>
              </div>
            ))
          ) : (
            <div>No activity yet.</div>
          )}
        </div>

        <div className='text-muted-foreground space-y-3 text-sm'>
          <h2 className='text-foreground text-base font-semibold'>Project Activity Stream</h2>
          <div className='flex flex-wrap gap-2'>
            <Select
              value={streamEventType}
              onValueChange={(value) => {
                setStreamEventType(value);
                setStreamPage(1);
              }}
            >
              <SelectTrigger className='w-[160px]'>
                <SelectValue placeholder='Event type' />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value='all'>All types</SelectItem>
                <SelectItem value='created'>Created</SelectItem>
                <SelectItem value='updated'>Updated</SelectItem>
                <SelectItem value='deleted'>Deleted</SelectItem>
                <SelectItem value='executed'>Executed</SelectItem>
                <SelectItem value='verified'>Verified</SelectItem>
              </SelectContent>
            </Select>
            <Select
              value={streamRange}
              onValueChange={(value) => {
                setStreamRange(value);
                setStreamPage(1);
              }}
            >
              <SelectTrigger className='w-[160px]'>
                <SelectValue placeholder='Range' />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value='24h'>Last 24h</SelectItem>
                <SelectItem value='7d'>Last 7 days</SelectItem>
                <SelectItem value='30d'>Last 30 days</SelectItem>
                <SelectItem value='90d'>Last 90 days</SelectItem>
                <SelectItem value='all'>All time</SelectItem>
              </SelectContent>
            </Select>
          </div>
          {projectActivities.length > 0 ? (
            projectActivities.map((activity: ScenarioActivity) => (
              <div
                key={`stream-${activity.id}`}
                className='border-border/50 flex items-center justify-between border-b pb-2 last:border-0'
              >
                <div>
                  <div className='text-foreground font-medium'>{activity.activityType}</div>
                  <div className='text-muted-foreground text-xs'>
                    {activity.description ?? 'Scenario updated'}
                  </div>
                </div>
                <div className='text-muted-foreground text-xs'>
                  {activity.createdAt
                    ? format(new Date(activity.createdAt), 'MMM d, yyyy HH:mm')
                    : '—'}
                </div>
              </div>
            ))
          ) : (
            <div>No activity stream yet.</div>
          )}
          <div className='text-muted-foreground flex items-center justify-between text-xs'>
            <button
              className='border-border/50 rounded border px-2 py-1 disabled:opacity-50'
              disabled={streamPage === 1}
              onClick={() => {
                setStreamPage((p) => Math.max(1, p - 1));
              }}
            >
              Prev
            </button>
            <span>
              Page {streamPage} of {Math.max(1, Math.ceil(projectActivityTotal / streamPageSize))}
            </span>
            <button
              className='border-border/50 rounded border px-2 py-1 disabled:opacity-50'
              disabled={streamPage >= Math.max(1, Math.ceil(projectActivityTotal / streamPageSize))}
              onClick={() => {
                setStreamPage((p) => p + 1);
              }}
            >
              Next
            </button>
          </div>
        </div>

        {sortedActivities.length > pageSize && (
          <div className='text-muted-foreground flex items-center justify-between text-xs'>
            <button
              className='border-border/50 rounded border px-2 py-1 disabled:opacity-50'
              disabled={page === 1}
              onClick={() => {
                setPage((p) => Math.max(1, p - 1));
              }}
            >
              Prev
            </button>
            <span>
              Page {page} of {totalPages}
            </span>
            <button
              className='border-border/50 rounded border px-2 py-1 disabled:opacity-50'
              disabled={page === totalPages}
              onClick={() => {
                setPage((p) => Math.min(totalPages, p + 1));
              }}
            >
              Next
            </button>
          </div>
        )}
      </Card>
    </div>
  );
}
