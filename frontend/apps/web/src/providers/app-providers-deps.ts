import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Toaster } from 'sonner';

import { logger } from '@/lib/logger';

import { getWebSocketManager } from '../api/websocket';
import { useAuth } from '../hooks/useAuth';
import { initializeCSRF } from '../lib/csrf';
import { useAuthStore } from '../stores/auth-store';
import { useWebSocketStore } from '../stores/websocket-store';

const appProvidersDeps = {
  ReactQueryDevtools,
  Toaster,
  getWebSocketManager,
  initializeCSRF,
  logger,
  useAuth,
  useAuthStore,
  useWebSocketStore,
};

export { appProvidersDeps };
