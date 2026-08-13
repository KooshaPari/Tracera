interface TraceabilityExportItem {
  id: string;
  title: string;
}

interface TraceabilityCsvInput {
  requirements: TraceabilityExportItem[];
  features: TraceabilityExportItem[];
  linkedFeatureIdsByRequirement: Record<string, ReadonlySet<string> | undefined>;
}

function escapeCsvValue(value: string): string {
  const spreadsheetSafeValue = /^[=+\-@]/.test(value) ? `'${value}` : value;
  return /[",\r\n]/.test(spreadsheetSafeValue)
    ? `"${spreadsheetSafeValue.replaceAll('"', '""')}"`
    : spreadsheetSafeValue;
}

function coverageLabel(linkedCount: number, featureCount: number): string {
  if (linkedCount === 0 || featureCount === 0) {
    return "UNCOVERED";
  }
  if (linkedCount >= featureCount) {
    return `COVERED ${linkedCount}/${featureCount}`;
  }
  return `PARTIAL ${linkedCount}/${featureCount}`;
}

/** Build a matrix CSV from the same requirements, features, and links on screen. */
export function buildTraceabilityCsv({
  requirements,
  features,
  linkedFeatureIdsByRequirement,
}: TraceabilityCsvInput): string {
  const header = [
    "Requirement ID",
    "Requirement",
    "Coverage",
    ...features.map((feature) => `Feature: ${feature.title}`),
  ];
  const rows = requirements.map((requirement) => {
    const linkedFeatureIds = linkedFeatureIdsByRequirement[requirement.id] ?? new Set<string>();
    return [
      requirement.id,
      requirement.title,
      coverageLabel(linkedFeatureIds.size, features.length),
      ...features.map((feature) => (linkedFeatureIds.has(feature.id) ? "Linked" : "")),
    ];
  });

  return [header, ...rows].map((row) => row.map(escapeCsvValue).join(",")).join("\r\n");
}

/** Trigger a browser download for a CSV string and promptly release its object URL. */
export function downloadTraceabilityCsv(csv: string, filename: string): void {
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.download = filename;
  anchor.href = objectUrl;
  anchor.style.display = "none";
  document.body.appendChild(anchor);

  try {
    anchor.click();
  } finally {
    anchor.remove();
    URL.revokeObjectURL(objectUrl);
  }
}
