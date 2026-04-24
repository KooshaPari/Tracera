import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useCallback, useEffect, useRef } from 'react';

import type { SSEClient } from '@/lib/sse-client';

import { createNotificationSSEClient } from '@/lib/sse-client';
import { useAuthStore } from '@/stores/authStore';

export interface Notification {
  id: string;
  user_id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  link?: string;
  read_at?: string;
  created_at: string;
}

export interface NotificationEvent {
  type: 'notification' | 'read' | 'read_all' | 'delete';
  notification?: Notification;
  user_id: string;
  timestamp: number;
}

export function useNotifications() {
  const { token } = useAuthStore();
  const queryClient = useQueryClient();
  const sseClientRef = useRef<SSEClient | null>(null);
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:4000';

  // Fetch initial notifications
  const query = useQuery({
    enabled: Boolean(token),
    queryFn: async () => {
      if (!token) {
        return [];
      }
      const response = await fetch(`${API_URL}/api/v1/notifications`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      // 404 = notifications API not implemented yet; treat as empty list
      if (response.status === 404) {
        return [];
      }
      if (!response.ok) {
        throw new Error('Failed to fetch notifications');
      }
      return response.json() as Promise<Notification[]>;
    },
    queryKey: ['notifications'],
    // No refetchInterval - we use SSE for real-time updates
  });

  // Handle notification events from SSE
  const handleNotificationEvent = useCallback(
    (data: unknown) => {
      const event = data as NotificationEvent;

      queryClient.setQueryData<Notification[]>(['notifications'], (oldData) => {
        if (!oldData) {
          return oldData;
        }

        switch (event.type) {
          case 'notification': {
            // Add new notification to the list
            if (event.notification) {
              return [event.notification, ...oldData];
            }
            return oldData;
          }

          case 'read': {
            // Mark notification as read
            return oldData.map((n) =>
              n.id === event.notification?.id ? { ...n, read_at: new Date().toISOString() } : n,
            );
          }

          case 'read_all': {
            // Mark all as read
            return oldData.map((n) => ({
              ...n,
              read_at: n.read_at ?? new Date().toISOString(),
            }));
          }

          case 'delete': {
            // Remove notification from list
            return oldData.filter((n) => n.id !== event.notification?.id);
          }

          default: {
            return oldData;
          }
        }
      });
    },
    [queryClient],
  );

  // Setup SSE connection
  useEffect(() => {
    if (!token) {
      // Cleanup existing connection if token is removed
      if (sseClientRef.current) {
        sseClientRef.current.close();
        sseClientRef.current = null;
      }
      return;
    }

    // Create SSE client
    sseClientRef.current = createNotificationSSEClient(
      token,
      handleNotificationEvent,
      (_error) => {},
    );

    // Connect to SSE stream
    sseClientRef.current?.connect();

    // Cleanup on unmount or token change
    return () => {
      if (sseClientRef.current) {
        sseClientRef.current.close();
        sseClientRef.current = null;
      }
    };
  }, [token, handleNotificationEvent]);

  const markAsRead = useMutation({
    mutationFn: async (id: string) => {
      const response = await fetch(`${API_URL}/api/v1/notifications/${id}/read`, {
        headers: { Authorization: `Bearer ${token}` },
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error('Failed to mark notification as read');
      }
    },
    onSuccess: () => {
      // SSE will update the cache automatically, but we can also update optimistically
      // QueryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  const markAllRead = useMutation({
    mutationFn: async () => {
      const response = await fetch(`${API_URL}/api/v1/notifications/read-all`, {
        headers: { Authorization: `Bearer ${token}` },
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error('Failed to mark all notifications as read');
      }
    },
    onSuccess: () => {
      // SSE will update the cache automatically
      // QueryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  const deleteNotification = useMutation({
    mutationFn: async (id: string) => {
      const response = await fetch(`${API_URL}/api/v1/notifications/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error('Failed to delete notification');
      }
    },
    onSuccess: () => {
      // SSE will update the cache automatically
    },
  });

  const unreadCount = query.data?.filter((n) => !n.read_at).length ?? 0;
  const isConnected = sseClientRef.current?.isConnected() ?? false;

  return {
    deleteNotification,
    isConnected,
    isLoading: query.isLoading,
    markAllRead,
    markAsRead,
    notifications: query.data ?? [],
    unreadCount,
  };
}
