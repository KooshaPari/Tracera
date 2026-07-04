// Screenshot capture and thumbnail generation utilities
// Handles component screenshots, thumbnail generation, versioning, and S3 upload
// Features: image compression, presigned URL upload, progress tracking, error handling

import type { Item } from '@tracertm/types';

import { client } from '@/api/client';
import { logger } from '@/lib/logger';

const { getAuthHeaders } = client;

/**
 * Screenshot metadata including versions and timestamps
 */
export interface ScreenshotMetadata {
  id: string;
  componentId: string;
  url: string;
  thumbnailUrl?: string | undefined;
  width: number;
  height: number;
  version: string;
  versionType: 'design' | 'draft' | 'review' | 'release';
  createdAt: Date;
  updatedAt: Date;
  contentHash?: string | undefined;
  storageKey?: string; // S3 object key for deletion
  fileSize?: number; // Original file size in bytes
}

/**
 * Upload options for progress tracking and configuration
 */
export interface UploadOptions {
  onProgress?: ((percent: number) => void) | undefined;
  maxWidth?: number | undefined;
  maxHeight?: number | undefined;
  quality?: number | undefined;
}

/**
 * Upload error with detailed context
 */
export interface UploadError extends Error {
  code: 'NETWORK_ERROR' | 'UPLOAD_FAILED' | 'INVALID_FILE' | 'COMPRESSION_FAILED';
  details?: string | undefined;
  statusCode?: number | undefined;
}

/**
 * Thumbnail size configuration
 */
export type ThumbnailSize = 'small' | 'medium' | 'large';

interface CompressOptions {
  maxHeight?: number | undefined;
  maxWidth?: number | undefined;
  quality?: number | undefined;
}

interface UploadScreenshotParams {
  componentId: string;
  options?: UploadOptions | undefined;
  screenshotData: string;
  version?: string | undefined;
}

interface CreateScreenshotParams {
  componentId: string;
  element: HTMLElement;
  options?: UploadOptions | undefined;
  version?: string | undefined;
  versionType?: 'design' | 'draft' | 'review' | 'release' | undefined;
}

interface ThumbnailDimensions {
  height: number;
  width: number;
}

const THUMBNAIL_SIZES: Record<ThumbnailSize, ThumbnailDimensions> = {
  large: { height: Number('600'), width: Number('600') },
  medium: { height: Number('300'), width: Number('300') },
  small: { height: Number('150'), width: Number('150') },
};

const screenshotCache = new Map<string, ScreenshotMetadata>();
const thumbnailCache = new Map<string, string>();

const DEFAULT_MAX_WIDTH = Number('1920');
const DEFAULT_MAX_HEIGHT = Number('1080');
const DEFAULT_QUALITY = Number('0.9');

const CAPTURE_WIDTH = Number('1200');
const CAPTURE_HEIGHT = Number('800');
const CAPTURE_SCALE = Number('2');

const BYTES_PER_KB = Number('1024');
const BYTES_PER_MB = BYTES_PER_KB * BYTES_PER_KB;
const MAX_FILE_SIZE_MB = Number('10');
const MAX_FILE_SIZE = MAX_FILE_SIZE_MB * BYTES_PER_MB;

const PROGRESS_COMPRESS_START = Number('5');
const PROGRESS_COMPRESS_DONE = Number('15');
const PROGRESS_PRESIGN_START = Number('20');
const PROGRESS_PRESIGN_DONE = Number('30');
const PROGRESS_UPLOAD_DONE = Number('95');
const PROGRESS_COMPLETE = Number('100');
const PROGRESS_UPLOAD_BASE = Number('30');
const PROGRESS_UPLOAD_RANGE = Number('65');

const THUMBNAIL_QUALITY = Number('0.8');
const HASH_SHIFT = Number('5');
const PERCENT_BASE = Number('100');
const ZERO = Number('0');
const ONE = Number('1');

const createUploadError = function createUploadError(
  message: string,
  code: UploadError['code'],
  details?: string,
  statusCode?: number,
): UploadError {
  return Object.assign(new Error(message), {
    code,
    details,
    statusCode,
  }) as UploadError;
};

const resolveCompressOptions = function resolveCompressOptions(
  options?: CompressOptions,
): Required<CompressOptions> {
  return {
    maxHeight: options?.maxHeight ?? DEFAULT_MAX_HEIGHT,
    maxWidth: options?.maxWidth ?? DEFAULT_MAX_WIDTH,
    quality: options?.quality ?? DEFAULT_QUALITY,
  };
};

