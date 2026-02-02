/**
 * Search Index Worker
 *
 * Handles CPU-intensive search operations:
 * - Full-text search index building
 * - Fuzzy matching
 * - Tokenization and stemming
 * - Search query processing
 */

import { expose } from 'comlink';

export interface SearchDocument {
  id: string;
  fields: Record<string, string | number | boolean>;
}

export interface SearchIndex {
  documents: Map<string, SearchDocument>;
  invertedIndex: Map<string, Set<string>>; // term -> document IDs
  fieldWeights: Record<string, number>;
}

export interface SearchOptions {
  fuzzy?: boolean;
  maxDistance?: number;
  fields?: string[];
  limit?: number;
  caseSensitive?: boolean;
}

export interface SearchResult {
  id: string;
  score: number;
  matches: Record<string, string[]>;
}

export interface ProgressCallback {
  (progress: number): void;
}

/**
 * Simple tokenizer
 */
function tokenize(text: string, caseSensitive = false): string[] {
  const normalized = caseSensitive ? text : text.toLowerCase();
  // Split on non-alphanumeric characters
  const tokens = normalized.split(/[^a-z0-9]+/i).filter(t => t.length > 0);
  return tokens;
}

/**
 * Simple stemmer (removes common suffixes)
 */
function stem(word: string): string {
  // Very basic stemming - remove common English suffixes
  const suffixes = ['ing', 'ed', 'es', 's', 'er', 'est', 'ly'];

  for (const suffix of suffixes) {
    if (word.endsWith(suffix) && word.length > suffix.length + 2) {
      return word.slice(0, -suffix.length);
    }
  }

  return word;
}

/**
 * Calculate Levenshtein distance (edit distance)
 */
function levenshteinDistance(a: string, b: string): number {
  const matrix: number[][] = [];

  for (let i = 0; i <= b.length; i++) {
    matrix[i] = [i];
  }

  for (let j = 0; j <= a.length; j++) {
    matrix[0][j] = j;
  }

  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      if (b.charAt(i - 1) === a.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1, // substitution
          matrix[i][j - 1] + 1,     // insertion
          matrix[i - 1][j] + 1,     // deletion
        );
      }
    }
  }

  return matrix[b.length][a.length];
}

/**
 * Build search index from documents
 */
function buildIndex(
  documents: SearchDocument[],
  fieldWeights: Record<string, number> = {},
  onProgress?: ProgressCallback,
): SearchIndex {
  onProgress?.(0);

  const index: SearchIndex = {
    documents: new Map(),
    invertedIndex: new Map(),
    fieldWeights: fieldWeights,
  };

  const chunkSize = 100;

  for (let i = 0; i < documents.length; i += chunkSize) {
    const chunk = documents.slice(i, Math.min(i + chunkSize, documents.length));

    for (const doc of chunk) {
      // Store document
      index.documents.set(doc.id, doc);

      // Index each field
      for (const [_field, value] of Object.entries(doc.fields)) {
        if (typeof value !== 'string') continue;

        const tokens = tokenize(value, false);
        const stemmedTokens = tokens.map(stem);

        // Add to inverted index
        for (const token of stemmedTokens) {
          if (!index.invertedIndex.has(token)) {
            index.invertedIndex.set(token, new Set());
          }
          index.invertedIndex.get(token)!.add(doc.id);
        }
      }
    }

    onProgress?.(((i + chunkSize) / documents.length) * 100);
  }

  onProgress?.(100);
  return index;
}

/**
 * Search the index
 */
