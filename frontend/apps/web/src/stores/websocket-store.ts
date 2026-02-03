import { create } from "zustand";
import type { RealtimeEvent } from "../api/websocket";
import { getWebSocketManager } from "../api/websocket";

const CONNECTION_CHECK_INTERVAL_MS = 1000;
const MAX_EVENTS = 100;
const ZERO = 0;

type ConnectionCheckInterval = ReturnType<typeof globalThis.setInterval>;

declare global {
	interface Window {
		__wsCheckInterval?: ConnectionCheckInterval;
	}
}

interface WebSocketState {
	// Connection state
	activeChannels: Set<string>;
	events: RealtimeEvent[];
	isConnected: boolean;
	lastEvent?: RealtimeEvent;
	reconnectAttempts: number;

	// Actions
	addEvent: (event: RealtimeEvent) => void;
	clearEvents: () => void;
	connect: () => Promise<void>;
	disconnect: () => void;
	setConnectionStatus: (isConnected: boolean) => void;
	subscribe: (
		channel: string,
		callback: (event: RealtimeEvent) => void,
	) => () => void;
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

const setConnectionCheckInterval = (
	intervalId: ConnectionCheckInterval,
): void => {
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

const createActiveChannels = (
	channels: Set<string>,
	channel: string,
): Set<string> => new Set([...channels, channel]);

const removeActiveChannel = (
	channels: Set<string>,
	channel: string,
): Set<string> => {
	const filtered = [...channels].filter((existing) => existing !== channel);
	return new Set(filtered);
};

const buildEvents = (
	event: RealtimeEvent,
	events: RealtimeEvent[],
): RealtimeEvent[] => [event, ...events].slice(ZERO, MAX_EVENTS);

const useWebSocketStore = create<WebSocketState>((set, get) => ({
	// Connection state
	activeChannels: new Set(),
	events: [],
	isConnected: false,
	lastEvent: undefined,
	reconnectAttempts: ZERO,

	// Actions
	addEvent: (event: RealtimeEvent): void => {
		set((state) => ({
			events: buildEvents(event, state.events),
			lastEvent: event,
		}));
	},
	clearEvents: (): void => {
		set({ events: [], lastEvent: undefined });
	},
	connect: (): Promise<void> => {
		const state = get();
		// Prevent multiple connection attempts
		if (state.isConnected) {
			return Promise.resolve();
		}

		const wsManager = getWebSocketManager();

		return wsManager.connect().then(() => {
			clearConnectionCheckInterval();

			const checkConnection = globalThis.setInterval((): void => {
				const currentState = get();
				const connected = wsManager.connected;
				// Only update if state actually changed to prevent infinite loops
				if (currentState.isConnected !== connected) {
					set({ isConnected: connected });
				}
			}, CONNECTION_CHECK_INTERVAL_MS);

			setConnectionCheckInterval(checkConnection);
		});
	},
	disconnect: (): void => {
		const wsManager = getWebSocketManager();
		wsManager.disconnect();
		set({ isConnected: false });
		clearConnectionCheckInterval();
	},
	setConnectionStatus: (isConnected: boolean): void => {
		set({ isConnected });
	},
	subscribe: (
		channel: string,
		callback: (event: RealtimeEvent) => void,
	): (() => void) => {
		const wsManager = getWebSocketManager();
		const unsubscribe = wsManager.subscribe(channel, (event: RealtimeEvent) => {
			get().addEvent(event);
			callback(event);
		});

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
}));

export { useWebSocketStore };
