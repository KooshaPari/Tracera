import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  Clock,
  RefreshCcw,
  Target,
  TestTube,
  TrendingDown,
  TrendingUp,
  Zap,
} from 'lucide-react';
import { useState } from 'react';

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  useCoverageMetrics,
  useDefectDensity,
  useExecutionHistory,
  useFlakyTests,
  usePassRateTrend,
  useQAMetricsSummary,
} from '@/hooks/useQaMetrics';
import {
  Badge,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Progress,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Skeleton,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@tracertm/ui';

interface QADashboardViewProps {
  projectId: string;
}

const statusColors: Record<string, string> = {
  blocked: 'bg-orange-500/10 text-orange-600 border-orange-500/30',
  cancelled: 'bg-gray-500/10 text-gray-600 border-gray-500/30',
  failed: 'bg-red-500/10 text-red-600 border-red-500/30',
  passed: 'bg-green-500/10 text-green-600 border-green-500/30',
  pending: 'bg-yellow-500/10 text-yellow-600 border-yellow-500/30',
  running: 'bg-blue-500/10 text-blue-600 border-blue-500/30',
};

function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${Math.round(seconds)}s`;
  }
  if (seconds < 3600) {
    return `${Math.round(seconds / 60)}m`;
  }
  return `${(seconds / 3600).toFixed(1)}h`;
}

export function QADashboardView({ projectId }: QADashboardViewProps) {
  const [trendDays, setTrendDays] = useState(30);

  const { data: summary, isLoading: summaryLoading } = useQAMetricsSummary(projectId);
  const { data: passRateTrend, isLoading: trendLoading } = usePassRateTrend(projectId, trendDays);
  const { data: coverageMetrics, isLoading: coverageLoading } = useCoverageMetrics(projectId);
  const { data: defectDensity, isLoading: defectLoading } = useDefectDensity(projectId);
  const { data: flakyTests, isLoading: flakyLoading } = useFlakyTests(projectId);
  const { data: executionHistory, isLoading: historyLoading } = useExecutionHistory(projectId);

  return (
    <div className='space-y-6 p-6'>
      {/* Header */}
      <div className='flex items-center justify-between'>
        <div>
          <h1 className='text-3xl font-bold tracking-tight'>QA Dashboard</h1>
          <p className='text-muted-foreground mt-1'>
            Quality engineering metrics and test analytics
          </p>
        </div>
        <Select
          value={String(trendDays)}
          onValueChange={(v) => {
            setTrendDays(Number.parseInt(v, 10));
          }}
        >
          <SelectTrigger className='w-[140px]'>
            <SelectValue placeholder='Time range' />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value='7'>Last 7 days</SelectItem>
            <SelectItem value='14'>Last 14 days</SelectItem>
            <SelectItem value='30'>Last 30 days</SelectItem>
            <SelectItem value='90'>Last 90 days</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Key Metrics Cards */}
      <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-4'>
        <Card>
          <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-2'>
            <CardTitle className='text-sm font-medium'>Total Test Cases</CardTitle>
            <TestTube className='text-muted-foreground h-4 w-4' />
          </CardHeader>
          <CardContent>
            {summaryLoading ? (
              <Skeleton className='h-8 w-20' />
            ) : (
              <>
                <div className='text-2xl font-bold'>{summary?.testCases.total ?? 0}</div>
                <p className='text-muted-foreground text-xs'>
                  {summary?.testCases.automationPercentage ?? 0}% automated
                </p>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-2'>
            <CardTitle className='text-sm font-medium'>Avg Pass Rate</CardTitle>
            {summary?.testRuns.averagePassRate && summary.testRuns.averagePassRate >= 80 ? (
              <TrendingUp className='h-4 w-4 text-green-500' />
            ) : (
              <TrendingDown className='h-4 w-4 text-red-500' />
            )}
          </CardHeader>
          <CardContent>
            {summaryLoading ? (
              <Skeleton className='h-8 w-20' />
            ) : (
              <>
                <div className='text-2xl font-bold'>
                  {summary?.testRuns.averagePassRate?.toFixed(1) ?? 0}%
                </div>
                <p className='text-muted-foreground text-xs'>
                  From {summary?.testRuns.total ?? 0} runs
                </p>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-2'>
            <CardTitle className='text-sm font-medium'>Coverage</CardTitle>
            <Target className='text-muted-foreground h-4 w-4' />
          </CardHeader>
          <CardContent>
            {summaryLoading ? (
              <Skeleton className='h-8 w-20' />
            ) : (
              <>
                <div className='text-2xl font-bold'>
                  {summary?.coverage.coveragePercentage?.toFixed(1) ?? 0}%
                </div>
                <p className='text-muted-foreground text-xs'>
                  {summary?.coverage.coveredRequirements ?? 0} /{' '}
                  {summary?.coverage.totalRequirements ?? 0} requirements
                </p>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-2'>
            <CardTitle className='text-sm font-medium'>Defect Density</CardTitle>
            <AlertTriangle className='text-muted-foreground h-4 w-4' />
          </CardHeader>
          <CardContent>
            {defectLoading ? (
              <Skeleton className='h-8 w-20' />
            ) : (
              <>
                <div className='text-2xl font-bold'>
                  {defectDensity?.overallDefectDensity?.toFixed(1) ?? 0}%
                </div>
                <p className='text-muted-foreground text-xs'>
                  {defectDensity?.totalFailures ?? 0} failures
                </p>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Tabs for detailed views */}
      <Tabs defaultValue='overview' className='space-y-4'>
        <TabsList>
          <TabsTrigger value='overview'>Overview</TabsTrigger>
          <TabsTrigger value='coverage'>Coverage</TabsTrigger>
          <TabsTrigger value='quality'>Quality</TabsTrigger>
          <TabsTrigger value='history'>Execution History</TabsTrigger>
        </TabsList>

        <TabsContent value='overview' className='space-y-4'>
          {/* Pass Rate Trend */}
          <Card>
            <CardHeader>
              <CardTitle>Pass Rate Trend</CardTitle>
              <CardDescription>Test execution results over time</CardDescription>
            </CardHeader>
            <CardContent>
              {trendLoading ? (
                <Skeleton className='h-[200px] w-full' />
              ) : passRateTrend?.trend.length === 0 ? (
                <div className='text-muted-foreground py-12 text-center'>
                  <BarChart3 className='mx-auto mb-4 h-12 w-12 opacity-50' />
                  <p>No test run data available</p>
                </div>
              ) : (
                <div className='space-y-4'>
                  {/* Simple bar representation of trend */}
                  <div className='flex h-[150px] items-end gap-1'>
                    {passRateTrend?.trend.map((point, i) => (
                      <div key={i} className='flex flex-1 flex-col items-center gap-1'>
                        <div
                          className='bg-primary w-full rounded-t transition-all'
                          style={{ height: `${point.avgPassRate * 1.5}px` }}
                          title={`${point.date}: ${point.avgPassRate}%`}
                        />
                        <span className='text-muted-foreground origin-left rotate-45 text-[10px]'>
                          {point.date?.slice(5) || ''}
                        </span>
                      </div>
                    ))}
                  </div>
                  <div className='grid grid-cols-3 gap-4 text-center text-sm'>
                    <div>
                      <p className='text-muted-foreground'>Total Runs</p>
                      <p className='font-bold'>
                        {passRateTrend?.trend.reduce((acc, p) => acc + p.totalRuns, 0) ?? 0}
                      </p>
                    </div>
                    <div>
                      <p className='text-muted-foreground'>Total Passed</p>
                      <p className='font-bold text-green-600'>
                        {passRateTrend?.trend.reduce((acc, p) => acc + p.totalPassed, 0) ?? 0}
                      </p>
                    </div>
                    <div>
                      <p className='text-muted-foreground'>Total Failed</p>
                      <p className='font-bold text-red-600'>
                        {passRateTrend?.trend.reduce((acc, p) => acc + p.totalFailed, 0) ?? 0}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Test Case Breakdown */}
          <div className='grid gap-4 md:grid-cols-2'>
            <Card>
              <CardHeader>
                <CardTitle>Test Cases by Status</CardTitle>
              </CardHeader>
              <CardContent>
                {summaryLoading ? (
                  <Skeleton className='h-[150px] w-full' />
                ) : (
                  <div className='space-y-3'>
                    {Object.entries(summary?.testCases.byStatus ?? {}).map(([status, count]) => (
                      <div key={status} className='flex items-center gap-3'>
                        <div className='w-24 text-sm capitalize'>{status}</div>
                        <Progress
                          value={(count / (summary?.testCases.total ?? 1)) * 100}
                          className='flex-1'
                        />
                        <div className='w-12 text-right text-sm font-medium'>{count}</div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Test Runs by Type</CardTitle>
              </CardHeader>
              <CardContent>
                {summaryLoading ? (
                  <Skeleton className='h-[150px] w-full' />
                ) : (
                  <div className='space-y-3'>
                    {Object.entries(summary?.testRuns.byType ?? {}).map(([type, count]) => (
                      <div key={type} className='flex items-center gap-3'>
                        <div className='w-24 text-sm capitalize'>{type.replace('_', ' ')}</div>
                        <Progress
                          value={(count / (summary?.testRuns.total ?? 1)) * 100}
                          className='flex-1'
                        />
                        <div className='w-12 text-right text-sm font-medium'>{count}</div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value='coverage' className='space-y-4'>
          {/* Coverage Overview */}
          <Card>
            <CardHeader>
              <CardTitle>Requirements Coverage</CardTitle>
              <CardDescription>Test coverage across requirements</CardDescription>
            </CardHeader>
            <CardContent>
              {coverageLoading ? (
                <Skeleton className='h-[200px] w-full' />
              ) : (
                <div className='space-y-6'>
                  {/* Overall Coverage */}
                  <div className='space-y-2'>
                    <div className='flex justify-between text-sm'>
                      <span>Overall Coverage</span>
                      <span className='font-bold'>
                        {coverageMetrics?.overall.coveragePercentage?.toFixed(1)}%
                      </span>
                    </div>
                    <Progress value={coverageMetrics?.overall.coveragePercentage ?? 0} />
                    <div className='text-muted-foreground flex justify-between text-xs'>
                      <span>{coverageMetrics?.overall.coveredRequirements ?? 0} covered</span>
                      <span>{coverageMetrics?.overall.totalRequirements ?? 0} total</span>
                    </div>
                  </div>

                  {/* Coverage by View */}
                  <div>
                    <h4 className='mb-3 text-sm font-semibold'>Coverage by Category</h4>
                    <div className='space-y-2'>
                      {Object.entries(coverageMetrics?.byView ?? {}).map(([view, data]) => (
                        <div key={view} className='flex items-center gap-3'>
                          <div className='w-32 truncate text-sm'>{view}</div>
                          <Progress value={data.percentage} className='flex-1' />
                          <div className='w-16 text-right text-sm'>
                            {data.covered}/{data.total}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Coverage Gaps Alert */}
                  {coverageMetrics && coverageMetrics.gapsCount > 0 && (
                    <div className='rounded-lg border border-yellow-500/30 bg-yellow-500/10 p-4'>
                      <div className='flex items-center gap-2 text-yellow-600'>
                        <AlertTriangle className='h-4 w-4' />
                        <span className='font-medium'>Coverage Gaps</span>
                      </div>
                      <p className='text-muted-foreground mt-1 text-sm'>
                        {coverageMetrics.gapsCount} requirements without test coverage
                        {coverageMetrics.highPriorityGaps > 0 && (
                          <span className='font-medium text-red-600'>
                            {' '}
                            ({coverageMetrics.highPriorityGaps} high priority)
                          </span>
                        )}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value='quality' className='space-y-4'>
          <div className='grid gap-4 md:grid-cols-2'>
            {/* Top Failing Tests */}
            <Card>
              <CardHeader>
                <CardTitle>Top Failing Tests</CardTitle>
                <CardDescription>Tests with highest failure rates</CardDescription>
              </CardHeader>
              <CardContent>
                {defectLoading ? (
                  <Skeleton className='h-[200px] w-full' />
                ) : defectDensity?.topFailingTests.length === 0 ? (
                  <div className='text-muted-foreground py-8 text-center'>
                    <CheckCircle2 className='mx-auto mb-2 h-8 w-8 text-green-500' />
                    <p>No failing tests</p>
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Test Case</TableHead>
                        <TableHead className='text-right'>Failures</TableHead>
                        <TableHead className='text-right'>Rate</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {defectDensity?.topFailingTests.slice(0, 5).map((test) => (
                        <TableRow key={test.testCaseId}>
                          <TableCell className='max-w-[150px] truncate font-medium'>
                            {test.testCaseId.slice(0, 8)}...
                          </TableCell>
                          <TableCell className='text-right text-red-600'>
                            {test.failureCount}
                          </TableCell>
                          <TableCell className='text-right'>{test.failureRate}%</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>

            {/* Flaky Tests */}
            <Card>
              <CardHeader>
                <CardTitle>Flaky Tests</CardTitle>
                <CardDescription>Tests with inconsistent results</CardDescription>
              </CardHeader>
              <CardContent>
                {flakyLoading ? (
                  <Skeleton className='h-[200px] w-full' />
                ) : (
                  <div className='space-y-4'>
                    <div className='bg-muted/50 flex items-center justify-between rounded-lg p-3'>
                      <div className='flex items-center gap-2'>
                        <RefreshCcw className='h-4 w-4 text-yellow-500' />
                        <span>Marked as Flaky</span>
                      </div>
                      <Badge variant='secondary'>{flakyTests?.markedFlakyCount ?? 0}</Badge>
                    </div>
                    <div className='bg-muted/50 flex items-center justify-between rounded-lg p-3'>
                      <div className='flex items-center gap-2'>
                        <Zap className='h-4 w-4 text-orange-500' />
                        <span>Potentially Flaky</span>
                      </div>
                      <Badge variant='secondary'>{flakyTests?.potentiallyFlakyCount ?? 0}</Badge>
                    </div>

                    {flakyTests &&
                      (flakyTests.markedFlakyCount > 0 || flakyTests.potentiallyFlakyCount > 0) && (
                        <div className='pt-2'>
                          <h5 className='mb-2 text-sm font-medium'>Top Flaky Tests</h5>
                          <div className='space-y-1'>
                            {[...flakyTests.markedFlaky, ...flakyTests.potentiallyFlaky]
                              .slice(0, 5)
                              .map((test, i) => (
                                <div key={i} className='flex items-center justify-between text-sm'>
                                  <span className='max-w-[180px] truncate'>
                                    {test.testCaseId.slice(0, 12)}...
                                  </span>
                                  <span className='text-muted-foreground'>
                                    {'flakyOccurrences' in test
                                      ? `${test.flakyOccurrences} times`
                                      : `${test.inconsistentDays} days`}
                                  </span>
                                </div>
                              ))}
                          </div>
                        </div>
                      )}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value='history' className='space-y-4'>
          <Card>
            <CardHeader>
              <CardTitle>Recent Test Runs</CardTitle>
              <CardDescription>Latest test execution results</CardDescription>
            </CardHeader>
            <CardContent>
              {historyLoading ? (
                <Skeleton className='h-[300px] w-full' />
              ) : executionHistory?.runs.length === 0 ? (
                <div className='text-muted-foreground py-12 text-center'>
                  <Clock className='mx-auto mb-4 h-12 w-12 opacity-50' />
                  <p>No test runs in the selected period</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Run</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead className='text-right'>Pass Rate</TableHead>
                      <TableHead className='text-right'>Duration</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {executionHistory?.runs.map((run) => (
                      <TableRow key={run.id}>
                        <TableCell>
                          <div className='font-medium'>{run.name}</div>
                          <div className='text-muted-foreground text-xs'>
                            {run.branch && `${run.branch} • `}
                            {run.buildNumber && `#${run.buildNumber}`}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge className={statusColors[run.status] ?? ''}>{run.status}</Badge>
                        </TableCell>
                        <TableCell className='capitalize'>
                          {run.runType.replace('_', ' ')}
                        </TableCell>
                        <TableCell className='text-right'>
                          {run.passRate != null ? (
                            <span
                              className={
                                (run.passRate ?? 0) >= 90
                                  ? 'text-green-600'
                                  : (run.passRate ?? 0) >= 70
                                    ? 'text-yellow-600'
                                    : 'text-red-600'
                              }
                            >
                              {(run.passRate ?? 0).toFixed(1)}%
                            </span>
                          ) : (
                            '-'
                          )}
                        </TableCell>
                        <TableCell className='text-right'>
                          {run.durationSeconds ? formatDuration(run.durationSeconds) : '-'}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
