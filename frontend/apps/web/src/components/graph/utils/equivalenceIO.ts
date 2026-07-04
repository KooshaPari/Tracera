// EquivalenceIO.ts - Serialization, validation, and conversion utilities for equivalence data
// Handles import/export of equivalence mappings and canonical concepts with format conversion

import { z } from 'zod';

import type {
  CanonicalConcept,
  CanonicalProjection,
  EquivalenceLink,
  EquivalenceLinkType,
  EquivalenceStrategy,
} from '@tracertm/types';

import { logger } from '@/lib/logger';

// =============================================================================
// VALIDATION SCHEMAS
// =============================================================================

/**
 * Schema for equivalence evidence validation
 */
const EquivalenceEvidenceSchema = z.object({
  confidence: z.number().min(0).max(1),
  details: z.string(),
  detectedAt: z.string(),
  metadata: z.record(z.string(), z.unknown()).optional(),
  strategy: z.enum([
    'explicit_annotation',
    'manual_link',
    'api_contract',
    'shared_canonical',
    'naming_pattern',
    'semantic_similarity',
    'structural',
    'temporal',
    'co_occurrence',
  ]) as z.ZodType<EquivalenceStrategy>,
});

/**
 * Schema for equivalence link validation
 */
const EquivalenceLinkSchema = z.object({
  canonicalId: z.string().optional(),
  confidence: z.number().min(0).max(1),
  confirmedAt: z.string().optional(),
  confirmedBy: z.string().optional(),
  createdAt: z.string(),
  equivalenceType: z.enum([
    'same_as',
    'represents',
    'manifests_as',
    'derived_from',
    'alternative_to',
  ]) as z.ZodType<EquivalenceLinkType>,
  id: z.string(),
  projectId: z.string(),
  rejectedReason: z.string().optional(),
  sourceItemId: z.string(),
  status: z.enum(['suggested', 'confirmed', 'rejected', 'auto_confirmed']),
  strategies: z.array(EquivalenceEvidenceSchema),
  targetItemId: z.string(),
  updatedAt: z.string(),
});

/**
 * Schema for canonical concept validation
 */
const CanonicalConceptSchema = z.object({
  category: z.string().optional(),
  childConceptIds: z.array(z.string()).optional(),
  confidence: z.number().min(0).max(1),
  createdAt: z.string(),
  createdBy: z.string().optional(),
  description: z.string().optional(),
  domain: z.string(),
  embedding: z.array(z.number()).optional(),
  embeddingModel: z.string().optional(),
  embeddingUpdatedAt: z.string().optional(),
  id: z.string(),
  name: z.string().min(1).max(255),
  parentConceptId: z.string().optional(),
  projectId: z.string(),
  projectionCount: z.number().min(0),
  projectionIds: z.array(z.string()).optional(),
  relatedConceptIds: z.array(z.string()).optional(),
  slug: z.string().min(1).max(255),
  source: z.enum(['manual', 'inferred', 'imported']),
  tags: z.array(z.string()).optional(),
  updatedAt: z.string(),
  version: z.number().min(1),
});

/**
 * Schema for canonical projection validation
 */
const CanonicalProjectionSchema = z.object({
  canonicalId: z.string(),
  confidence: z.number().min(0).max(1),
  confirmedAt: z.string().optional(),
  confirmedBy: z.string().optional(),
  createdAt: z.string(),
  id: z.string(),
  isConfirmed: z.boolean(),
  isRejected: z.boolean(),
  itemId: z.string(),
  metadata: z.record(z.string(), z.unknown()).optional(),
  perspective: z.string(),
  projectId: z.string(),
  strategy: z.enum([
    'explicit_annotation',
    'manual_link',
    'api_contract',
    'shared_canonical',
    'naming_pattern',
    'semantic_similarity',
    'structural',
    'temporal',
    'co_occurrence',
  ]) as z.ZodType<EquivalenceStrategy>,
  updatedAt: z.string(),
});

/**
 * Schema for complete equivalence export package
 */
const EquivalenceExportPackageSchema = z.object({
  canonicalConcepts: z.array(CanonicalConceptSchema),
  canonicalProjections: z.array(CanonicalProjectionSchema),
  equivalenceLinks: z.array(EquivalenceLinkSchema),
  exportedAt: z.string(),
  exportedBy: z.string().optional(),
  metadata: z
    .object({
      confidence: z.object({
        average: z.number(),
        max: z.number(),
        min: z.number(),
      }),
      totalConcepts: z.number(),
      totalLinks: z.number(),
      totalProjections: z.number(),
    })
    .optional(),
  projectId: z.string(),
  version: z.literal('1.0'),
});

