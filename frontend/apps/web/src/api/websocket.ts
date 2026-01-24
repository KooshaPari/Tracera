// WebSocket Real-time Connection Manager
import { API_BASE_URL } from "./client";

export interface RealtimeEvent {
	type: "created" | "updated" | "deleted";
	table: "projects" | "items" | "links" | "agents";
	schema: string;
	record: Record<string, any>;
	timestamp: number;
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
	private heartbeatInterval: number | null = null;
	private url: string;

	constructor() {
		if (typeof globalThis.window === "undefined") {
			throw new Error("WebSocketManager requires a browser environment");
		}
		const wsProtocol =
			globalThis.window.location.protocol === "https:" ? "wss:" : "ws:";
		const apiUrl = API_BASE_URL.replace(/^https?:/, wsProtocol);
		this.url = `${apiUrl}/ws`;
	}

	connect(): void {
		if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
			return;
		}

		this.isConnecting = true;

		try {
			this.ws = new WebSocket(this.url);

			this.ws.onopen = () => {
				console.log("[WebSocket] Connected");
				this.isConnected = true;
				this.isConnecting = false;
				this.reconnectAttempts = 0;
				this.startHeartbeat();
			};

			this.ws.onmessage = (event) => {
				try {
					const message: RealtimeEvent = JSON.parse(event.data);
					this.handleMessage(message);
				} catch (error) {
					console.error("[WebSocket] Failed to parse message:", error);
				}
			};

			this.ws.onerror = (error) => {
				console.error("[WebSocket] Error:", error);
				this.isConnected = false;
			};

			this.ws.onclose = () => {
				console.log("[WebSocket] Disconnected");
				this.isConnected = false;
				this.isConnecting = false;
				this.stopHeartbeat();
				this.attemptReconnect();
			};
		} catch (error) {
			console.error("[WebSocket] Connection failed:", error);
			this.isConnecting = false;
			this.attemptReconnect();
		}
	}

	disconnect(): void {
		this.stopHeartbeat();
		if (this.ws) {
			this.ws.close();
			this.ws = null;
		}
		this.isConnected = false;
		this.isConnecting = false;
	}

	subscribe(channel: string, callback: EventCallback): () => void {
		if (!this.subscriptions.has(channel)) {
			this.subscriptions.set(channel, new Set());
		}
		this.subscriptions.get(channel)?.add(callback);

		// Send subscribe message if connected
		if (this.isConnected && this.ws) {
			this.send({ type: "subscribe", channel });
		}

		// Return unsubscribe function
		return () => {
			const callbacks = this.subscriptions.get(channel);
			if (callbacks) {
				callbacks.delete(callback);
				if (callbacks.size === 0) {
					this.subscriptions.delete(channel);
					if (this.isConnected && this.ws) {
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

	private attemptReconnect(): void {
		if (this.reconnectAttempts >= this.maxReconnectAttempts) {
			console.error("[WebSocket] Max reconnection attempts reached");
			return;
		}

		this.reconnectAttempts++;
		const delay = this.reconnectDelay * 2 ** (this.reconnectAttempts - 1);

		console.log(
			`[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`,
		);

		setTimeout(() => {
			this.connect();
		}, delay);
	}

	get connected(): boolean {
		return this.isConnected;
	}
}

// Singleton instance
let wsManager: WebSocketManager | null = null;

export function getWebSocketManager(): WebSocketManager {
	if (!wsManager) {
		wsManager = new WebSocketManager();
	}
	return wsManager;
}

export function connectWebSocket(): void {
	getWebSocketManager().connect();
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
