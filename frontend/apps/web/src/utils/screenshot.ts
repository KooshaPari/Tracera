// Screenshot capture and thumbnail generation utilities
// Handles component screenshots, thumbnail generation, versioning, and S3 upload
// Features: image compression, presigned URL upload, progress tracking, error handling

import type { Item } from "@tracertm/types";
import { logger } from '@/lib/logger';
import client from "@/api/client";

const { getAuthHeaders } = client;

/**
 * Screenshot metadata including versions and timestamps
 */
export interface ScreenshotMetadata {
	id: string;
	componentId: string;
	url: string;
	thumbnailUrl?: string;
	width: number;
	height: number;
	version: string;
	versionType: "design" | "draft" | "review" | "release";
	createdAt: Date;
	updatedAt: Date;
	contentHash?: string;
	storageKey?: string; // S3 object key for deletion
	fileSize?: number; // Original file size in bytes
}

/**
 * Upload options for progress tracking and configuration
 */
export interface UploadOptions {
	onProgress?: (percent: number) => void;
	maxWidth?: number;
	maxHeight?: number;
	quality?: number;
}

/**
 * Upload error with detailed context
 */
export interface UploadError extends Error {
	code:
		| "NETWORK_ERROR"
		| "UPLOAD_FAILED"
		| "INVALID_FILE"
		| "COMPRESSION_FAILED";
	details?: string;
	statusCode?: number;
}

/**
 * Thumbnail size configuration
 */
export type ThumbnailSize = "small" | "medium" | "large";

const THUMBNAIL_SIZES: Record<
	ThumbnailSize,
	{ width: number; height: number }
> = {
	small: { width: 150, height: 150 },
	medium: { width: 300, height: 300 },
	large: { width: 600, height: 600 },
};

/**
 * Cache for generated screenshots and thumbnails (in-memory for now)
 */
const screenshotCache = new Map<string, ScreenshotMetadata>();
const thumbnailCache = new Map<string, string>();

/**
 * Maximum image dimensions to prevent excessive compression
 */
const DEFAULT_MAX_WIDTH = 1920;
const DEFAULT_MAX_HEIGHT = 1080;
const DEFAULT_QUALITY = 0.9;

/**
 * Maximum file size (10MB) before rejecting upload
 */
const MAX_FILE_SIZE = 10 * 1024 * 1024;

/**
 * Compress image to reduce bandwidth and storage
 *
 * @param dataUrl - Data URL of the image to compress
 * @param maxWidth - Maximum width in pixels
 * @param maxHeight - Maximum height in pixels
 * @param quality - JPEG quality (0-1)
 * @returns Promise resolving to compressed data URL
 */
async function compressImage(
	dataUrl: string,
	maxWidth: number = DEFAULT_MAX_WIDTH,
	maxHeight: number = DEFAULT_MAX_HEIGHT,
	quality: number = DEFAULT_QUALITY,
): Promise<string> {
	return new Promise((resolve, reject) => {
		const img = new Image();
		/* eslint-disable unicorn/prefer-add-event-listener -- Image API uses .onload/.onerror */
		img.onload = () => {
			const canvas = document.createElement("canvas");

			// Calculate dimensions while maintaining aspect ratio
			let width = img.width;
			let height = img.height;

			if (width > maxWidth || height > maxHeight) {
				const aspectRatio = width / height;
				if (width > maxWidth) {
					width = maxWidth;
					height = width / aspectRatio;
				}
				if (height > maxHeight) {
					height = maxHeight;
					width = height * aspectRatio;
				}
			}

			canvas.width = width;
			canvas.height = height;

			const ctx = canvas.getContext("2d");
			if (!ctx) {
				reject(
					Object.assign(new Error("Failed to get canvas context"), {
						code: "COMPRESSION_FAILED" as const,
					}),
				);
				return;
			}

			ctx.drawImage(img, 0, 0, width, height);

			try {
				const compressedUrl = canvas.toDataURL("image/jpeg", quality);
				resolve(compressedUrl);
			} catch (error) {
				reject(
					Object.assign(new Error("Failed to compress image"), {
						code: "COMPRESSION_FAILED" as const,
						details: String(error),
					}),
				);
			}
		};

		img.onerror = () => {
			reject(
				Object.assign(new Error("Failed to load image for compression"), {
					code: "INVALID_FILE" as const,
				}),
			);
		};
		/* eslint-enable unicorn/prefer-add-event-listener */

		img.src = dataUrl;
	});
}

