/**
 * React Hook for Real-time NATS Event Updates via WebSocket
 *
 * Automatically subscribes to project-specific events and invalidates
 * React Query cache for real-time UI updates.
 */

import { useQueryClient } from '@tanstack/react-query';
import { useEffect, useState, useRef } from 'react';
import { toast } from 'sonner';

import { logger } from '@/lib/logger';
import { useAuthToken } from '@/context/AuthTokenContext';

import { realtimeClient } from '../lib/websocket';

export interface RealtimeConfig {
  projectId?: string;
  onEvent?: (event: any) => void;
  enableToasts?: boolean;
  onTokenRefreshNeeded?: () => Promise<void>;
}

export function useRealtime(config: RealtimeConfig = {}) {
  const { projectId, onEvent, onTokenRefreshNeeded } = config;
  // Const queryClient = useQueryClient();
  const [isConnected, setIsConnected] = useState(false);
  const { token, isTokenExpired } = useAuthToken();
  const tokenRefreshIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!token) {
      logger.warn('No auth token found, skipping WebSocket connection');
      return;
    }

    // Connect to WebSocket with token and optional project ID
    realtimeClient.connect(token, projectId);

    // Monitor connection status
    const checkConnection = setInterval(() => {
      setIsConnected(realtimeClient.isConnected());
    }, 1000);

    // Set up token refresh interval (refresh every 50 minutes for 1-hour tokens)
    const tokenRefreshInterval = setInterval(async () => {
      if (isTokenExpired()) {
        logger.warn('Token expired, triggering refresh');
        if (onTokenRefreshNeeded) {
          try {
            await onTokenRefreshNeeded();
          } catch (error) {
            logger.error('Failed to refresh token', error);
            realtimeClient.disconnect();
          }
        } else {
          realtimeClient.disconnect();
        }
      }
    }, 50 * 60 * 1000); // 50 minutes

    tokenRefreshIntervalRef.current = tokenRefreshInterval;

    // Cleanup
    return () => {
      clearInterval(checkConnection);
      if (tokenRefreshIntervalRef.current) {
        clearInterval(tokenRefreshIntervalRef.current);
      }
      realtimeClient.disconnect();
    };
  }, [projectId, token, onTokenRefreshNeeded, isTokenExpired]);

  // Listen for all events and call custom handler
  useEffect(() => {
    if (!onEvent) {
      return;
    }

    const unsubscribe = realtimeClient.on('*', onEvent);
    return unsubscribe;
  }, [onEvent]);

  return { isConnected };
}

export function useRealtimeUpdates(projectId?: string) {
  const queryClient = useQueryClient();
  const { token } = useAuthToken();

  useEffect(() => {
    if (!projectId || !token) {
      return;
    }

    // Connect to WebSocket
    realtimeClient.connect(token, projectId);

    // Subscribe to item events
    const unsubItem = realtimeClient.on('item.created', (event) => {});

    const unsubItemUpdate = realtimeClient.on('item.updated', (event) => {});

    const unsubItemDelete = realtimeClient.on('item.deleted', (event) => {});

    // Subscribe to link events
    const unsubLink = realtimeClient.on('link.created', (event) => {});

    const unsubLinkDelete = realtimeClient.on('link.deleted', (event) => {});

    // Subscribe to spec events (from Python backend)
    const unsubSpec = realtimeClient.on('spec.created', (event) => {});

    const unsubSpecUpdate = realtimeClient.on('spec.updated', (event) => {});

    // Subscribe to AI analysis events
    const unsubAI = realtimeClient.on('ai.analysis.complete', (event) => {});

    // Subscribe to execution events
    const unsubExecution = realtimeClient.on('execution.completed', (event) => {});

    const unsubExecutionFailed = realtimeClient.on('execution.failed', (event) => {});

    // Subscribe to workflow events
    const unsubWorkflow = realtimeClient.on('workflow.completed', (event) => {});

    // Subscribe to project events
    const unsubProject = realtimeClient.on('project.updated', (event) => {});

    // Cleanup all subscriptions
    return () => {
      unsubItem();
      unsubItemUpdate();
      unsubItemDelete();
      unsubLink();
      unsubLinkDelete();
      unsubSpec();
      unsubSpecUpdate();
      unsubAI();
      unsubExecution();
      unsubExecutionFailed();
      unsubWorkflow();
      unsubProject();
      realtimeClient.disconnect();
    };
  }, [projectId, queryClient]);
}

export function useRealtimeEvent(eventType: string, callback: (event: any) => void) {
  useEffect(() => {
    const unsubscribe = realtimeClient.on(eventType, callback);
    return unsubscribe;
  }, [eventType, callback]);
}
