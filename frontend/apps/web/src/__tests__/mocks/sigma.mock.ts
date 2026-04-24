import { vi } from 'vitest';

// Mock Sigma.js to avoid WebGL dependencies in tests
export default class MockSigma {
  on = vi.fn();
  off = vi.fn();
  kill = vi.fn();
  getGraph = vi.fn(() => ({
    edges: vi.fn(() => []),
    nodes: vi.fn(() => []),
  }));
}

// Export types that might be used
export type { NodeDisplayData, EdgeDisplayData } from 'sigma/types';
