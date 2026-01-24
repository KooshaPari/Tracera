// Date formatting utilities
export function formatDate(
	date: string | Date,
	format: "short" | "long" | "relative" = "short",
): string {
	const d = typeof date === "string" ? new Date(date) : date;

	if (format === "relative") {
		return formatRelativeTime(d);
	}

	const options: Intl.DateTimeFormatOptions =
		format === "long"
			? {
					year: "numeric",
					month: "long",
					day: "numeric",
					hour: "2-digit",
					minute: "2-digit",
				}
			: { year: "numeric", month: "short", day: "numeric" };

	return d.toLocaleDateString("en-US", options);
}

export function formatRelativeTime(date: Date): string {
	const now = new Date();
	const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

	if (diffInSeconds < 60) return "just now";
	if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
	if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
	if (diffInSeconds < 604800)
		return `${Math.floor(diffInSeconds / 86400)}d ago`;
	if (diffInSeconds < 2592000)
		return `${Math.floor(diffInSeconds / 604800)}w ago`;

	return formatDate(date, "short");
}

export function formatTime(date: string | Date): string {
	const d = typeof date === "string" ? new Date(date) : date;
	return d.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
}

// Number formatting utilities
export function formatNumber(
	num: number,
	options?: Intl.NumberFormatOptions,
): string {
	return new Intl.NumberFormat("en-US", options).format(num);
}

export function formatPercentage(
	value: number,
	total: number,
	decimals: number = 0,
): string {
	if (total === 0) return "0%";
	const percentage = (value / total) * 100;
	return `${percentage.toFixed(decimals)}%`;
}

export function formatBytes(bytes: number, decimals: number = 2): string {
	if (bytes === 0) return "0 Bytes";

	const k = 1024;
	const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
	const i = Math.floor(Math.log(bytes) / Math.log(k));

	return `${parseFloat((bytes / k ** i).toFixed(decimals))} ${sizes[i]}`;
}

// String formatting utilities
export function truncate(
	text: string,
	length: number,
	suffix: string = "...",
): string {
	if (text.length <= length) return text;
	return text.slice(0, length - suffix.length) + suffix;
}

export function capitalize(text: string): string {
	return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
}

export function titleCase(text: string): string {
	return text
		.split(" ")
		.map((word) => capitalize(word))
		.join(" ");
}

export function kebabCase(text: string): string {
	return text
		.toLowerCase()
		.replace(/\s+/g, "-")
		.replace(/[^\w-]/g, "");
}

export function camelCase(text: string): string {
	return text
		.toLowerCase()
		.replace(/[^a-zA-Z0-9]+(.)/g, (_, chr) => chr.toUpperCase());
}

// Status formatting
export function formatStatus(status: string): string {
	return status
		.split("_")
		.map((word) => capitalize(word))
		.join(" ");
}

// Priority formatting with colors
export function getPriorityColor(priority: string): string {
	const colors: Record<string, string> = {
		critical: "red",
		high: "orange",
		medium: "yellow",
		low: "green",
	};
	return colors[priority.toLowerCase()] || "gray";
}

// Status formatting with colors
export function getStatusColor(status: string): string {
	const colors: Record<string, string> = {
		todo: "gray",
		in_progress: "blue",
		done: "green",
		blocked: "red",
		cancelled: "gray",
	};
	return colors[status.toLowerCase()] || "gray";
}

// Duration formatting
export function formatDuration(seconds: number): string {
	if (seconds < 60) return `${seconds}s`;
	if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;

	const hours = Math.floor(seconds / 3600);
	const minutes = Math.floor((seconds % 3600) / 60);
	return `${hours}h ${minutes}m`;
}
