import { useEffect, useRef } from "react";
import { useConnectionStatusStore } from "@/stores/connectionStatusStore";
import client from "@/api/client";

const { apiClient } = client;

const POLL_INTERVAL_MS = 25_000;
const RETRY_ATTEMPTS = 3;
const RETRY_DELAY_MS = 2_000;

/**
 * Background health polling for the important backend (Python API).
 * On failure: sets reconnecting, retries; after retries exhausted sets lost.
 * On success: sets online.
 * Also reacts to 5xx from API client (handled in client middleware).
 */
export function useConnectionHealth(): void {
	const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
	const setOnline = useConnectionStatusStore((s) => s.setOnline);
	const setLost = useConnectionStatusStore((s) => s.setLost);
	const setReconnecting = useConnectionStatusStore((s) => s.setReconnecting);
	const setConnecting = useConnectionStatusStore((s) => s.setConnecting);

	useEffect(() => {
		let cancelled = false;
		let hasEverConnected = false;

		async function poll(): Promise<void> {
			try {
				if (!hasEverConnected) {
					setConnecting("Connecting…");
				}
				const { response, error, data } = await apiClient.GET(
					"/api/v1/health",
					{},
				);
				if (cancelled) return;
				const unhealthy =
					error ||
					!response?.ok ||
					(data && (data as { status?: string }).status === "unhealthy");
				if (unhealthy) {
					if (!hasEverConnected) {
						setConnecting("Still waiting for backend…");
					} else {
						setReconnecting("Reconnecting…");
					}
					for (let i = 0; i < RETRY_ATTEMPTS && !cancelled; i++) {
						await new Promise((r) => setTimeout(r, RETRY_DELAY_MS));
						const retry = await apiClient.GET("/api/v1/health", {});
						if (cancelled) return;
						const retryOk =
							!retry.error &&
							retry.response?.ok &&
							!(retry.data && (retry.data as { status?: string }).status === "unhealthy");
						if (retryOk) {
							setOnline();
							hasEverConnected = true;
							return;
						}
					}
					setLost(
						hasEverConnected
							? "Connection to backend lost"
							: "Backend unavailable",
					);
					return;
				}
				setOnline();
				hasEverConnected = true;
            } catch {
                if (cancelled) return;
				if (!hasEverConnected) {
					setConnecting("Still waiting for backend…");
				} else {
					setReconnecting("Reconnecting…");
				}
				for (let i = 0; i < RETRY_ATTEMPTS && !cancelled; i++) {
					await new Promise((r) => setTimeout(r, RETRY_DELAY_MS));
					try {
						const retry = await apiClient.GET("/api/v1/health", {});
						if (cancelled) return;
						const retryOk =
							!retry.error &&
							retry.response?.ok &&
							!(retry.data && (retry.data as { status?: string }).status === "unhealthy");
						if (retryOk) {
							setOnline();
							hasEverConnected = true;
							return;
						}
                    } catch {
                        // continue retries
					}
				}
				setLost(
					hasEverConnected
						? "Connection to backend lost"
						: "Backend unavailable",
				);
			}
		}

		// Initial poll after a short delay so we don't block first paint
		const initial = setTimeout(() => {
			void poll();
		}, 2000);

		intervalRef.current = setInterval(poll, POLL_INTERVAL_MS);

		return () => {
			cancelled = true;
			clearTimeout(initial);
			if (intervalRef.current) {
				clearInterval(intervalRef.current);
				intervalRef.current = null;
			}
		};
	}, [setOnline, setLost, setReconnecting]);
}
