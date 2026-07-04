import { create } from 'zustand';

import type { RealtimeEvent } from '../api/websocket';

import { getWebSocketManager } from '../api/websocket';

const CONNECTION_CHECK_INTERVAL_MS = Number('1000');
const MAX_EVENTS = Number('100');
const ZERO = Number('0');

type ConnectionCheckInterval = ReturnType<typeof globalThis.setInterval>;

type WebSocketStoreSetter = (
  partial:
    | Partial<WebSocketState>
    | ((state: WebSocketState) => Partial<WebSocketState> | WebSocketState),
) => void;

type WebSocketStoreGetter = () => WebSocketState;

declare global {
  interface Window {
    __wsCheckInterval?: ConnectionCheckInterval | undefined;
  }
}

interface WebSocketState {
  // Connection state
  activeChannels: Set<string>;
  events: RealtimeEvent[];
  isConnected: boolean;
  lastEvent?: RealtimeEvent | undefined;
  reconnectAttempts: number;

  // Actions
  addEvent: (event: RealtimeEvent) => void;
  clearEvents: () => void;
  connect: () => Promise<void>;
  disconnect: () => void;
  setConnectionStatus: (isConnected: boolean) => void;
  subscribe: (channel: string, callback: (event: RealtimeEvent) => void) => () => void;
}

const getWindowRef = (): Window | undefined => {
  if (globalThis.window === undefined) {
    return undefined;
  }

  return globalThis.window;
};

const getConnectionCheckInterval = (): ConnectionCheckInterval | undefined => {
  const windowRef = getWindowRef();
  if (!windowRef) {
    return undefined;
  }

  return windowRef.__wsCheckInterval;
};

const setConnectionCheckInterval = (intervalId: ConnectionCheckInterval): void => {
  const windowRef = getWindowRef();
  if (windowRef) {
    windowRef.__wsCheckInterval = intervalId;
  }
};

const clearConnectionCheckInterval = (): void => {
  const intervalId = getConnectionCheckInterval();
  if (intervalId !== undefined) {
    clearInterval(intervalId);
  }
};

const createActiveChannels = (channels: Set<string>, channel: string): Set<string> =>
  new Set([...channels, channel]);

const removeActiveChannel = (channels: Set<string>, channel: string): Set<string> => {
  const filtered = [...channels].filter((existing) => existing !== channel);
  return new Set(filtered);
};

const buildEvents = (event: RealtimeEvent, events: RealtimeEvent[]): RealtimeEvent[] =>
  [event, ...events].slice(ZERO, MAX_EVENTS);

const startConnectionMonitor = (set: WebSocketStoreSetter, get: WebSocketStoreGetter): void => {
  const wsManager = getWebSocketManager();
  clearConnectionCheckInterval();

  const checkConnection = globalThis.setInterval((): void => {
    const { isConnected } = get();
    const { connected } = wsManager;
    // Only update if state actually changed to prevent infinite loops
    if (isConnected !== connected) {
      set({ isConnected: connected });
    }
  }, CONNECTION_CHECK_INTERVAL_MS);

  setConnectionCheckInterval(checkConnection);
};

const ensureConnected = async (
  set: WebSocketStoreSetter,
  get: WebSocketStoreGetter,
): Promise<void> => {
  const { isConnected } = get();
  if (isConnected) {
    return;
  }

  const wsManager = getWebSocketManager();
  await wsManager.connect();
  startConnectionMonitor(set, get);
};

const createInitialState = (): Pick<
  WebSocketState,
  'activeChannels' | 'events' | 'isConnected' | 'lastEvent' | 'reconnectAttempts'
> => ({
  activeChannels: new Set(),
  events: [],
  isConnected: false,
  lastEvent: undefined,
  reconnectAttempts: ZERO,
});

const createWebSocketActions = (
  set: WebSocketStoreSetter,
  get: WebSocketStoreGetter,
): Pick<
  WebSocketState,
  'addEvent' | 'clearEvents' | 'connect' | 'disconnect' | 'setConnectionStatus' | 'subscribe'
> => ({
  addEvent: (event: RealtimeEvent): void => {
    set((state) => ({
      events: buildEvents(event, state.events),
      lastEvent: event,
    }));
  },
  clearEvents: (): void => {
    set({ events: [], lastEvent: undefined });
  },
  connect: async (): Promise<void> => ensureConnected(set, get),
  disconnect: (): void => {
    const wsManager = getWebSocketManager();
    wsManager.disconnect();
    set({ isConnected: false });
    clearConnectionCheckInterval();
  },
  setConnectionStatus: (isConnected: boolean): void => {
    set({ isConnected });
  },
  subscribe: (channel: string, onEvent: (event: RealtimeEvent) => void): (() => void) => {
    const wsManager = getWebSocketManager();
    const handleEvent = (event: RealtimeEvent): void => {
      get().addEvent(event);
      onEvent(event);
    };
    const unsubscribe = wsManager.subscribe(channel, handleEvent);

    set((state) => ({
      activeChannels: createActiveChannels(state.activeChannels, channel),
    }));

    // Return enhanced unsubscribe function
    return (): void => {
      unsubscribe();
      set((state) => ({
        activeChannels: removeActiveChannel(state.activeChannels, channel),
      }));
    };
  },
});

const buildWebSocketStore = (
  set: WebSocketStoreSetter,
  get: WebSocketStoreGetter,
): WebSocketState => ({
  ...createInitialState(),
  ...createWebSocketActions(set, get),
});

const useWebSocketStore = create<WebSocketState>((set, get) => buildWebSocketStore(set, get));

export type { WebSocketState };
export { useWebSocketStore };
