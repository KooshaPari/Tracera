import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuthStore } from "@/stores/authStore";

export interface Notification {
	id: string;
	type: "info" | "success" | "warning" | "error";
	title: string;
	message: string;
	link?: string;
	read_at?: string;
	created_at: string;
}

export function useNotifications() {
	const { token } = useAuthStore();
	const queryClient = useQueryClient();
	const API_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";

	const query = useQuery({
		queryKey: ["notifications"],
		queryFn: async () => {
			if (!token) return [];
			const response = await fetch(`${API_URL}/api/v1/notifications/`, {
				headers: { Authorization: `Bearer ${token}` },
			});
			// 404 = notifications API not implemented yet; treat as empty list
			if (response.status === 404) return [];
			if (!response.ok) throw new Error("Failed to fetch notifications");
			return response.json() as Promise<Notification[]>;
		},
		enabled: !!token,
		refetchInterval: 30000, // Poll every 30s
	});

	const markAsRead = useMutation({
		mutationFn: async (id: string) => {
			await fetch(`${API_URL}/api/v1/notifications/${id}/read`, {
				method: "POST",
				headers: { Authorization: `Bearer ${token}` },
			});
		},
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["notifications"] });
		},
	});

	const markAllRead = useMutation({
		mutationFn: async () => {
			await fetch(`${API_URL}/api/v1/notifications/read-all`, {
				method: "POST",
				headers: { Authorization: `Bearer ${token}` },
			});
		},
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["notifications"] });
		},
	});

	const unreadCount = query.data?.filter((n) => !n.read_at).length || 0;

	return {
		notifications: query.data || [],
		isLoading: query.isLoading,
		unreadCount,
		markAsRead,
		markAllRead,
	};
}
