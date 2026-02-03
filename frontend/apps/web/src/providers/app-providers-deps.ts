import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { AuthKitProvider, useAuth } from "@workos-inc/authkit-react";
import { logger } from "@/lib/logger";
import { Toaster } from "sonner";
import { getWebSocketManager } from "../api/websocket";
import { AuthKitSync } from "../components/auth/AuthKitSync";
import { initializeCSRF } from "../lib/csrf";
import { useAuthStore } from "../stores/authStore";
import { useWebSocketStore } from "../stores/websocketStore";

const appProvidersDeps = {
	AuthKitProvider,
	AuthKitSync,
	ReactQueryDevtools,
	Toaster,
	getWebSocketManager,
	initializeCSRF,
	logger,
	useAuth,
	useAuthStore,
	useWebSocketStore,
};

export default appProvidersDeps;