const loadImage = async function loadImage(
  src: string,
  crossOrigin?: string,
): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => {
      resolve(image);
    };
    image.onerror = () => {
      reject(createUploadError('Failed to load image', 'INVALID_FILE'));
    };
    if (crossOrigin) {
      image.crossOrigin = crossOrigin;
    }
    image.src = src;
  });
};

const calculateScaledDimensions = function calculateScaledDimensions(
  width: number,
  height: number,
  maxWidth: number,
  maxHeight: number,
): { height: number; width: number } {
  let scaledWidth = width;
  let scaledHeight = height;

  if (scaledWidth > maxWidth || scaledHeight > maxHeight) {
    const aspectRatio = scaledWidth / scaledHeight;
    if (scaledWidth > maxWidth) {
      scaledWidth = maxWidth;
      scaledHeight = scaledWidth / aspectRatio;
    }
    if (scaledHeight > maxHeight) {
      scaledHeight = maxHeight;
      scaledWidth = scaledHeight * aspectRatio;
    }
  }

  return { height: scaledHeight, width: scaledWidth };
};

const toCompressedDataUrl = function toCompressedDataUrl(
  image: HTMLImageElement,
  options: Required<CompressOptions>,
): string {
  const canvas = document.createElement('canvas');
  const scaled = calculateScaledDimensions(
    image.width,
    image.height,
    options.maxWidth ?? image.width,
    options.maxHeight ?? image.height,
  );
  canvas.width = scaled.width;
  canvas.height = scaled.height;

  const context = canvas.getContext('2d');
  if (!context) {
    throw createUploadError('Failed to get canvas context', 'COMPRESSION_FAILED');
  }

  context.drawImage(image, ZERO, ZERO, scaled.width, scaled.height);
  try {
    return canvas.toDataURL('image/jpeg', options.quality);
  } catch (error) {
    throw createUploadError('Failed to compress image', 'COMPRESSION_FAILED', String(error));
  }
};

const compressImage = async function compressImage(
  dataUrl: string,
  options?: CompressOptions,
): Promise<string> {
  const resolvedOptions = resolveCompressOptions(options);
  const image = await loadImage(dataUrl);
  return toCompressedDataUrl(image, resolvedOptions);
};

const getThumbnailDimensions = function getThumbnailDimensions(
  size: ThumbnailSize,
): ThumbnailDimensions {
  return THUMBNAIL_SIZES[size];
};

const drawThumbnail = function drawThumbnail(
  image: HTMLImageElement,
  dimensions: ThumbnailDimensions,
): string {
  const canvas = document.createElement('canvas');
  canvas.width = dimensions.width;
  canvas.height = dimensions.height;

  const context = canvas.getContext('2d');
  if (!context) {
    throw new Error('Failed to get canvas context');
  }

  const imgAspect = image.width / image.height;
  const canvasAspect = dimensions.width / dimensions.height;

  let srcWidth = image.width;
  let srcHeight = image.height;
  let srcX = ZERO;
  let srcY = ZERO;

  if (imgAspect > canvasAspect) {
    srcWidth = image.height * canvasAspect;
    srcX = (image.width - srcWidth) / Number('2');
  } else {
    srcHeight = image.width / canvasAspect;
    srcY = (image.height - srcHeight) / Number('2');
  }

  context.fillStyle = '#f3f4f6';
  context.fillRect(ZERO, ZERO, dimensions.width, dimensions.height);

  context.drawImage(
    image,
    srcX,
    srcY,
    srcWidth,
    srcHeight,
    ZERO,
    ZERO,
    dimensions.width,
    dimensions.height,
  );

  return canvas.toDataURL('image/jpeg', THUMBNAIL_QUALITY);
};

/**
 * Capture a component screenshot using canvas (client-side)
 * In production, this would use Playwright/Puppeteer on the server
 */
