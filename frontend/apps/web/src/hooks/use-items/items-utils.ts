import {
  EMPTY_STRING,
  extractItemsArray,
  extractTotalCount,
  isRecord,
  normalizeBaseItem,
  normalizeCreateItemData,
  normalizeCreateItemWithSpecData,
  normalizeItem,
  readNonEmptyString,
} from '@/hooks/useItems/index';

export type { CreateItemData, CreateItemWithSpecData } from '@/hooks/useItems/index';

const itemsUtils = {
  EMPTY_STRING,
  extractItemsArray,
  extractTotalCount,
  isRecord,
  normalizeBaseItem,
  normalizeCreateItemData,
  normalizeCreateItemWithSpecData,
  normalizeItem,
  readNonEmptyString,
} as const;

export default itemsUtils;
