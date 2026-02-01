import { create } from "zustand";
import { logger } from '@/lib/logger';
import { createJSONStorage, persist } from "zustand/middleware";

// SSR-safe storage that only accesses localStorage on the client
const noopStorage = {
	getItem: (_key: string) => null,
	setItem: (_key: string, _value: string) => {},
	removeItem: (_key: string) => {},
};

const getStorage = () => {
	// Check if we're in a browser environment with proper localStorage
	if (
		typeof window === "undefined" ||
		typeof localStorage === "undefined" ||
		typeof localStorage.getItem !== "function"
	) {
		return noopStorage;
	}
	return localStorage;
};

/**
 * User metadata from authentication
 */
export interface UserMetadata {
	[key: string]: string | number | boolean | object | null | undefined;
}

export interface User {
	id: string;
	email: string;
	name?: string;
	avatar?: string;
	role?: string;
	metadata?: UserMetadata;
}

export interface Account {
	id: string;
	name: string;
	slug: string;
	account_type: string;
}

interface AuthState {
	// Auth state
	user: User | null;
	token: string | null;
	account: Account | null;
	isAuthenticated: boolean;
	isLoading: boolean;
	refreshTimer: NodeJS.Timeout | null;

	// Actions
	setUser: (user: User | null) => void;
	setToken: (token: string | null) => void;
	setAccount: (account: Account | null) => void;
	login: (email: string, password: string) => Promise<void>;
	logout: () => Promise<void>;
	validateSession: () => Promise<boolean>;
	refreshToken: () => Promise<void>;
	updateProfile: (updates: Partial<User>) => void;
	setAuthFromWorkOS: (user: User | null, token: string | null) => void;
	switchAccount: (accountId: string) => Promise<void>;
	initializeAutoRefresh: () => void;
	stopAutoRefresh: () => void;
}

