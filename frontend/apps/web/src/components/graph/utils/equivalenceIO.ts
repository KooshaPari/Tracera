// equivalenceIO.ts - Serialization, validation, and conversion utilities for equivalence data
// Handles import/export of equivalence mappings and canonical concepts with format conversion

import { z } from "zod";
import type {
	EquivalenceLink,
	EquivalenceLinkType,
	EquivalenceStrategy,
	EquivalenceEvidence,
	CanonicalConcept,
	CanonicalProjection,
} from "@tracertm/types";

// =============================================================================
// VALIDATION SCHEMAS
// =============================================================================

/**
 * Schema for equivalence evidence validation
 */
const EquivalenceEvidenceSchema = z.object({
	strategy: z.enum([
		"explicit_annotation",
		"manual_link",
		"api_contract",
		"shared_canonical",
		"naming_pattern",
		"semantic_similarity",
		"structural",
		"temporal",
		"co_occurrence",
	]) as z.ZodType<EquivalenceStrategy>,
	confidence: z.number().min(0).max(1),
	details: z.string(),
	detectedAt: z.string(),
	metadata: z.record(z.unknown()).optional(),
});

/**
 * Schema for equivalence link validation
 */
const EquivalenceLinkSchema = z.object({
	id: z.string(),
	projectId: z.string(),
	sourceItemId: z.string(),
	targetItemId: z.string(),
	equivalenceType: z.enum([
		"same_as",
		"represents",
		"manifests_as",
		"derived_from",
		"alternative_to",
	]) as z.ZodType<EquivalenceLinkType>,
	confidence: z.number().min(0).max(1),
	strategies: z.array(EquivalenceEvidenceSchema),
	canonicalId: z.string().optional(),
	status: z.enum(["suggested", "confirmed", "rejected", "auto_confirmed"]),
	confirmedBy: z.string().optional(),
	confirmedAt: z.string().optional(),
	rejectedReason: z.string().optional(),
	createdAt: z.string(),
	updatedAt: z.string(),
});

/**
 * Schema for canonical concept validation
 */
const CanonicalConceptSchema = z.object({
	id: z.string(),
	projectId: z.string(),
	name: z.string().min(1).max(255),
	slug: z.string().min(1).max(255),
	description: z.string().optional(),
	domain: z.string(),
	category: z.string().optional(),
	tags: z.array(z.string()).optional(),
	embedding: z.array(z.number()).optional(),
	embeddingModel: z.string().optional(),
	embeddingUpdatedAt: z.string().optional(),
	projectionCount: z.number().min(0),
	projectionIds: z.array(z.string()).optional(),
	relatedConceptIds: z.array(z.string()).optional(),
	parentConceptId: z.string().optional(),
	childConceptIds: z.array(z.string()).optional(),
	confidence: z.number().min(0).max(1),
	source: z.enum(["manual", "inferred", "imported"]),
	createdBy: z.string().optional(),
	createdAt: z.string(),
	updatedAt: z.string(),
	version: z.number().min(1),
});

/**
 * Schema for canonical projection validation
 */
const CanonicalProjectionSchema = z.object({
	id: z.string(),
	canonicalId: z.string(),
	itemId: z.string(),
	projectId: z.string(),
	perspective: z.string(),
	confidence: z.number().min(0).max(1),
	strategy: z.enum([
		"explicit_annotation",
		"manual_link",
		"api_contract",
		"shared_canonical",
		"naming_pattern",
		"semantic_similarity",
		"structural",
		"temporal",
		"co_occurrence",
	]) as z.ZodType<EquivalenceStrategy>,
	isConfirmed: z.boolean(),
	isRejected: z.boolean(),
	confirmedBy: z.string().optional(),
	confirmedAt: z.string().optional(),
	metadata: z.record(z.unknown()).optional(),
	createdAt: z.string(),
	updatedAt: z.string(),
});

/**
 * Schema for complete equivalence export package
 */
const EquivalenceExportPackageSchema = z.object({
	version: z.literal("1.0"),
	exportedAt: z.string(),
	projectId: z.string(),
	exportedBy: z.string().optional(),
	metadata: z
		.object({
			totalLinks: z.number(),
			totalConcepts: z.number(),
			totalProjections: z.number(),
			confidence: z.object({
				min: z.number(),
				max: z.number(),
				average: z.number(),
			}),
		})
		.optional(),
	equivalenceLinks: z.array(EquivalenceLinkSchema),
	canonicalConcepts: z.array(CanonicalConceptSchema),
	canonicalProjections: z.array(CanonicalProjectionSchema),
});

