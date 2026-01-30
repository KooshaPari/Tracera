# S3 Screenshot Storage Integration

## Overview

The screenshot storage system has been updated from a mock implementation to real S3 integration with the following features:

- **Presigned URL Upload**: Uses backend-generated presigned URLs for direct S3 uploads
- **Image Compression**: Automatic compression before upload to reduce bandwidth
- **Progress Tracking**: Real-time progress callbacks for upload operations
- **Error Handling**: Comprehensive error types with detailed context
- **File Size Validation**: Enforces 10MB maximum file size
- **Deletion Support**: Ability to delete screenshots from S3
- **Metadata Management**: Tracks storage keys and file sizes for cleanup

## Architecture

### Upload Flow

```
1. Client captures/receives screenshot data
   ↓
2. Compress image (1920x1080, quality 0.9)
   ↓
3. Request presigned upload URL from backend
   ↓
4. Upload file directly to S3 using presigned URL
   ↓
5. Return S3 storage key and permanent URL
   ↓
6. Cache metadata locally
```

### Backend Integration

The frontend expects the following backend endpoint:

```http
POST /api/v1/storage/presigned-upload
Content-Type: application/json
Cookie: (auth token)

{
  "filename": "component-id-version-timestamp.jpg",
  "contentType": "image/jpeg"
}

200 OK
{
  "uploadUrl": "https://s3.bucket.com/upload/signed-url",
  "key": "screenshots/component-id/version-timestamp.jpg"
}
```

And for deletion:

```http
DELETE /api/v1/storage/{key}
Cookie: (auth token)

200 OK
```

## API Reference

### Main Functions

#### uploadScreenshot()

Upload a screenshot to S3 with compression and progress tracking.

```typescript
async function uploadScreenshot(
  screenshotData: string,           // Data URL
  componentId: string,              // Component identifier
  version: string = "v1",           // Version string
  options: UploadOptions = {}       // Optional settings
): Promise<{
  url: string;                      // Permanent URL: /api/v1/storage/{key}
  key: string;                      // S3 object key for deletion
  fileSize: number;                 // Compressed file size
}>
```

**Example:**
```typescript
const result = await uploadScreenshot(
  dataUrl,
  "button-component",
  "v1.0.0",
  {
    onProgress: (percent) => console.log(`${percent}% uploaded`),
    maxWidth: 1920,
    maxHeight: 1080,
    quality: 0.9
  }
);

// result: {
//   url: "/api/v1/storage/screenshots/button-component/v1.0.0-1706572345678.jpg",
//   key: "screenshots/button-component/v1.0.0-1706572345678.jpg",
//   fileSize: 145000
// }
```

#### createScreenshot()

Complete workflow: capture → compress → upload → generate thumbnail → cache.

```typescript
async function createScreenshot(
  element: HTMLElement,
  componentId: string,
  version: string = "1.0.0",
  versionType: "design" | "draft" | "review" | "release" = "draft",
  options: UploadOptions = {}
): Promise<ScreenshotMetadata>
```

#### deleteScreenshot()

Remove screenshot from S3 storage.

```typescript
async function deleteScreenshot(key: string): Promise<void>
```

**Example:**
```typescript
// Delete using the key from uploadScreenshot result
await deleteScreenshot("screenshots/button-component/v1.0.0-1706572345678.jpg");
```

#### batchCaptureScreenshots()

Capture and upload multiple screenshots with aggregate progress tracking.

```typescript
async function batchCaptureScreenshots(
  elements: Array<{
    element: HTMLElement;
    componentId: string;
    version: string;
  }>,
  options: UploadOptions = {}
): Promise<ScreenshotMetadata[]>
```

**Example:**
```typescript
const screenshots = await batchCaptureScreenshots(
  [
    { element: btn1, componentId: "button-1", version: "v1" },
    { element: btn2, componentId: "button-2", version: "v1" }
  ],
  {
    onProgress: (percent) => {
      // 0-100% progress across all elements
      console.log(`Overall progress: ${percent}%`);
    }
  }
);
```

### Caching Functions

#### cacheScreenshot()
Store metadata locally for quick access.

```typescript
cacheScreenshot(metadata: ScreenshotMetadata): void
```

#### getScreenshotFromCache()
Retrieve cached metadata.

```typescript
getScreenshotFromCache(id: string): ScreenshotMetadata | undefined
```

#### getComponentScreenshots()
Get all screenshots for a component, sorted by recency.

```typescript
getComponentScreenshots(componentId: string): ScreenshotMetadata[]
```

#### clearScreenshotCache()
Clear in-memory cache.

```typescript
clearScreenshotCache(): void
```

#### getScreenshotCacheStats()
Get cache statistics.

```typescript
getScreenshotCacheStats(): {
  screenshots: number;
  thumbnails: number;
  totalFileSize: number;
}
```

