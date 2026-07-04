import type { Item, ItemStatus, Priority } from '@tracertm/types';

const EMPTY_STRING = '';

const STATUS_OPTIONS = ['todo', 'in_progress', 'blocked', 'done'] as const;
const PRIORITY_OPTIONS = ['critical', 'high', 'medium', 'low'] as const;

type StatusOption = (typeof STATUS_OPTIONS)[number];
type PriorityOption = (typeof PRIORITY_OPTIONS)[number];

interface DraftState {
  title: string;
  description: string;
  owner: string;
  status: ItemStatus;
  priority: Priority;
}

interface TimelineEvent {
  label: string;
  timestamp: string;
  detail?: string | undefined;
}

type DimensionEntry = readonly [label: string, value: unknown];

interface ItemLink {
  id: string;
  type: string;
  sourceId: string;
  targetId: string;
}

type ItemQueryState =
  | { kind: 'loading' }
  | { kind: 'not_found'; message?: string }
  | { kind: 'ready'; item: Item };

export {
  EMPTY_STRING,
  PRIORITY_OPTIONS,
  STATUS_OPTIONS,
  type DimensionEntry,
  type DraftState,
  type ItemLink,
  type ItemQueryState,
  type PriorityOption,
  type StatusOption,
  type TimelineEvent,
};
