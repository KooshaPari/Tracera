import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect } from "react";
import { appProvidersDeps } from "./app-providers-deps";

const {
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
} = appProvidersDeps;

const MINUTE_MS = 60_000;
const DEFAULT_RETRY_COUNT = 1;
const QUERY_STALE_MINUTES = 2;
const QUERY_CACHE_MINUTES = 10;
const MAX_CLIENT_ID_LOG_LENGTH = 20;
const SLICE_START_INDEX = 0;
const DEFAULT_API_HOSTNAME = "(default: api.workos.com)";
const AUTH_CALLBACK_PATH = "/auth/callback";
const AUTH_DOMAIN_ENV = "VITE_WORKOS_AUTH_DOMAIN";
const CLIENT_ID_ENV = "VITE_WORKOS_CLIENT_ID";

const buildQueryClient = () =>
	new QueryClient({
		defaultOptions: {
			mutations: {
				retry: DEFAULT_RETRY_COUNT,
			},
			queries: {
				gcTime: QUERY_CACHE_MINUTES * MINUTE_MS,
				refetchOnMount: false,
				refetchOnReconnect: false,
				refetchOnWindowFocus: false,
				retry: DEFAULT_RETRY_COUNT,
				staleTime: QUERY_STALE_MINUTES * MINUTE_MS,
				structuralSharing: true,
			},
		},
	});

const queryClient = buildQueryClient();

const getWorkosClientId = () => import.meta.env[CLIENT_ID_ENV];

const getWorkosAuthDomain = () => import.meta.env[AUTH_DOMAIN_ENV];

const getClientIdStatus = (workosClientId) => {
	if (workosClientId) {
		return "Found";
	}
	return "Missing";
};

const getTokenStorageLabel = () => {
	if (import.meta.env.DEV) {
		return "localStorage (devMode)";
	}
	return "HttpOnly Cookies";
};

const logWorkosConfig = (workosClientId, workosAuthDomain) => {
	if (!import.meta.env.DEV) {
		return;
	}

	logger.info(
		"[AppProviders] WorkOS Client ID:",
		getClientIdStatus(workosClientId),
	);
	logger.info("[AppProviders] Token Storage:", getTokenStorageLabel());

	if (!import.meta.env.DEV && !workosAuthDomain) {
		logger.warn(
			"[AppProviders] Production mode requires VITE_WORKOS_AUTH_DOMAIN for HttpOnly cookies",
		);
	}
};

const buildProviderProps = (workosClientId, workosAuthDomain) => {
	const providerProps = {
		clientId: workosClientId,
		devMode: import.meta.env.DEV,
	};

	if (!import.meta.env.DEV && workosAuthDomain) {
		providerProps.apiHostname = workosAuthDomain;
	}

	if (typeof globalThis !== "undefined" && globalThis.location) {
		providerProps.redirectUri = `${globalThis.location.origin}${AUTH_CALLBACK_PATH}`;
	}

	return providerProps;
};

const logProviderProps = (providerProps) => {
	if (!import.meta.env.DEV) {
		return;
	}

	const clientIdPreview = `${providerProps.clientId.slice(
		SLICE_START_INDEX,
		MAX_CLIENT_ID_LOG_LENGTH,
	)}...`;
	const apiHostname = providerProps.apiHostname || DEFAULT_API_HOSTNAME;

	logger.info("[AppProviders] AuthKitProvider props:", {
		apiHostname,
		clientId: clientIdPreview,
		devMode: providerProps.devMode,
		redirectUri: providerProps.redirectUri,
	});
};

const buildContent = (children) => {
	const devtools = (() => {
		if (import.meta.env.DEV) {
			return <ReactQueryDevtools initialIsOpen={false} />;
		}
	})();

	return (
		<QueryClientProvider client={queryClient}>
			<WebSocketInitializer />
			{children}
			<Toaster position="top-right" />
			{devtools}
		</QueryClientProvider>
	);
};

const createTokenGetter = (isSignedIn, getAccessToken) => {
	if (!isSignedIn) {
		return () => undefined;
	}

	return () => getAccessToken();
};

const WebSocketInitializer = () => {
	const { getAccessToken, user } = useAuth();
	const connect = useWebSocketStore((state) => state.connect);
	const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
	const isConnected = useWebSocketStore((state) => state.isConnected);
	const isSignedIn = Boolean(user);

	useEffect(() => {
		initializeCSRF();
	}, []);

	useEffect(() => {
		const tokenGetter = createTokenGetter(isSignedIn, getAccessToken);
		getWebSocketManager(tokenGetter);
	}, [getAccessToken, isSignedIn]);

	useEffect(() => {
		if (!isAuthenticated || !isSignedIn || isConnected) {
			return;
		}

		Promise.resolve(connect());
	}, [connect, isAuthenticated, isConnected, isSignedIn]);

	return null;
};

const shouldUseAuthKit = (workosClientId) => {
	if (!workosClientId) {
		return false;
	}
	return Boolean(workosClientId.trim());
};

const renderAuthKitProvider = (content, workosClientId, workosAuthDomain) => {
	const providerProps = buildProviderProps(workosClientId, workosAuthDomain);

	logProviderProps(providerProps);

	return (
		<AuthKitProvider
			apiHostname={providerProps.apiHostname}
			clientId={providerProps.clientId}
			devMode={providerProps.devMode}
			redirectUri={providerProps.redirectUri}
		>
			{content}
			<AuthKitSync />
		</AuthKitProvider>
	);
};

const warnMissingClientId = () => {
	if (import.meta.env.DEV) {
		logger.warn(
			"[AppProviders] VITE_WORKOS_CLIENT_ID is not set. AuthKit features will not work.",
		);
	}
};

const AppProviders = ({ children }) => {
	const workosClientId = getWorkosClientId();
	const workosAuthDomain = getWorkosAuthDomain();

	logWorkosConfig(workosClientId, workosAuthDomain);

	const content = buildContent(children);

	if (shouldUseAuthKit(workosClientId)) {
		return renderAuthKitProvider(content, workosClientId, workosAuthDomain);
	}

	warnMissingClientId();

	return content;
};

export { AppProviders };