/**
 * Capture a component screenshot using canvas (client-side)
 * In production, this would use Playwright/Puppeteer on the server
 *
 * @param element - DOM element to capture
 * @param width - Screenshot width (default: 1200)
 * @param height - Screenshot height (default: 800)
 * @returns Promise resolving to data URL
 */
export async function captureComponentScreenshot(
	element: HTMLElement,
	width: number = 1200,
	height: number = 800,
): Promise<string> {
	try {
		// Dynamically import html2canvas (note: requires npm install html2canvas)
		// For now, use a mock implementation or rely on server-side screenshots
		let html2canvas: ((element: HTMLElement, options?: Record<string, unknown>) => Promise<HTMLCanvasElement>) | undefined;
		try {
			// any: external library with incomplete type definitions
			html2canvas = (await import("html2canvas")).default as any;
		} catch {
			// Fallback: return mock data URL if html2canvas not available
			return `data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==`;
		}

		if (!html2canvas) {
			return `data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==`;
		}

		// Capture the element
		const canvas = await html2canvas(element, {
			width,
			height,
			backgroundColor: "#ffffff",
			scale: 2, // 2x resolution for crisp thumbnails
			logging: false,
		});

		return canvas.toDataURL("image/png");
	} catch (error) {
		logger.error("Failed to capture screenshot:", error);
		throw new Error("Screenshot capture failed", { cause: error });
	}
}

/**
 * Generate thumbnail from a larger screenshot
 *
 * @param screenshotUrl - URL of the full screenshot
 * @param size - Thumbnail size preset
 * @returns Promise resolving to thumbnail data URL
 */
export async function generateThumbnail(
	screenshotUrl: string,
	size: ThumbnailSize = "medium",
): Promise<string> {
	const cacheKey = `${screenshotUrl}-${size}`;

	// Check cache first
	if (thumbnailCache.has(cacheKey)) {
		return thumbnailCache.get(cacheKey)!;
	}

	try {
		const img = new Image();
		img.crossOrigin = "anonymous";

		const promise = new Promise<string>((resolve, reject) => {
			/* eslint-disable unicorn/prefer-add-event-listener -- Image API uses .onload/.onerror */
			img.onload = () => {
				const canvas = document.createElement("canvas");
				const { width, height } = THUMBNAIL_SIZES[size];
				canvas.width = width;
				canvas.height = height;

				const ctx = canvas.getContext("2d");
				if (!ctx) {
					reject(new Error("Failed to get canvas context"));
					return;
				}

				// Calculate aspect-preserving dimensions
				const imgAspect = img.width / img.height;
				const canvasAspect = width / height;

				let srcWidth = img.width;
				let srcHeight = img.height;
				let srcX = 0;
				let srcY = 0;

				if (imgAspect > canvasAspect) {
					srcWidth = img.height * canvasAspect;
					srcX = (img.width - srcWidth) / 2;
				} else {
					srcHeight = img.width / canvasAspect;
					srcY = (img.height - srcHeight) / 2;
				}

				// Fill background
				ctx.fillStyle = "#f3f4f6";
				ctx.fillRect(0, 0, width, height);

				// Draw scaled image
				ctx.drawImage(
					img,
					srcX,
					srcY,
					srcWidth,
					srcHeight,
					0,
					0,
					width,
					height,
				);

				const dataUrl = canvas.toDataURL("image/jpeg", 0.8);
				thumbnailCache.set(cacheKey, dataUrl);
				resolve(dataUrl);
			};

			img.onerror = () => {
				reject(new Error("Failed to load image"));
			};
			/* eslint-enable unicorn/prefer-add-event-listener */

			img.src = screenshotUrl;
		});

		return promise;
	} catch (error) {
		logger.error("Failed to generate thumbnail:", error);
		throw error;
	}
}

