// Hook to fetch and transform QA data for QAEnhancedNode components

import type {
  QANodeArtifact,
  QANodeMetrics,
  QANodePreview,
} from '../components/graph/nodes/QAEnhancedNode';

import { useExecutionArtifacts, useExecutions } from './useExecutions';

interface UseQAEnhancedNodeDataOptions {
  projectId: string;
  itemId: string;
  enabled?: boolean | undefined;
}

export function useQAEnhancedNodeData({ projectId, itemId }: UseQAEnhancedNodeDataOptions) {
  // Fetch executions for this item
  const { data: executionsData } = useExecutions(projectId, {
    limit: 100,
  });

  // Find executions linked to this item
  const itemExecutions = executionsData?.executions.filter((e) => e.item_id === itemId) ?? [];

  // Calculate metrics from executions
  const metrics: QANodeMetrics | undefined = (() => {
    if (itemExecutions.length === 0) {
      return;
    }

    const completed = itemExecutions.filter((e) => e.status === 'passed' || e.status === 'failed');
    const passed = completed.filter((e) => e.status === 'passed');
    const failed = completed.filter((e) => e.status === 'failed');

    const totalTests = completed.length;
    const passCount = passed.length;
    const failCount = failed.length;
    const passRate = totalTests > 0 ? Math.round((passCount / totalTests) * 100) : 0;

    const durations = completed
      .map((e) => e.duration_ms)
      .filter((d): d is number => d !== undefined && d !== null);
    const avgDuration =
      durations.length > 0
        ? Math.round(durations.reduce((a, b) => a + b, 0) / durations.length)
        : undefined;

    // Get latest execution for lastRunAt
    const latest = [...completed].toSorted(
      (
        a: { completed_at?: string; created_at: string },
        b: { completed_at?: string; created_at: string },
      ) =>
        new Date(b.completed_at ?? b.created_at).getTime() -
        new Date(a.completed_at ?? a.created_at).getTime(),
    )[0];

    return {
      passRate,
      testCount: totalTests,
      passCount,
      failCount,
      ...(avgDuration !== undefined && { avgDuration }),
      ...(latest?.completed_at || latest?.created_at
        ? { lastRunAt: latest?.completed_at ?? latest?.created_at }
        : {}),
    } as QANodeMetrics;
  })();

  // Get artifacts from latest execution
  const latestExecution = [...itemExecutions].toSorted(
    (a: { created_at: string }, b: { created_at: string }) =>
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
  )[0];

  const { data: artifactsData } = useExecutionArtifacts(projectId, latestExecution?.id ?? '');

  // Transform artifacts
  const artifacts: QANodeArtifact[] | undefined =
    artifactsData?.artifacts.map((a) =>
      Object.assign(
        {
          id: a.id,
          type: a.artifact_type as QANodeArtifact[`type`],
          url:
            a.url ??
            `/api/v1/projects/${projectId}/executions/${a.execution_id}/artifacts/${a.id}/download`,
        },
        a.thumbnail_url || a.thumbnail_path
          ? { thumbnailUrl: a.thumbnail_url ?? a.thumbnail_path }
          : {},
        { capturedAt: a.captured_at },
      ),
    ) ?? undefined;

  // Build preview from latest artifact
  const preview: QANodePreview | undefined = (() => {
    if (!artifacts || artifacts.length === 0) {
      return;
    }

    const screenshot = artifacts.find((a) => a.type === 'screenshot');
    const gif = artifacts.find((a) => a.type === 'gif');
    const video = artifacts.find((a) => a.type === 'video');

    return {
      ...(screenshot?.thumbnailUrl || screenshot?.url
        ? { thumbnailUrl: screenshot?.thumbnailUrl ?? screenshot?.url }
        : {}),
      ...(screenshot?.url ? { screenshotUrl: screenshot.url } : {}),
      ...(gif?.url ? { gifUrl: gif.url } : {}),
      ...(video?.url ? { videoUrl: video.url } : {}),
      hasLiveDemo: Boolean(gif) || Boolean(video),
    } as QANodePreview;
  })();

  return {
    artifacts,
    executions: itemExecutions,
    isLoading: false,
    metrics,
    preview,
  };
}
