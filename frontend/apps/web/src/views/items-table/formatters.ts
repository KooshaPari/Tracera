import type { Priority, TypedItem, ViewType } from '@tracertm/types';

import itemsTableConstants from './constants';

function readString(value: unknown): string | undefined {
  if (typeof value === 'string') {
    return value;
  }
  return undefined;
}

function hasValue(value: string | undefined): boolean {
  if (value === undefined) {
    return false;
  }
  return value.trim() !== '';
}

function getViewSegment(view?: ViewType, fallback?: ViewType): string {
  if (view !== undefined) {
    return view.toLowerCase();
  }
  if (fallback !== undefined) {
    return fallback.toLowerCase();
  }
  return itemsTableConstants.DEFAULT_VIEW;
}

function getItemOwnerLabel(owner?: string): { label: string; initial: string } {
  if (owner !== undefined && owner.trim() !== '') {
    return { label: owner, initial: owner.charAt(0) };
  }
  return { label: 'Unassigned', initial: '?' };
}

function getPriorityLabel(priority?: Priority): string {
  if (priority !== undefined) {
    return priority;
  }
  return itemsTableConstants.DEFAULT_PRIORITY;
}

function getSearchValue(searchParams: Record<string, unknown>, key: string): string | undefined {
  const value = readString(searchParams[key]);
  if (value !== undefined && value.trim() !== '') {
    return value;
  }
  return undefined;
}

function createViewTypeValue(value: string | undefined): string {
  if (value !== undefined && value.trim() !== '') {
    return value;
  }
  return itemsTableConstants.FILTER_ALL;
}

function getFilterValue(value: string | undefined): string | undefined {
  if (value === undefined) {
    return undefined;
  }
  if (value === itemsTableConstants.FILTER_ALL) {
    return undefined;
  }
  return value;
}

function getItemTypeValue(type: string | undefined, view: ViewType | undefined): string {
  if (type !== undefined && type.trim() !== '') {
    return type;
  }
  if (view !== undefined) {
    return view;
  }
  return itemsTableConstants.DEFAULT_VIEW;
}

function getViewValue(view: ViewType | undefined): ViewType {
  if (view !== undefined) {
    return view;
  }
  return itemsTableConstants.DEFAULT_VIEW as ViewType;
}

function getSearchMessage(liveMessage: string, title: string): string {
  if (liveMessage.trim() !== '') {
    return liveMessage;
  }
  return `Loading ${title.toLowerCase()}...`;
}

function getLiveMessage(message: string): string {
  if (message.trim() !== '') {
    return message;
  }
  return 'Items loaded.';
}

function getSortDirection(
  sortColumn: string,
  sortOrder: 'asc' | 'desc',
  column: string,
): 'ascending' | 'descending' | 'none' {
  if (sortColumn !== column) {
    return 'none';
  }
  if (sortOrder === 'asc') {
    return 'ascending';
  }
  return 'descending';
}

function getSortAriaLabel(sortColumn: string, sortOrder: 'asc' | 'desc', column: string): string {
  if (sortColumn !== column) {
    return 'not sorted';
  }
  return `sorted ${sortOrder}`;
}

function getSortedItems(
  items: TypedItem[],
  effectiveTypeFilter: string | undefined,
  query: string,
  sortColumn: string,
  sortOrder: 'asc' | 'desc',
): TypedItem[] {
  const filtered = items.filter((item) => {
    let matchesType = true;
    const filterValue = getFilterValue(effectiveTypeFilter);
    if (filterValue !== undefined) {
      matchesType = item.type === filterValue;
    }

    let matchesQuery = true;
    if (query !== itemsTableConstants.EMPTY_STRING) {
      const titleMatch = item.title.toLowerCase().includes(query);
      const idMatch = item.id.toLowerCase().includes(query);
      matchesQuery = titleMatch || idMatch;
    }

    return matchesType && matchesQuery;
  });

  const direction = sortOrder === 'asc' ? 1 : -1;

  return filtered.toSorted((a, b) => {
    if (sortColumn === 'title') {
      return a.title.localeCompare(b.title) * direction;
    }
    if (sortColumn === 'created') {
      return (new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()) * direction;
    }
    return 0;
  });
}

const itemsTableFormatters = {
  createViewTypeValue,
  getFilterValue,
  getItemOwnerLabel,
  getItemTypeValue,
  getLiveMessage,
  getPriorityLabel,
  getSearchMessage,
  getSearchValue,
  getSortedItems,
  getSortAriaLabel,
  getSortDirection,
  getViewSegment,
  getViewValue,
  hasValue,
} as const;

export default itemsTableFormatters;
