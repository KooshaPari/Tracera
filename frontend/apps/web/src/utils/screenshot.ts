// Screenshot capture and thumbnail generation utilities
// Handles component screenshots, thumbnail generation, and versioning
// Currently uses mock implementation (S3 upload simulation for future integration)

import type { Item } from "@tracertm/types";

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
}

/**
 * Thumbnail size configuration
 */
export type ThumbnailSize = "small" | "medium" | "large";

const THUMBNAIL_SIZES: Record<ThumbnailSize, { width: number; height: number }> = {
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
 * Mock S3 storage (for future integration with real S3)
 */
interface MockS3Storage {
  [key: string]: string;
}
const mockS3Storage: MockS3Storage = {};

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
  height: number = 800
): Promise<string> {
  try {
    // Dynamically import html2canvas (note: requires npm install html2canvas)
    // For now, use a mock implementation or rely on server-side screenshots
    let html2canvas: any;
    try {
      // @ts-ignore - html2canvas is optional dependency
      html2canvas = (await import("html2canvas")).default;
    } catch {
      // Fallback: return mock data URL if html2canvas not available
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
    console.error("Failed to capture screenshot:", error);
    throw new Error("Screenshot capture failed");
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
  size: ThumbnailSize = "medium"
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
        ctx.drawImage(img, srcX, srcY, srcWidth, srcHeight, 0, 0, width, height);

        const dataUrl = canvas.toDataURL("image/jpeg", 0.8);
        thumbnailCache.set(cacheKey, dataUrl);
        resolve(dataUrl);
      };

      img.onerror = () => {
        reject(new Error("Failed to load image"));
      };

      img.src = screenshotUrl;
    });

    return promise;
  } catch (error) {
    console.error("Failed to generate thumbnail:", error);
    throw error;
  }
}

/**
 * Upload screenshot to storage (mock implementation)
 * In production, this would upload to S3/cloud storage
 *
 * @param screenshotData - Base64 encoded screenshot data or data URL
 * @param componentId - ID of the component being screenshotted
 * @param version - Version string
 * @returns Promise resolving to storage URL
 */
export async function uploadScreenshot(
  screenshotData: string,
  componentId: string,
  version: string = "v1"
): Promise<string> {
  const storageKey = `screenshots/${componentId}/${version}-${Date.now()}.png`;

  try {
    // Mock S3 storage
    mockS3Storage[storageKey] = screenshotData;

    // Return mock URL
    return `/api/screenshots/${componentId}/${version}`;
  } catch (error) {
    console.error("Failed to upload screenshot:", error);
    throw new Error("Screenshot upload failed");
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
export function getScreenshotFromCache(id: string): ScreenshotMetadata | undefined {
  return screenshotCache.get(id);
}

/**
 * Get all screenshots for a component
 */
export function getComponentScreenshots(componentId: string): ScreenshotMetadata[] {
  const screenshots: ScreenshotMetadata[] = [];

  for (const metadata of screenshotCache.values()) {
    if (metadata.componentId === componentId) {
      screenshots.push(metadata);
    }
  }

  return screenshots.sort(
    (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
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
 */
export async function createScreenshot(
  element: HTMLElement,
  componentId: string,
  version: string = "1.0.0",
  versionType: "design" | "draft" | "review" | "release" = "draft"
): Promise<ScreenshotMetadata> {
  // Capture screenshot
  const screenshotData = await captureComponentScreenshot(element);

  // Upload to storage
  const url = await uploadScreenshot(screenshotData, componentId, versionType);

  // Generate thumbnail
  let thumbnailUrl: string | undefined;
  try {
    thumbnailUrl = await generateThumbnail(screenshotData, "medium");
  } catch {
    // Thumbnail generation is optional, don't fail if it errors
  }

  // Create metadata
  const metadata: ScreenshotMetadata = {
    id: `screenshot_${componentId}_${Date.now()}`,
    componentId,
    url,
    ...(thumbnailUrl ? { thumbnailUrl } : {}),
    width: 1200,
    height: 800,
    version,
    versionType,
    createdAt: new Date(),
    updatedAt: new Date(),
    ...(screenshotData ? { contentHash: generateContentHash(screenshotData) } : {}),
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
  screenshot: ScreenshotMetadata
): Item {
  return {
    ...item,
    metadata: {
      ...(item.metadata || {}),
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
  newContentHash: string
): boolean {
  if (!existingMetadata) return true;
  return existingMetadata.contentHash !== newContentHash;
}

/**
 * Batch capture multiple component screenshots
 */
export async function batchCaptureScreenshots(
  elements: Array<{ element: HTMLElement; componentId: string; version: string }>
): Promise<ScreenshotMetadata[]> {
  const results: ScreenshotMetadata[] = [];

  for (const { element, componentId, version } of elements) {
    try {
      const screenshot = await createScreenshot(element, componentId, version);
      results.push(screenshot);
    } catch (error) {
      console.error(`Failed to capture screenshot for ${componentId}:`, error);
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
  mockStorageSize: number;
} {
  return {
    screenshots: screenshotCache.size,
    thumbnails: thumbnailCache.size,
    mockStorageSize: Object.keys(mockS3Storage).length,
  };
}
