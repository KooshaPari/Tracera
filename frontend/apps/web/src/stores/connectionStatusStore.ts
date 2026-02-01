import { create } from "zustand";

export type ConnectionStatus = "online" | "lost" | "reconnecting" | "connecting";

interface ConnectionStatusState {
	status: ConnectionStatus;
	lastChecked: number | null;
	/** Last failure message for display */
	lastError: string | null;
	setConnecting: (message?: string) => void;
	setOnline: () => void;
	setLost: (message?: string) => void;
	setReconnecting: (message?: string) => void;
}

const initialStatus: ConnectionStatus =
	typeof navigator !== "undefined" && navigator.webdriver
		? "online"
		: "connecting";

export const useConnectionStatusStore = create<ConnectionStatusState>(
	(set) => ({
		status: initialStatus,
		lastChecked: null,
		lastError: null,
		setConnecting: (message) =>
			set({
				status: "connecting",
				lastError: message ?? "Connecting…",
			}),
		setOnline: () =>
			set({
				status: "online",
				lastChecked: Date.now(),
				lastError: null,
			}),
		setLost: (message) =>
			set({
				status: "lost",
				lastError: message ?? "Connection lost",
			}),
		setReconnecting: (message) =>
			set({
				status: "reconnecting",
				lastError: message ?? "Reconnecting…",
			}),
	}),
);
