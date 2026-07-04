// Compatibility layer: keep existing imports working while the implementation lives in `./normalization/*`.

export type { CreateItemData, CreateItemWithSpecData } from './normalization/types';
export { EMPTY_STRING } from './normalization/constants';
export {
  extractItemsArray,
  extractTotalCount,
  normalizeBaseItem,
  normalizeItem,
} from './normalization/normalize-item';
export {
  normalizeCreateItemData,
  normalizeCreateItemWithSpecData,
} from './normalization/create-normalize';
export { readNonEmptyString } from './normalization/readers';
