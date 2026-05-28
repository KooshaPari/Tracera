import { useCallback, useState } from 'react';
import { toast } from 'sonner';

import { downloadTraceMatrixFromApi } from '@/api/traceMatrixExport';
import {
  buildTraceabilityMatrixCsv,
  downloadTraceabilityMatrixCsv,
} from '@/lib/traceabilityMatrixExport';

interface MatrixItem {
  id: string;
  title: string;
  type?: string;
  view?: string;
}

export interface TraceabilityMatrixData {
  coverage: Record<string, Set<string>>;
  features: MatrixItem[];
  requirements: MatrixItem[];
}

export function useTraceabilityMatrixExport(projectId: string, matrix: TraceabilityMatrixData) {
  const [isExporting, setIsExporting] = useState(false);

  const canExport = matrix.requirements.length > 0 && matrix.features.length > 0;

  const handleExportCsv = useCallback(async () => {
    if (matrix.requirements.length === 0 && matrix.features.length === 0) {
      toast.error('Nothing to export — add requirements and features first');
      return;
    }
    if (matrix.requirements.length === 0) {
      toast.error('Nothing to export — add requirements first');
      return;
    }
    if (matrix.features.length === 0) {
      toast.error('Nothing to export — add features first');
      return;
    }

    const firstReq = matrix.requirements[0];
    const firstFeat = matrix.features[0];
    const sourceView = firstReq?.type ?? firstReq?.view;
    const targetView = firstFeat?.type ?? firstFeat?.view;
    if (!sourceView || !targetView) {
      toast.error('Nothing to export — matrix views are not configured');
      return;
    }

    const exportOptions = { sourceView, targetView };

    setIsExporting(true);
    try {
      await downloadTraceMatrixFromApi(projectId, exportOptions);
      toast.success('Matrix exported to CSV');
    } catch {
      try {
        const csv = buildTraceabilityMatrixCsv(
          matrix.requirements.map((r) => ({ id: r.id, title: r.title })),
          matrix.features.map((f) => ({ id: f.id, title: f.title })),
          matrix.coverage,
        );
        downloadTraceabilityMatrixCsv(csv, projectId);
        toast.success('Matrix exported to CSV (from current view)');
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Export failed';
        toast.error(`Could not export matrix: ${message}`);
      }
    } finally {
      setIsExporting(false);
    }
  }, [matrix, projectId]);

  return { canExport, handleExportCsv, isExporting };
}