/**
 * Convert data URL to File object
 */
function dataUrlToFile(dataUrl: string, filename: string): File {
	const arr = dataUrl.split(",");
	const mime = arr[0]?.match(/:(.*?);/)?.[1] ?? "image/png";
	const bstr = atob(arr[1] ?? "");
	const n = bstr.length;
	const u8arr = new Uint8Array(n);

	for (let i = 0; i < n; i++) {
		u8arr[i] = bstr.charCodeAt(i);
	}

	return new File([u8arr], filename, { type: mime });
}

/**
 * Get presigned upload URL from backend
 */
async function getPresignedUploadUrl(
	filename: string,
	contentType: string,
): Promise<{ uploadUrl: string; key: string }> {
	try {
		const response = await fetch("/api/v1/storage/presigned-upload", {
			method: "POST",
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			credentials: "include",
			body: JSON.stringify({
				filename,
				contentType,
			}),
		});

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			throw Object.assign(new Error("Failed to get upload URL"), {
				code: "UPLOAD_FAILED" as const,
				statusCode: response.status,
				details: errorData.error || response.statusText,
			});
		}

		const data = await response.json();
		return { uploadUrl: data.uploadUrl, key: data.key };
	} catch (error) {
		if (error instanceof Error && "code" in error) {
			throw error;
		}
		throw Object.assign(new Error("Failed to get presigned upload URL"), {
			code: "NETWORK_ERROR" as const,
			details: String(error),
		});
	}
}

/**
 * Upload file to S3 using presigned URL with progress tracking
 */
async function uploadToS3(
	file: File,
	uploadUrl: string,
	onProgress?: (percent: number) => void,
): Promise<void> {
	return new Promise((resolve, reject) => {
		const xhr = new XMLHttpRequest();

		// Track upload progress
		xhr.upload.addEventListener("progress", (e) => {
			if (e.lengthComputable && onProgress) {
				const percentComplete = (e.loaded / e.total) * 100;
				onProgress(percentComplete);
			}
		});

		xhr.addEventListener("load", () => {
			if (xhr.status >= 200 && xhr.status < 300) {
				resolve();
			} else {
				reject(
					Object.assign(
						new Error(`S3 upload failed with status ${xhr.status}`),
						{
							code: "UPLOAD_FAILED" as const,
							statusCode: xhr.status,
							details: xhr.responseText,
						},
					),
				);
			}
		});

		xhr.addEventListener("error", () => {
			reject(
				Object.assign(new Error("Network error during upload"), {
					code: "NETWORK_ERROR" as const,
				}),
			);
		});

		xhr.addEventListener("abort", () => {
			reject(
				Object.assign(new Error("Upload cancelled"), {
					code: "UPLOAD_FAILED" as const,
				}),
			);
		});

		xhr.open("PUT", uploadUrl);
		xhr.setRequestHeader("Content-Type", file.type);
		xhr.send(file);
	});
}

/**
 * Upload screenshot to S3 storage with compression and progress tracking
 *
 * @param screenshotData - Base64 encoded screenshot data or data URL
 * @param componentId - ID of the component being screenshotted
 * @param version - Version string
 * @param options - Upload options including progress callback and compression settings
 * @returns Promise resolving to storage URL and metadata
 */