/**
 * Schema for import request with options
 */
const EquivalenceImportOptionsSchema = z.object({
	mode: z.enum(["replace", "merge"]).default("merge"),
	conflictResolution: z
		.enum(["skip", "overwrite", "merge_metadata"])
		.default("skip"),
	validateReferences: z.boolean().default(true),
	preserveTimestamps: z.boolean().default(false),
	updateProjectId: z.boolean().default(true),
	targetProjectId: z.string().optional(),
});

export type EquivalenceImportOptions = z.infer<
	typeof EquivalenceImportOptionsSchema
>;
export type EquivalenceExportPackage = {
	version: "1.0";
	exportedAt: string;
	projectId: string;
	exportedBy?: string;
	metadata?: {
		totalLinks: number;
		totalConcepts: number;
		totalProjections: number;
		confidence?: {
			min: number;
			max: number;
			average: number;
		};
	};
	equivalenceLinks: EquivalenceLink[];
	canonicalConcepts: CanonicalConcept[];
	canonicalProjections: CanonicalProjection[];
};

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
		links: linksCSV,
		concepts: conceptsCSV,
		projections: projectionsCSV,
	};
}

/**
 * Convert CSV string back to equivalence links
 */
export function deserializeLinksFromCSV(csv: string): EquivalenceLink[] {
	const lines = csv.trim().split("\n");
	if (lines.length < 2) return [];

	const header = lines[0].split(",");
	const links: EquivalenceLink[] = [];

	for (let i = 1; i < lines.length; i++) {
		const values = parseCSVLine(lines[i]);
		if (values.length !== header.length) continue;

		const record: Record<string, string> = {};
		header.forEach((key, idx) => {
			record[key] = values[idx];
		});

		try {
			const link: EquivalenceLink = {
				id: record["id"],
				projectId: record["projectId"],
				sourceItemId: record["sourceItemId"],
				targetItemId: record["targetItemId"],
				equivalenceType: record["equivalenceType"] as EquivalenceLinkType,
				confidence: parseFloat(record["confidence"]),
				strategies: JSON.parse(record["strategies"] || "[]"),
				canonicalId: record["canonicalId"],
				status: record["status"] as
					| "suggested"
					| "confirmed"
					| "rejected"
					| "auto_confirmed",
				confirmedBy: record["confirmedBy"],
				confirmedAt: record["confirmedAt"],
				rejectedReason: record["rejectedReason"],
				createdAt: record["createdAt"],
				updatedAt: record["updatedAt"],
			};
			EquivalenceLinkSchema.parse(link);
			links.push(link);
		} catch (error) {
			console.warn(`Failed to parse CSV line ${i}:`, error);
		}
	}

	return links;
}

/**
 * Convert CSV string back to canonical concepts
 */
export function deserializeConceptsFromCSV(csv: string): CanonicalConcept[] {
	const lines = csv.trim().split("\n");
	if (lines.length < 2) return [];

	const header = lines[0].split(",");
	const concepts: CanonicalConcept[] = [];

	for (let i = 1; i < lines.length; i++) {
		const values = parseCSVLine(lines[i]);
		if (values.length !== header.length) continue;

		const record: Record<string, string> = {};
		header.forEach((key, idx) => {
			record[key] = values[idx];
		});

		try {
			const concept: CanonicalConcept = {
				id: record["id"],
				projectId: record["projectId"],
				name: record["name"],
				slug: record["slug"],
				description: record["description"],
				domain: record["domain"],
				category: record["category"],
				tags: record["tags"] ? record["tags"].split("|") : undefined,
				embedding: record["embedding"]
					? JSON.parse(record["embedding"])
					: undefined,
				embeddingModel: record["embeddingModel"],
				embeddingUpdatedAt: record["embeddingUpdatedAt"],
				projectionCount: parseInt(record["projectionCount"], 10),
				projectionIds: record["projectionIds"]
					? record["projectionIds"].split("|")
					: undefined,
				relatedConceptIds: record["relatedConceptIds"]
					? record["relatedConceptIds"].split("|")
					: undefined,
				parentConceptId: record["parentConceptId"],
				childConceptIds: record["childConceptIds"]
					? record["childConceptIds"].split("|")
					: undefined,
				confidence: parseFloat(record["confidence"]),
				source: record["source"] as "manual" | "inferred" | "imported",
				createdBy: record["createdBy"],
				createdAt: record["createdAt"],
				updatedAt: record["updatedAt"],
				version: parseInt(record["version"], 10),
			};
			CanonicalConceptSchema.parse(concept);
			concepts.push(concept);
		} catch (error) {
			console.warn(`Failed to parse CSV line ${i}:`, error);
		}
	}

	return concepts;
}

