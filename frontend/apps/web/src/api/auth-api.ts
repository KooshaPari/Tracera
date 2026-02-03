import authConstants from "./auth-constants";
import client from "./client";
import {
	ensureCSRFToken,
	getStoredToken,
	handleAuthResponse,
} from "./auth-utils";
import { AuthError } from "./auth-types";
import type {
	AuthResponse,
	ChangePasswordRequest,
	LoginRequest,
	ResetPasswordConfirm,
	ResetPasswordRequest,
	UpdateUserProfileRequest,
	User,
} from "./auth-types";

const apiClient = client.apiClient;
const safeApiCall = client.safeApiCall;

const get = apiClient.GET.bind(apiClient);
const post = apiClient.POST.bind(apiClient);
const put = apiClient.PUT.bind(apiClient);
const del = apiClient.DELETE.bind(apiClient);

const fetchCurrentUser = (): Promise<User> =>
	handleAuthResponse(
		safeApiCall(
			get("/api/v1/auth/me", {
				params: { query: {} },
			}),
		),
	);

type AuthApi = {
	changePassword: (request: ChangePasswordRequest) => Promise<void>;
	confirmPasswordReset: (request: ResetPasswordConfirm) => Promise<void>;
	deleteAccount: () => Promise<void>;
	getCurrentUser: () => Promise<User | undefined>;
	login: (credentials: LoginRequest) => Promise<AuthResponse>;
	logout: () => Promise<void>;
	refresh: () => Promise<AuthResponse>;
	requestEmailVerification: () => Promise<void>;
	requestPasswordReset: (request: ResetPasswordRequest) => Promise<void>;
	updateProfile: (updates: UpdateUserProfileRequest) => Promise<User>;
	verifyEmail: (token: string) => Promise<void>;
};

const authApi: AuthApi = {
	changePassword: async (request: ChangePasswordRequest): Promise<void> => {
		await ensureCSRFToken();
		await handleAuthResponse(
			safeApiCall(
				post("/api/v1/auth/change-password", {
					body: request,
				}),
			),
		);
	},
	confirmPasswordReset: async (request: ResetPasswordConfirm): Promise<void> => {
		await ensureCSRFToken();
		await handleAuthResponse(
			safeApiCall(
				post("/api/v1/auth/reset-password/confirm", {
					body: request,
				}),
			),
		);
	},
	deleteAccount: async (): Promise<void> => {
		await ensureCSRFToken();
		await handleAuthResponse(
			safeApiCall(
				del("/api/v1/auth/account", {
					params: { query: {} },
				}),
			),
		);
	},
	getCurrentUser: async (): Promise<User | undefined> => {
		const token = getStoredToken();
		if (token === undefined) {
			return undefined;
		}
		try {
			return await fetchCurrentUser();
		} catch (error) {
			if (
				error instanceof AuthError &&
				error.statusCode === authConstants.httpUnauthorized
			) {
				return undefined;
			}
			throw error;
		}
	},
	login: async (credentials: LoginRequest): Promise<AuthResponse> => {
		await ensureCSRFToken();
		return handleAuthResponse(
			safeApiCall(
				post("/api/v1/auth/login", {
					body: credentials,
				}),
			),
		);
	},
	logout: async (): Promise<void> => {
		await ensureCSRFToken();
		await handleAuthResponse(
			safeApiCall(
				post("/api/v1/auth/logout", {
					body: {},
				}),
			),
		);
	},
	refresh: async (): Promise<AuthResponse> => {
		await ensureCSRFToken();
		return handleAuthResponse(
			safeApiCall(
				post("/api/v1/auth/refresh", {
					body: {},
				}),
			),
		);
	},
	requestEmailVerification: async (): Promise<void> => {
		await ensureCSRFToken();
		await handleAuthResponse(
			safeApiCall(
				post("/api/v1/auth/request-verification", {
					body: {},
				}),
			),
		);
	},
	requestPasswordReset: async (request: ResetPasswordRequest): Promise<void> => {
		await ensureCSRFToken();
		await handleAuthResponse(
			safeApiCall(
				post("/api/v1/auth/reset-password", {
					body: request,
				}),
			),
		);
	},
	updateProfile: async (updates: UpdateUserProfileRequest): Promise<User> => {
		await ensureCSRFToken();
		return handleAuthResponse(
			safeApiCall(
				put("/api/v1/auth/profile", {
					body: updates,
				}),
			),
		);
	},
	verifyEmail: async (token: string): Promise<void> => {
		await ensureCSRFToken();
		await handleAuthResponse(
			safeApiCall(
				post("/api/v1/auth/verify-email", {
					body: { token },
				}),
			),
		);
	},
};

export { authApi, type AuthApi };
