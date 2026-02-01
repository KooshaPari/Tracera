import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { logger } from '@/lib/logger';
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { AuthKitProvider, useAuth } from "@workos-inc/authkit-react";
import { useEffect } from "react";
// import { BrowserRouter } from 'react-router-dom' // Not used - app uses @tanstack/react-router
import { Toaster } from "sonner";
import { getWebSocketManager } from "../api/websocket";
import { AuthKitSync } from "../components/auth/AuthKitSync";
import { initializeCSRF } from "../lib/csrf";
import { useAuthStore } from "../stores/authStore";
import { useWebSocketStore } from "../stores/websocketStore";

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
			logger.warn("[AppProviders] CSRF initialization warning:", error);
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
				logger.error("[WebSocket] Failed to get access token:", error);
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
					logger.error("[WebSocketInitializer] Failed to connect:", error);
				}
			};
			connectAsync();
		}
	}, [isAuthenticated, isSignedIn, isConnected, connect]);

	return null;
}

export function AppProviders({ children }: { children: React.ReactNode }) {
	// Read environment variables using bracket notation for index signatures
	const workosClientId = import.meta.env['VITE_WORKOS_CLIENT_ID'] as
		| string
		| undefined;
	const workosAuthDomain = import.meta.env['VITE_WORKOS_AUTH_DOMAIN'] as
		| string
		| undefined;

	/**
	 * Production Setup Required for HttpOnly Cookies:
	 *
	 * 1. Set up custom authentication domain (e.g., auth.tracertm.com)
	 * 2. Configure VITE_WORKOS_AUTH_DOMAIN in environment
	 * 3. Ensure HTTPS is enabled (required for secure cookies)
	 *
	 * Development:
	 * - devMode={true} allows localStorage (no custom domain needed)
	 * - Works with http://localhost
	 * - Automatically enabled when import.meta.env.DEV is true
	 */

	// Debug: Log if client ID is found (only in dev)
	if (import.meta.env.DEV) {
		logger.info(
			"[AppProviders] WorkOS Client ID:",
			workosClientId ? "Found" : "Missing",
		);
		logger.info(
			"[AppProviders] Token Storage:",
			import.meta.env.DEV ? "localStorage (devMode)" : "HttpOnly Cookies",
		);
		if (!import.meta.env.DEV && !workosAuthDomain) {
			logger.warn(
				"[AppProviders] Production mode requires VITE_WORKOS_AUTH_DOMAIN for HttpOnly cookies",
			);
		}
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
		// WorkOS React SDK configuration with HttpOnly cookie support
		// redirectUri should be set on AuthKitProvider, not passed to signIn()
		const providerProps: {
			clientId: string;
			redirectUri?: string;
			devMode?: boolean;
			apiHostname?: string;
		} = {
			clientId: workosClientId,
			// Development: Use localStorage via devMode (no custom domain needed)
			// Production: Use HttpOnly cookies via custom auth domain
			devMode: import.meta.env.DEV,
		};

		// Production: Set custom auth domain for HttpOnly cookie storage
		// Only set if we're in production and have a custom domain configured
		if (!import.meta.env.DEV && workosAuthDomain) {
			providerProps.apiHostname = workosAuthDomain;
		}

		// Set redirectUri on provider - this is used when constructing sign-in/sign-up URLs
		// Must match EXACTLY an entry in WorkOS Dashboard Redirect URIs list
		// Points to /auth/callback route which handles OAuth callback
		if (typeof window !== "undefined") {
			providerProps.redirectUri = `${window.location.origin}/auth/callback`;
		}

		if (import.meta.env.DEV) {
			logger.info("[AppProviders] AuthKitProvider props:", {
				clientId: `${providerProps.clientId?.substring(0, 20)}...`,
				redirectUri: providerProps.redirectUri,
				devMode: providerProps.devMode,
				apiHostname: providerProps.apiHostname || "(default: api.workos.com)",
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
		logger.warn(
			"[AppProviders] VITE_WORKOS_CLIENT_ID is not set. AuthKit features will not work.",
		);
	}

	return content;
}
