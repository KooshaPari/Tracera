import {
  buildItemLink,
  buildTimelineEvents,
  createdAtLabel,
  defaultViewTypeFromParams,
  dimensionEntries,
  filterMetadata,
  formatValue,
  metadataEntries,
  readLinksFromResponse,
  readNonEmptyString,
  readStringParam,
  shortId,
  splitMetadata,
  updatedAtLabel,
} from './selectors';

const itemDetailSelectors = {
  buildItemLink,
  buildTimelineEvents,
  createdAtLabel,
  defaultViewTypeFromParams,
  dimensionEntries,
  filterMetadata,
  formatValue,
  metadataEntries,
  readLinksFromResponse,
  readNonEmptyString,
  readStringParam,
  shortId,
  splitMetadata,
  updatedAtLabel,
} as const;

export { itemDetailSelectors };

export type ItemDetailSelectors = typeof itemDetailSelectors;
