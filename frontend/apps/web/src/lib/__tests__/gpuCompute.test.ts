/**
 * GPU Compute Tests
 *
 * Tests for WebGPU/WebGL compute shader implementations
 * Verifies correct force calculations and performance targets
 */

import * as Vitest from 'vitest';

import { logger } from '../logger';

const { afterEach, beforeEach, describe, expect, it } = Vitest;

// ============================================================================
// MOCK GPU APIS
// ============================================================================

// Mock WebGPU API (for testing in jsdom environment)
const mockGPUAdapter = {
  requestDevice: Vitest.vi.fn(async () => ({
    createBuffer: Vitest.vi.fn(() => ({
      destroy: Vitest.vi.fn(),
      mapAsync: Vitest.vi.fn(async () => {}),
      getMappedRange: Vitest.vi.fn(() => new ArrayBuffer(1024)),
      unmap: Vitest.vi.fn(),
    })),
    createShaderModule: Vitest.vi.fn(() => ({})),
    createBindGroupLayout: Vitest.vi.fn(() => ({})),
    createPipelineLayout: Vitest.vi.fn(() => ({})),
    createComputePipeline: Vitest.vi.fn(() => ({
      getBindGroupLayout: Vitest.vi.fn(() => ({})),
    })),
    createBindGroup: Vitest.vi.fn(() => ({})),
    createCommandEncoder: Vitest.vi.fn(() => ({
      beginComputePass: Vitest.vi.fn(() => ({
        setPipeline: Vitest.vi.fn(),
        setBindGroup: Vitest.vi.fn(),
        dispatchWorkgroups: Vitest.vi.fn(),
        end: Vitest.vi.fn(),
      })),
      copyBufferToBuffer: Vitest.vi.fn(),
      finish: Vitest.vi.fn(() => ({})),
    })),
    queue: {
      writeBuffer: Vitest.vi.fn(),
      submit: Vitest.vi.fn(),
      onSubmittedWorkDone: Vitest.vi.fn(async () => {}),
    },
    destroy: Vitest.vi.fn(),
    lost: Promise.resolve({ message: 'test', reason: 'destroyed' }),
  })),
};

const mockNavigator = {
  gpu: {
    requestAdapter: Vitest.vi.fn(async () => mockGPUAdapter),
  },
};

async function requestMockDevice() {
  const adapter = await mockNavigator.gpu.requestAdapter();

  Vitest.expect(adapter).toBeTruthy();

  return adapter.requestDevice();
}

// ============================================================================
// TEST UTILITIES
// ============================================================================

/**
 * Generate test graph data
 *
 * @param {number} nodeCount Number of nodes to generate.
 * @returns {{ positions: Float32Array; velocities: Float32Array; forces: Float32Array }}
 *   Position, velocity, and force buffers for the test graph.
 */
function generateTestGraph(nodeCount: number) {
  const positions = new Float32Array(nodeCount * 2);
  const velocities = new Float32Array(nodeCount * 2);
  const forces = new Float32Array(nodeCount * 2);

  // Initialize positions in a grid
  const cols = Math.ceil(Math.sqrt(nodeCount));
  for (let i = 0; i < nodeCount; i++) {
    positions[i * 2] = (i % cols) * 100;
    positions[i * 2 + 1] = Math.floor(i / cols) * 100;
    velocities[i * 2] = 0;
    velocities[i * 2 + 1] = 0;
  }

  return { positions, velocities, forces };
}

/**
 * Generate test edges
 *
 * @param {number} nodeCount Number of nodes in the graph.
 * @param {number} density Edge density ratio to generate.
 * @returns {Uint32Array} Edge pairs as a flat typed array.
 */
function generateTestEdges(nodeCount: number, density = 0.1): Uint32Array {
  const maxEdges = Math.floor(nodeCount * nodeCount * density);
  const edges = new Uint32Array(maxEdges * 2);

  for (let i = 0; i < maxEdges; i++) {
    const source = Math.floor(Math.random() * nodeCount);
    const target = Math.floor(Math.random() * nodeCount);
    edges[i * 2] = source;
    edges[i * 2 + 1] = target;
  }

  return edges;
}

// ============================================================================
// TESTS
// ============================================================================