export async function uploadScreenshot(
	screenshotData: string,
	componentId: string,
	version: string = "v1",
	options: UploadOptions = {},
): Promise<{
	url: string;
	key: string;
	fileSize: number;
}> {
	try {
		// Validate input
		if (!screenshotData) {
			throw Object.assign(new Error("Screenshot data is empty"), {
				code: "INVALID_FILE" as const,
			});
		}

		// Compress image before upload
		options.onProgress?.(5);
		const compressedData = await compressImage(
			screenshotData,
			options.maxWidth,
			options.maxHeight,
			options.quality,
		);
		options.onProgress?.(15);

		// Convert to File object
		const timestamp = Date.now();
		const filename = `${componentId}-${version}-${timestamp}.jpg`;
		const file = dataUrlToFile(compressedData, filename);

		// Validate file size
		if (file.size > MAX_FILE_SIZE) {
			throw Object.assign(
				new Error(
					`File size ${file.size} bytes exceeds maximum ${MAX_FILE_SIZE} bytes`,
				),
				{
					code: "INVALID_FILE" as const,
				},
			);
		}

		// Get presigned upload URL from backend
		options.onProgress?.(20);
		const { uploadUrl, key } = await getPresignedUploadUrl(filename, file.type);
		options.onProgress?.(30);

		// Upload file to S3
		await uploadToS3(file, uploadUrl, (percent) => {
			// Map 30-95% to the S3 upload progress
			const uploadProgress = 30 + (percent * 65) / 100;
			options.onProgress?.(uploadProgress);
		});

		options.onProgress?.(95);

		// Return success with metadata
		const url = `/api/v1/storage/${key}`;
		options.onProgress?.(100);

		return { url, key, fileSize: file.size };
	} catch (error) {
		logger.error("Screenshot upload failed:", error);

		// Ensure error has proper structure
		if (error instanceof Error && "code" in error) {
			throw error as UploadError;
		}

		throw Object.assign(new Error("Screenshot upload failed"), {
			code: "UPLOAD_FAILED" as const,
			details: String(error),
		}) as UploadError;
	}
}

/**
 * Delete screenshot from S3 storage
 *
 * @param key - S3 object key
 */
export async function deleteScreenshot(key: string): Promise<void> {
	try {
		const response = await fetch(`/api/v1/storage/${key}`, {
			method: "DELETE",
			headers: getAuthHeaders(),
			credentials: "include",
		});

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			throw Object.assign(new Error("Failed to delete screenshot"), {
				code: "UPLOAD_FAILED" as const,
				statusCode: response.status,
				details: errorData.error || response.statusText,
			});
		}
	} catch (error) {
		logger.error("Failed to delete screenshot:", error);
		if (error instanceof Error && "code" in error) {
			throw error as UploadError;
		}
		throw Object.assign(new Error("Failed to delete screenshot"), {
			code: "NETWORK_ERROR" as const,
			details: String(error),
		}) as UploadError;
	}
}

/**
 * Cache screenshot metadata
 */
export function cacheScreenshot(metadata: ScreenshotMetadata): void {
	screenshotCache.set(metadata.id, metadata);
}

/**
 * Retrieve screenshot metadata from cache
 */
export function getScreenshotFromCache(
	id: string,
): ScreenshotMetadata | undefined {
	return screenshotCache.get(id);
}

/**
 * Get all screenshots for a component
 */
export function getComponentScreenshots(
	componentId: string,
): ScreenshotMetadata[] {
	const screenshots: ScreenshotMetadata[] = [];

	for (const metadata of screenshotCache.values()) {
		if (metadata.componentId === componentId) {
			screenshots.push(metadata);
		}
	}

	return screenshots.toSorted(
		(a: ScreenshotMetadata, b: ScreenshotMetadata) =>
			new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime(),
	);
}

/**
 * Generate content hash for screenshot comparison (simple implementation)
 */
function generateContentHash(data: string): string {
	let hash = 0;
	for (let i = 0; i < data.length; i++) {
		const char = data.charCodeAt(i);
		hash = (hash << 5) - hash + char;
		hash = hash & hash; // Convert to 32-bit integer
	}
	return `hash_${Math.abs(hash)}`;
}

/**
 * Create screenshot with full metadata workflow
 *
 * @param element - DOM element to screenshot
 * @param componentId - Component ID for organization
 * @param version - Version string
 * @param versionType - Type of version (design, draft, review, release)
 * @param options - Upload options including progress tracking
 * @returns Promise resolving to screenshot metadata
 */
