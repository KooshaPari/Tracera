import { create } from "zustand";
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

export interface User {
	id: string;
	email: string;
	name?: string;
	avatar?: string;
	role?: string;
	metadata?: Record<string, any>;
}

interface AuthState {
	// Auth state
	user: User | null;
	token: string | null;
	isAuthenticated: boolean;
	isLoading: boolean;

	// Actions
	setUser: (user: User | null) => void;
	setToken: (token: string | null) => void;
	login: (email: string, password: string) => Promise<void>;
	logout: () => void;
	refreshToken: () => Promise<void>;
	updateProfile: (updates: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
	persist(
		(set, get) => ({
			// Initial state
			user: null,
			token: null,
			isAuthenticated: false,
			isLoading: false,

			// Actions
			setUser: (user) => {
				set({
					user,
					isAuthenticated: !!user,
				});
			},

			setToken: (token) => {
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

			login: async (email, _password) => {
				set({ isLoading: true });
				try {
					// TODO: Implement actual login API call
					// For now, mock authentication
					if (!email || !_password) {
						throw new Error("Email and password are required");
					}

					const userName = email.split("@")[0];
					const mockUser: User = {
						id: "1",
						email,
						...(userName && { name: userName }),
					};
					const mockToken = "mock-jwt-token";

					get().setToken(mockToken);
					get().setUser(mockUser);
				} catch (error) {
					set({ user: null, token: null, isAuthenticated: false });
					console.error("Login failed:", error);
					throw error;
				} finally {
					set({ isLoading: false });
				}
			},

			logout: () => {
				get().setToken(null);
				get().setUser(null);
				set({ isAuthenticated: false });
			},

			refreshToken: async () => {
				// TODO: Implement token refresh logic
				console.log("Token refresh not implemented yet");
			},

			updateProfile: (updates) => {
				const currentUser = get().user;
				if (currentUser) {
					set({
						user: { ...currentUser, ...updates },
					});
				}
			},
		}),
		{
			name: "tracertm-auth-store",
			storage: createJSONStorage(() => getStorage()),
			partialize: (state) => ({
				user: state.user,
				token: state.token,
				isAuthenticated: state.isAuthenticated,
			}),
		},
	),
);
