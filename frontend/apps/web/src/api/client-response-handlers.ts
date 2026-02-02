import {
	extractCSRFTokenFromResponse,
	handleCSRFError,
} from "../lib/csrf";
import { logger } from "@/lib/logger";
import { useConnectionStatusStore } from "../stores/connectionStatusStore";
import apiConstants from "./client-constants";

interface ToastAction {
	label: string;
	onClick: () => void;
}

interface ToastOptions {
	action?: ToastAction;
	description: string;
}

interface IntegrationAuthBody {
	code?: string;
	detail?: string;
}

interface RateLimitBody {
	detail?: string;
	retry_after?: number;
}

const parseJson = async <TData>(response: Response): Promise<TData> => {
	try {
		return (await response.clone().json()) as TData;
	} catch {
		return {} as TData;
	}
};

const showToast = async (
	title: string,
	description: string,
	action?: ToastAction,
): Promise<boolean> => {
	if (globalThis.window) {
		const { toast } = await import("sonner");
		const toastOptions: ToastOptions = {
			description,
		};

		if (action) {
			toastOptions.action = action;
		}

		toast.error(title, toastOptions);
		return true;
	}

	return false;
};

const handleCsrf = async (response: Response): Promise<boolean> => {
	if (response.status !== apiConstants.statusForbidden) {
		return false;
	}

	const wasCsrfError = await handleCSRFError(response.clone());
	if (wasCsrfError) {
		logger.warn(
			"[API Client] CSRF token was refreshed, request may need to be retried",
		);
	}
	return wasCsrfError;
};

const showIntegrationAuthToast = (detail: string): Promise<boolean> =>
	showToast("Connection expired", detail, {
		label: "Settings",
		onClick: () => {
			if (globalThis.window) {
				globalThis.window.location.href = apiConstants.settingsPath;
			}
		},
	});

const getIntegrationAuthDetail = (body: IntegrationAuthBody): string | null => {
	if (body.code === "integration_auth_required") {
		return body.detail || "Reconnect this integration in Settings.";
	}
	return null;
};

const handleUnauthorized = async (
	response: Response,
	handleLogout: () => void,
): Promise<boolean> => {
	if (response.status !== apiConstants.statusUnauthorized) {
		return false;
	}

	if (response.url.includes(apiConstants.authLoginPath)) {
		return true;
	}

	const body = await parseJson<IntegrationAuthBody>(response);
	const detail = getIntegrationAuthDetail(body);
	if (detail) {
		return showIntegrationAuthToast(detail);
	}

	logger.warn("[Auth] Session expired or invalid - redirecting to login");
	handleLogout();
	return true;
};

const buildRateLimitMessage = (seconds: number): string => {
	if (seconds >= apiConstants.secondsPerMinute) {
		return `Try again in ${Math.ceil(seconds / apiConstants.secondsPerMinute)} minute(s).`;
	}
	return `Try again in ${seconds} second(s).`;
};

const resolveRateLimitSeconds = (
	retryAfterHeader: string,
	body: RateLimitBody,
): number => {
	if (retryAfterHeader !== "") {
		return Number.parseInt(retryAfterHeader, 10);
	}
	if (body.retry_after) {
		return body.retry_after;
	}
	return apiConstants.defaultRateLimitSeconds;
};

const handleRateLimited = async (response: Response): Promise<boolean> => {
	if (response.status !== apiConstants.statusRateLimited) {
		return false;
	}

	const body = await parseJson<RateLimitBody>(response);
	const retryAfterHeader =
		response.headers.get(apiConstants.retryAfterHeader) || "";
	const seconds = resolveRateLimitSeconds(retryAfterHeader, body);

	const message = buildRateLimitMessage(seconds);
	const detail = body.detail || message;
	await showToast("Rate limited", detail);
	return true;
};

const handleForbidden = async (
	response: Response,
	wasCsrfError: boolean,
): Promise<boolean> => {
	if (response.status === apiConstants.statusForbidden && !wasCsrfError) {
		await showToast(
			"Access denied",
			"You don't have permission for this action.",
		);
		return true;
	}

	return false;
};

const handleNotFound = async (response: Response): Promise<boolean> => {
	if (response.status !== apiConstants.statusNotFound) {
		return false;
	}

	const body = await parseJson<IntegrationAuthBody>(response);
	if (body.code === "integration_not_found") {
		const detail = body.detail || "The requested item was not found.";
		return showToast("Resource not found", detail);
	}

	return false;
};

const handleServerError = async (response: Response): Promise<boolean> => {
	if (response.status < apiConstants.statusServerError) {
		return false;
	}

	const message = `Backend error ${response.status}`;
	useConnectionStatusStore.getState().setLost(message);
	await showToast(
		"Server error",
		"Connection issue. We'll retry; check back in a moment.",
	);
	return true;
};

const handleNonCsrfResponses = async (
	response: Response,
	wasCsrfError: boolean,
	handleLogout: () => void,
): Promise<void> => {
	await handleUnauthorized(response, handleLogout);
	await handleRateLimited(response);
	await handleForbidden(response, wasCsrfError);
	await handleNotFound(response);
	await handleServerError(response);
};

const handleResponse = async (
	response: Response,
	handleLogout: () => void,
): Promise<Response> => {
	extractCSRFTokenFromResponse(response);
	const wasCsrfError = await handleCsrf(response);
	await handleNonCsrfResponses(response, wasCsrfError, handleLogout);
	return response;
};

const responseHandlers = {
	handleResponse,
};

export default responseHandlers;