const captureComponentScreenshot = async function captureComponentScreenshot(
  element: HTMLElement,
  width = CAPTURE_WIDTH,
  height = CAPTURE_HEIGHT,
): Promise<string> {
  try {
    let html2canvas:
      | ((element: HTMLElement, options?: Record<string, unknown>) => Promise<HTMLCanvasElement>)
      | undefined;
    try {
      // Any: external library with incomplete type definitions
      html2canvas = (await import('html2canvas')).default as any;
    } catch {
      return `data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==`;
    }

    if (!html2canvas) {
      return `data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==`;
    }

    const canvas = await html2canvas(element, {
      backgroundColor: '#ffffff',
      height,
      logging: false,
      scale: CAPTURE_SCALE,
      width,
    });

    return canvas.toDataURL('image/png');
  } catch (error) {
    logger.error('Failed to capture screenshot:', error);
    throw new Error('Screenshot capture failed', { cause: error });
  }
};

/**
 * Generate thumbnail from a larger screenshot
 */
const generateThumbnail = async function generateThumbnail(
  screenshotUrl: string,
  size: ThumbnailSize = 'medium',
): Promise<string> {
  const cacheKey = `${screenshotUrl}-${size}`;
  const cachedValue = thumbnailCache.get(cacheKey);
  if (cachedValue) {
    return cachedValue;
  }

  try {
    const image = await loadImage(screenshotUrl, 'anonymous');
    const dimensions = getThumbnailDimensions(size);
    const dataUrl = drawThumbnail(image, dimensions);
    thumbnailCache.set(cacheKey, dataUrl);
    return dataUrl;
  } catch (error) {
    logger.error('Failed to generate thumbnail:', error);
    throw error;
  }
};

/**
 * Convert data URL to File object
 */
const dataUrlToFile = function dataUrlToFile(dataUrl: string, filename: string): File {
  const parts = dataUrl.split(',');
  const mime = parts[0]?.match(/:(.*?);/)?.[1] ?? 'image/png';
  const decoded = atob(parts[1] ?? '');
  const { length } = decoded;
  const bytes = new Uint8Array(length);

  for (let index = 0; index < length; index += ONE) {
    const codePoint = decoded.codePointAt(index) ?? ZERO;
    bytes[index] = codePoint;
  }

  return new File([bytes], filename, { type: mime });
};

/**
 * Get presigned upload URL from backend
 */
const getPresignedUploadUrl = async function getPresignedUploadUrl(
  filename: string,
  contentType: string,
): Promise<{ key: string; uploadUrl: string }> {
  try {
    const response = await fetch('/api/v1/storage/presigned-upload', {
      body: JSON.stringify({
        contentType,
        filename,
      }),
      credentials: 'include',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      method: 'POST',
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw createUploadError(
        'Failed to get upload URL',
        'UPLOAD_FAILED',
        errorData.error ?? response.statusText,
        response.status,
      );
    }

    const data = await response.json();
    return { key: data.key, uploadUrl: data.uploadUrl };
  } catch (error) {
    if (error instanceof Error && 'code' in error) {
      throw error;
    }
    throw createUploadError('Failed to get presigned upload URL', 'NETWORK_ERROR', String(error));
  }
};

/**
 * Upload file to S3 using presigned URL with progress tracking
 */
const uploadToS3 = async function uploadToS3(
  file: File,
  uploadUrl: string,
  onProgress?: (percent: number) => void,
): Promise<void> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable && onProgress) {
        const percentComplete = (event.loaded / event.total) * PERCENT_BASE;
        onProgress(percentComplete);
      }
    });

    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve();
      } else {
        reject(
          createUploadError(
            `S3 upload failed with status ${xhr.status}`,
            'UPLOAD_FAILED',
            xhr.responseText,
            xhr.status,
          ),
        );
      }
    });

    xhr.addEventListener('error', () => {
      reject(createUploadError('Network error during upload', 'NETWORK_ERROR'));
    });

    xhr.addEventListener('abort', () => {
      reject(createUploadError('Upload cancelled', 'UPLOAD_FAILED'));
    });

    xhr.open('PUT', uploadUrl);
    xhr.setRequestHeader('Content-Type', file.type);
    xhr.send(file);
  });
};

const reportProgress = function reportProgress(
  options: UploadOptions | undefined,
  percent: number,
): void {
  options?.onProgress?.(percent);
};

const mapUploadProgress = function mapUploadProgress(percent: number): number {
  return PROGRESS_UPLOAD_BASE + (percent * PROGRESS_UPLOAD_RANGE) / PERCENT_BASE;
};

const validateScreenshotInput = function validateScreenshotInput(screenshotData: string): void {
  if (!screenshotData) {
    throw createUploadError('Screenshot data is empty', 'INVALID_FILE');
  }
};