function search(
  index: SearchIndex,
  query: string,
  options: SearchOptions = {},
  onProgress?: ProgressCallback,
): SearchResult[] {
  onProgress?.(0);

  const fuzzy = options.fuzzy ?? false;
  const maxDistance = options.maxDistance ?? 2;
  const fields = options.fields;
  const limit = options.limit ?? 100;
  const caseSensitive = options.caseSensitive ?? false;

  // Tokenize and stem query
  const queryTokens = tokenize(query, caseSensitive).map(stem);

  onProgress?.(20);

  // Find matching documents
  const docScores = new Map<string, { score: number; matches: Record<string, string[]> }>();

  for (const queryToken of queryTokens) {
    // Exact matches
    const exactMatches = index.invertedIndex.get(queryToken);
    if (exactMatches) {
      for (const docId of exactMatches) {
        if (!docScores.has(docId)) {
          docScores.set(docId, { score: 0, matches: {} });
        }
        docScores.get(docId)!.score += 1.0;
      }
    }

    // Fuzzy matches
    if (fuzzy) {
      for (const [indexToken, docIds] of index.invertedIndex) {
        const distance = levenshteinDistance(queryToken, indexToken);
        if (distance > 0 && distance <= maxDistance) {
          const score = 1.0 / (distance + 1);
          for (const docId of docIds) {
            if (!docScores.has(docId)) {
              docScores.set(docId, { score: 0, matches: {} });
            }
            docScores.get(docId)!.score += score * 0.5; // Fuzzy matches get half score
          }
        }
      }
    }
  }

  onProgress?.(60);

  // Calculate field-specific scores and collect matches
  for (const [docId, scoreData] of docScores) {
    const doc = index.documents.get(docId);
    if (!doc) continue;

    for (const [field, value] of Object.entries(doc.fields)) {
      if (typeof value !== 'string') continue;
      if (fields && !fields.includes(field)) continue;

      const fieldText = caseSensitive ? value : value.toLowerCase();
      const normalizedQuery = caseSensitive ? query : query.toLowerCase();

      // Check for query matches in this field
      if (fieldText.includes(normalizedQuery)) {
        const weight = index.fieldWeights[field] ?? 1.0;
        scoreData.score += 2.0 * weight; // Boost for phrase match

        if (!scoreData.matches[field]) {
          scoreData.matches[field] = [];
        }
        scoreData.matches[field].push(normalizedQuery);
      }
    }
  }

  onProgress?.(80);

  // Convert to results and sort by score
  const results: SearchResult[] = [...Array.from(docScores.entries())
    .map(([id, { score, matches }]) => ({ id, score, matches }))]
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);

  onProgress?.(100);
  return results;
}

/**
 * Update index with new documents
 */
function updateIndex(
  index: SearchIndex,
  updates: Array<{ id: string; action: 'add' | 'remove'; document?: SearchDocument }>,
  onProgress?: ProgressCallback,
): SearchIndex {
  onProgress?.(0);

  const updatedIndex = {
    documents: new Map(index.documents),
    invertedIndex: new Map(index.invertedIndex),
    fieldWeights: index.fieldWeights,
  };

  for (let i = 0; i < updates.length; i++) {
    const update = updates[i];

    if (update.action === 'remove') {
      // Remove from documents
      updatedIndex.documents.delete(update.id);

      // Remove from inverted index
      for (const [term, docIds] of updatedIndex.invertedIndex) {
        docIds.delete(update.id);
        if (docIds.size === 0) {
          updatedIndex.invertedIndex.delete(term);
        }
      }
    } else if (update.action === 'add' && update.document) {
      // Add/update document
      updatedIndex.documents.set(update.id, update.document);

      // Index fields
      for (const [_field, value] of Object.entries(update.document.fields)) {
        if (typeof value !== 'string') continue;

        const tokens = tokenize(value, false);
        const stemmedTokens = tokens.map(stem);

        for (const token of stemmedTokens) {
          if (!updatedIndex.invertedIndex.has(token)) {
            updatedIndex.invertedIndex.set(token, new Set());
          }
          updatedIndex.invertedIndex.get(token)!.add(update.id);
        }
      }
    }

    onProgress?.(((i + 1) / updates.length) * 100);
  }

  onProgress?.(100);
  return updatedIndex;
}

/**
 * Get index statistics
 */
function getIndexStats(index: SearchIndex): {
  documentCount: number;
  termCount: number;
  avgTermsPerDocument: number;
} {
  const documentCount = index.documents.size;
  const termCount = index.invertedIndex.size;

  let totalTerms = 0;
  for (const docIds of index.invertedIndex.values()) {
    totalTerms += docIds.size;
  }

  const avgTermsPerDocument = documentCount > 0 ? totalTerms / documentCount : 0;

  return {
    documentCount,
    termCount,
    avgTermsPerDocument,
  };
}

/**
 * Auto-suggest/autocomplete
 */
function autoSuggest(
  index: SearchIndex,
  prefix: string,
  limit = 10,
  onProgress?: ProgressCallback,
): string[] {
  onProgress?.(0);

  const normalizedPrefix = prefix.toLowerCase();
  const suggestions = new Set<string>();

  let processed = 0;
  const total = index.invertedIndex.size;

  for (const term of index.invertedIndex.keys()) {
    if (term.startsWith(normalizedPrefix)) {
      suggestions.add(term);

      if (suggestions.size >= limit) break;
    }

    processed++;
    if (processed % 100 === 0) {
      onProgress?.((processed / total) * 100);
    }
  }

  onProgress?.(100);
  return Array.from(suggestions).slice(0, limit);
}

// Worker API
const api = {
  buildIndex,
  search,
  updateIndex,
  getIndexStats,
  autoSuggest,
  tokenize,
  stem,
  levenshteinDistance,
};

expose(api);

export type SearchIndexWorkerAPI = typeof api;
