// General helper utilities

import { logger } from "@/lib/logger";
import type { Item, Link } from "@tracertm/types";

const BASE36_RADIX = Number("36");
const ID_SLICE_START = Number("2");
const ID_SLICE_END = Number("9");
const FULL_PERCENT = Number("100");
const ORDER_BEFORE = Number("-1");
const ORDER_AFTER = Number("1");

// Array utilities
const groupBy = function <T>(
	array: T[],
	key: keyof T,
): Record<string, T[]> {
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
};

const sortBy = function <T>(
	array: T[],
	key: keyof T,
	order: "asc" | "desc" = "asc",
): T[] {
	return [...array].toSorted((a: T, b: T) => {
		const aVal = a[key];
		const bVal = b[key];

		if (aVal < bVal) {
			return order === "asc" ? ORDER_BEFORE : ORDER_AFTER;
		}
		if (aVal > bVal) {
			return order === "asc" ? ORDER_AFTER : ORDER_BEFORE;
		}
		return 0;
	});
};

const unique = function <T>(array: T[]): T[] {
	return [...new Set(array)];
};

const chunk = function <T>(array: T[], size: number): T[][] {
	const chunks: T[][] = [];
	for (let index = 0; index < array.length; index += size) {
		chunks.push(array.slice(index, index + size));
	}
	return chunks;
};

const shuffle = function <T>(array: T[]): T[] {
	const shuffled = [...array];
	for (let index = shuffled.length - 1; index > 0; index -= 1) {
		const swapIndex = Math.floor(Math.random() * (index + 1));
		const temp = shuffled[index];
		shuffled[index] = shuffled[swapIndex]!;
		shuffled[swapIndex] = temp!;
	}
	return shuffled;
};

// Object utilities
const pick = function <T extends object, K extends keyof T>(
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
};

const omit = function <T extends object, K extends keyof T>(
	obj: T,
	keys: K[],
): Omit<T, K> {
	const result = { ...obj };
	keys.forEach((key) => {
		delete result[key];
	});
	return result;
};

const deepClone = function <T>(obj: T): T {
	return structuredClone(obj);
};

const isEmpty = function (obj: object): boolean {
	return Object.keys(obj).length === 0;
};

const merge = function <T extends object>(
	target: T,
	...sources: Partial<T>[]
): T {
	return Object.assign({}, target, ...sources);
};

// String utilities
const generateId = function (): string {
	return `${Date.now()}-${Math.random()
		.toString(BASE36_RADIX)
		.slice(ID_SLICE_START, ID_SLICE_END)}`;
};

const slugify = function (text: string): string {
	return text
		.toLowerCase()
		.trim()
		.replaceAll(/[^\w\s-]/g, "")
		.replaceAll(/[\s_-]+/g, "-")
		.replaceAll(/^-+|-+$/g, "");
};

const randomString = function (length: number): string {
	const chars =
		"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
	let result = "";
	for (let index = 0; index < length; index += 1) {
		result += chars.charAt(Math.floor(Math.random() * chars.length));
	}
	return result;
};

// Type guards
const isNotNull = function <T>(value: T | null | undefined): value is T {
	return value !== null && value !== undefined;
};

const isDefined = function <T>(value: T | undefined): value is T {
	return value !== undefined;
};

// Async utilities
const sleep = function (ms: number): Promise<void> {
	return new Promise((resolve) => setTimeout(resolve, ms));
};

const debounce = function <T extends (...args: never[]) => unknown>(
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
};

const throttle = function <T extends (...args: never[]) => unknown>(
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
};

// TraceRTM specific utilities
const getItemsByView = function (items: Item[], view: string): Item[] {
	return items.filter((item) => item.view === view);
};

const getItemChildren = function (
	items: Item[],
	parentId: string,
): Item[] {
	return items.filter((item) => item.parentId === parentId);
};

const getItemAncestors = function (items: Item[], itemId: string): Item[] {
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
};

const getLinkedItems = function (
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
};

const calculateProgress = function (items: Item[]): number {
	if (items.length === 0) {
		return 0;
	}
	const doneItems = items.filter((item) => item.status === "done").length;
	return (doneItems / items.length) * FULL_PERCENT;
};

// Local storage utilities (SSR-safe)
const isLocalStorageAvailable = function (): boolean {
	return (
		typeof localStorage !== "undefined" &&
		typeof localStorage.getItem === "function"
	);
};

const getFromStorage = function <T>(key: string, defaultValue: T): T {
	if (!isLocalStorageAvailable()) {
		return defaultValue;
	}
	try {
		const item = localStorage.getItem(key);
		return item ? JSON.parse(item) : defaultValue;
	} catch {
		return defaultValue;
	}
};

const setToStorage = function <T>(key: string, value: T): void {
	if (!isLocalStorageAvailable()) {
		return;
	}
	try {
		localStorage.setItem(key, JSON.stringify(value));
	} catch (error) {
		logger.error("Error saving to localStorage:", error);
	}
};

const removeFromStorage = function (key: string): void {
	if (!isLocalStorageAvailable()) {
		return;
	}
	try {
		localStorage.removeItem(key);
	} catch (error) {
		logger.error("Error removing from localStorage:", error);
	}
};

// Copy to clipboard
const copyToClipboard = async function (text: string): Promise<boolean> {
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
};

// Download file
const downloadFile = function (
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
};

export {
	calculateProgress,
	chunk,
	copyToClipboard,
	debounce,
	deepClone,
	downloadFile,
	generateId,
	getFromStorage,
	getItemAncestors,
	getItemChildren,
	getItemsByView,
	getLinkedItems,
	groupBy,
	isDefined,
	isEmpty,
	isNotNull,
	merge,
	omit,
	pick,
	randomString,
	removeFromStorage,
	setToStorage,
	shuffle,
	slugify,
	sleep,
	sortBy,
	throttle,
	unique,
};
