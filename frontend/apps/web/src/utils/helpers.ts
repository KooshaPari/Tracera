// General helper utilities

import type { Item, Link } from "@tracertm/types";
import { logger } from "@/lib/logger";

// Array utilities
export function groupBy<T>(array: T[], key: keyof T): Record<string, T[]> {
	return array.reduce(
		(result, item) => {
			const groupKey = String(item[key]);
			if (!result[groupKey]) {
				result[groupKey] = [];
			}
			result[groupKey].push(item);
			return result;
		},
		{} as Record<string, T[]>,
	);
}

export function sortBy<T>(
	array: T[],
	key: keyof T,
	order: "asc" | "desc" = "asc",
): T[] {
	return [...array].toSorted((a: T, b: T) => {
		const aVal = a[key];
		const bVal = b[key];

		if (aVal < bVal) {
			return order === "asc" ? -1 : 1;
		}
		if (aVal > bVal) {
			return order === "asc" ? 1 : -1;
		}
		return 0;
	});
}

export function unique<T>(array: T[]): T[] {
	return [...new Set(array)];
}

export function chunk<T>(array: T[], size: number): T[][] {
	const chunks: T[][] = [];
	for (let i = 0; i < array.length; i += size) {
		chunks.push(array.slice(i, i + size));
	}
	return chunks;
}

export function shuffle<T>(array: T[]): T[] {
	const shuffled = [...array];
	for (let i = shuffled.length - 1; i > 0; i -= 1) {
		const j = Math.floor(Math.random() * (i + 1));
		const temp = shuffled[i];
		shuffled[i] = shuffled[j]!;
		shuffled[j] = temp!;
	}
	return shuffled;
}

// Object utilities
export function pick<T extends object, K extends keyof T>(
	obj: T,
	keys: K[],
): Pick<T, K> {
	const result = {} as Pick<T, K>;
	keys.forEach((key) => {
		if (key in obj) {
			result[key] = obj[key];
		}
	});
	return result;
}

export function omit<T extends object, K extends keyof T>(
	obj: T,
	keys: K[],
): Omit<T, K> {
	const result = { ...obj };
	keys.forEach((key) => {
		delete result[key];
	});
	return result;
}

export function deepClone<T>(obj: T): T {
	return structuredClone(obj);
}

export function isEmpty(obj: object): boolean {
	return Object.keys(obj).length === 0;
}

export function merge<T extends object>(
	target: T,
	...sources: Partial<T>[]
): T {
	return Object.assign({}, target, ...sources);
}