/**
 * Convert CSV string back to canonical projections
 */
export function deserializeProjectionsFromCSV(
	csv: string,
): CanonicalProjection[] {
	const lines = csv.trim().split("\n");
	if (lines.length < 2) return [];

	const header = lines[0].split(",");
	const projections: CanonicalProjection[] = [];

	for (let i = 1; i < lines.length; i++) {
		const values = parseCSVLine(lines[i]);
		if (values.length !== header.length) continue;

		const record: Record<string, string> = {};
		header.forEach((key, idx) => {
			record[key] = values[idx];
		});

		try {
			const projection: CanonicalProjection = {
				id: record["id"],
				canonicalId: record["canonicalId"],
				itemId: record["itemId"],
				projectId: record["projectId"],
				perspective: record["perspective"],
				confidence: parseFloat(record["confidence"]),
				strategy: record["strategy"] as EquivalenceStrategy,
				isConfirmed: record["isConfirmed"] === "true",
				isRejected: record["isRejected"] === "true",
				confirmedBy: record["confirmedBy"],
				confirmedAt: record["confirmedAt"],
				metadata: record["metadata"]
					? JSON.parse(record["metadata"])
					: undefined,
				createdAt: record["createdAt"],
				updatedAt: record["updatedAt"],
			};
			CanonicalProjectionSchema.parse(projection);
			projections.push(projection);
		} catch (error) {
			console.warn(`Failed to parse CSV line ${i}:`, error);
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
		"id",
		"projectId",
		"sourceItemId",
		"targetItemId",
		"equivalenceType",
		"confidence",
		"strategies",
		"canonicalId",
		"status",
		"confirmedBy",
		"confirmedAt",
		"rejectedReason",
		"createdAt",
		"updatedAt",
	];

	const rows = links.map((link) => [
		link.id,
		link.projectId,
		link.sourceItemId,
		link.targetItemId,
		link.equivalenceType,
		link.confidence.toString(),
		JSON.stringify(link.strategies),
		link.canonicalId || "",
		link.status,
		link.confirmedBy || "",
		link.confirmedAt || "",
		link.rejectedReason || "",
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
		"id",
		"projectId",
		"name",
		"slug",
		"description",
		"domain",
		"category",
		"tags",
		"embedding",
		"embeddingModel",
		"embeddingUpdatedAt",
		"projectionCount",
		"projectionIds",
		"relatedConceptIds",
		"parentConceptId",
		"childConceptIds",
		"confidence",
		"source",
		"createdBy",
		"createdAt",
		"updatedAt",
		"version",
	];

	const rows = concepts.map((concept) => [
		concept.id,
		concept.projectId,
		concept.name,
		concept.slug,
		concept.description || "",
		concept.domain,
		concept.category || "",
		concept.tags?.join("|") || "",
		concept.embedding ? JSON.stringify(concept.embedding) : "",
		concept.embeddingModel || "",
		concept.embeddingUpdatedAt || "",
		concept.projectionCount.toString(),
		concept.projectionIds?.join("|") || "",
		concept.relatedConceptIds?.join("|") || "",
		concept.parentConceptId || "",
		concept.childConceptIds?.join("|") || "",
		concept.confidence.toString(),
		concept.source,
		concept.createdBy || "",
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
		"id",
		"canonicalId",
		"itemId",
		"projectId",
		"perspective",
		"confidence",
		"strategy",
		"isConfirmed",
		"isRejected",
		"confirmedBy",
		"confirmedAt",
		"metadata",
		"createdAt",
		"updatedAt",
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
		proj.confirmedBy || "",
		proj.confirmedAt || "",
		proj.metadata ? JSON.stringify(proj.metadata) : "",
		proj.createdAt,
		proj.updatedAt,
	]);

	return formatAsCSV(headers, rows);
}

/**
 * Format headers and rows as CSV string
 */
function formatAsCSV(headers: string[], rows: string[][]): string {
	const csvHeaders = headers.map(escapeCSVField).join(",");
	const csvRows = rows
		.map((row) => row.map(escapeCSVField).join(","))
		.join("\n");
	return csvHeaders + "\n" + csvRows;
}

/**
 * Escape special characters in CSV field
 */
function escapeCSVField(field: string): string {
	if (!field) return '""';
	if (field.includes(",") || field.includes('"') || field.includes("\n")) {
		return `"${field.replace(/"/g, '""')}"`;
	}
	return field;
}

/**
 * Parse CSV line handling quoted fields
 */
function parseCSVLine(line: string): string[] {
	const result: string[] = [];
	let current = "";
	let inQuotes = false;

	for (let i = 0; i < line.length; i++) {
		const char = line[i];
		const nextChar = line[i + 1];

		if (char === '"') {
			if (inQuotes && nextChar === '"') {
				current += '"';
				i++;
			} else {
				inQuotes = !inQuotes;
			}
		} else if (char === "," && !inQuotes) {
			result.push(current);
			current = "";
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
		return { valid: true, errors: [] };
	} catch (error) {
		if (error instanceof z.ZodError) {
			return {
				valid: false,
				errors: error.issues.map(
					(issue) => `${issue.path.join(".")}: ${issue.message}`,
				),
			};
		}
		return { valid: false, errors: ["Unknown validation error"] };
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
		return { valid: true, errors: [] };
	} catch (error) {
		if (error instanceof z.ZodError) {
			return {
				valid: false,
				errors: error.issues.map(
					(issue) => `${issue.path.join(".")}: ${issue.message}`,
				),
			};
		}
		return { valid: false, errors: ["Unknown validation error"] };
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

	if (options.mode === "replace") {
		merged.equivalenceLinks = incoming.equivalenceLinks;
		merged.canonicalConcepts = incoming.canonicalConcepts;
		merged.canonicalProjections = incoming.canonicalProjections;
	} else {
		// Merge mode
		const existingLinkIds = new Set(existing.equivalenceLinks.map((l) => l.id));
		const existingConceptIds = new Set(
			existing.canonicalConcepts.map((c) => c.id),
		);
		const existingProjectionIds = new Set(
			existing.canonicalProjections.map((p) => p.id),
		);

		// Merge links
		for (const incomingLink of incoming.equivalenceLinks) {
			if (existingLinkIds.has(incomingLink.id)) {
				if (options.conflictResolution === "overwrite") {
					const idx = merged.equivalenceLinks.findIndex(
						(l) => l.id === incomingLink.id,
					);
					if (idx >= 0) merged.equivalenceLinks[idx] = incomingLink;
				}
				// else skip
			} else {
				merged.equivalenceLinks.push(incomingLink);
			}
		}

		// Merge concepts
		for (const incomingConcept of incoming.canonicalConcepts) {
			if (existingConceptIds.has(incomingConcept.id)) {
				if (options.conflictResolution === "overwrite") {
					const idx = merged.canonicalConcepts.findIndex(
						(c) => c.id === incomingConcept.id,
					);
					if (idx >= 0) merged.canonicalConcepts[idx] = incomingConcept;
				}
				// else skip
			} else {
				merged.canonicalConcepts.push(incomingConcept);
			}
		}

		// Merge projections
		for (const incomingProjection of incoming.canonicalProjections) {
			if (existingProjectionIds.has(incomingProjection.id)) {
				if (options.conflictResolution === "overwrite") {
					const idx = merged.canonicalProjections.findIndex(
						(p) => p.id === incomingProjection.id,
					);
					if (idx >= 0) merged.canonicalProjections[idx] = incomingProjection;
				}
				// else skip
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
		(l) => l.status === "confirmed" || l.status === "auto_confirmed",
	).length;
	const suggestedCount = links.filter((l) => l.status === "suggested").length;
	const rejectedCount = links.filter((l) => l.status === "rejected").length;

	const confidences = [...links.map((l) => l.confidence)];
	const domainBreakdown: Record<string, number> = {};
	const strategyBreakdown: Record<string, number> = {};

	concepts.forEach((c) => {
		domainBreakdown[c.domain] = (domainBreakdown[c.domain] || 0) + 1;
	});

	projections.forEach((p) => {
		strategyBreakdown[p.strategy] = (strategyBreakdown[p.strategy] || 0) + 1;
	});

	return {
		totalLinks: links.length,
		totalConcepts: concepts.length,
		totalProjections: projections.length,
		confirmedCount,
		suggestedCount,
		rejectedCount,
		confidenceStats: {
			min: confidences.length ? Math.min(...confidences) : 0,
			max: confidences.length ? Math.max(...confidences) : 0,
			average:
				confidences.length > 0
					? confidences.reduce((a, b) => a + b) / confidences.length
					: 0,
		},
		domainBreakdown,
		strategyBreakdown,
	};
}
