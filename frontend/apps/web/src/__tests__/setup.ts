/**
 * Test setup and configuration
 */

import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { toHaveNoViolations } from 'jest-axe';
import { createRequire } from 'node:module';
import React from 'react';
import { afterEach, afterAll, beforeAll, expect, vi } from 'vitest';

// Keep the shared keyboard/mouse surface available to legacy a11y tests.  The
// CJS entrypoint avoids Bun + ESM interop returning an object without setup().
const require = createRequire(import.meta.url);
const userEventModule = require('@testing-library/user-event') as {
  default?: { setup: typeof import('@testing-library/user-event').default.setup };
  setup?: typeof import('@testing-library/user-event').default.setup;
};
const userEvent = userEventModule.default ?? userEventModule;

expect.extend({ toHaveNoViolations });

type TestGlobals = typeof globalThis & {
  WebGL2RenderingContext?: unknown;
  WebGLRenderingContext?: unknown;
  IntersectionObserver?: new (...args: unknown[]) => unknown;
  ResizeObserver?: new (...args: unknown[]) => unknown;
  WebSocket?: new (url: string) => unknown;
  HTMLCanvasElement?: new (...args: unknown[]) => unknown;
  __setFetchImpl__?: (impl: typeof fetch) => void;
};

// Sigma reads WebGL constants while its module is loading. Keep this import-time
// contract constructor-free: rendering behavior remains covered by graph mocks.
if (typeof globalThis !== 'undefined') {
  const WebGLRenderingContextMock = {
    BOOL: 35_670,
    BYTE: 5120,
    FLOAT: 5126,
    INT: 5124,
    SHORT: 5122,
    TRIANGLES: 4,
    UNSIGNED_BYTE: 5121,
    UNSIGNED_INT: 5125,
    UNSIGNED_SHORT: 5123,
  };
  Object.defineProperty(globalThis, 'WebGLRenderingContext', {
    configurable: true,
    value: WebGLRenderingContextMock as unknown as typeof WebGLRenderingContext,
    writable: true,
  });
  Object.defineProperty(globalThis, 'WebGL2RenderingContext', {
    configurable: true,
    value: WebGLRenderingContextMock as unknown as typeof WebGL2RenderingContext,
    writable: true,
  });
}

// Mock TanStack Router API routes (createAPIFileRoute is from TanStack Start but imported from react-router)
vi.mock('@tanstack/react-router', async () => {
  const actual = await vi.importActual('@tanstack/react-router');
  return {
    ...actual,
    createAPIFileRoute: () => () => ({ GET: vi.fn(), POST: vi.fn() }),
    useNavigate: () => vi.fn(),
    useRouter: () => ({
      navigate: vi.fn(),
    }),
    useLocation: () => ({ pathname: '/' }),
    useParams: () => ({}),
    Link: ({ children, to, ...props }: any) =>
      React.createElement(
        'a',
        {
          href: typeof to === 'string' ? to : to?.toString?.(),
          ...props,
        },
        children,
      ),
  };
});

// Mock elkjs to avoid worker initialization issues in tests
vi.mock('elkjs', () => ({
  default: class MockELK {
    async layout() {
      return { children: [], edges: [] };
    }
  },
}));

// Already defined at top of file

