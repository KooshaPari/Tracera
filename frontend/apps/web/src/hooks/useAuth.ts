import type { User } from "../stores/authStore";
import { useAuthStore } from "../stores/authStore";

export function useAuth() {
	const {
		user,
		token,
		isAuthenticated,
		isLoading,
		login,
		logout,
		refreshToken,
		updateProfile,
	} = useAuthStore();

	return {
		user,
		token,
		isAuthenticated,
		isLoading,
		login,
		logout,
		refreshToken,
		updateProfile,
	};
}

export function useUser(): User | null {
	return useAuthStore((state) => state.user);
}

export function useIsAuthenticated(): boolean {
	return useAuthStore((state) => state.isAuthenticated);
}
