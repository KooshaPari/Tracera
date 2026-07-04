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
  invertedIndex: Map<string, Set<string>>; // Term -> document IDs
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

export type ProgressCallback = (progress: number) => void;

const ZERO = 0;
const ONE = 1;
const TWO = 2;
const HALF = 0.5;
const ONE_HUNDRED = 100;
const MIN_TOKEN_LENGTH = 1;
const MIN_STEM_EXTRA = 2;
const DEFAULT_MAX_DISTANCE = 2;
const DEFAULT_RESULT_LIMIT = 100;
const DEFAULT_SUGGEST_LIMIT = 10;
const CHUNK_SIZE = 100;
const PROGRESS_TOKENIZED = 20;
const PROGRESS_MATCHED = 60;
const PROGRESS_SCORED = 80;
const PROGRESS_INTERVAL = 100;

type SearchTaskOptions = SearchOptions & { onProgress?: ProgressCallback };
interface AutoSuggestOptions {
  limit?: number;
  onProgress?: ProgressCallback;
}

/**
 * Simple tokenizer
 */
const tokenize = (text: string, caseSensitive = false): string[] => {
  const normalized = caseSensitive ? text : text.toLowerCase();
  // Split on non-alphanumeric characters
  const tokens = normalized.split(/[^a-z0-9]+/i).filter((token) => token.length > MIN_TOKEN_LENGTH);
  return tokens;
};

/**
 * Simple stemmer (removes common suffixes)
 */
const stem = (word: string): string => {
  // Very basic stemming - remove common English suffixes
  const suffixes = ['ing', 'ed', 'es', 's', 'er', 'est', 'ly'];

  for (const suffix of suffixes) {
    if (word.endsWith(suffix) && word.length > suffix.length + MIN_STEM_EXTRA) {
      return word.slice(0, -suffix.length);
    }
  }

  return word;
};

/**
 * Calculate Levenshtein distance (edit distance)
 */
const levenshteinDistance = (a: string, b: string): number => {
  const matrix: number[][] = Array.from({ length: b.length + ONE }, () =>
    Array.from({ length: a.length + ONE }, () => ZERO),
  );

  for (let i = ZERO; i <= b.length; i += ONE) {
    const row = matrix[i];
    if (!row) {
      continue;
    }
    row[ZERO] = i;
  }

  for (let j = ZERO; j <= a.length; j += ONE) {
    const firstRow = matrix[ZERO];
    if (!firstRow) {
      continue;
    }
    firstRow[j] = j;
  }

  for (let i = ONE; i <= b.length; i += ONE) {
    const row = matrix[i];
    const previousRow = matrix[i - ONE];
    if (!row || !previousRow) {
      continue;
    }
    for (let j = ONE; j <= a.length; j += ONE) {
      const currentLeft = row[j - ONE];
      const previousTop = previousRow[j];
      const previousDiag = previousRow[j - ONE];
      if (currentLeft === undefined || previousTop === undefined || previousDiag === undefined) {
        continue;
      }

      if (b.charAt(i - ONE) === a.charAt(j - ONE)) {
        row[j] = previousDiag;
      } else {
        row[j] = Math.min(
          previousDiag + ONE, // Substitution
          currentLeft + ONE, // Insertion
          previousTop + ONE, // Deletion
        );
      }
    }
  }

  const lastRow = matrix[b.length];
  if (!lastRow) {
    return ZERO;
  }
  const value = lastRow[a.length];
  if (value === undefined) {
    return ZERO;
  }
  return value;
};

const reportProgress = (onProgress: ProgressCallback | undefined, value: number): void => {
  if (onProgress) {
    onProgress(value);
  }
};

const calculatePercent = (current: number, total: number): number => {
  if (total <= ZERO) {
    return ONE_HUNDRED;
  }
  return (current / total) * ONE_HUNDRED;
};

const buildEmptyIndex = (fieldWeights: Record<string, number>): SearchIndex => ({
  documents: new Map(),
  fieldWeights,
  invertedIndex: new Map(),
});

const ensureTokenBucket = (index: SearchIndex, token: string): Set<string> => {
  const existing = index.invertedIndex.get(token);
  if (existing) {
    return existing;
  }
  const created = new Set<string>();
  index.invertedIndex.set(token, created);
  return created;
};