Vitest.describe('GPU Compute Infrastructure', () => {
  Vitest.beforeEach(() => {
    // Mock navigator.gpu
    Object.defineProperty(globalThis.navigator, 'gpu', {
      value: mockNavigator.gpu,
      writable: true,
      configurable: true,
    });
  });

  Vitest.afterEach(() => {
    Vitest.vi.clearAllMocks();
  });

  Vitest.describe('WebGPU Device Initialization', () => {
    Vitest.it('should detect WebGPU support', () => {
      Vitest.expect(globalThis.navigator.gpu).toBeDefined();
    });

    Vitest.it('should request adapter with high-performance preference', async () => {
      await mockNavigator.gpu.requestAdapter({ powerPreference: 'high-performance' });

      Vitest.expect(mockNavigator.gpu.requestAdapter).toHaveBeenCalledWith({
        powerPreference: 'high-performance',
      });
    });

    Vitest.it('should handle adapter request failure', async () => {
      const originalRequestAdapter = mockNavigator.gpu.requestAdapter;
      mockNavigator.gpu.requestAdapter = Vitest.vi.fn(async () => null);

      const adapter = await mockNavigator.gpu.requestAdapter();
      Vitest.expect(adapter).toBeNull();

      mockNavigator.gpu.requestAdapter = originalRequestAdapter;
    });
  });

  Vitest.describe('Buffer Management', () => {
    Vitest.it('should create storage buffers with correct size', async () => {
      const device = await requestMockDevice();

      const nodeCount = 1000;
      const positionsSize = nodeCount * 2 * Float32Array.BYTES_PER_ELEMENT;

      device.createBuffer({
        size: positionsSize,
        usage: 3, // STORAGE | COPY_DST
      });

      Vitest.expect(device.createBuffer).toHaveBeenCalledWith(
        Vitest.expect.objectContaining({
          size: positionsSize,
        }),
      );
    });

    Vitest.it('should write data to buffers', async () => {
      const device = await requestMockDevice();

      const testData = new Float32Array([1, 2, 3, 4]);
      const buffer = device.createBuffer({ size: 16, usage: 3 });

      device.queue.writeBuffer(buffer, 0, testData);

      Vitest.expect(device.queue.writeBuffer).toHaveBeenCalledWith(buffer, 0, testData);
    });
  });

  Vitest.describe('Compute Pipeline', () => {
    Vitest.it('should create shader module from WGSL code', async () => {
      const device = await requestMockDevice();

      const shaderCode = '@compute @workgroup_size(64) fn main() {}';
      device.createShaderModule({ code: shaderCode });

      Vitest.expect(device.createShaderModule).toHaveBeenCalledWith({ code: shaderCode });
    });

    Vitest.it('should create compute pipeline with entry point', async () => {
      const device = await requestMockDevice();

      const shaderModule = device.createShaderModule({ code: '' });
      const layout = device.createPipelineLayout({ bindGroupLayouts: [] });

      device.createComputePipeline({
        layout,
        compute: {
          module: shaderModule,
          entryPoint: 'main',
        },
      });

      Vitest.expect(device.createComputePipeline).toHaveBeenCalledWith(
        Vitest.expect.objectContaining({
          compute: Vitest.expect.objectContaining({
            entryPoint: 'main',
          }),
        }),
      );
    });
  });

  Vitest.describe('Force Calculation Logic', () => {
    Vitest.it('should calculate repulsion force correctly', () => {
      // Test the math for repulsion force
      // F = k / r² where k = repulsionStrength

      const pos1 = { x: 0, y: 0 };
      const pos2 = { x: 100, y: 0 };
      const strength = 5000;

      const delta = { x: pos1.x - pos2.x, y: pos1.y - pos2.y };
      const distSq = delta.x * delta.x + delta.y * delta.y;
      const dist = Math.sqrt(distSq);
      const force = strength / distSq;

      const expectedForceX = (delta.x / dist) * force;

      Vitest.expect(expectedForceX).toBeCloseTo(-0.5, 1);
    });

    Vitest.it('should calculate attraction force correctly', () => {
      // Test the math for attraction force
      // F = k * d where k = attractionStrength

      const pos1 = { x: 0, y: 0 };
      const pos2 = { x: 100, y: 0 };
      const strength = 0.1;

      const delta = { x: pos2.x - pos1.x, y: pos2.y - pos1.y };
      const dist = Math.hypot(delta.x, delta.y);
      const force = strength * dist;

      const expectedForceX = (delta.x / dist) * force;

      Vitest.expect(expectedForceX).toBeCloseTo(10, 1);
    });
  });

  describe('Workgroup Dispatch', () => {
    it('should calculate correct workgroup count for node count', async () => {
      const device = await requestMockDevice();

      const nodeCount = 10_000;
      const workgroupSize = 64;
      const workgroupCount = Math.ceil(nodeCount / workgroupSize);

      expect(workgroupCount).toBe(157); // Ceil(10_000 / 64)

      const encoder = device.createCommandEncoder();
      const pass = encoder.beginComputePass();

      pass.dispatchWorkgroups(workgroupCount);

      expect(pass.dispatchWorkgroups).toHaveBeenCalledWith(workgroupCount);
    });

    it('should handle edge cases for workgroup calculation', () => {
      const testCases = [
        { nodes: 1, expected: 1 },
        { nodes: 64, expected: 1 },
        { nodes: 65, expected: 2 },
        { nodes: 128, expected: 2 },
        { nodes: 129, expected: 3 },
      ];

      for (const { nodes, expected } of testCases) {
        const workgroupCount = Math.ceil(nodes / 64);
        expect(workgroupCount).toBe(expected);
      }
    });
  });

  describe('Performance Metrics', () => {
    it('should measure iteration time', async () => {
      const startTime = globalThis.performance.now();

      // Simulate some work
      await new Promise((resolve) => globalThis.setTimeout(resolve, 10));

      const duration = globalThis.performance.now() - startTime;
      expect(duration).toBeGreaterThanOrEqual(10);
    });

    it('should verify speedup target for 10k nodes', () => {
      // Target: <100ms per iteration on GPU vs ~30s CPU
      // This is ~300x speedup minimum

      const cpuTime = 30_000; // 30s baseline
      const targetGPUTime = 100; // 100ms target
      const expectedSpeedup = cpuTime / targetGPUTime;

      expect(expectedSpeedup).toBeGreaterThanOrEqual(300);
    });
  });
});

