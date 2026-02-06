import { create } from 'zustand';

type ConnectionStatus = 'connecting' | 'lost' | 'online' | 'reconnecting';

export interface ConnectionStatusState {
  lastChecked: number;
  /** Last failure message for display */
  lastError: string;
  setConnecting: (message?: string) => void;
  setLost: (message?: string) => void;
  setOnline: () => void;
  setReconnecting: (message?: string) => void;
  status: ConnectionStatus;
}

const getInitialStatus = (): ConnectionStatus => {
  if ('navigator' in globalThis && globalThis.navigator.webdriver) {
    return 'online';
  }

  return 'connecting';
};

const useConnectionStatusStore = create<ConnectionStatusState>((set) => ({
  lastChecked: 0,
  lastError: '',
  setConnecting: (message?: string): void => {
    set({
      lastError: message ?? 'Connecting…',
      status: 'connecting',
    });
  },
  setLost: (message?: string): void => {
    set({
      lastError: message ?? 'Connection lost',
      status: 'lost',
    });
  },
  setOnline: (): void => {
    set({
      lastChecked: Date.now(),
      lastError: '',
      status: 'online',
    });
  },
  setReconnecting: (message?: string): void => {
    set({
      lastError: message ?? 'Reconnecting…',
      status: 'reconnecting',
    });
  },
  status: getInitialStatus(),
}));

export { useConnectionStatusStore };