## Types

### ScreenshotMetadata

```typescript
interface ScreenshotMetadata {
  id: string;                                      // Unique ID
  componentId: string;                             // Component reference
  url: string;                                     // Permanent URL
  thumbnailUrl?: string;                           // Optional thumbnail
  width: number;                                   // Original width
  height: number;                                  // Original height
  version: string;                                 // Version string
  versionType: "design" | "draft" | "review" | "release";
  createdAt: Date;                                 // Creation timestamp
  updatedAt: Date;                                 // Update timestamp
  contentHash?: string;                            // Change detection hash
  storageKey?: string;                             // S3 key for deletion
  fileSize?: number;                               // Compressed file size
}
```

### UploadOptions

```typescript
interface UploadOptions {
  onProgress?: (percent: number) => void;         // 0-100 progress
  maxWidth?: number;                               // Default: 1920
  maxHeight?: number;                              // Default: 1080
  quality?: number;                                // JPEG quality 0-1, default: 0.9
}
```

### UploadError

```typescript
interface UploadError extends Error {
  code: "NETWORK_ERROR"      // Network connectivity issues
       | "UPLOAD_FAILED"     // S3 upload or API errors
       | "INVALID_FILE"      // File size/format validation
       | "COMPRESSION_FAILED"; // Image compression issues
  details?: string;           // Additional context
  statusCode?: number;        // HTTP status code if applicable
}
```

## Implementation Details

### Image Compression

Before upload, images are automatically compressed:
- **Max dimensions**: 1920x1080 (preserves aspect ratio)
- **Format**: JPEG
- **Quality**: 0.9 (90% quality, ~10% bandwidth savings)
- **Size limit**: 10MB maximum

### Progress Tracking

Progress callback is called at multiple stages:
- 5%: Compression starting
- 15%: Compression complete
- 20%: Presigned URL requested
- 30%: Presigned URL received
- 30-95%: S3 upload in progress (mapped from XHR progress)
- 100%: Complete

### Error Handling

All errors include:
- `code`: Machine-readable error type
- `message`: Human-readable error description
- `details`: Additional context (stack traces, API responses)
- `statusCode`: HTTP status code if applicable

**Example error handling:**
```typescript
try {
  await uploadScreenshot(data, componentId, version);
} catch (error) {
  const uploadError = error as UploadError;

  if (uploadError.code === "NETWORK_ERROR") {
    // Retry upload
  } else if (uploadError.code === "INVALID_FILE") {
    // Show user: file too large
  } else if (uploadError.code === "UPLOAD_FAILED" && uploadError.statusCode === 429) {
    // Rate limited - wait and retry
  }
}
```

## Testing

### Unit Tests
```bash
bun run test -- src/__tests__/utils/screenshot.test.ts
```

Tests cover:
- S3 upload with presigned URLs
- Image compression
- Progress tracking
- Error handling
- File size validation
- Caching operations
- Batch operations

### Integration Tests
```bash
bun run test:e2e
```

E2E tests verify:
- Complete screenshot lifecycle
- Progress UI updates
- Error recovery
- Component screenshot capture

## Migration Guide

### From Mock Implementation

Old code (mock):
```typescript
const url = await uploadScreenshot(data, componentId, version);
// url was like: "/api/screenshots/component-id/version"
```

New code (S3):
```typescript
const { url, key, fileSize } = await uploadScreenshot(
  data,
  componentId,
  version
);
// url is: "/api/v1/storage/screenshots/component-id/version-timestamp.jpg"
// key is: "screenshots/component-id/version-timestamp.jpg" (for deletion)
```

### Storing Metadata

Always store the S3 `key` if you need to delete the screenshot later:

```typescript
const screenshot = await createScreenshot(element, componentId, version);
// screenshot.storageKey contains the S3 key for deletion

// Later, to delete:
await deleteScreenshot(screenshot.storageKey);
```

## Performance Considerations

1. **Compression**: Reduces bandwidth by ~70% before S3 upload
2. **Presigned URLs**: Direct S3 upload avoids server proxy overhead
3. **Caching**: Local metadata cache reduces database queries
4. **Progress tracking**: Non-blocking progress updates (0-5ms overhead)

## Security

- **No service keys in client**: Only anon key + presigned URLs
- **Presigned URLs**: Generated server-side with expiration
- **Authentication**: Required to request presigned URLs
- **Deletion**: Requires authentication
- **File validation**: 10MB size limit prevents abuse

## Future Enhancements

- [ ] WebP support for better compression
- [ ] Multiple format selection (PNG, WebP, AVIF)
- [ ] Background upload queue
- [ ] Partial upload resume on reconnect
- [ ] Automatic cleanup of old versions
- [ ] CDN caching headers
