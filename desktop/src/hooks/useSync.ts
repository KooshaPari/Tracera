import { useState, useEffect, useCallback } from 'react';
import { syncApi, SyncStatus } from '../lib/api';
import { listen } from '@tauri-apps/api/event';

export function useSync() {
  const [status, setStatus] = useState<SyncStatus>({
    is_syncing: false,
    pending_changes: 0,
    online: false,
  });
  const [error, setError] = useState<string | null>(null);

  const loadStatus = useCallback(async () => {
    try {
      const data = await syncApi.getStatus();
      setStatus(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get sync status');
      console.error('Failed to get sync status:', err);
    }
  }, []);

  useEffect(() => {
    loadStatus();

    // Listen for sync events
    const listeners = Promise.all([
      listen('sync-started', () => {
        setStatus(prev => ({ ...prev, is_syncing: true }));
      }),
      listen('sync-completed', (event: any) => {
        setStatus(event.payload);
        setError(null);
      }),
      listen('sync-error', (event: any) => {
        setError(event.payload);
        setStatus(prev => ({ ...prev, is_syncing: false }));
      }),
    ]);

    // Poll for status every 30 seconds
    const interval = setInterval(loadStatus, 30000);

    return () => {
      clearInterval(interval);
      listeners.then(fns => fns.forEach(fn => fn()));
    };
  }, [loadStatus]);

  const sync = useCallback(async () => {
    try {
      setError(null);
      await syncApi.forceSync();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sync failed');
      throw err;
    }
  }, []);

  return {
    status,
    error,
    sync,
    loadStatus,
  };
}
