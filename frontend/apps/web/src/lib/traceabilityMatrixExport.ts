export interface MatrixExportItem {
  id: string;
  title: string;
}

export type MatrixCoverageMap = Record<string, Set<string>>;

export type CoverageStatus = 'covered' | 'partial' | 'uncovered';

export function getCoverageStatus(
  coveredCount: number,
  totalFeatures: number,
): CoverageStatus {
  if (totalFeatures === 0 || coveredCount === 0) {
    return 'uncovered';
  }
  if (coveredCount >= totalFeatures) {
    return 'covered';
  }
  return 'partial';
}

function escapeCsvCell(value: string): string {
  return `"${value.replace(/"/g, '""')}"`;
}

/** Build a CSV matching the on-screen requirements × features matrix. */
export function buildTraceabilityMatrixCsv(
  requirements: MatrixExportItem[],
  features: MatrixExportItem[],
  coverage: MatrixCoverageMap,
): string {
  const header = [
    'Requirement ID',
    'Requirement',
    'Coverage',
    ...features.map((f) => f.title),
  ];
  const lines = [header.map(escapeCsvCell).join(',')];

  for (const req of requirements) {
    const coveredCount = coverage[req.id]?.size ?? 0;
    const status = getCoverageStatus(coveredCount, features.length);
    const row = [
      req.id,
      req.title,
      status.toUpperCase(),
      ...features.map((feature) => (coverage[req.id]?.has(feature.id) ? 'linked' : '')),
    ];
    lines.push(row.map(escapeCsvCell).join(','));
  }

  lines.push('');
  lines.push(
    [
      escapeCsvCell('Summary'),
      escapeCsvCell(`${requirements.length} requirements`),
      escapeCsvCell(`${features.length} features`),
    ].join(','),
  );

  return lines.join('\n');
}

export function downloadTextFile(content: string, filename: string, mimeType: string): void {
  const blob = new Blob([content], { type: mimeType });
  const url = globalThis.URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.append(anchor);
  anchor.click();
  globalThis.URL.revokeObjectURL(url);
  anchor.remove();
}

export function downloadTraceabilityMatrixCsv(
  csv: string,
  projectId: string,
): void {
  const [day] = new Date().toISOString().split('T');
  const slug = projectId.slice(0, 8) || 'project';
  downloadTextFile(csv, `tracera-matrix-${slug}-${day}.csv`, 'text/csv;charset=utf-8');
}
