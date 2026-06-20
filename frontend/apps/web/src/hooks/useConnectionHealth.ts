import { useEffect, useRef } from 'react';

import type { ConnectionStatusState } from '@/stores/connection-status-store';

import { client } from '@/api/client';
import { useConnectionStatusStore } from '@/stores/connection-status-store';

const { apiClient } = client;

const POLL_INTERVAL_MS = 25_000;
const RETRY_ATTEMPTS = 3;
const RETRY_DELAY_MS = 2000;

/**
 * Background health polling for the important backend (Python API).
 * On failure: sets reconnecting, retries; after retries exhausted sets lost.
 * On success: sets online.
 * Also reacts to 5xx from API client (handled in client middleware).
 */
export function useConnectionHealth(): void {
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const setOnline = useConnectionStatusStore((s: ConnectionStatusState) => s.setOnline);
  const setLost = useConnectionStatusStore((s: ConnectionStatusState) => s.setLost);
  const setReconnecting = useConnectionStatusStore((s: ConnectionStatusState) => s.setReconnecting);
  const setConnecting = useConnectionStatusStore((s: ConnectionStatusState) => s.setConnecting);

  useEffect(() => {
    let cancelled = false;
    let hasEverConnected = false;

    async function poll(): Promise<void> {
      try {
        if (!hasEverConnected) {
          setConnecting('Connecting…');
        }
        const { response, error, data } = await apiClient.GET('/api/v1/health', {});
        if (cancelled) {
          return;
        }
        const unhealthy =
          error !== undefined ||
          !response?.ok ||
          (data as { status?: string })?.status === 'unhealthy';
        if (unhealthy) {
          if (!hasEverConnected) {
            setConnecting('Still waiting for backend…');
          } else {
            setReconnecting('Reconnecting…');
          }
          for (let i = 0; i < RETRY_ATTEMPTS && !cancelled; i += 1) {
            await new Promise((r) => setTimeout(r, RETRY_DELAY_MS));
            const retry = await apiClient.GET('/api/v1/health', {});
            if (cancelled) {
              return;
            }
            const retryOk =
              !retry.error &&
              retry.response?.ok &&
              !((retry.data as { status?: string }).status === 'unhealthy');
            if (retryOk) {
              setOnline();
              hasEverConnected = true;
              return;
            }
          }
          setLost(hasEverConnected ? 'Connection to backend lost' : 'Backend unavailable');
          return;
        }
        setOnline();
        hasEverConnected = true;
      } catch {
        if (cancelled) {
          return;
        }
        if (!hasEverConnected) {
          setConnecting('Still waiting for backend…');
        } else {
          setReconnecting('Reconnecting…');
        }
        for (let i = 0; i < RETRY_ATTEMPTS && !cancelled; i += 1) {
          await new Promise((r) => setTimeout(r, RETRY_DELAY_MS));
          try {
            const retry = await apiClient.GET('/api/v1/health', {});
            if (cancelled) {
              return;
            }
            const retryOk =
              !retry.error &&
              retry.response?.ok &&
              !((retry.data as { status?: string }).status === 'unhealthy');
            if (retryOk) {
              setOnline();
              hasEverConnected = true;
              return;
            }
          } catch {
            // Continue retries
          }
        }
        setLost(hasEverConnected ? 'Connection to backend lost' : 'Backend unavailable');
      }
    }

    // Initial poll immediately to check backend health on app startup
    poll();

    intervalRef.current = setInterval(poll, POLL_INTERVAL_MS);

    return () => {
      cancelled = true;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [setOnline, setLost, setReconnecting]);
}