/**
 * Schema for import request with options
 */
const EquivalenceImportOptionsSchema = z.object({
  conflictResolution: z.enum(['skip', 'overwrite', 'merge_metadata']).default('skip'),
  mode: z.enum(['replace', 'merge']).default('merge'),
  preserveTimestamps: z.boolean().default(false),
  targetProjectId: z.string().optional(),
  updateProjectId: z.boolean().default(true),
  validateReferences: z.boolean().default(true),
});

export type EquivalenceImportOptions = z.infer<typeof EquivalenceImportOptionsSchema>;
export interface EquivalenceExportPackage {
  version: '1.0';
  exportedAt: string;
  projectId: string;
  exportedBy?: string | undefined;
  metadata?:
    | {
        totalLinks: number;
        totalConcepts: number;
        totalProjections: number;
        confidence?:
          | {
              min: number;
              max: number;
              average: number;
            }
          | undefined;
      }
    | undefined;
  equivalenceLinks: EquivalenceLink[];
  canonicalConcepts: CanonicalConcept[];
  canonicalProjections: CanonicalProjection[];
}

// =============================================================================
// SERIALIZATION / DESERIALIZATION
// =============================================================================

/**
 * Serialize equivalence data to JSON string
 */
export function serializeToJSON(data: EquivalenceExportPackage): string {
  return JSON.stringify(data, null, 2);
}

/**
 * Deserialize JSON string to equivalence data
 */
export function deserializeFromJSON(json: string): EquivalenceExportPackage {
  const parsed = JSON.parse(json);
  return EquivalenceExportPackageSchema.parse(parsed);
}

/**
 * Convert equivalence data to CSV format
 * Returns: { linksCSV: string, conceptsCSV: string, projectionsCSV: string }
 */
export function serializeToCSV(data: EquivalenceExportPackage): {
  links: string;
  concepts: string;
  projections: string;
} {
  const linksCSV = serializeLinksToCSV(data.equivalenceLinks);
  const conceptsCSV = serializeConceptsToCSV(data.canonicalConcepts);
  const projectionsCSV = serializeProjectionsToCSV(data.canonicalProjections);

  return {
    concepts: conceptsCSV,
    links: linksCSV,
    projections: projectionsCSV,
  };
}

/**
 * Convert CSV string back to equivalence links
 */
export function deserializeLinksFromCSV(csv: string): EquivalenceLink[] {
  const lines = csv.trim().split('\n');
  if (lines.length < 2) {
    return [];
  }

  const headerLine = lines[0];
  if (!headerLine) return [];
  const header = headerLine.split(',');
  const links: EquivalenceLink[] = [];

  for (let i = 1; i < lines.length; i += 1) {
    const line = lines[i];
    if (line === undefined) {
      continue;
    }
    const values = parseCSVLine(line);
    if (values.length !== header.length) {
      continue;
    }

    const record: Record<string, string> = {};
    header.forEach((key, idx) => {
      record[key] = values[idx] ?? '';
    });

    try {
      const link: EquivalenceLink = {
        canonicalId: record['canonicalId'] ?? '',
        confidence: Number.parseFloat(record['confidence'] ?? '0'),
        confirmedAt: record['confirmedAt'] ?? '',
        confirmedBy: record['confirmedBy'] ?? '',
        createdAt: record['createdAt'] ?? '',
        equivalenceType: record['equivalenceType'] as EquivalenceLinkType,
        id: record['id'] ?? '',
        projectId: record['projectId'] ?? '',
        rejectedReason: record['rejectedReason'] ?? '',
        sourceItemId: record['sourceItemId'] ?? '',
        status: record['status'] as 'suggested' | 'confirmed' | 'rejected' | 'auto_confirmed',
        strategies: JSON.parse(record['strategies'] ?? '[]'),
        targetItemId: record['targetItemId'] ?? '',
        updatedAt: record['updatedAt'] ?? '',
      };
      EquivalenceLinkSchema.parse(link);
      links.push(link);
    } catch (error) {
      logger.warn(`Failed to parse CSV line ${i}:`, error);
    }
  }

  return links;
}

/**
 * Convert CSV string back to canonical concepts
 */