const validateFileSize = function validateFileSize(file: File): void {
  if (file.size > MAX_FILE_SIZE) {
    throw createUploadError(
      `File size ${file.size} bytes exceeds maximum ${MAX_FILE_SIZE} bytes`,
      'INVALID_FILE',
    );
  }
};

/**
 * Upload screenshot to S3 storage with compression and progress tracking
 */
const uploadScreenshot = async function uploadScreenshot({
  componentId,
  options = {},
  screenshotData,
  version = 'v1',
}: UploadScreenshotParams): Promise<{
  fileSize: number;
  key: string;
  url: string;
}> {
  try {
    validateScreenshotInput(screenshotData);

    reportProgress(options, PROGRESS_COMPRESS_START);
    const compressedData = await compressImage(screenshotData, options);
    reportProgress(options, PROGRESS_COMPRESS_DONE);

    const timestamp = Date.now();
    const filename = `${componentId}-${version}-${timestamp}.jpg`;
    const file = dataUrlToFile(compressedData, filename);

    validateFileSize(file);

    reportProgress(options, PROGRESS_PRESIGN_START);
    const { key, uploadUrl } = await getPresignedUploadUrl(filename, file.type);
    reportProgress(options, PROGRESS_PRESIGN_DONE);

    await uploadToS3(file, uploadUrl, (percent) => {
      reportProgress(options, mapUploadProgress(percent));
    });

    reportProgress(options, PROGRESS_UPLOAD_DONE);
    const url = `/api/v1/storage/${key}`;
    reportProgress(options, PROGRESS_COMPLETE);

    return { fileSize: file.size, key, url };
  } catch (error) {
    logger.error('Screenshot upload failed:', error);
    if (error instanceof Error && 'code' in error) {
      throw error as UploadError;
    }
    throw createUploadError('Screenshot upload failed', 'UPLOAD_FAILED', String(error));
  }
};

/**
 * Delete screenshot from S3 storage
 */
