/**
 * Test setup and configuration
 */

import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";
import "@testing-library/jest-dom";
import { toHaveNoViolations } from "jest-axe";
import { expect } from "vitest";

// Extend Vitest matchers with jest-axe
expect.extend(toHaveNoViolations);

// Mock TanStack Router API routes (createAPIFileRoute is from TanStack Start but imported from react-router)
vi.mock("@tanstack/react-router", async () => {
	const actual = await vi.importActual("@tanstack/react-router");
	return {
		...actual,
		createAPIFileRoute: () => () => ({ GET: vi.fn(), POST: vi.fn() }),
	};
});

// Setup localStorage mock BEFORE importing MSW
const localStorageMock = (() => {
	let store: Record<string, string> = {};
	return {
		getItem: (key: string) => store[key] || null,
		setItem: (key: string, value: string) => {
			store[key] = value.toString();
		},
		removeItem: (key: string) => {
			delete store[key];
		},
		clear: () => {
			store = {};
		},
		length: 0,
		key: (index: number) => {
			const keys = Object.keys(store);
			return keys[index] || null;
		},
	};
})();

Object.defineProperty(global, "localStorage", {
	value: localStorageMock,
	writable: true,
	configurable: true,
});

// Cleanup after each test
afterEach(() => {
	cleanup();
	localStorageMock.clear();
});

// Mock window.matchMedia
if (typeof globalThis.window !== "undefined") {
	Object.defineProperty(globalThis.window, "matchMedia", {
		writable: true,
		value: vi.fn().mockImplementation((query) => ({
			matches: false,
			media: query,
			onchange: null,
			addListener: vi.fn(),
			removeListener: vi.fn(),
			addEventListener: vi.fn(),
			removeEventListener: vi.fn(),
			dispatchEvent: vi.fn(),
		})),
	});
}
// Mock IntersectionObserver
(globalThis as any).IntersectionObserver = class IntersectionObserver {
	disconnect() {}
	observe() {}
	takeRecords() {
		return [];
	}
	unobserve() {}
} as any;

// Mock ResizeObserver
(globalThis as any).ResizeObserver = class ResizeObserver {
	disconnect() {}
	observe() {}
	unobserve() {}
} as any;

// Mock pointer capture methods for Radix UI components
if (typeof globalThis !== "undefined" && typeof Element !== "undefined") {
	Element.prototype.hasPointerCapture = vi.fn().mockReturnValue(false);
	Element.prototype.setPointerCapture = vi.fn();
	Element.prototype.releasePointerCapture = vi.fn();
}

// Mock scrollIntoView for Radix UI components
if (typeof globalThis !== "undefined" && typeof Element !== "undefined") {
	Element.prototype.scrollIntoView = vi.fn();
}

// Mock WebSocket
class MockWebSocket {
	static readonly CONNECTING = 0;
	static readonly OPEN = 1;
	static readonly CLOSING = 2;
	static readonly CLOSED = 3;

	url: string;
	readyState: number = MockWebSocket.CONNECTING;
	onopen: ((event: Event) => void) | null = null;
	onclose: ((event: CloseEvent) => void) | null = null;
	onmessage: ((event: MessageEvent) => void) | null = null;
	onerror: ((event: Event) => void) | null = null;

	constructor(url: string) {
		this.url = url;
		setTimeout(() => {
			this.readyState = MockWebSocket.OPEN;
			if (this.onopen) {
				this.onopen(new Event("open"));
			}
		}, 0);
	}

	send(_data: string) {}
	close() {
		this.readyState = MockWebSocket.CLOSED;
		if (this.onclose) {
			this.onclose(new CloseEvent("close"));
		}
	}
	addEventListener(_type: string, _listener: EventListener) {}
	removeEventListener(_type: string, _listener: EventListener) {}
	dispatchEvent(_event: Event) {
		return true;
	}
}

(globalThis as any).WebSocket = MockWebSocket as any;

// Mock HTMLCanvasElement for graph visualization
if (typeof globalThis !== "undefined") {
	(globalThis as any).HTMLCanvasElement = class MockCanvas {
		width: number = 300;
		height: number = 150;

		getContext(_type: string) {
			return {
				fillRect: vi.fn(),
				clearRect: vi.fn(),
				getImageData: vi.fn(() => ({ data: new Array(4) })),
				putImageData: vi.fn(),
				createImageData: vi.fn(() => ({ data: new Array(4) })),
				setTransform: vi.fn(),
				drawImage: vi.fn(),
				save: vi.fn(),
				fillText: vi.fn(),
				restore: vi.fn(),
				beginPath: vi.fn(),
				moveTo: vi.fn(),
				lineTo: vi.fn(),
				closePath: vi.fn(),
				stroke: vi.fn(),
				translate: vi.fn(),
				scale: vi.fn(),
				rotate: vi.fn(),
				arc: vi.fn(),
				fill: vi.fn(),
				measureText: vi.fn(() => ({ width: 0 })),
				transform: vi.fn(),
				rect: vi.fn(),
				clip: vi.fn(),
				createLinearGradient: vi.fn(() => ({ addColorStop: vi.fn() })),
				createRadialGradient: vi.fn(() => ({ addColorStop: vi.fn() })),
			};
		}

		toDataURL() {
			return "data:image/png;base64,iVBORw0KGgo=";
		}

		toBlob(callback: BlobCallback) {
			callback(new Blob());
		}
	} as any;
}

// Mock fetch globally for API tests
// Use a delegating mock so tests can override it in beforeEach
let globalFetchImpl: typeof fetch = async (url) => {
	console.warn(`[WARN] Unmocked fetch to ${url}`);
	return new Response(JSON.stringify({ error: "Not mocked" }), {
		status: 404,
		headers: { "Content-Type": "application/json" },
	});
};

global.fetch = vi.fn(async (url: any, options?: any) => {
	return globalFetchImpl(url, options);
}) as unknown as typeof fetch;

// Export so tests can replace the implementation
(globalThis as any).__setFetchImpl__ = (impl: typeof fetch) => {
	globalFetchImpl = impl;
};

import {
	type RenderOptions,
	render as rtlRender,
} from "@testing-library/react";
// Add React testing utilities wrapper for provider-based tests
import React from "react";

// Create test wrapper with all necessary providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
	return React.createElement(React.Fragment, null, children);
};

// Custom render function that wraps components with providers
export const render = (
	ui: React.ReactElement,
	options?: Omit<RenderOptions, "wrapper">,
) => {
	return rtlRender(ui, { wrapper: AllTheProviders, ...options });
};

// Re-export everything from testing library
export * from "@testing-library/react";