export function deserializeConceptsFromCSV(csv: string): CanonicalConcept[] {
  const lines = csv.trim().split('\n');
  if (lines.length < 2) {
    return [];
  }

  const headerLine = lines[0];
  if (!headerLine) return [];
  const header = headerLine.split(',');
  const concepts: CanonicalConcept[] = [];

  for (let i = 1; i < lines.length; i += 1) {
    const line = lines[i];
    if (line === undefined) {
      continue;
    }
    const values = parseCSVLine(line);
    if (values.length !== header.length) {
      continue;
    }

    const record: Record<string, string> = {};
    header.forEach((key, idx) => {
      record[key] = values[idx] ?? '';
    });

    try {
      const concept: CanonicalConcept = {
        category: record['category'],
        childConceptIds: record['childConceptIds']
          ? record['childConceptIds'].split('|')
          : undefined,
        confidence: Number.parseFloat(record['confidence'] ?? '0'),
        createdAt: record['createdAt'] ?? '',
        createdBy: record['createdBy'],
        description: record['description'],
        domain: record['domain'] ?? '',
        embedding: record['embedding'] ? JSON.parse(record['embedding']) : undefined,
        embeddingModel: record['embeddingModel'],
        embeddingUpdatedAt: record['embeddingUpdatedAt'],
        id: record['id'] ?? '',
        name: record['name'] ?? '',
        parentConceptId: record['parentConceptId'],
        projectId: record['projectId'] ?? '',
        projectionCount: Number.parseInt(record['projectionCount'] ?? '0', 10),
        projectionIds: record['projectionIds'] ? record['projectionIds'].split('|') : undefined,
        relatedConceptIds: record['relatedConceptIds']
          ? record['relatedConceptIds'].split('|')
          : undefined,
        slug: record['slug'] ?? '',
        source: record['source'] as 'manual' | 'inferred' | 'imported',
        tags: record['tags'] ? record['tags'].split('|') : undefined,
        updatedAt: record['updatedAt'] ?? '',
        version: Number.parseInt(record['version'] ?? '0', 10),
      };
      CanonicalConceptSchema.parse(concept);
      concepts.push(concept);
    } catch (error) {
      logger.warn(`Failed to parse CSV line ${i}:`, error);
    }
  }

  return concepts;
}

/**
 * Convert CSV string back to canonical projections
 */
export function deserializeProjectionsFromCSV(csv: string): CanonicalProjection[] {
  const lines = csv.trim().split('\n');
  if (lines.length < 2) {
    return [];
  }

  const headerLine = lines[0];
  if (!headerLine) return [];
  const header = headerLine.split(',');
  const projections: CanonicalProjection[] = [];

  for (let i = 1; i < lines.length; i += 1) {
    const line = lines[i];
    if (line === undefined) {
      continue;
    }
    const values = parseCSVLine(line);
    if (values.length !== header.length) {
      continue;
    }

    const record: Record<string, string> = {};
    header.forEach((key, idx) => {
      record[key] = values[idx] ?? '';
    });

    try {
      const projection: CanonicalProjection = {
        canonicalId: record['canonicalId'] ?? '',
        confidence: Number.parseFloat(record['confidence'] ?? '0'),
        confirmedAt: record['confirmedAt'],
        confirmedBy: record['confirmedBy'],
        createdAt: record['createdAt'] ?? '',
        id: record['id'] ?? '',
        isConfirmed: record['isConfirmed'] === 'true',
        isRejected: record['isRejected'] === 'true',
        itemId: record['itemId'] ?? '',
        metadata: record['metadata'] ? JSON.parse(record['metadata']) : undefined,
        perspective: record['perspective'] ?? '',
        projectId: record['projectId'] ?? '',
        strategy: record['strategy'] as EquivalenceStrategy,
        updatedAt: record['updatedAt'] ?? '',
      };
      CanonicalProjectionSchema.parse(projection);
      projections.push(projection);
    } catch (error) {
      logger.warn(`Failed to parse CSV line ${i}:`, error);
    }
  }

  return projections;
}

// =============================================================================
// FORMAT CONVERSION HELPERS
// =============================================================================

/**
 * Convert equivalence links to CSV format
 */
function serializeLinksToCSV(links: EquivalenceLink[]): string {
  const headers = [
    'id',
    'projectId',
    'sourceItemId',
    'targetItemId',
    'equivalenceType',
    'confidence',
    'strategies',
    'canonicalId',
    'status',
    'confirmedBy',
    'confirmedAt',
    'rejectedReason',
    'createdAt',
    'updatedAt',
  ];

  const rows = links.map((link) => [
    link.id,
    link.projectId,
    link.sourceItemId,
    link.targetItemId,
    link.equivalenceType,
    link.confidence.toString(),
    JSON.stringify(link.strategies),
    link.canonicalId ?? '',
    link.status,
    link.confirmedBy ?? '',
    link.confirmedAt ?? '',
    link.rejectedReason ?? '',
    link.createdAt,
    link.updatedAt,
  ]);

  return formatAsCSV(headers, rows);
}

