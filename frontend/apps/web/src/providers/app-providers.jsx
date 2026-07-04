import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEffect, useRef } from 'react';

import { appProvidersDeps } from './app-providers-deps';

const {
  ReactQueryDevtools,
  Toaster,
  getWebSocketManager,
  initializeCSRF,
  useAuth,
  useAuthStore,
  useWebSocketStore,
} = appProvidersDeps;

const MINUTE_MS = 60_000;
const DEFAULT_RETRY_COUNT = 1;
const QUERY_STALE_MINUTES = 2;
const QUERY_CACHE_MINUTES = 10;

const buildQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      mutations: {
        retry: DEFAULT_RETRY_COUNT,
      },
      queries: {
        gcTime: QUERY_CACHE_MINUTES * MINUTE_MS,
        refetchOnMount: false,
        refetchOnReconnect: false,
        refetchOnWindowFocus: false,
        retry: DEFAULT_RETRY_COUNT,
        staleTime: QUERY_STALE_MINUTES * MINUTE_MS,
        structuralSharing: true,
      },
    },
  });

const queryClient = buildQueryClient();

const WebSocketInitializer = () => {
  const { token, user } = useAuth();
  const connect = useWebSocketStore((state) => state.connect);
  const validateSession = useAuthStore((state) => state.validateSession);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const isConnected = useWebSocketStore((state) => state.isConnected);
  const isSignedIn = Boolean(user);
  const hasValidatedRef = useRef(false);

  useEffect(() => {
    initializeCSRF();
  }, []);

  useEffect(() => {
    const tokenGetter = () => token;
    getWebSocketManager(tokenGetter);
  }, [token]);

  useEffect(() => {
    if (!isAuthenticated || !isSignedIn || isConnected) {
      return;
    }

    Promise.resolve(connect());
  }, [connect, isAuthenticated, isConnected, isSignedIn]);

  useEffect(() => {
    if (hasValidatedRef.current) {
      return;
    }
    if (!token) {
      return;
    }
    hasValidatedRef.current = true;
    Promise.resolve(validateSession());
  }, [token, validateSession]);

  return null;
};

const buildContent = (children) => {
  const devtools = (() => {
    if (import.meta.env.DEV) {
      return <ReactQueryDevtools initialIsOpen={false} />;
    }
  })();

  return (
    <QueryClientProvider client={queryClient}>
      <WebSocketInitializer />
      {children}
      <Toaster position='top-right' />
      {devtools}
    </QueryClientProvider>
  );
};

const AppProviders = ({ children }) => buildContent(children);

export { AppProviders };