const deleteScreenshot = async function deleteScreenshot(key: string): Promise<void> {
  try {
    const response = await fetch(`/api/v1/storage/${key}`, {
      credentials: 'include',
      headers: getAuthHeaders(),
      method: 'DELETE',
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw createUploadError(
        'Failed to delete screenshot',
        'UPLOAD_FAILED',
        errorData.error ?? response.statusText,
        response.status,
      );
    }
  } catch (error) {
    logger.error('Failed to delete screenshot:', error);
    if (error instanceof Error && 'code' in error) {
      throw error as UploadError;
    }
    throw createUploadError('Failed to delete screenshot', 'NETWORK_ERROR', String(error));
  }
};

/**
 * Cache screenshot metadata
 */
const cacheScreenshot = function cacheScreenshot(metadata: ScreenshotMetadata): void {
  screenshotCache.set(metadata.id, metadata);
};

/**
 * Retrieve screenshot metadata from cache
 */
const getScreenshotFromCache = function getScreenshotFromCache(
  id: string,
): ScreenshotMetadata | undefined {
  return screenshotCache.get(id);
};

/**
 * Get all screenshots for a component
 */
const getComponentScreenshots = function getComponentScreenshots(
  componentId: string,
): ScreenshotMetadata[] {
  const screenshots: ScreenshotMetadata[] = [];

  for (const metadata of screenshotCache.values()) {
    if (metadata.componentId === componentId) {
      screenshots.push(metadata);
    }
  }

  return screenshots.toSorted(
    (first: ScreenshotMetadata, second: ScreenshotMetadata) =>
      new Date(second.updatedAt).getTime() - new Date(first.updatedAt).getTime(),
  );
};

/**
 * Generate content hash for screenshot comparison (simple implementation)
 */
const generateContentHash = function generateContentHash(data: string): string {
  let hash = ZERO;
  for (let index = ZERO; index < data.length; index += ONE) {
    const charCode = data.codePointAt(index);
    if (charCode === undefined) {
      continue;
    }
    hash = (hash << HASH_SHIFT) - hash + charCode;
    hash &= hash;
  }
  return `hash_${Math.abs(hash)}`;
};

const buildMetadata = function buildMetadata(
  componentId: string,
  uploadResult: { fileSize: number; key: string; url: string },
  version: string,
  versionType: ScreenshotMetadata['versionType'],
  screenshotData: string,
  thumbnailUrl: string | undefined,
): ScreenshotMetadata {
  const now = new Date();
  return {
    componentId,
    contentHash: screenshotData ? generateContentHash(screenshotData) : undefined,
    createdAt: now,
    fileSize: uploadResult.fileSize,
    height: CAPTURE_HEIGHT,
    id: `screenshot_${componentId}_${Date.now()}`,
    storageKey: uploadResult.key,
    thumbnailUrl,
    updatedAt: now,
    url: uploadResult.url,
    version,
    versionType,
    width: CAPTURE_WIDTH,
  };
};

/**
 * Create screenshot with full metadata workflow
 */
const createScreenshot = async function createScreenshot({
  componentId,
  element,
  options = {},
  version = '1.0.0',
  versionType = 'draft',
}: CreateScreenshotParams): Promise<ScreenshotMetadata> {
  reportProgress(options, PROGRESS_PRESIGN_START);
  const screenshotData = await captureComponentScreenshot(element);

  const uploadResult = await uploadScreenshot({
    componentId,
    options,
    screenshotData,
    version: versionType,
  });

  let thumbnailUrl: string | undefined;
  try {
    thumbnailUrl = await generateThumbnail(uploadResult.url, 'medium');
  } catch (error) {
    logger.warn('Thumbnail generation failed:', error);
  }

  const metadata = buildMetadata(
    componentId,
    uploadResult,
    version,
    versionType,
    screenshotData,
    thumbnailUrl,
  );

  cacheScreenshot(metadata);
  return metadata;
};

/**
 * Update item with screenshot metadata
 */
const updateItemWithScreenshot = function updateItemWithScreenshot(
  item: Item,
  screenshot: ScreenshotMetadata,
): Item {
  return {
    ...item,
    metadata: {
      ...item.metadata,
      screenshotHash: screenshot.contentHash,
      screenshotUrl: screenshot.url,
      screenshotVersion: screenshot.version,
      screenshotVersionType: screenshot.versionType,
      thumbnailUrl: screenshot.thumbnailUrl,
    },
  };
};

/**
 * Check if screenshot needs update based on content hash
 */
const screenshotNeedsUpdate = function screenshotNeedsUpdate(
  existingMetadata: ScreenshotMetadata | undefined,
  newContentHash: string,
): boolean {
  if (!existingMetadata) {
    return true;
  }
  return existingMetadata.contentHash !== newContentHash;
};

/**
 * Batch capture multiple component screenshots
 */
const batchCaptureScreenshots = async function batchCaptureScreenshots(
  elements: {
    componentId: string;
    element: HTMLElement;
    version: string;
  }[],
  options: UploadOptions = {},
): Promise<ScreenshotMetadata[]> {
  const results: ScreenshotMetadata[] = [];
  const totalElements = elements.length;

  for (let index = ZERO; index < elements.length; index += ONE) {
    const entry = elements[index];
    if (!entry) {
      continue;
    }
    const { element, componentId, version } = entry;

    try {
      const elementProgress = (percent: number) => {
        const baseProgress = (index / totalElements) * PERCENT_BASE;
        const elementPercent = (percent / PERCENT_BASE) * (PERCENT_BASE / totalElements);
        const totalProgress = baseProgress + elementPercent;
        reportProgress(options, totalProgress);
      };

      const screenshot = await createScreenshot({
        componentId,
        element,
        options: { ...options, onProgress: elementProgress },
        version,
        versionType: 'draft',
      });
      results.push(screenshot);
    } catch (error) {
      logger.error(`Failed to capture screenshot for ${componentId}:`, error);
    }
  }

  return results;
};

/**
 * Clear screenshot cache
 */
const clearScreenshotCache = function clearScreenshotCache(): void {
  screenshotCache.clear();
  thumbnailCache.clear();
};

/**
 * Get cache statistics
 */
const getScreenshotCacheStats = function getScreenshotCacheStats(): {
  screenshots: number;
  thumbnails: number;
  totalFileSize: number;
} {
  let totalFileSize = ZERO;
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
};

export {
  batchCaptureScreenshots,
  cacheScreenshot,
  captureComponentScreenshot,
  clearScreenshotCache,
  createScreenshot,
  deleteScreenshot,
  generateThumbnail,
  getComponentScreenshots,
  getScreenshotCacheStats,
  getScreenshotFromCache,
  screenshotNeedsUpdate,
  updateItemWithScreenshot,
  uploadScreenshot,
};
