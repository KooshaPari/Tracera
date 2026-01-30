// WebSocket Real-time Connection Manager
import { API_BASE_URL } from "./client";

/**
 * Record data from database table
 */
export interface DatabaseRecord {
	[key: string]: string | number | boolean | object | null | undefined;
}

export interface RealtimeEvent {
	type: "created" | "updated" | "deleted";
	table: "projects" | "items" | "links";
	schema: string;
	record: DatabaseRecord;
	timestamp: number;
}

export interface AuthMessage {
	type: "auth";
	token: string;
}

export interface AuthResponse {
	type: "auth_success" | "auth_failed";
	message?: string;
}

export type EventCallback = (event: RealtimeEvent) => void;

export class WebSocketManager {
	private ws: WebSocket | null = null;
	private reconnectAttempts = 0;
	private maxReconnectAttempts = 5;
	private reconnectDelay = 1000;
	private subscriptions = new Map<string, Set<EventCallback>>();
	private isConnecting = false;
	private isConnected = false;
	private isAuthenticated = false;
	private heartbeatInterval: number | null = null;
	private baseUrl: string;
	private getToken: (() => string | null | Promise<string | null>) | null =
		null;
	private authTimeout: number | null = null;
	private token: string | null = null;

	constructor(getToken?: () => string | null | Promise<string | null>) {
		if (typeof globalThis.window === "undefined") {
			throw new Error("WebSocketManager requires a browser environment");
		}
		const wsProtocol =
			globalThis.window.location.protocol === "https:" ? "wss:" : "ws:";
		const apiUrl = API_BASE_URL.replace(/^https?:/, wsProtocol);
		this.baseUrl = `${apiUrl}/ws`;
		this.getToken = getToken || null;
	}

	async connect(): Promise<void> {
		if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
			return;
		}

		this.isConnecting = true;
		this.isAuthenticated = false;

		// Get authentication token from provided callback
		// For WebSocket, we need a token since cookies cannot be sent directly
		// The backend should validate the token embedded in the WebSocket message
		let token: string | null = null;
		if (this.getToken) {
			const tokenResult = this.getToken();
			token = tokenResult instanceof Promise ? await tokenResult : tokenResult;
		}

		if (!token) {
			console.error(
				"[WebSocket] Authentication token required. Please authenticate first.",
			);
			this.isConnecting = false;
			return;
		}

		// Store token for authentication message
		this.token = token;

		// Build WebSocket URL WITHOUT token parameter (security fix)
		const url = `${this.baseUrl}`;

