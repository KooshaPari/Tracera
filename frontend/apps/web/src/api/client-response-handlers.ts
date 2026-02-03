/* eslint-disable promise/prefer-await-to-then */
import { logger } from "@/lib/logger";
import { extractCSRFTokenFromResponse, handleCSRFError } from "../lib/csrf";
import { useConnectionStatusStore } from "../stores/connection-status-store";
import { apiConstants } from "./client-constants";

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

const isRecordObject = (value: unknown): value is Record<string, unknown> =>
	Object.prototype.toString.call(value) === "[object Object]";

const parseJsonObject = async (
	response: Response,
): Promise<Record<string, unknown>> => {
	try {
		const data = await response.clone().json();
		if (isRecordObject(data)) {
			return data;
		}
		return {};
	} catch {
		return {};
	}
};

const parseIntegrationAuthBody = async (
	response: Response,
): Promise<IntegrationAuthBody> => {
	const data = await parseJsonObject(response);
	const code = typeof data["code"] === "string" ? data["code"] : undefined;
	const detail =
		typeof data["detail"] === "string" ? data["detail"] : undefined;
	return { code, detail };
};

const parseRateLimitBody = async (
	response: Response,
): Promise<RateLimitBody> => {
	const data = await parseJsonObject(response);
	const detail =
		typeof data["detail"] === "string" ? data["detail"] : undefined;
	const retryAfter =
		typeof data["retry_after"] === "number" ? data["retry_after"] : undefined;
	return { detail, retry_after: retryAfter };
};

const showToast = (
	title: string,
	description: string,
	action?: ToastAction,
): Promise<boolean> => {
	if (!globalThis.window) {
		return Promise.resolve(false);
	}

	return import("sonner").then(({ toast }) => {
		const toastOptions: ToastOptions = { description };
		if (action) {
			toastOptions.action = action;
		}
		toast.error(title, toastOptions);
		return true;
	});
};

const handleCsrf = (response: Response): Promise<boolean> => {
	if (response.status !== apiConstants.statusForbidden) {
		return Promise.resolve(false);
	}

	return handleCSRFError(response.clone()).then((wasCsrfError) => {
		if (wasCsrfError) {
			logger.warn(
				"[API Client] CSRF token was refreshed, request may need to be retried",
			);
		}
		return wasCsrfError;
	});
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
		return body.detail ?? "Reconnect this integration in Settings.";
	}
	return null;
};

const isUnauthorizedResponse = (response: Response): boolean =>
	response.status === apiConstants.statusUnauthorized;

const isLoginFailureResponse = (response: Response): boolean =>
	response.url.includes(apiConstants.authLoginPath);

const handleUnauthorizedBody = (
	response: Response,
	handleLogout: () => void,
): Promise<boolean> => {
	return parseIntegrationAuthBody(response).then((body) => {
		const detail = getIntegrationAuthDetail(body);
		if (detail) {
			return showIntegrationAuthToast(detail);
		}
		logger.warn("[Auth] Session expired or invalid - redirecting to login");
		handleLogout();
		return true;
	});
};

const handleUnauthorized = (
	response: Response,
	handleLogout: () => void,
): Promise<boolean> => {
	if (!isUnauthorizedResponse(response)) {
		return Promise.resolve(false);
	}
	if (isLoginFailureResponse(response)) {
		return Promise.resolve(true);
	}
	return handleUnauthorizedBody(response, handleLogout);
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
	return body.retry_after ?? apiConstants.defaultRateLimitSeconds;
};

const buildRateLimitDetail = (seconds: number, body: RateLimitBody): string => {
	const message = buildRateLimitMessage(seconds);
	return body.detail ?? message;
};

const handleRateLimited = (response: Response): Promise<boolean> => {
	if (response.status !== apiConstants.statusRateLimited) {
		return Promise.resolve(false);
	}
	return parseRateLimitBody(response).then((body) => {
		const retryAfterHeader =
			response.headers.get(apiConstants.retryAfterHeader) ?? "";
		const seconds = resolveRateLimitSeconds(retryAfterHeader, body);
		const detail = buildRateLimitDetail(seconds, body);
		return showToast("Rate limited", detail).then(() => true);
	});
};

const handleForbidden = (
	response: Response,
	wasCsrfError: boolean,
): Promise<boolean> => {
	if (response.status === apiConstants.statusForbidden && !wasCsrfError) {
		return showToast(
			"Access denied",
			"You don't have permission for this action.",
		).then(() => true);
	}
	return Promise.resolve(false);
};

const handleNotFound = (response: Response): Promise<boolean> => {
	if (response.status !== apiConstants.statusNotFound) {
		return Promise.resolve(false);
	}
	return parseIntegrationAuthBody(response).then((body) => {
		if (body.code === "integration_not_found") {
			const detail = body.detail ?? "The requested item was not found.";
			return showToast("Resource not found", detail);
		}
		return false;
	});
};

const handleServerError = (response: Response): Promise<boolean> => {
	if (response.status < apiConstants.statusServerError) {
		return Promise.resolve(false);
	}
	const message = `Backend error ${response.status}`;
	useConnectionStatusStore.getState().setLost(message);
	return showToast(
		"Server error",
		"Connection issue. We'll retry; check back in a moment.",
	).then(() => true);
};

const handleNonCsrfResponses = (
	response: Response,
	wasCsrfError: boolean,
	handleLogout: () => void,
): Promise<void> => {
	return handleUnauthorized(response, handleLogout)
		.then(() => handleRateLimited(response))
		.then(() => handleForbidden(response, wasCsrfError))
		.then(() => handleNotFound(response))
		.then(() => handleServerError(response))
		.then(() => undefined);
};

const handleResponse = (
	response: Response,
	handleLogout: () => void,
): Promise<Response> => {
	extractCSRFTokenFromResponse(response);
	return handleCsrf(response).then((wasCsrfError) =>
		handleNonCsrfResponses(response, wasCsrfError, handleLogout).then(
			() => response,
		),
	);
};

const responseHandlers = {
	handleResponse,
};

export { responseHandlers };