const indexDocumentFields = (index: SearchIndex, document: SearchDocument): void => {
  for (const [_field, value] of Object.entries(document.fields)) {
    if (typeof value !== 'string') {
      continue;
    }

    const tokens = tokenize(value, false);
    const stemmedTokens = tokens.map(stem);

    for (const token of stemmedTokens) {
      ensureTokenBucket(index, token).add(document.id);
    }
  }
};

const applyExactMatches = (
  docScores: Map<string, { score: number; matches: Record<string, string[]> }>,
  docIds: Set<string>,
): void => {
  for (const docId of docIds) {
    const current = docScores.get(docId);
    if (current) {
      current.score += ONE;
    } else {
      docScores.set(docId, { matches: {}, score: ONE });
    }
  }
};

const applyFuzzyMatches = (
  docScores: Map<string, { score: number; matches: Record<string, string[]> }>,
  index: SearchIndex,
  queryToken: string,
  maxDistance: number,
): void => {
  for (const [indexToken, docIds] of index.invertedIndex) {
    const distance = levenshteinDistance(queryToken, indexToken);
    if (distance <= ZERO || distance > maxDistance) {
      continue;
    }
    const score = ONE / (distance + ONE);
    for (const docId of docIds) {
      const current = docScores.get(docId);
      if (current) {
        current.score += score * HALF;
      } else {
        docScores.set(docId, { matches: {}, score: score * HALF });
      }
    }
  }
};

const applyFieldMatches = (
  docScores: Map<string, { score: number; matches: Record<string, string[]> }>,
  index: SearchIndex,
  query: string,
  caseSensitive: boolean,
  fields?: string[],
): void => {
  for (const [docId, scoreData] of docScores) {
    const doc = index.documents.get(docId);
    if (!doc) {
      continue;
    }

    for (const [field, value] of Object.entries(doc.fields)) {
      if (typeof value !== 'string') {
        continue;
      }
      if (fields && !fields.includes(field)) {
        continue;
      }

      const fieldText = caseSensitive ? value : value.toLowerCase();
      const normalizedQuery = caseSensitive ? query : query.toLowerCase();

      if (!fieldText.includes(normalizedQuery)) {
        continue;
      }

      const weight = index.fieldWeights[field] ?? ONE;
      scoreData.score += TWO * weight;

      scoreData.matches[field] ??= [];
      scoreData.matches[field].push(normalizedQuery);
    }
  }
};

const buildResults = (
  docScores: Map<string, { score: number; matches: Record<string, string[]> }>,
  limit: number,
): SearchResult[] =>
  [...docScores.entries()]
    .map(([id, { score, matches }]) => ({ id, matches, score }))
    .toSorted((a, b) => b.score - a.score)
    .slice(ZERO, limit);

/**
 * Build search index from documents
 */
const buildIndex = (
  documents: SearchDocument[],
  fieldWeights: Record<string, number> = {},
  onProgress?: ProgressCallback,
): SearchIndex => {
  reportProgress(onProgress, ZERO);

  const index = buildEmptyIndex(fieldWeights);

  for (let i = ZERO; i < documents.length; i += CHUNK_SIZE) {
    const chunkEnd = Math.min(i + CHUNK_SIZE, documents.length);
    const chunk = documents.slice(i, chunkEnd);

    for (const doc of chunk) {
      index.documents.set(doc.id, doc);
      indexDocumentFields(index, doc);
    }

    reportProgress(onProgress, calculatePercent(chunkEnd, documents.length));
  }

  reportProgress(onProgress, ONE_HUNDRED);
  return index;
};

/**
 * Search the index
 */