		try {
			this.ws = new WebSocket(url);

			this.ws.onopen = () => {
				console.log(
					"[WebSocket] Connection established, waiting for authentication",
				);
				this.isConnecting = false;
				this.reconnectAttempts = 0;

				// Send authentication message after connection
				this.sendAuthMessage();

				// Set auth timeout (5 seconds)
				this.authTimeout = window.setTimeout(() => {
					console.error("[WebSocket] Authentication timeout");
					if (this.ws?.readyState === WebSocket.OPEN) {
						this.ws.close(1008, "Authentication timeout");
					}
				}, 5000);
			};

			this.ws.onmessage = (event) => {
				try {
					const message = JSON.parse(event.data);

					// Handle authentication response
					if (message.type === "auth_success") {
						console.log("[WebSocket] Authentication successful");
						this.isAuthenticated = true;
						this.isConnected = true;
						if (this.authTimeout) {
							clearTimeout(this.authTimeout);
							this.authTimeout = null;
						}
						this.startHeartbeat();
						return;
					}

					if (message.type === "auth_failed") {
						console.error(
							"[WebSocket] Authentication failed:",
							message.message,
						);
						this.isAuthenticated = false;
						this.isConnected = false;
						if (this.authTimeout) {
							clearTimeout(this.authTimeout);
							this.authTimeout = null;
						}
						if (this.ws?.readyState === WebSocket.OPEN) {
							this.ws.close(1008, "Authentication failed");
						}
						return;
					}

					// Only process event messages after authentication
					if (this.isAuthenticated && message.type !== "auth") {
						const realtimeEvent: RealtimeEvent = message;
						this.handleMessage(realtimeEvent);
					}
				} catch (error) {
					console.error("[WebSocket] Failed to parse message:", error);
				}
			};

			this.ws.onerror = (error) => {
				console.error("[WebSocket] Error:", error);
				this.isConnected = false;
				this.isAuthenticated = false;
			};

			this.ws.onclose = (event) => {
				console.log("[WebSocket] Disconnected", {
					code: event.code,
					reason: event.reason,
				});
				this.isConnected = false;
				this.isAuthenticated = false;
				this.isConnecting = false;
				this.stopHeartbeat();

				if (this.authTimeout) {
					clearTimeout(this.authTimeout);
					this.authTimeout = null;
				}

				// Don't reconnect if closed due to authentication failure
				if (event.code === 1008 && event.reason?.includes("Authentication")) {
					console.error(
						"[WebSocket] Authentication failed. Please re-authenticate.",
					);
					return;
				}

				this.attemptReconnect();
			};
		} catch (error) {
			console.error("[WebSocket] Connection failed:", error);
			this.isConnecting = false;
			this.attemptReconnect();
		}
	}

	private sendAuthMessage(): void {
		if (!this.ws || this.ws.readyState !== WebSocket.OPEN || !this.token) {
			console.error(
				"[WebSocket] Cannot send auth message: connection not ready",
			);
			return;
		}

		const authMessage: AuthMessage = {
			type: "auth",
			token: this.token,
		};

		try {
			this.ws.send(JSON.stringify(authMessage));
			console.log("[WebSocket] Auth message sent");
		} catch (error) {
			console.error("[WebSocket] Failed to send auth message:", error);
		}
	}

	disconnect(): void {
		this.stopHeartbeat();
		if (this.authTimeout) {
			clearTimeout(this.authTimeout);
			this.authTimeout = null;
		}
		if (this.ws) {
			this.ws.close();
			this.ws = null;
		}
		this.isConnected = false;
		this.isAuthenticated = false;
		this.isConnecting = false;
		this.token = null;
	}

	subscribe(channel: string, callback: EventCallback): () => void {
		if (!this.subscriptions.has(channel)) {
			this.subscriptions.set(channel, new Set());
		}
		this.subscriptions.get(channel)?.add(callback);

		// Send subscribe message if authenticated
		if (this.isAuthenticated && this.ws) {
			this.send({ type: "subscribe", channel });
		}

		// Return unsubscribe function
		return () => {
			const callbacks = this.subscriptions.get(channel);
			if (callbacks) {
				callbacks.delete(callback);
				if (callbacks.size === 0) {
					this.subscriptions.delete(channel);
					if (this.isAuthenticated && this.ws) {
						this.send({ type: "unsubscribe", channel });
					}
				}
			}
		};
	}

	private handleMessage(event: RealtimeEvent): void {
		// Broadcast to all subscribers
		const channel = `${event.table}:${event.type}`;
		const allChannel = `${event.table}:*`;
		const globalChannel = "*";

		const channels = [channel, allChannel, globalChannel];
		channels.forEach((ch) => {
			const callbacks = this.subscriptions.get(ch);
			if (callbacks) {
				callbacks.forEach((callback) => {
					try {
						callback(event);
					} catch (error) {
						console.error(`[WebSocket] Error in callback for ${ch}:`, error);
					}
				});
			}
		});
	}

	private send(data: any): void {
		if (this.ws?.readyState === WebSocket.OPEN) {
			this.ws.send(JSON.stringify(data));
		}
	}

	private startHeartbeat(): void {
		if (typeof globalThis.window === "undefined") return;
		this.heartbeatInterval = globalThis.window.setInterval(() => {
			if (this.ws?.readyState === WebSocket.OPEN) {
				this.send({ type: "ping" });
			}
		}, 30000); // Send heartbeat every 30 seconds
	}

	private stopHeartbeat(): void {
		if (this.heartbeatInterval !== null) {
			clearInterval(this.heartbeatInterval);
			this.heartbeatInterval = null;
		}
	}

	private async attemptReconnect(): Promise<void> {
		if (this.reconnectAttempts >= this.maxReconnectAttempts) {
			console.error("[WebSocket] Max reconnection attempts reached");
			return;
		}

		this.reconnectAttempts++;
		const delay = this.reconnectDelay * 2 ** (this.reconnectAttempts - 1);

		console.log(
			`[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`,
		);

		setTimeout(async () => {
			await this.connect();
		}, delay);
	}

	get connected(): boolean {
		return this.isConnected;
	}
}

// Singleton instance
let wsManager: WebSocketManager | null = null;

export function getWebSocketManager(
	getToken?: () => string | null | Promise<string | null>,
): WebSocketManager {
	if (!wsManager) {
		wsManager = new WebSocketManager(getToken);
	} else if (getToken) {
		// Update token getter if provided
		(wsManager as any).getToken = getToken;
	}
	return wsManager;
}

export async function connectWebSocket(
	getToken?: () => string | null | Promise<string | null>,
): Promise<void> {
	await getWebSocketManager(getToken).connect();
}

export function disconnectWebSocket(): void {
	getWebSocketManager().disconnect();
}

export function subscribeToChannel(
	channel: string,
	callback: EventCallback,
): () => void {
	return getWebSocketManager().subscribe(channel, callback);
}