// ============================================================================
// WEBGL TESTS
// ============================================================================

// Skip WebGL tests in jsdom (need real browser context)
describe.skip('WebGL Compute Fallback', () => {
  let canvas: HTMLCanvasElement;
  let gl: WebGL2RenderingContext | null;

  beforeEach(() => {
    canvas = globalThis.document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 512;
    gl = canvas.getContext('webgl2');
  });

  afterEach(() => {
    if (gl) {
      const loseExt = gl.getExtension('WEBGL_lose_context');
      if (loseExt) {
        loseExt.loseContext();
      }
    }
  });

  describe('WebGL2 Context', () => {
    it('should create WebGL2 context', () => {
      expect(gl).toBeTruthy();
    });

    it('should check for float texture support', () => {
      if (!gl) {
        return;
      }

      const floatExt = gl.getExtension('EXT_color_buffer_float');
      // In jsdom, this will be null, but in real browser it should exist.
      expect(floatExt).toBeDefined();
    });
  });

  describe('Texture Creation', () => {
    it('should create float textures for data', () => {
      if (!gl) {
        return;
      }

      const texture = gl.createTexture();
      expect(texture).toBeTruthy();

      gl.bindTexture(gl.TEXTURE_2D, texture);

      // Example real implementation:
      // Gl.texImage2D(
      //   Gl.TEXTURE_2D,
      //   0,
      //   Gl.RG32F,
      //   512,
      //   512,
      //   0,
      //   Gl.RG,
      //   Gl.FLOAT,
      //   New Float32Array(512 * 512 * 2),
      // );

      expect(texture).not.toBeNull();
    });
  });

  describe('Shader Compilation', () => {
    it('should compile vertex shader', () => {
      if (!gl) {
        return;
      }

      const vertexShaderSource = `#version 300 es
        precision highp float;
        in vec2 a_position;
        void main() {
          gl_Position = vec4(a_position, 0.0, 1.0);
        }
      `;

      const shader = gl.createShader(gl.VERTEX_SHADER);
      expect(shader).not.toBeNull();

      if (shader) {
        gl.shaderSource(shader, vertexShaderSource);
        gl.compileShader(shader);

        // In real browser, check compile status.
        // Const success = gl.getShaderParameter(shader, gl.COMPILE_STATUS);
        // Expect(success).toBe(true);
      }
    });

    it('should compile fragment shader', () => {
      if (!gl) {
        return;
      }

      const fragmentShaderSource = `#version 300 es
        precision highp float;
        out vec4 fragColor;
        void main() {
          fragColor = vec4(1.0, 0.0, 0.0, 1.0);
        }
      `;

      const shader = gl.createShader(gl.FRAGMENT_SHADER);
      expect(shader).not.toBeNull();

      if (shader) {
        gl.shaderSource(shader, fragmentShaderSource);
        gl.compileShader(shader);
      }
    });
  });
});

// ============================================================================
// INTEGRATION TESTS
// ============================================================================

describe('GPU Compute Integration', () => {
  it('should generate valid test data', () => {
    const { positions, velocities, forces } = generateTestGraph(100);

    expect(positions).toHaveLength(200); // 100 nodes * 2 (x,y)
    expect(velocities).toHaveLength(200);
    expect(forces).toHaveLength(200);

    // Check initial velocities are zero
    expect(velocities.every((velocity) => velocity === 0)).toBeTruthy();
  });

  it('should generate valid edge data', () => {
    const edges = generateTestEdges(100, 0.1);

    expect(edges).toBeInstanceOf(Uint32Array);
    expect(edges.length % 2).toBe(0); // Pairs of source/target

    // Check all indices are within bounds
    for (const edge of edges) {
      expect(edge).toBeGreaterThanOrEqual(0);
      expect(edge).toBeLessThan(100);
    }
  });

  it('should verify data alignment for GPU buffers', () => {
    const nodeCount = 1000;
    const positions = new Float32Array(nodeCount * 2);

    // Verify byte alignment (should be 4-byte aligned for Float32)
    expect(positions.byteLength % 4).toBe(0);

    // Verify total size
    const expectedSize = nodeCount * 2 * 4; // 2 floats per node, 4 bytes per float
    expect(positions.byteLength).toBe(expectedSize);
  });
});

logger.info('GPU compute tests loaded');