// String utilities
export function generateId(): string {
	return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export function slugify(text: string): string {
	return text
		.toLowerCase()
		.trim()
		.replaceAll(/[^\w\s-]/g, "")
		.replaceAll(/[\s_-]+/g, "-")
		.replaceAll(/^-+|-+$/g, "");
}

export function randomString(length: number): string {
	const chars =
		"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
	let result = "";
	for (let i = 0; i < length; i += 1) {
		result += chars.charAt(Math.floor(Math.random() * chars.length));
	}
	return result;
}

// Type guards
export function isNotNull<T>(value: T | null | undefined): value is T {
	return value !== null && value !== undefined;
}

export function isDefined<T>(value: T | undefined): value is T {
	return value !== undefined;
}

// Async utilities
export function sleep(ms: number): Promise<void> {
	return new Promise((resolve) => setTimeout(resolve, ms));
}

export function debounce<T extends (...args: never[]) => unknown>(
	func: T,
	wait: number,
): (...args: Parameters<T>) => void {
	let timeout: ReturnType<typeof setTimeout> | null = null;

	return function executedFunction(...args: Parameters<T>) {
		const later = () => {
			timeout = null;
			func(...args);
		};

		if (timeout) {
			clearTimeout(timeout);
		}
		timeout = setTimeout(later, wait);
	};
}

export function throttle<T extends (...args: never[]) => unknown>(
	func: T,
	limit: number,
): (...args: Parameters<T>) => void {
	let inThrottle = false;

	return function executedFunction(...args: Parameters<T>) {
		if (!inThrottle) {
			func(...args);
			inThrottle = true;
			setTimeout(() => (inThrottle = false), limit);
		}
	};
}

// TraceRTM specific utilities
export function getItemsByView(items: Item[], view: string): Item[] {
	return items.filter((item) => item.view === view);
}

export function getItemChildren(items: Item[], parentId: string): Item[] {
	return items.filter((item) => item.parentId === parentId);
}

export function getItemAncestors(items: Item[], itemId: string): Item[] {
	const ancestors: Item[] = [];
	let currentItem = items.find((item) => item.id === itemId);

	while (currentItem?.parentId) {
		const parent = items.find((item) => item.id === currentItem?.parentId);
		if (parent) {
			ancestors.unshift(parent);
			currentItem = parent;
		} else {
			break;
		}
	}

	return ancestors;
}

export function getLinkedItems(
	items: Item[],
	links: Link[],
	itemId: string,
): {
	sources: Item[];
	targets: Item[];
} {
	const sourceLinks = links.filter((link) => link.targetId === itemId);
	const targetLinks = links.filter((link) => link.sourceId === itemId);

	return {
		sources: sourceLinks
			.map((link) => items.find((item) => item.id === link.sourceId))
			.filter(isNotNull),
		targets: targetLinks
			.map((link) => items.find((item) => item.id === link.targetId))
			.filter(isNotNull),
	};
}

export function calculateProgress(items: Item[]): number {
	if (items.length === 0) {
		return 0;
	}
	const doneItems = items.filter((item) => item.status === "done").length;
	return (doneItems / items.length) * 100;
}

// Local storage utilities (SSR-safe)
const isLocalStorageAvailable = () =>
	typeof localStorage !== "undefined" &&
	typeof localStorage.getItem === "function";

export function getFromStorage<T>(key: string, defaultValue: T): T {
	if (!isLocalStorageAvailable()) {
		return defaultValue;
	}
	try {
		const item = localStorage.getItem(key);
		return item ? JSON.parse(item) : defaultValue;
	} catch {
		return defaultValue;
	}
}

export function setToStorage<T>(key: string, value: T): void {
	if (!isLocalStorageAvailable()) {
		return;
	}
	try {
		localStorage.setItem(key, JSON.stringify(value));
	} catch (error) {
		logger.error("Error saving to localStorage:", error);
	}
}

export function removeFromStorage(key: string): void {
	if (!isLocalStorageAvailable()) {
		return;
	}
	try {
		localStorage.removeItem(key);
	} catch (error) {
		logger.error("Error removing from localStorage:", error);
	}
}

// Copy to clipboard
export async function copyToClipboard(text: string): Promise<boolean> {
	if (
		typeof globalThis.window === "undefined" ||
		typeof navigator === "undefined" ||
		typeof document === "undefined"
	) {
		return false;
	}

	try {
		if (navigator.clipboard?.writeText) {
			await navigator.clipboard.writeText(text);
			return true;
		}
	} catch {
		// Fallback for older browsers
	}

	// Fallback for older browsers
	try {
		const textArea = document.createElement("textarea");
		textArea.value = text;
		textArea.style.position = "fixed";
		textArea.style.left = "-999999px";
		document.body.append(textArea);
		textArea.select();
		try {
			document.execCommand("copy");
			document.body.removeChild(textArea);
			return true;
		} catch {
			document.body.removeChild(textArea);
			return false;
		}
	} catch {
		return false;
	}
}

// Download file
export function downloadFile(
	content: string,
	filename: string,
	type = "text/plain",
): void {
	if (
		typeof globalThis.window === "undefined" ||
		typeof document === "undefined"
	) {
		return;
	}

	const blob = new Blob([content], { type });
	const url = URL.createObjectURL(blob);
	const link = document.createElement("a");
	link.href = url;
	link.download = filename;
	document.body.append(link);
	link.click();
	document.body.removeChild(link);
	URL.revokeObjectURL(url);
}
