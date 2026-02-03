// Time constants for relative/duration formatting
const MS_PER_SEC = 1000;
const SEC_PER_MIN = 60;
const SEC_PER_HOUR = 3600;
const SEC_PER_DAY = 86_400;
const SEC_PER_WEEK = 604_800;
const SEC_PER_MONTH = 2_592_000;
const PERCENT_DENOM = 100;
const BYTES_K = 1024;

// Date formatting utilities
export const formatDate = (
	date: string | Date,
	format: "short" | "long" | "relative" = "short",
): string => {
	const d = typeof date === "string" ? new Date(date) : date;

	if (format === "relative") {
		return formatRelativeTime(d);
	}

	const options: Intl.DateTimeFormatOptions =
		format === "long"
			? {
					day: "numeric",
					hour: "2-digit",
					minute: "2-digit",
					month: "long",
					year: "numeric",
				}
			: { day: "numeric", month: "short", year: "numeric" };

	return d.toLocaleDateString("en-US", options);
};

export const formatRelativeTime = (date: Date): string => {
	const now = new Date();
	const diffInSeconds = Math.floor(
		(now.getTime() - date.getTime()) / MS_PER_SEC,
	);

	if (diffInSeconds < SEC_PER_MIN) {
		return "just now";
	}
	if (diffInSeconds < SEC_PER_HOUR) {
		return `${Math.floor(diffInSeconds / SEC_PER_MIN)}m ago`;
	}
	if (diffInSeconds < SEC_PER_DAY) {
		return `${Math.floor(diffInSeconds / SEC_PER_HOUR)}h ago`;
	}
	if (diffInSeconds < SEC_PER_WEEK) {
		return `${Math.floor(diffInSeconds / SEC_PER_DAY)}d ago`;
	}
	if (diffInSeconds < SEC_PER_MONTH) {
		return `${Math.floor(diffInSeconds / SEC_PER_WEEK)}w ago`;
	}

	return formatDate(date, "short");
};

export const formatTime = (date: string | Date): string => {
	const d = typeof date === "string" ? new Date(date) : date;
	return d.toLocaleTimeString("en-US", {
		hour: "2-digit",
		minute: "2-digit",
	});
};

// Number formatting utilities
export const formatNumber = (
	num: number,
	options?: Intl.NumberFormatOptions,
): string => new Intl.NumberFormat("en-US", options).format(num);

export const formatPercentage = (
	value: number,
	total: number,
	decimals = 0,
): string => {
	if (total === 0) {
		return "0%";
	}
	const percentage = (value / total) * PERCENT_DENOM;
	return `${percentage.toFixed(decimals)}%`;
};

export const formatBytes = (bytes: number, decimals = 2): string => {
	if (bytes === 0) {
		return "0 Bytes";
	}

	const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
	const i = Math.floor(Math.log(bytes) / Math.log(BYTES_K));

	return `${Number.parseFloat((bytes / BYTES_K ** i).toFixed(decimals))} ${sizes[i]}`;
};

// String formatting utilities
export const truncate = (
	text: string,
	length: number,
	suffix = "...",
): string => {
	if (text.length <= length) {
		return text;
	}
	return text.slice(0, length - suffix.length) + suffix;
};

export const capitalize = (text: string): string =>
	text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();

export const titleCase = (text: string): string =>
	text
		.split(" ")
		.map((word) => capitalize(word))
		.join(" ");

export const kebabCase = (text: string): string =>
	text
		.toLowerCase()
		.replaceAll(/\s+/g, "-")
		.replaceAll(/[^\w-]/g, "");

export const camelCase = (text: string): string =>
	text
		.toLowerCase()
		.replaceAll(/[^a-zA-Z0-9]+(.)/g, (_, chr) => chr.toUpperCase());

// Status formatting
export const formatStatus = (status: string): string =>
	status
		.split("_")
		.map((word) => capitalize(word))
		.join(" ");

// Priority formatting with colors
export const getPriorityColor = (priority: string): string => {
	const colors: Record<string, string> = {
		critical: "red",
		high: "orange",
		low: "green",
		medium: "yellow",
	};
	return colors[priority.toLowerCase()] || "gray";
};

// Status formatting with colors
export const getStatusColor = (status: string): string => {
	const colors: Record<string, string> = {
		blocked: "red",
		cancelled: "gray",
		done: "green",
		in_progress: "blue",
		todo: "gray",
	};
	return colors[status.toLowerCase()] || "gray";
};

// Duration formatting
export const formatDuration = (seconds: number): string => {
	if (seconds < SEC_PER_MIN) {
		return `${seconds}s`;
	}
	if (seconds < SEC_PER_HOUR) {
		return `${Math.floor(seconds / SEC_PER_MIN)}m ${seconds % SEC_PER_MIN}s`;
	}

	const hours = Math.floor(seconds / SEC_PER_HOUR);
	const minutes = Math.floor((seconds % SEC_PER_HOUR) / SEC_PER_MIN);
	return `${hours}h ${minutes}m`;
};