const search = (
  index: SearchIndex,
  query: string,
  options: SearchTaskOptions = {},
): SearchResult[] => {
  const { onProgress } = options;
  reportProgress(onProgress, ZERO);

  const fuzzy = options.fuzzy ?? false;
  const maxDistance = options.maxDistance ?? DEFAULT_MAX_DISTANCE;
  const { fields } = options;
  const limit = options.limit ?? DEFAULT_RESULT_LIMIT;
  const caseSensitive = options.caseSensitive ?? false;

  // Tokenize and stem query
  const queryTokens = tokenize(query, caseSensitive).map(stem);

  reportProgress(onProgress, PROGRESS_TOKENIZED);

  // Find matching documents
  const docScores = new Map<string, { score: number; matches: Record<string, string[]> }>();

  for (const queryToken of queryTokens) {
    const exactMatches = index.invertedIndex.get(queryToken);
    if (exactMatches) {
      applyExactMatches(docScores, exactMatches);
    }

    if (fuzzy) {
      applyFuzzyMatches(docScores, index, queryToken, maxDistance);
    }
  }

  reportProgress(onProgress, PROGRESS_MATCHED);

  applyFieldMatches(docScores, index, query, caseSensitive, fields);
  reportProgress(onProgress, PROGRESS_SCORED);

  const results = buildResults(docScores, limit);
  reportProgress(onProgress, ONE_HUNDRED);
  return results;
};

/**
 * Update index with new documents
 */
const removeDocumentFromIndex = (index: SearchIndex, docId: string): void => {
  index.documents.delete(docId);

  for (const [term, docIds] of index.invertedIndex) {
    docIds.delete(docId);
    if (docIds.size === ZERO) {
      index.invertedIndex.delete(term);
    }
  }
};

const addDocumentToIndex = (index: SearchIndex, document: SearchDocument): void => {
  index.documents.set(document.id, document);
  indexDocumentFields(index, document);
};

const updateIndex = (
  index: SearchIndex,
  updates: {
    id: string;
    action: 'add' | 'remove';
    document?: SearchDocument;
  }[],
  onProgress?: ProgressCallback,
): SearchIndex => {
  reportProgress(onProgress, ZERO);

  const updatedIndex = {
    documents: new Map(index.documents),
    fieldWeights: index.fieldWeights,
    invertedIndex: new Map(index.invertedIndex),
  };

  for (let i = ZERO; i < updates.length; i += ONE) {
    const update = updates[i];
    if (!update) {
      continue;
    }

    if (update.action === 'remove') {
      removeDocumentFromIndex(updatedIndex, update.id);
    } else if (update.action === 'add' && update.document) {
      addDocumentToIndex(updatedIndex, update.document);
    }

    reportProgress(onProgress, calculatePercent(i + ONE, updates.length));
  }

  reportProgress(onProgress, ONE_HUNDRED);
  return updatedIndex;
};

/**
 * Get index statistics
 */
const getIndexStats = (
  index: SearchIndex,
): {
  documentCount: number;
  termCount: number;
  avgTermsPerDocument: number;
} => {
  const documentCount = index.documents.size;
  const termCount = index.invertedIndex.size;

  let totalTerms = ZERO;
  for (const docIds of index.invertedIndex.values()) {
    totalTerms += docIds.size;
  }

  const avgTermsPerDocument = documentCount > ZERO ? totalTerms / documentCount : ZERO;

  return {
    avgTermsPerDocument,
    documentCount,
    termCount,
  };
};

/**
 * Auto-suggest/autocomplete
 */
const autoSuggest = (
  index: SearchIndex,
  prefix: string,
  options: AutoSuggestOptions = {},
): string[] => {
  const { limit = DEFAULT_SUGGEST_LIMIT, onProgress } = options;
  reportProgress(onProgress, ZERO);

  const normalizedPrefix = prefix.toLowerCase();
  const suggestions = new Set<string>();

  let processed = ZERO;
  const total = index.invertedIndex.size;

  for (const term of index.invertedIndex.keys()) {
    if (term.startsWith(normalizedPrefix)) {
      suggestions.add(term);

      if (suggestions.size >= limit) {
        break;
      }
    }

    processed += ONE;
    if (processed % PROGRESS_INTERVAL === ZERO) {
      reportProgress(onProgress, calculatePercent(processed, total));
    }
  }

  reportProgress(onProgress, ONE_HUNDRED);
  return [...suggestions].slice(ZERO, limit);
};

// Worker API
const api = {
  autoSuggest,
  buildIndex,
  getIndexStats,
  levenshteinDistance,
  search,
  stem,
  tokenize,
  updateIndex,
};

expose(api);

export type SearchIndexWorkerAPI = typeof api;