export async function createScreenshot(
	element: HTMLElement,
	componentId: string,
	version: string = "1.0.0",
	versionType: "design" | "draft" | "review" | "release" = "draft",
	options: UploadOptions = {},
): Promise<ScreenshotMetadata> {
	// Capture screenshot
	options.onProgress?.(10);
	const screenshotData = await captureComponentScreenshot(element);

	// Upload to storage with progress tracking
	const uploadResult = await uploadScreenshot(
		screenshotData,
		componentId,
		versionType,
		options,
	);

	// Generate thumbnail
	let thumbnailUrl: string | undefined;
	try {
		thumbnailUrl = await generateThumbnail(uploadResult.url, "medium");
	} catch (error) {
		// Thumbnail generation is optional, don't fail if it errors
		logger.warn("Thumbnail generation failed:", error);
	}

	// Create metadata
	const metadata: ScreenshotMetadata = {
		id: `screenshot_${componentId}_${Date.now()}`,
		componentId,
		url: uploadResult.url,
		storageKey: uploadResult.key,
		fileSize: uploadResult.fileSize,
		...(thumbnailUrl ? { thumbnailUrl } : {}),
		width: 1200,
		height: 800,
		version,
		versionType,
		createdAt: new Date(),
		updatedAt: new Date(),
		...(screenshotData
			? { contentHash: generateContentHash(screenshotData) }
			: {}),
	};

	// Cache it
	cacheScreenshot(metadata);

	return metadata;
}

/**
 * Update item with screenshot metadata
 */
export function updateItemWithScreenshot(
	item: Item,
	screenshot: ScreenshotMetadata,
): Item {
	return {
		...item,
		metadata: {
			...item.metadata,
			screenshotUrl: screenshot.url,
			thumbnailUrl: screenshot.thumbnailUrl,
			screenshotVersion: screenshot.version,
			screenshotVersionType: screenshot.versionType,
			screenshotHash: screenshot.contentHash,
		},
	};
}

/**
 * Check if screenshot needs update based on content hash
 */
export function screenshotNeedsUpdate(
	existingMetadata: ScreenshotMetadata | undefined,
	newContentHash: string,
): boolean {
	if (!existingMetadata) return true;
	return existingMetadata.contentHash !== newContentHash;
}

/**
 * Batch capture multiple component screenshots
 *
 * @param elements - Array of elements to screenshot
 * @param options - Upload options including progress tracking
 * @returns Promise resolving to array of screenshot metadata
 */
export async function batchCaptureScreenshots(
	elements: Array<{
		element: HTMLElement;
		componentId: string;
		version: string;
	}>,
	options: UploadOptions = {},
): Promise<ScreenshotMetadata[]> {
	const results: ScreenshotMetadata[] = [];
	const totalElements = elements.length;

	for (let i = 0; i < elements.length; i++) {
		const entry = elements[i];
		if (!entry) continue;
		const { element, componentId, version } = entry;

		try {
			// Create progress callback that updates for this specific element
			const elementProgress = (percent: number) => {
				const baseProgress = (i / totalElements) * 100;
				const elementPercent = (percent / 100) * (100 / totalElements);
				const totalProgress = baseProgress + elementPercent;
				options.onProgress?.(totalProgress);
			};

			const screenshot = await createScreenshot(
				element,
				componentId,
				version,
				"draft",
				{ ...options, onProgress: elementProgress },
			);
			results.push(screenshot);
		} catch (error) {
			logger.error(`Failed to capture screenshot for ${componentId}:`, error);
			// Continue with next screenshot even if one fails
		}
	}

	return results;
}

/**
 * Clear screenshot cache
 */
export function clearScreenshotCache(): void {
	screenshotCache.clear();
	thumbnailCache.clear();
}

/**
 * Get cache statistics
 */
export function getScreenshotCacheStats(): {
	screenshots: number;
	thumbnails: number;
	totalFileSize: number;
} {
	let totalFileSize = 0;
	for (const metadata of screenshotCache.values()) {
		if (metadata.fileSize) {
			totalFileSize += metadata.fileSize;
		}
	}

	return {
		screenshots: screenshotCache.size,
		thumbnails: thumbnailCache.size,
		totalFileSize,
	};
}
