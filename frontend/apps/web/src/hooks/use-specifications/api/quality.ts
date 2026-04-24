import { logger } from '@/lib/logger';

import { API_URL, getAuthHeaders, withFallback } from './base';
import { asNumber, asOptionalStringArray, asRecordArray, asString, toApiRecord } from './decoders';

interface QualityReport {
  id: string;
  itemId: string;
  smells: string[];
  ambiguityScore: number;
  completenessScore: number;
  suggestions: string[];
  lastAnalyzedAt: string;
  version: number;
  createdAt: string;
  updatedAt: string;
}

async function fetchQualityReports(projectId: string): Promise<QualityReport[]> {
  const authHeaders = getAuthHeaders();
  const itemsRes = await fetch(`${API_URL}/api/v1/items?project_id=${projectId}&limit=1000`, {
    headers: { 'X-Bulk-Operation': 'true', ...authHeaders },
  });
  if (!itemsRes.ok) {
    throw new Error(`Failed to fetch items: ${itemsRes.status}`);
  }

  const itemsData = toApiRecord(await itemsRes.json());
  const items = asRecordArray(itemsData['items'])
    .map((item) => asString(item['id']))
    .filter((itemId) => itemId.length > 0);

  const qualityPromises = items.map(async (itemId) => {
    try {
      const qualityRes = await fetch(`${API_URL}/api/v1/quality/items/${itemId}`, {
        headers: authHeaders,
      });
      if (qualityRes.ok) {
        const qualityData = toApiRecord(await qualityRes.json());
        return {
          ambiguityScore: asNumber(qualityData['ambiguity_score']),
          completenessScore: asNumber(qualityData['completeness_score']),
          createdAt: asString(qualityData['created_at']),
          id: asString(qualityData['id']),
          itemId: asString(qualityData['item_id']),
          lastAnalyzedAt: asString(qualityData['last_analyzed_at']),
          smells: withFallback(asOptionalStringArray(qualityData['smells']), []),
          suggestions: withFallback(asOptionalStringArray(qualityData['suggestions']), []),
          updatedAt: asString(qualityData['updated_at']),
          version: asNumber(qualityData['version']),
        };
      }
      return undefined;
    } catch (error) {
      logger.warn(`Failed to fetch quality for item ${itemId}:`, error);
      return undefined;
    }
  });

  const results = await Promise.all(qualityPromises);
  return results.filter((report): report is QualityReport => report !== undefined);
}

export { fetchQualityReports, type QualityReport };
