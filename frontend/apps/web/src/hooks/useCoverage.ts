// Barrel re-export for coverage hooks. The implementation lives in `./hooks.ts`.
//
// The barrel preserves the public API consumed by views (e.g.
// `pages/projects/views/CoverageMatrixView.tsx` → `useCoverageGaps`,
// `useTraceabilityMatrix`). It re-exports the concrete hooks plus the
// generic CRUD hooks so existing imports work unchanged.

export {
  useCoverageGaps,
  useCoverageActivities,
  useCoverageStats,
  useCoverage,
  useCoverages,
  useCreateCoverage,
  useUpdateCoverage,
  useDeleteCoverage,
  useVerifyCoverage,
  useTraceabilityMatrix,
} from "./coverage/hooks";
