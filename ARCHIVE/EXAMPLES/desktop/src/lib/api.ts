import { invoke } from '@tauri-apps/api/core';

// Types matching Rust models
export interface Project {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  synced_at?: string;
  is_deleted: boolean;
}

export interface Item {
  id: string;
  project_id: string;
  item_type: ItemType;
  title: string;
  content: string;
  status: string;
  priority?: string;
  version: number;
  created_at: string;
  updated_at: string;
  synced_at?: string;
  is_deleted: boolean;
}

export type ItemType =
  | 'feature'
  | 'code'
  | 'test'
  | 'api'
  | 'database'
  | 'wireframe'
  | 'documentation'
  | 'deployment';

export interface Link {
  id: string;
  project_id: string;
  source_id: string;
  target_id: string;
  link_type: string;
  metadata?: string;
  created_at: string;
  is_deleted: boolean;
}

export interface SyncStatus {
  is_syncing: boolean;
  last_sync?: string;
  sync_error?: string;
  pending_changes: number;
  online: boolean;
}

export interface AppInfo {
  version: string;
  platform: string;
  arch: string;
}

// Project API
export const projectApi = {
  create: (name: string, description?: string): Promise<Project> =>
    invoke('create_project', { name, description }),

  get: (id: string): Promise<Project | null> =>
    invoke('get_project', { id }),

  list: (): Promise<Project[]> =>
    invoke('list_projects'),

  update: (project: Project): Promise<void> =>
    invoke('update_project', { project }),

  delete: (id: string): Promise<void> =>
    invoke('delete_project', { id }),
};

// Item API
export const itemApi = {
  create: (
    project_id: string,
    item_type: ItemType,
    title: string,
    content: string,
    status: string,
    priority?: string
  ): Promise<Item> =>
    invoke('create_item', { project_id, item_type, title, content, status, priority }),

  get: (id: string): Promise<Item | null> =>
    invoke('get_item', { id }),

  list: (project_id: string, item_type?: ItemType): Promise<Item[]> =>
    invoke('list_items', { project_id, item_type }),

  update: (item: Item): Promise<void> =>
    invoke('update_item', { item }),

  delete: (id: string): Promise<void> =>
    invoke('delete_item', { id }),
};

// Link API
export const linkApi = {
  create: (
    project_id: string,
    source_id: string,
    target_id: string,
    link_type: string,
    metadata?: string
  ): Promise<Link> =>
    invoke('create_link', { project_id, source_id, target_id, link_type, metadata }),

  list: (project_id: string): Promise<Link[]> =>
    invoke('list_links', { project_id }),

  delete: (id: string): Promise<void> =>
    invoke('delete_link', { id }),
};

// Sync API
export const syncApi = {
  sync: (): Promise<void> =>
    invoke('sync_data'),

  getStatus: (): Promise<SyncStatus> =>
    invoke('get_sync_status'),

  forceSync: (): Promise<void> =>
    invoke('force_sync'),

  getPendingCount: (): Promise<number> =>
    invoke('get_pending_sync_count'),
};

// Export API
export const exportApi = {
  json: (project_id: string, output_path: string): Promise<void> =>
    invoke('export_project_json', { project_id, output_path }),

  csv: (project_id: string, output_path: string): Promise<void> =>
    invoke('export_project_csv', { project_id, output_path }),

  traceabilityMatrix: (project_id: string, output_path: string): Promise<void> =>
    invoke('export_traceability_matrix', { project_id, output_path }),

  markdown: (project_id: string, output_path: string): Promise<void> =>
    invoke('export_project_markdown', { project_id, output_path }),
};

// Storage API
export const storageApi = {
  get: (key: string): Promise<any> =>
    invoke('get_local_data', { key }),

  save: (key: string, value: any): Promise<void> =>
    invoke('save_local_data', { key, value }),

  clear: (): Promise<void> =>
    invoke('clear_cache'),
};

// App API
export const appApi = {
  getInfo: (): Promise<AppInfo> =>
    invoke('get_app_info'),
};
