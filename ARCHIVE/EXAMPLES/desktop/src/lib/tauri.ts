import { invoke } from '@tauri-apps/api/core';

export interface SyncStatus {
  is_syncing: boolean;
  last_sync: string | null;
  sync_error: string | null;
  pending_changes: number;
  online: boolean;
}

export interface AppInfo {
  version: string;
  platform: string;
  arch: string;
}

// Command wrappers for type safety

export async function syncData(): Promise<void> {
  return invoke('sync_data');
}

export async function getSyncStatus(): Promise<SyncStatus> {
  return invoke('get_sync_status');
}

export async function forceSync(): Promise<void> {
  return invoke('force_sync');
}

export async function getLocalData(key: string): Promise<any> {
  return invoke('get_local_data', { key });
}

export async function saveLocalData(key: string, value: any): Promise<void> {
  return invoke('save_local_data', { key, value });
}

export async function clearCache(): Promise<void> {
  return invoke('clear_cache');
}

export async function getAppInfo(): Promise<AppInfo> {
  return invoke('get_app_info');
}