// Mock sigma.js to avoid WebGL initialization issues
vi.mock('sigma', () => ({
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
const localStorageMock: Storage = (() => {
  let store: Record<string, string> = {};
  return {
    clear() {
      store = {};
    },
    getItem(key: string) {
      return store[key] ?? null;
    },
    key(index: number) {
      const keys = Object.keys(store);
      return keys[index] ?? null;
    },
    get length() {
      return Object.keys(store).length;
    },
    removeItem(key: string) {
      delete store[key];
    },
    setItem(key: string, value: string) {
      store[key] = value.toString();
    },
  };
})();

Object.defineProperty(globalThis, 'localStorage', {
  configurable: true,
  value: localStorageMock,
  writable: true,
});

// Cleanup after each test
beforeEach(() => {
  globalThis.user = userEvent.setup();
});

afterEach(() => {
  cleanup();
  localStorageMock.clear();
});

// Mock window.matchMedia
if (typeof globalThis.window !== 'undefined') {
  Object.defineProperty(globalThis.window, 'matchMedia', {
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
if (typeof navigator !== 'undefined') {
  Object.defineProperty(navigator, 'clipboard', {
    configurable: true,
    value: {
      readText: vi.fn(async () => ''),
      writeText: vi.fn(async () => {}),
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
Object.defineProperty(globalThis, 'IntersectionObserver', {
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
Object.defineProperty(globalThis, 'ResizeObserver', {
  configurable: true,
  value: ResizeObserverMock as unknown as typeof ResizeObserver,
  writable: true,
});

// Mock pointer capture methods for Radix UI components
if (typeof globalThis !== 'undefined' && typeof Element !== 'undefined') {
  Element.prototype.hasPointerCapture = vi.fn().mockReturnValue(false);
  Element.prototype.setPointerCapture = vi.fn();
  Element.prototype.releasePointerCapture = vi.fn();
}

// Mock scrollIntoView for Radix UI components
if (typeof globalThis !== 'undefined' && typeof Element !== 'undefined') {
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
        this.onopen(new Event('open'));
      }
    }, 0);
  }

  send(_data: string) {}
  close() {
    this.readyState = MockWebSocket.CLOSED;
    if (this.onclose) {
      this.onclose(new CloseEvent('close'));
    }
  }
  addEventListener(_type: string, _listener: EventListener) {}
  removeEventListener(_type: string, _listener: EventListener) {}
  dispatchEvent(_event: Event) {
    return true;
  }
}

Object.defineProperty(globalThis, 'WebSocket', {
  configurable: true,
  value: MockWebSocket as unknown as typeof WebSocket,
  writable: true,
});

// Mock HTMLCanvasElement for graph visualization
if (typeof globalThis !== 'undefined') {
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
      return 'data:image/png;base64,iVBORw0KGgo=';
    }

    toBlob(callback: BlobCallback) {
      callback(new Blob());
    }
  };
  const nativeCanvas = globalThis.HTMLCanvasElement;
  if (typeof nativeCanvas === 'function') {
    // document.createElement('canvas') uses jsdom's original realm constructor.
    // Patch that prototype instead of replacing the global constructor, which
    // would leave created canvases on the unimplemented jsdom prototype.
    Object.defineProperties(nativeCanvas.prototype, {
      getContext: {
        configurable: true,
        value: MockCanvas.prototype.getContext,
        writable: true,
      },
      toBlob: {
        configurable: true,
        value: MockCanvas.prototype.toBlob,
        writable: true,
      },
      toDataURL: {
        configurable: true,
        value: MockCanvas.prototype.toDataURL,
        writable: true,
      },
    });
  } else {
    Object.defineProperty(globalThis, 'HTMLCanvasElement', {
      configurable: true,
      value: MockCanvas as unknown as typeof HTMLCanvasElement,
      writable: true,
    });
  }
}

// axe asks for pseudo-element styles. jsdom does not implement that optional
// branch and emits a console error before returning ordinary computed styles,
// so retain its useful behavior without forwarding the unsupported argument.
if (typeof globalThis.getComputedStyle === 'function') {
  const nativeGetComputedStyle = globalThis.getComputedStyle.bind(globalThis);
  Object.defineProperty(globalThis, 'getComputedStyle', {
    configurable: true,
    value: (element: Element): CSSStyleDeclaration => nativeGetComputedStyle(element),
    writable: true,
  });
}

// Radix uses scrollTo while positioning dialogs; jsdom exposes only a noisy
// not-implemented stub, so provide the browser side-effect boundary explicitly.
Object.defineProperty(globalThis, 'scrollTo', {
  configurable: true,
  value: vi.fn(),
  writable: true,
});

// Mock fetch globally for API tests
// Use a delegating mock so tests can override it in beforeEach
let globalFetchImpl: typeof fetch = async (url) => {
  console.warn(`[WARN] Unmocked fetch to ${url}`);
  return Response.json(
    { error: 'Not mocked' },
    {
      headers: { 'Content-Type': 'application/json' },
      status: 404,
    },
  );
};

globalThis.fetch = vi.fn(async (url: string | URL | Request, options?: RequestInit) =>
  globalFetchImpl(url, options),
) as typeof fetch;

// Export so tests can replace the implementation
(globalThis as TestGlobals).__setFetchImpl__ = (impl: typeof fetch) => {
  globalFetchImpl = impl;
};

import type { RenderOptions } from '@testing-library/react';

import { render as rtlRender } from '@testing-library/react';
// Add React testing utilities wrapper for provider-based tests

// Create test wrapper with all necessary providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) =>
  React.createElement(React.Fragment, null, children);

// Custom render function that wraps components with providers
export const render = (ui: React.ReactElement, options?: Omit<RenderOptions, 'wrapper'>) =>
  rtlRender(ui, { wrapper: AllTheProviders, ...options });

// Re-export everything from testing library
export * from '@testing-library/react';

// ============================================================================
// MSW Server Setup
// ============================================================================

import { waitFor } from '@testing-library/react';
// MSW TEMPORARILY DISABLED DUE TO GRAPHQL ESM/COMMONJS IMPORT ISSUE
// See: CRITICAL_BLOCKER_MSW_GRAPHQL.md
// TODO: Re-enable after fixing graphql import or replacing MSW
// Start MSW server before all tests
// BeforeAll(() => {
//   Try {
//     Const server = getServer();
//     Server.listen();
//   } catch (error) {
//     Console.warn('MSW server initialization failed:', error);
//     // Continue anyway - tests that don't need HTTP mocking will still work
//   }
// });
// Stop MSW server after all tests
// AfterAll(() => {
//   Try {
//     Const server = getServer();
//     Server.close();
//   } catch (error) {
//     // Ignore cleanup errors
//   }
// });
// Reset handlers after each test
// AfterEach(() => {
//   Try {
//     Const server = getServer();
//     Server.resetHandlers();
//   } catch (error) {
//     // Ignore reset errors
//   }
// });
// ============================================================================
// Async Test Helpers
// ============================================================================

import { getServer } from './mocks/server';

/**
 * Wait for loading state to appear and then disappear
 * Useful for async operations that show loading UI
 */
export const waitForLoadingState = async (container: HTMLElement, timeout: number = 3000) => {
  // Wait for loading indicator to appear
  await waitFor(
    () => {
      const loader = container.querySelector('[data-testid="loading"]');
      if (!loader) {
        throw new Error('Loading indicator not found');
      }
    },
    { timeout: 500 },
  ).catch(() => {
    // Some tests may not have a loading indicator
  });

  // Wait for loading indicator to disappear
  await waitFor(
    () => {
      const loader = container.querySelector('[data-testid="loading"]');
      if (loader) {
        throw new Error('Loading indicator still visible');
      }
    },
    { timeout },
  );
};

/**
 * Wait for an element with text content to appear
 */
export const waitForElementWithText = async (
  container: HTMLElement,
  text: string,
  timeout: number = 3000,
) => {
  let element: HTMLElement | null = null;
  await waitFor(
    () => {
      element = [...container.querySelectorAll('*')].find((el) => el.textContent?.includes(text)) as
        | HTMLElement
        | undefined;
      if (!element) {
        throw new Error(`Element with text "${text}" not found`);
      }
    },
    { timeout },
  );
  return element;
};

/**
 * Clear all stores and caches for a clean test state
 * Includes: zustand stores, React Query cache, localStorage
 */
export const clearAllStores = () => {
  // Clear localStorage
  if (typeof localStorage !== 'undefined') {
    localStorage.clear();
  }

  // Clear React Query cache (if it exists in the test)
  if (typeof window !== 'undefined') {
    (window as any).__REACT_QUERY_CACHE__ = undefined;
  }

  // Clear any zustand stores by removing from localStorage
  Object.keys(localStorageMock).forEach((key) => {
    if (key.includes('store') || key.includes('zustand')) {
      localStorageMock.removeItem(key);
    }
  });
};

/**
 * Wrapper for async test operations with auto-cleanup
 */
export const withAsyncCleanup = async (testFn: () => Promise<void>) => {
  try {
    await testFn();
  } finally {
    clearAllStores();
  }
};