/**
 * Convert canonical concepts to CSV format
 */
function serializeConceptsToCSV(concepts: CanonicalConcept[]): string {
  const headers = [
    'id',
    'projectId',
    'name',
    'slug',
    'description',
    'domain',
    'category',
    'tags',
    'embedding',
    'embeddingModel',
    'embeddingUpdatedAt',
    'projectionCount',
    'projectionIds',
    'relatedConceptIds',
    'parentConceptId',
    'childConceptIds',
    'confidence',
    'source',
    'createdBy',
    'createdAt',
    'updatedAt',
    'version',
  ];

  const rows = concepts.map((concept) => [
    concept.id,
    concept.projectId,
    concept.name,
    concept.slug,
    concept.description ?? '',
    concept.domain,
    concept.category ?? '',
    concept.tags?.join('|') ?? '',
    concept.embedding ? JSON.stringify(concept.embedding) : '',
    concept.embeddingModel ?? '',
    concept.embeddingUpdatedAt ?? '',
    concept.projectionCount.toString(),
    concept.projectionIds?.join('|') ?? '',
    concept.relatedConceptIds?.join('|') ?? '',
    concept.parentConceptId ?? '',
    concept.childConceptIds?.join('|') ?? '',
    concept.confidence.toString(),
    concept.source,
    concept.createdBy ?? '',
    concept.createdAt,
    concept.updatedAt,
    concept.version.toString(),
  ]);

  return formatAsCSV(headers, rows);
}

/**
 * Convert canonical projections to CSV format
 */
function serializeProjectionsToCSV(projections: CanonicalProjection[]): string {
  const headers = [
    'id',
    'canonicalId',
    'itemId',
    'projectId',
    'perspective',
    'confidence',
    'strategy',
    'isConfirmed',
    'isRejected',
    'confirmedBy',
    'confirmedAt',
    'metadata',
    'createdAt',
    'updatedAt',
  ];

  const rows = projections.map((proj) => [
    proj.id,
    proj.canonicalId,
    proj.itemId,
    proj.projectId,
    proj.perspective,
    proj.confidence.toString(),
    proj.strategy,
    proj.isConfirmed.toString(),
    proj.isRejected.toString(),
    proj.confirmedBy ?? '',
    proj.confirmedAt ?? '',
    proj.metadata ? JSON.stringify(proj.metadata) : '',
    proj.createdAt,
    proj.updatedAt,
  ]);

  return formatAsCSV(headers, rows);
}

/**
 * Format headers and rows as CSV string
 */
function formatAsCSV(headers: string[], rows: string[][]): string {
  const csvHeaders = headers.map(escapeCSVField).join(',');
  const csvRows = rows.map((row) => row.map(escapeCSVField).join(',')).join('\n');
  return `${csvHeaders}\n${csvRows}`;
}

/**
 * Escape special characters in CSV field
 */
function escapeCSVField(field: string): string {
  if (!field) {
    return '""';
  }
  if (field.includes(',') || field.includes('"') || field.includes('\n')) {
    return `"${field.replaceAll('"', '""')}"`;
  }
  return field;
}

/**
 * Parse CSV line handling quoted fields
 */
function parseCSVLine(line: string): string[] {
  const result: string[] = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < line.length; i += 1) {
    const char = line[i];
    const nextChar = line[i + 1];

    if (char === '"') {
      if (inQuotes && nextChar === '"') {
        current += '"';
        i += 1;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (char === ',' && !inQuotes) {
      result.push(current);
      current = '';
    } else {
      current += char;
    }
  }

  result.push(current);
  return result;
}

// =============================================================================
// VALIDATION AND MERGING
// =============================================================================

/**
 * Validate entire export package
 */
export function validateExportPackage(data: unknown): {
  valid: boolean;
  errors: string[];
} {
  try {
    EquivalenceExportPackageSchema.parse(data);
    return { errors: [], valid: true };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return {
        errors: error.issues.map(
          (issue: z.ZodIssue) => `${issue.path.join('.')}: ${issue.message}`,
        ),
        valid: false,
      };
    }
    return { errors: ['Unknown validation error'], valid: false };
  }
}

/**
 * Validate import options
 */
export function validateImportOptions(options: unknown): {
  valid: boolean;
  errors: string[];
} {
  try {
    EquivalenceImportOptionsSchema.parse(options);
    return { errors: [], valid: true };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return {
        errors: error.issues.map(
          (issue: z.ZodIssue) => `${issue.path.join('.')}: ${issue.message}`,
        ),
        valid: false,
      };
    }
    return { errors: ['Unknown validation error'], valid: false };
  }
}

