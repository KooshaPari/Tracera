/**
 * Service Worker for TraceRTM
 *
 * Provides offline support and intelligent caching for API responses.
 * Implements network-first strategy with cache fallback.
 *
 * Plain JS run in Worker context; typescript-eslint strict rules disabled for this file.
 */
/* eslint-disable @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-argument, @typescript-eslint/no-unsafe-return, @typescript-eslint/strict-boolean-expressions, @typescript-eslint/prefer-nullish-coalescing, @typescript-eslint/promise-function-async */

const CACHE_VERSION = 'v1';
const API_CACHE_NAME = `trace-api-cache-${CACHE_VERSION}`;
const STATIC_CACHE_NAME = `trace-static-cache-${CACHE_VERSION}`;
const MAX_CACHE_AGE = 5 * 60 * 1000; // 5 minutes

/**
 * Install event - setup caches
 */
self.addEventListener('install', (event) => {
	console.log('[ServiceWorker] Installing...');

	event.waitUntil(
		Promise.all([
			caches.open(API_CACHE_NAME),
			caches.open(STATIC_CACHE_NAME),
		]).then(() => {
			console.log('[ServiceWorker] Caches created');
			// Skip waiting to activate immediately
			return self.skipWaiting();
		})
	);
});

/**
 * Activate event - cleanup old caches
 */
self.addEventListener('activate', (event) => {
	console.log('[ServiceWorker] Activating...');

	event.waitUntil(
		caches.keys().then((cacheNames) => {
			return Promise.all(
				cacheNames.map((cacheName) => {
					// Delete old versions
					if (
						(cacheName.startsWith('trace-api-cache-') && cacheName !== API_CACHE_NAME) ||
						(cacheName.startsWith('trace-static-cache-') && cacheName !== STATIC_CACHE_NAME)
					) {
						console.log('[ServiceWorker] Deleting old cache:', cacheName);
						return caches.delete(cacheName);
					}
				})
			);
		}).then(() => {
			// Claim all clients immediately
			return self.clients.claim();
		})
	);
});

/**
 * Fetch event - intercept network requests
 */
self.addEventListener('fetch', (event) => {
	const { request } = event;
	const url = new URL(request.url);

	// Only handle GET requests
	if (request.method !== 'GET') {
		return;
	}

	// Skip chrome-extension and other non-http protocols
	if (!url.protocol.startsWith('http')) {
		return;
	}

	// Determine caching strategy based on request type
	if (isAPIRequest(url)) {
		// API requests: Network-first with cache fallback
		event.respondWith(networkFirstStrategy(request, API_CACHE_NAME));
	} else if (isStaticAsset(url)) {
		// Static assets: Cache-first with network fallback
		event.respondWith(cacheFirstStrategy(request, STATIC_CACHE_NAME));
	} else {
		// Other requests: Network only
		event.respondWith(fetch(request));
	}
});

/**
 * Check if request is an API request
 */
function isAPIRequest(url) {
	return url.pathname.startsWith('/api/');
}

/**
 * Check if request is a static asset
 */
function isStaticAsset(url) {
	const staticExtensions = [
		'.js',
		'.css',
		'.png',
		'.jpg',
		'.jpeg',
		'.gif',
		'.svg',
		'.woff',
		'.woff2',
		'.ttf',
		'.eot',
		'.webp',
		'.ico',
	];

	return staticExtensions.some((ext) => url.pathname.endsWith(ext));
}

/**
 * Network-first strategy
 * Try network first, fall back to cache if offline
 */
