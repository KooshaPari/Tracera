import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { useEffect } from "react";
import { AuthKitProvider, useAuth } from "@workos-inc/authkit-react";
// import { BrowserRouter } from 'react-router-dom' // Not used - app uses @tanstack/react-router
import { Toaster } from "sonner";
import { AuthKitSync } from "../components/auth/AuthKitSync";
import { useAuthStore } from "../stores/authStore";
import { useWebSocketStore } from "../stores/websocketStore";
import { getWebSocketManager } from "../api/websocket";
import { initializeCSRF } from "../lib/csrf";

// Create a client with optimized caching for performance
const queryClient = new QueryClient({
	defaultOptions: {
		queries: {
			// Aggressive caching - data considered fresh for 2 minutes
			staleTime: 2 * 60 * 1000,
			// Keep unused data in cache for 10 minutes
			gcTime: 10 * 60 * 1000,
			// Only retry once to avoid blocking UI
			retry: 1,
			// Disable automatic refetches - user controls refresh
			refetchOnWindowFocus: false,
			refetchOnReconnect: false,
			// Use structural sharing for better performance
			structuralSharing: true,
			// Network-only fetching on mount, then use cache
			refetchOnMount: false,
		},
		mutations: {
			retry: 1,
		},
	},
});

function WebSocketInitializer() {
	const { getAccessToken, user } = useAuth();
	const isSignedIn = user !== null;
	const connect = useWebSocketStore((state) => state.connect);
	const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
	const isConnected = useWebSocketStore((state) => state.isConnected);

	// Initialize CSRF protection on app startup
	useEffect(() => {
		initializeCSRF().catch((error) => {
			console.warn("[AppProviders] CSRF initialization warning:", error);
			// Don't throw - CSRF is optional in development
		});
	}, []);

	useEffect(() => {
		// Initialize WebSocket manager with token getter function
		// This ensures WebSocket connections use WorkOS AuthKit tokens
		const tokenGetter = async () => {
			if (!isSignedIn) {
				return null;
			}
			try {
				const token = await getAccessToken();
				return token || null;
			} catch (error) {
				console.error("[WebSocket] Failed to get access token:", error);
				return null;
			}
		};

		// Update WebSocket manager with token getter
		getWebSocketManager(tokenGetter);
	}, [getAccessToken, isSignedIn]);

	useEffect(() => {
		// Connect to WebSocket if authenticated and not already connected
		if (isAuthenticated && isSignedIn && !isConnected) {
			const connectAsync = async () => {
				try {
					await connect();
				} catch (error) {
					console.error("[WebSocketInitializer] Failed to connect:", error);
				}
			};
			connectAsync();
		}
	}, [isAuthenticated, isSignedIn, isConnected, connect]);

	return null;
}

export function AppProviders({ children }: { children: React.ReactNode }) {
	// Read environment variables using bracket notation for index signatures
	const workosClientId = import.meta.env["VITE_WORKOS_CLIENT_ID"] as
		| string
		| undefined;
	// NOTE: apiHostname removed - SDK will use default api.workos.com
	// Only set apiHostname if you have a custom Authentication API domain
	// The VITE_WORKOS_API_HOSTNAME env var is for custom API domains, not AuthKit hosted UI

	// Debug: Log if client ID is found (only in dev)
	if (import.meta.env.DEV) {
		console.log(
			"[AppProviders] WorkOS Client ID:",
			workosClientId ? "Found" : "Missing",
		);
		console.log(
			"[AppProviders] Using default WorkOS API endpoints (api.workos.com)",
		);
	}

	const content = (
		<QueryClientProvider client={queryClient}>
			<WebSocketInitializer />
			{children}
			<Toaster position="top-right" />
			{import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
		</QueryClientProvider>
	);

	// CRITICAL: Always wrap with AuthKitProvider if client ID exists
	// This ensures useAuth hook is available in all components
	if (workosClientId && workosClientId.trim() !== "") {
		// WorkOS React SDK configuration
		// redirectUri should be set on AuthKitProvider, not passed to signIn()
		const providerProps: { clientId: string; redirectUri?: string } = {
			clientId: workosClientId,
		};

		// Set redirectUri on provider - this is used when constructing sign-in/sign-up URLs
		// Must match EXACTLY an entry in WorkOS Dashboard Redirect URIs list
		if (typeof window !== "undefined") {
			providerProps.redirectUri = `${window.location.origin}/auth/callback`;
		}

		if (import.meta.env.DEV) {
			console.log("[AppProviders] AuthKitProvider props:", {
				clientId: providerProps.clientId?.substring(0, 20) + "...",
				redirectUri: providerProps.redirectUri,
			});
		}

		return (
			<AuthKitProvider {...providerProps}>
				{content}
				<AuthKitSync />
			</AuthKitProvider>
		);
	}

	// If WorkOS is not configured, show error in dev, return content in prod
	if (import.meta.env.DEV) {
		console.warn(
			"[AppProviders] VITE_WORKOS_CLIENT_ID is not set. AuthKit features will not work.",
		);
	}

	return content;
}
