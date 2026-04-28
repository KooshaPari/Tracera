import type { ItemStatus, Priority } from '@tracertm/types';

const STATUS_VALUES: ItemStatus[] = ['todo', 'in_progress', 'done', 'blocked', 'cancelled'];
const PRIORITY_VALUES: Priority[] = ['low', 'medium', 'high', 'critical'];

const DEFAULT_VIEW = 'feature';
const DEFAULT_PRIORITY: Priority = 'medium';
const DEFAULT_STATUS: ItemStatus = 'todo';

const DEFAULT_TITLE = 'Item Registry';
const DEFAULT_EMPTY_TITLE = 'No items yet';
const DEFAULT_EMPTY_DESCRIPTION = 'Create your first item to get started.';
const DEFAULT_DESCRIPTION = 'Manage project items and artifacts in a unified registry.';
const DEFAULT_CREATE_LABEL = 'Create Item';
const DEFAULT_NEW_LABEL = 'New Item';

const ITEM_ID_PREFIX_LENGTH = 12;
const ROW_INDEX_OFFSET = 1;
const MAX_COL_INDEX = 5;
const LAST_INDEX_OFFSET = 1;
const KEYBOARD_PAGE_OFFSET = 5;
const VIRTUAL_ROW_HEIGHT = 68;
const VIRTUAL_OVERSCAN = 15;
const LOADING_OVERLAY_DELAY_MS = 250;
const LOADING_COMPLETE_DELAY_MS = 100;
const TABLE_MAX_INLINE = 200;
const TABLE_MIN_HEIGHT = 400;
const SEARCH_INPUT_MIN_WIDTH = 250;
const TABLE_HEADER_WIDTH = 400;
const LOADING_ROW_COUNT = 6;

const EMPTY_STRING = '';
const FILTER_ALL = 'all';
const SEARCH_PARAM_PROJECT = 'project';
const SEARCH_PARAM_TYPE = 'type';
const SEARCH_PARAM_ACTION = 'action';
const ACTION_CREATE = 'create';

const VIEW_TYPE_OPTIONS: string[] = ['requirement', 'feature', 'test', 'bug', 'task'];

const itemsTableConstants = {
  ACTION_CREATE,
  DEFAULT_CREATE_LABEL,
  DEFAULT_DESCRIPTION,
  DEFAULT_EMPTY_DESCRIPTION,
  DEFAULT_EMPTY_TITLE,
  DEFAULT_NEW_LABEL,
  DEFAULT_PRIORITY,
  DEFAULT_STATUS,
  DEFAULT_TITLE,
  DEFAULT_VIEW,
  EMPTY_STRING,
  FILTER_ALL,
  ITEM_ID_PREFIX_LENGTH,
  KEYBOARD_PAGE_OFFSET,
  LAST_INDEX_OFFSET,
  LOADING_COMPLETE_DELAY_MS,
  LOADING_OVERLAY_DELAY_MS,
  LOADING_ROW_COUNT,
  MAX_COL_INDEX,
  PRIORITY_VALUES,
  ROW_INDEX_OFFSET,
  SEARCH_INPUT_MIN_WIDTH,
  SEARCH_PARAM_ACTION,
  SEARCH_PARAM_PROJECT,
  SEARCH_PARAM_TYPE,
  STATUS_VALUES,
  TABLE_HEADER_WIDTH,
  TABLE_MAX_INLINE,
  TABLE_MIN_HEIGHT,
  VIRTUAL_OVERSCAN,
  VIRTUAL_ROW_HEIGHT,
  VIEW_TYPE_OPTIONS,
} as const;

export default itemsTableConstants;
