import type { CreateItemData, CreateItemWithSpecData } from './types';

import { normalizePriority, normalizeStatus } from './normalize-item';
import { readNonEmptyString } from './readers';

function normalizeCreateItemData(data: CreateItemData): CreateItemData {
  return {
    ...data,
    description: readNonEmptyString(data.description),
    owner: readNonEmptyString(data.owner),
    priority: normalizePriority(data.priority),
    status: normalizeStatus(data.status),
  };
}

function normalizeCreateItemWithSpecData(data: CreateItemWithSpecData): CreateItemWithSpecData {
  return {
    ...data,
    item: {
      ...data.item,
      description: readNonEmptyString(data.item.description),
      owner: readNonEmptyString(data.item.owner),
    },
  };
}

export { normalizeCreateItemData, normalizeCreateItemWithSpecData };