async function networkFirstStrategy(request, cacheName) {
	try {
		// Try network
		const networkResponse = await fetch(request);

		// Cache successful responses (200-299)
		if (networkResponse.ok) {
			const cache = await caches.open(cacheName);

			// Clone response before caching (can only read once)
			const responseToCache = networkResponse.clone();

			// Add custom headers for cache metadata
			const headers = new Headers(responseToCache.headers);
			headers.set('X-Cache-Timestamp', Date.now().toString());
			headers.set('X-Cache-Strategy', 'network-first');

			const responseWithMetadata = new Response(responseToCache.body, {
				status: responseToCache.status,
				statusText: responseToCache.statusText,
				headers: headers,
			});

			void cache.put(request, responseWithMetadata);
		}

		return networkResponse;
	} catch {
		// Network failed, try cache
		console.log('[ServiceWorker] Network failed, trying cache:', request.url);

		const cachedResponse = await caches.match(request);

		if (cachedResponse) {
			// Check if cached response is expired
			const timestamp = cachedResponse.headers.get('X-Cache-Timestamp');
			if (timestamp) {
				const age = Date.now() - parseInt(timestamp, 10);
				if (age > MAX_CACHE_AGE) {
					console.log('[ServiceWorker] Cached response expired:', request.url);
					// Return cached response with warning header
					const headers = new Headers(cachedResponse.headers);
					headers.set('X-Cache-Expired', 'true');
					return new Response(cachedResponse.body, {
						status: cachedResponse.status,
						statusText: cachedResponse.statusText,
						headers: headers,
					});
				}
			}

			console.log('[ServiceWorker] Serving from cache:', request.url);
			return cachedResponse;
		}

		// No cache available, return error response
		return new Response(
			JSON.stringify({
				error: 'Network request failed and no cached response available',
				offline: true,
			}),
			{
				status: 503,
				statusText: 'Service Unavailable',
				headers: { 'Content-Type': 'application/json' },
			}
		);
	}
}

/**
 * Cache-first strategy
 * Try cache first, fall back to network
 */
async function cacheFirstStrategy(request, cacheName) {
	// Try cache first
	const cachedResponse = await caches.match(request);

	if (cachedResponse) {
		console.log('[ServiceWorker] Serving from cache:', request.url);
		return cachedResponse;
	}

	// Cache miss, fetch from network
	try {
		const networkResponse = await fetch(request);

		// Cache successful responses
		if (networkResponse.ok) {
			const cache = await caches.open(cacheName);
			void cache.put(request, networkResponse.clone());
		}

		return networkResponse;
	} catch (error) {
		console.error('[ServiceWorker] Fetch failed:', error);

		// Return fallback response
		return new Response(
			'Offline - resource not available',
			{
				status: 503,
				statusText: 'Service Unavailable',
			}
		);
	}
}

/**
 * Message handler for cache management
 */
self.addEventListener('message', (event) => {
	const { type, payload } = event.data;

	switch (type) {
		case 'CLEAR_CACHE':
			void handleClearCache(payload).then(() => {
				event.ports[0].postMessage({ success: true }, self.location.origin);
			});
			break;

		case 'INVALIDATE_PATTERN':
			void handleInvalidatePattern(payload).then((count) => {
				event.ports[0].postMessage({ success: true, count }, self.location.origin);
			});
			break;

		case 'GET_STATS':
			void handleGetStats().then((stats) => {
				event.ports[0].postMessage({ success: true, stats }, self.location.origin);
			});
			break;

		default:
			console.warn('[ServiceWorker] Unknown message type:', type);
	}
});

/**
 * Clear cache
 */
async function handleClearCache(payload) {
	const { cacheName } = payload || {};

	if (cacheName) {
		await caches.delete(cacheName);
	} else {
		// Clear all caches
		const cacheNames = await caches.keys();
		await Promise.all(cacheNames.map((name) => caches.delete(name)));
	}

	console.log('[ServiceWorker] Cache cleared');
}

/**
 * Invalidate cache entries by pattern
 */
async function handleInvalidatePattern(payload) {
	const { pattern, cacheName } = payload || {};
	const targetCache = cacheName || API_CACHE_NAME;

	const cache = await caches.open(targetCache);
	const requests = await cache.keys();

	const regex = new RegExp(pattern.replace(/\*/g, '.*').replace(/\?/g, '.'));
	let count = 0;

	for (const request of requests) {
		if (regex.test(request.url)) {
			await cache.delete(request);
			count++;
		}
	}

	console.log(`[ServiceWorker] Invalidated ${count} entries matching pattern:`, pattern);
	return count;
}

/**
 * Get cache statistics
 */
async function handleGetStats() {
	const cacheNames = await caches.keys();
	const stats = {};

	for (const cacheName of cacheNames) {
		const cache = await caches.open(cacheName);
		const keys = await cache.keys();

		let totalSize = 0;
		for (const request of keys.slice(0, 50)) {
			try {
				const response = await cache.match(request);
				if (response) {
					const blob = await response.blob();
					totalSize += blob.size;
				}
			} catch {
				// Ignore errors for individual entries
			}
		}

		// Extrapolate total size
		if (keys.length > 50) {
			totalSize = Math.floor((totalSize / 50) * keys.length);
		}

		stats[cacheName] = {
			entries: keys.length,
			estimatedSize: totalSize,
		};
	}

	return stats;
}

console.log('[ServiceWorker] Loaded');
