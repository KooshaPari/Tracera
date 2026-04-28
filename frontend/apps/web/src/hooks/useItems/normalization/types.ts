import type { Item, ItemStatus, Priority, ViewType } from '@tracertm/types';

interface CreateItemData {
  projectId: string;
  view: ViewType;
  type: string;
  title: string;
  description?: string | undefined;
  status: ItemStatus;
  priority: Priority;
  parentId?: string | undefined;
  owner?: string | undefined;
}

interface CreateItemWithSpecData {
  projectId: string;
  item: Partial<Item>;
  spec: Record<string, unknown>;
}

export type { CreateItemData, CreateItemWithSpecData };
