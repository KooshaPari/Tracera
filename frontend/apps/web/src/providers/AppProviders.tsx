import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { useEffect } from "react";
// import { BrowserRouter } from 'react-router-dom' // Not used - app uses @tanstack/react-router
import { Toaster } from "sonner";
import { useAuthStore } from "../stores/authStore";
import { useWebSocketStore } from "../stores/websocketStore";

// Create a client
const queryClient = new QueryClient({
	defaultOptions: {
		queries: {
			staleTime: 30000, // 30 seconds
			gcTime: 5 * 60 * 1000, // 5 minutes
			retry: 1,
			refetchOnWindowFocus: false,
		},
		mutations: {
			retry: 1,
		},
	},
});

function WebSocketInitializer() {
	const connect = useWebSocketStore((state) => state.connect);
	const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

	useEffect(() => {
		// Connect to WebSocket if authenticated
		if (isAuthenticated) {
			connect();
		}
	}, [isAuthenticated, connect]);

	return null;
}

export function AppProviders({ children }: { children: React.ReactNode }) {
	return (
		<QueryClientProvider client={queryClient}>
			<WebSocketInitializer />
			{children}
			<Toaster position="top-right" />
			{import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
		</QueryClientProvider>
	);
}