/**
 * Merge two equivalence export packages
 */
export function mergeExportPackages(
  existing: EquivalenceExportPackage,
  incoming: EquivalenceExportPackage,
  options: EquivalenceImportOptions,
): EquivalenceExportPackage {
  const merged = { ...existing };

  if (options.mode === 'replace') {
    merged.equivalenceLinks = incoming.equivalenceLinks;
    merged.canonicalConcepts = incoming.canonicalConcepts;
    merged.canonicalProjections = incoming.canonicalProjections;
  } else {
    // Merge mode
    const existingLinkIds = new Set(existing.equivalenceLinks.map((l) => l.id));
    const existingConceptIds = new Set(existing.canonicalConcepts.map((c) => c.id));
    const existingProjectionIds = new Set(existing.canonicalProjections.map((p) => p.id));

    // Merge links
    for (const incomingLink of incoming.equivalenceLinks) {
      if (existingLinkIds.has(incomingLink.id)) {
        if (options.conflictResolution === 'overwrite') {
          const idx = merged.equivalenceLinks.findIndex((l) => l.id === incomingLink.id);
          if (idx !== -1) {
            merged.equivalenceLinks[idx] = incomingLink;
          }
        }
        // Else skip
      } else {
        merged.equivalenceLinks.push(incomingLink);
      }
    }

    // Merge concepts
    for (const incomingConcept of incoming.canonicalConcepts) {
      if (existingConceptIds.has(incomingConcept.id)) {
        if (options.conflictResolution === 'overwrite') {
          const idx = merged.canonicalConcepts.findIndex((c) => c.id === incomingConcept.id);
          if (idx !== -1) {
            merged.canonicalConcepts[idx] = incomingConcept;
          }
        }
        // Else skip
      } else {
        merged.canonicalConcepts.push(incomingConcept);
      }
    }

    // Merge projections
    for (const incomingProjection of incoming.canonicalProjections) {
      if (existingProjectionIds.has(incomingProjection.id)) {
        if (options.conflictResolution === 'overwrite') {
          const idx = merged.canonicalProjections.findIndex((p) => p.id === incomingProjection.id);
          if (idx !== -1) {
            merged.canonicalProjections[idx] = incomingProjection;
          }
        }
        // Else skip
      } else {
        merged.canonicalProjections.push(incomingProjection);
      }
    }
  }

  // Update project ID if needed
  if (options.updateProjectId && options.targetProjectId) {
    merged.equivalenceLinks.forEach((l) => {
      l.projectId = options.targetProjectId!;
    });
    merged.canonicalConcepts.forEach((c) => {
      c.projectId = options.targetProjectId!;
    });
    merged.canonicalProjections.forEach((p) => {
      p.projectId = options.targetProjectId!;
    });
  }

  return merged;
}

/**
 * Create a summary of export package contents
 */
export function createExportSummary(data: EquivalenceExportPackage): {
  totalLinks: number;
  totalConcepts: number;
  totalProjections: number;
  confirmedCount: number;
  suggestedCount: number;
  rejectedCount: number;
  confidenceStats: {
    min: number;
    max: number;
    average: number;
  };
  domainBreakdown: Record<string, number>;
  strategyBreakdown: Record<string, number>;
} {
  const links = data.equivalenceLinks;
  const concepts = data.canonicalConcepts;
  const projections = data.canonicalProjections;

  const confirmedCount = links.filter(
    (l) => l.status === 'confirmed' || l.status === 'auto_confirmed',
  ).length;
  const suggestedCount = links.filter((l) => l.status === 'suggested').length;
  const rejectedCount = links.filter((l) => l.status === 'rejected').length;

  const confidences = links.map((l) => l.confidence);
  const domainBreakdown: Record<string, number> = {};
  const strategyBreakdown: Record<string, number> = {};

  concepts.forEach((c) => {
    domainBreakdown[c.domain] = (domainBreakdown[c.domain] ?? 0) + 1;
  });

  projections.forEach((p) => {
    strategyBreakdown[p.strategy] = (strategyBreakdown[p.strategy] ?? 0) + 1;
  });

  return {
    confidenceStats: {
      average:
        confidences.length > 0 ? confidences.reduce((a, b) => a + b) / confidences.length : 0,
      max: confidences.length > 0 ? Math.max(...confidences) : 0,
      min: confidences.length > 0 ? Math.min(...confidences) : 0,
    },
    confirmedCount,
    domainBreakdown,
    rejectedCount,
    strategyBreakdown,
    suggestedCount,
    totalConcepts: concepts.length,
    totalLinks: links.length,
    totalProjections: projections.length,
  };
}