export const useAuthStore = create<AuthState>()(
	persist(
		(set, get) => ({
			// Initial state
			user: null,
			token: null,
			account: null,
			isAuthenticated: false,
			isLoading: false,
			refreshTimer: null,

			// Actions
			setUser: (user) => {
				set({
					user,
					isAuthenticated: !!user,
				});
			},

			setToken: (token) => {
				/**
				 * Token Storage Strategy:
				 *
				 * Development (devMode=true):
				 * - WorkOS SDK manages tokens in localStorage
				 * - This store mirrors the token for state management
				 * - Acceptable for development without custom domain
				 *
				 * Production (devMode=false):
				 * - WorkOS SDK uses HttpOnly cookies (requires custom auth domain)
				 * - This localStorage token becomes a fallback/cache
				 * - Backend validates actual HttpOnly cookie tokens
				 *
				 * The token here is primarily for:
				 * 1. State management (isAuthenticated checks)
				 * 2. Development mode compatibility
				 * 3. Backwards compatibility with existing code
				 */
				// Treat empty string as null
				const normalizedToken = token?.trim() ? token : null;
				if (typeof localStorage !== "undefined") {
					if (normalizedToken) {
						localStorage.setItem("auth_token", normalizedToken);
					} else {
						localStorage.removeItem("auth_token");
					}
				}
				set({ token: normalizedToken });
			},

			login: async (email, password) => {
				set({ isLoading: true });
				try {
					if (!email || !password) {
						throw new Error("Email and password are required");
					}

					const API_URL =
						import.meta.env.VITE_API_URL || "http://localhost:4000";
					const response = await fetch(`${API_URL}/api/v1/auth/login`, {
						method: "POST",
						headers: { "Content-Type": "application/json" },
						credentials: "include", // Important for HttpOnly cookies
						body: JSON.stringify({ email, password }),
					});

					if (!response.ok) {
						const errorData = await response
							.json()
							.catch(() => ({ detail: "Login failed" }));
						throw new Error(
							errorData.detail || `Login failed: ${response.status}`,
						);
					}

					const data = (await response.json()) as {
						user: User;
						access_token?: string;
					};

					if (!data.user) {
						throw new Error("Invalid response from login endpoint");
					}

					get().setUser(data.user);
					// Store token if provided in response
					if (data.access_token) {
						get().setToken(data.access_token);
					}

					// Start auto-refresh on successful login
					get().initializeAutoRefresh();
				} catch (error) {
					set({ user: null, token: null, isAuthenticated: false });
					logger.error("Login failed:", error);
					throw error;
				} finally {
					set({ isLoading: false });
				}
			},

			logout: async () => {
				try {
					// Stop auto-refresh
					get().stopAutoRefresh();

					// Call logout endpoint to clear server-side session
					const API_URL =
						import.meta.env.VITE_API_URL || "http://localhost:4000";
					await fetch(`${API_URL}/api/v1/auth/logout`, {
						method: "POST",
						credentials: "include",
						headers: {
							"Content-Type": "application/json",
						},
					}).catch(() => {
						// Ignore errors during logout - proceed with local cleanup
						logger.warn("Logout API call failed, clearing local state");
					});
				} catch (error) {
					logger.error("Logout error:", error);
				} finally {
					// Clear local state regardless of API success
					get().setToken(null);
					get().setUser(null);
					set({ isAuthenticated: false });
				}
			},

			validateSession: async () => {
				try {
					const token = get().token?.trim();
					// Don't call /auth/me without a token — backend returns 401
					if (!token) {
						return false;
					}
					const API_URL =
						import.meta.env.VITE_API_URL || "http://localhost:4000";
					const headers: Record<string, string> = {
						"Content-Type": "application/json",
						Authorization: `Bearer ${token}`,
					};
					const res = await fetch(`${API_URL}/api/v1/auth/me`, {
						method: "GET",
						credentials: "include", // Send HttpOnly cookies
						headers,
					});

					if (res.status === 401) {
						// Session expired
						await get().logout();
						return false;
					}

					if (!res.ok) {
						throw new Error(`Session validation failed: ${res.status}`);
					}

					const data = (await res.json()) as { user?: User; account?: Account };
					if (data.user) {
						get().setUser(data.user);
					}
					if (data.account) {
						get().setAccount(data.account);
					}

					return true;
				} catch (error) {
					logger.error("Session validation error:", error);
					await get().logout();
					return false;
				}
			},

			refreshToken: async () => {
				try {
					const API_URL =
						import.meta.env.VITE_API_URL || "http://localhost:4000";
					const response = await fetch(`${API_URL}/api/v1/auth/refresh`, {
						method: "POST",
						credentials: "include",
						headers: {
							"Content-Type": "application/json",
						},
					});

					if (!response.ok) {
						// If refresh fails, logout the user
						await get().logout();
						return;
					}

					const data = (await response.json()) as {
						user?: User;
						access_token?: string;
					};

					if (data.user) {
						get().setUser(data.user);
					}
					if (data.access_token) {
						get().setToken(data.access_token);
					}
				} catch (error) {
					logger.error("Token refresh failed:", error);
					await get().logout();
				}
			},

			updateProfile: (updates) => {
				const currentUser = get().user;
				if (currentUser) {
					set({
						user: { ...currentUser, ...updates },
					});
				}
			},

			setAuthFromWorkOS: (user, token) => {
				get().setUser(user);
				if (token) {
					get().setToken(token);
				}
				// Start auto-refresh
				get().initializeAutoRefresh();
			},

			setAccount: (account) => {
				set({ account });
			},

			switchAccount: async (accountId: string) => {
				if (!get().user) {
					throw new Error("Not authenticated");
				}

				try {
					const API_URL =
						import.meta.env.VITE_API_URL || "http://localhost:4000";
					const res = await fetch(
						`${API_URL}/api/v1/accounts/${accountId}/switch`,
						{
							method: "POST",
							credentials: "include", // Send HttpOnly cookies
							headers: {
								"Content-Type": "application/json",
							},
						},
					);

					if (!res.ok) {
						throw new Error("Failed to switch account");
					}

					const data = (await res.json()) as { account?: Account };
					if (data.account) {
						get().setAccount(data.account);
					}
				} catch (error) {
					logger.error("Failed to switch account:", error);
					throw error;
				}
			},

			initializeAutoRefresh: () => {
				// Stop existing timer if any
				get().stopAutoRefresh();

				// Start new timer to refresh token every 20 minutes (1200000ms)
				const timer = setInterval(
					() => {
						get().refreshToken();
					},
					20 * 60 * 1000,
				);

				set({ refreshTimer: timer });
			},

			stopAutoRefresh: () => {
				const timer = get().refreshTimer;
				if (timer) {
					clearInterval(timer);
					set({ refreshTimer: null });
				}
			},
		}),
		{
			name: "tracertm-auth-store",
			storage: createJSONStorage(() => getStorage()),
			partialize: (state) => ({
				user: state.user,
				token: state.token,
				account: state.account,
				isAuthenticated: state.isAuthenticated,
			}),
		},
	),
);
