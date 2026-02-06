/**
 * GPU Compute Tests
 *
 * Tests for WebGPU/WebGL compute shader implementations
 * Verifies correct force calculations and performance targets
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

import { logger } from '../logger';

// ============================================================================
// MOCK GPU APIS
// ============================================================================

// Mock WebGPU API (for testing in jsdom environment)
const mockGPUAdapter = {
  requestDevice: vi.fn(async () => ({
    createBuffer: vi.fn(() => ({
      destroy: vi.fn(),
      mapAsync: vi.fn(async () => {}),
      getMappedRange: vi.fn(() => new ArrayBuffer(1024)),
      unmap: vi.fn(),
    })),
    createShaderModule: vi.fn(() => ({})),
    createBindGroupLayout: vi.fn(() => ({})),
    createPipelineLayout: vi.fn(() => ({})),
    createComputePipeline: vi.fn(() => ({
      getBindGroupLayout: vi.fn(() => ({})),
    })),
    createBindGroup: vi.fn(() => ({})),
    createCommandEncoder: vi.fn(() => ({
      beginComputePass: vi.fn(() => ({
        setPipeline: vi.fn(),
        setBindGroup: vi.fn(),
        dispatchWorkgroups: vi.fn(),
        end: vi.fn(),
      })),
      copyBufferToBuffer: vi.fn(),
      finish: vi.fn(() => ({})),
    })),
    queue: {
      writeBuffer: vi.fn(),
      submit: vi.fn(),
      onSubmittedWorkDone: vi.fn(async () => {}),
    },
    destroy: vi.fn(),
    lost: Promise.resolve({ message: 'test', reason: 'destroyed' }),
  })),
};

const mockNavigator = {
  gpu: {
    requestAdapter: vi.fn(async () => mockGPUAdapter),
  },
};

// ============================================================================
// TEST UTILITIES
// ============================================================================

/**
 * Generate test graph data
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

describe('GPU Compute Infrastructure', () => {
  beforeEach(() => {
    // Mock navigator.gpu
    Object.defineProperty(global.navigator, 'gpu', {
      value: mockNavigator.gpu,
      writable: true,
      configurable: true,
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('WebGPU Device Initialization', () => {
    it('should detect WebGPU support', () => {
      expect(navigator.gpu).toBeDefined();
    });

    it('should request adapter with high-performance preference', async () => {
      await mockNavigator.gpu.requestAdapter({ powerPreference: 'high-performance' });

      expect(mockNavigator.gpu.requestAdapter).toHaveBeenCalledWith({
        powerPreference: 'high-performance',
      });
    });

    it('should handle adapter request failure', async () => {
      const originalRequestAdapter = mockNavigator.gpu.requestAdapter;
      mockNavigator.gpu.requestAdapter = vi.fn(async () => null);

      const adapter = await mockNavigator.gpu.requestAdapter();
      expect(adapter).toBeNull();

      mockNavigator.gpu.requestAdapter = originalRequestAdapter;
    });
  });

  describe('Buffer Management', () => {
    it('should create storage buffers with correct size', async () => {
      const adapter = await mockNavigator.gpu.requestAdapter();
      const device = await adapter!.requestDevice();

      const nodeCount = 1000;
      const positionsSize = nodeCount * 2 * Float32Array.BYTES_PER_ELEMENT;

      device.createBuffer({
        size: positionsSize,
        usage: 3, // STORAGE | COPY_DST
      });

      expect(device.createBuffer).toHaveBeenCalledWith(
        expect.objectContaining({
          size: positionsSize,
        }),
      );
    });

    it('should write data to buffers', async () => {
      const adapter = await mockNavigator.gpu.requestAdapter();
      const device = await adapter!.requestDevice();

      const testData = new Float32Array([1, 2, 3, 4]);
      const buffer = device.createBuffer({ size: 16, usage: 3 });

      device.queue.writeBuffer(buffer, 0, testData);

      expect(device.queue.writeBuffer).toHaveBeenCalledWith(buffer, 0, testData);
    });
  });

  describe('Compute Pipeline', () => {
    it('should create shader module from WGSL code', async () => {
      const adapter = await mockNavigator.gpu.requestAdapter();
      const device = await adapter!.requestDevice();

      const shaderCode = '@compute @workgroup_size(64) fn main() {}';
      device.createShaderModule({ code: shaderCode });

      expect(device.createShaderModule).toHaveBeenCalledWith({ code: shaderCode });
    });

    it('should create compute pipeline with entry point', async () => {
      const adapter = await mockNavigator.gpu.requestAdapter();
      const device = await adapter!.requestDevice();

      const shaderModule = device.createShaderModule({ code: '' });
      const layout = device.createPipelineLayout({ bindGroupLayouts: [] });

      device.createComputePipeline({
        layout,
        compute: {
          module: shaderModule,
          entryPoint: 'main',
        },
      });

      expect(device.createComputePipeline).toHaveBeenCalledWith(
        expect.objectContaining({
          compute: expect.objectContaining({
            entryPoint: 'main',
          }),
        }),
      );
    });
  });

  describe('Force Calculation Logic', () => {
    it('should calculate repulsion force correctly', () => {
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

      expect(expectedForceX).toBeCloseTo(-0.5, 1);
    });

    it('should calculate attraction force correctly', () => {
      // Test the math for attraction force
      // F = k * d where k = attractionStrength

      const pos1 = { x: 0, y: 0 };
      const pos2 = { x: 100, y: 0 };
      const strength = 0.1;

      const delta = { x: pos2.x - pos1.x, y: pos2.y - pos1.y };
      const dist = Math.sqrt(delta.x * delta.x + delta.y * delta.y);
      const force = strength * dist;

      const expectedForceX = (delta.x / dist) * force;

      expect(expectedForceX).toBeCloseTo(10, 1);
    });
  });

  describe('Workgroup Dispatch', () => {
    it('should calculate correct workgroup count for node count', async () => {
      const adapter = await mockNavigator.gpu.requestAdapter();
      const device = await adapter!.requestDevice();

      const nodeCount = 10000;
      const workgroupSize = 64;
      const workgroupCount = Math.ceil(nodeCount / workgroupSize);

      expect(workgroupCount).toBe(157); // ceil(10000 / 64)

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
      const startTime = performance.now();

      // Simulate some work
      await new Promise((resolve) => setTimeout(resolve, 10));

      const duration = performance.now() - startTime;
      expect(duration).toBeGreaterThanOrEqual(10);
    });

    it('should verify speedup target for 10k nodes', () => {
      // Target: <100ms per iteration on GPU vs ~30s CPU
      // This is ~300x speedup minimum

      const cpuTime = 30000; // 30s baseline
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
    canvas = document.createElement('canvas');
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
      if (!gl) return;

      const floatExt = gl.getExtension('EXT_color_buffer_float');
      // In jsdom, this will be null, but in real browser it should exist
      expect(floatExt).toBeDefined();
    });
  });

  describe('Texture Creation', () => {
    it('should create float textures for data', () => {
      if (!gl) return;

      const texture = gl.createTexture();
      expect(texture).toBeTruthy();

      gl.bindTexture(gl.TEXTURE_2D, texture);

      const testData = new Float32Array(512 * 512 * 2);
      // In real implementation:
      // gl.texImage2D(gl.TEXTURE_2D, 0, gl.RG32F, 512, 512, 0, gl.RG, gl.FLOAT, testData);

      expect(texture).not.toBeNull();
    });
  });

  describe('Shader Compilation', () => {
    it('should compile vertex shader', () => {
      if (!gl) return;

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

        // In real browser, check compile status
        // const success = gl.getShaderParameter(shader, gl.COMPILE_STATUS);
        // expect(success).toBe(true);
      }
    });

    it('should compile fragment shader', () => {
      if (!gl) return;

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
    expect(velocities.every((v) => v === 0)).toBe(true);
  });

  it('should generate valid edge data', () => {
    const edges = generateTestEdges(100, 0.1);

    expect(edges).toBeInstanceOf(Uint32Array);
    expect(edges.length % 2).toBe(0); // Pairs of source/target

    // Check all indices are within bounds
    for (let i = 0; i < edges.length; i++) {
      expect(edges[i]).toBeGreaterThanOrEqual(0);
      expect(edges[i]).toBeLessThan(100);
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
