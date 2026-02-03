/**
 * Test setup and configuration
 */

import "@testing-library/jest-dom";
import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";

type TestGlobals = typeof globalThis & {
	WebGL2RenderingContext?: unknown;
	IntersectionObserver?: new (...args: unknown[]) => unknown;
	ResizeObserver?: new (...args: unknown[]) => unknown;
	WebSocket?: new (url: string) => unknown;
	HTMLCanvasElement?: new (...args: unknown[]) => unknown;
	__setFetchImpl__?: (impl: typeof fetch) => void;
};

// Mock WebGL2RenderingContext FIRST before any imports
if (typeof globalThis !== "undefined") {
	const WebGL2RenderingContextMock = {
		BOOL: 35_670,
		BYTE: 5120,
		FLOAT: 5126,
		INT: 5124,
		SHORT: 5122,
		UNSIGNED_BYTE: 5121,
		UNSIGNED_INT: 5125,
		UNSIGNED_SHORT: 5123,
	};
	Object.defineProperty(globalThis, "WebGL2RenderingContext", {
		configurable: true,
		value: WebGL2RenderingContextMock as unknown as typeof WebGL2RenderingContext,
		writable: true,
	});
}

// Mock TanStack Router API routes (createAPIFileRoute is from TanStack Start but imported from react-router)
vi.mock("@tanstack/react-router", async () => {
	const actual = await vi.importActual("@tanstack/react-router");
	return {
		...actual,
		createAPIFileRoute: () => () => ({ GET: vi.fn(), POST: vi.fn() }),
	};
});

// Mock elkjs to avoid worker initialization issues in tests
vi.mock("elkjs", () => ({
	default: class MockELK {
		layout() {
			return Promise.resolve({ children: [], edges: [] });
		}
	},
}));

// Already defined at top of file

// Mock sigma.js to avoid WebGL initialization issues
vi.mock("sigma", () => ({
	default: class MockSigma {
		on = vi.fn();
		off = vi.fn();
		kill = vi.fn();
		getGraph = vi.fn(() => ({
			edges: vi.fn(() => []),
			nodes: vi.fn(() => []),
		}));
	},
}));

// Setup localStorage mock BEFORE importing MSW
const localStorageMock = (() => {
	let store: Record<string, string> = {};
	return {
		clear: () => {
			store = {};
		},
		getItem: (key: string) => store[key] || null,
		key: (index: number) => {
			const keys = Object.keys(store);
			return keys[index] || null;
		},
		length: 0,
		removeItem: (key: string) => {
			delete store[key];
		},
		setItem: (key: string, value: string) => {
			store[key] = value.toString();
		},
	};
})();

Object.defineProperty(globalThis, "localStorage", {
	configurable: true,
	value: localStorageMock,
	writable: true,
});

// Cleanup after each test
afterEach(() => {
	cleanup();
	localStorageMock.clear();
});

// Mock window.matchMedia
if (typeof globalThis.window !== "undefined") {
	Object.defineProperty(globalThis.window, "matchMedia", {
		value: vi.fn().mockImplementation((query) => ({
			addEventListener: vi.fn(),
			addListener: vi.fn(),
			dispatchEvent: vi.fn(),
			matches: false,
			media: query,
			onchange: null,
			removeEventListener: vi.fn(),
			removeListener: vi.fn(),
		})),
		writable: true,
	});
}

// Mock navigator.clipboard
if (typeof navigator !== "undefined") {
	Object.defineProperty(navigator, "clipboard", {
		value: {
			readText: vi.fn(() => Promise.resolve("")),
			writeText: vi.fn(() => Promise.resolve()),
		},
		writable: true,
	});
}
// Mock IntersectionObserver
const IntersectionObserverMock = class {
	disconnect() {}
	observe() {}
	takeRecords() {
		return [];
	}
	unobserve() {}
};
Object.defineProperty(globalThis, "IntersectionObserver", {
	configurable: true,
	value: IntersectionObserverMock as unknown as typeof IntersectionObserver,
	writable: true,
});

// Mock ResizeObserver
const ResizeObserverMock = class {
	disconnect() {}
	observe() {}
	unobserve() {}
};
Object.defineProperty(globalThis, "ResizeObserver", {
	configurable: true,
	value: ResizeObserverMock as unknown as typeof ResizeObserver,
	writable: true,
});

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

Object.defineProperty(globalThis, "WebSocket", {
	configurable: true,
	value: MockWebSocket as unknown as typeof WebSocket,
	writable: true,
});

// Mock HTMLCanvasElement for graph visualization
if (typeof globalThis !== "undefined") {
	const MockCanvas = class {
		width = 300;
		height = 150;

		getContext(_type: string) {
			return {
				arc: vi.fn(),
				beginPath: vi.fn(),
				clearRect: vi.fn(),
				clip: vi.fn(),
				closePath: vi.fn(),
				createImageData: vi.fn(() => ({ data: Array.from({ length: 4 }) })),
				createLinearGradient: vi.fn(() => ({ addColorStop: vi.fn() })),
				createRadialGradient: vi.fn(() => ({ addColorStop: vi.fn() })),
				drawImage: vi.fn(),
				fill: vi.fn(),
				fillRect: vi.fn(),
				fillText: vi.fn(),
				getImageData: vi.fn(() => ({ data: Array.from({ length: 4 }) })),
				lineTo: vi.fn(),
				measureText: vi.fn(() => ({ width: 0 })),
				moveTo: vi.fn(),
				putImageData: vi.fn(),
				rect: vi.fn(),
				restore: vi.fn(),
				rotate: vi.fn(),
				save: vi.fn(),
				scale: vi.fn(),
				setTransform: vi.fn(),
				stroke: vi.fn(),
				transform: vi.fn(),
				translate: vi.fn(),
			};
		}

		toDataURL() {
			return "data:image/png;base64,iVBORw0KGgo=";
		}

		toBlob(callback: BlobCallback) {
			callback(new Blob());
		}
	};
	Object.defineProperty(globalThis, "HTMLCanvasElement", {
		configurable: true,
		value: MockCanvas as unknown as typeof HTMLCanvasElement,
		writable: true,
	});
}

// Mock fetch globally for API tests
// Use a delegating mock so tests can override it in beforeEach
let globalFetchImpl: typeof fetch = async (url) => {
	console.warn(`[WARN] Unmocked fetch to ${url}`);
	return Response.json(
		{ error: "Not mocked" },
		{
			headers: { "Content-Type": "application/json" },
			status: 404,
		},
	);
};

globalThis.fetch = vi.fn(
	async (url: string | URL | Request, options?: RequestInit) =>
		globalFetchImpl(url, options),
) as typeof fetch;

// Export so tests can replace the implementation
(globalThis as TestGlobals).__setFetchImpl__ = (impl: typeof fetch) => {
	globalFetchImpl = impl;
};

import { render as rtlRender } from "@testing-library/react";
import type { RenderOptions } from "@testing-library/react";
// Add React testing utilities wrapper for provider-based tests
import React from "react";

// Create test wrapper with all necessary providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) =>
	React.createElement(React.Fragment, null, children);

// Custom render function that wraps components with providers
export const render = (
	ui: React.ReactElement,
	options?: Omit<RenderOptions, "wrapper">,
) => rtlRender(ui, { wrapper: AllTheProviders, ...options });

// Re-export everything from testing library
export * from "@testing-library/react";
