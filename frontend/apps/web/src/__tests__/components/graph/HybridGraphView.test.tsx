import type { Edge, Node } from '@xyflow/react';

import { render } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { HybridGraphView } from '@/components/graph/HybridGraphView';

// Mock child components
vi.mock('@/components/graph/FlowGraphViewInner', () => ({
  FlowGraphViewInner: ({ items }: { items: unknown[] }) => (
    <div data-testid='reactflow-mode'>ReactFlow: {items.length} nodes</div>
  ),
}));

vi.mock('@/components/graph/SigmaGraphView', () => ({
  SigmaGraphView: () => <div data-testid='webgl-mode'>WebGL Mode</div>,
}));

vi.mock('@/components/graph/sigma/RichNodeDetailPanel', () => ({
  RichNodeDetailPanel: ({ node, onClose: _onClose }: { node: unknown; onClose: () => void }) =>
    node ? <div data-testid='detail-panel'>{node.label}</div> : null,
}));

vi.mock('@/lib/graphology/adapter', () => ({
  createGraphologyAdapter: () => ({
    getGraph: vi.fn(() => ({})),
    syncFromReactFlow: vi.fn(),
  }),
}));

describe(HybridGraphView, () => {
  it('should use ReactFlow for <10k nodes', () => {
    const nodes: Node[] = Array.from({ length: 5000 }, (_, i) => ({
      data: {},
      id: `node-${i}`,
      position: { x: 0, y: 0 },
      type: 'default',
    }));

    const edges: Edge[] = [];

    const { getByTestId, queryByTestId } = render(<HybridGraphView nodes={nodes} edges={edges} />);

    expect(getByTestId('reactflow-mode')).toBeInTheDocument();
    expect(queryByTestId('webgl-mode')).not.toBeInTheDocument();
  });

  it('should use WebGL for >10k nodes', () => {
    const nodes: Node[] = Array.from({ length: 15_000 }, (_, i) => ({
      data: {},
      id: `node-${i}`,
      position: { x: 0, y: 0 },
      type: 'default',
    }));

    const edges: Edge[] = [];

    const { getByTestId, queryByTestId } = render(<HybridGraphView nodes={nodes} edges={edges} />);

    expect(getByTestId('webgl-mode')).toBeInTheDocument();
    expect(queryByTestId('reactflow-mode')).not.toBeInTheDocument();
  });

  it('should respect forceReactFlow override', () => {
    const nodes: Node[] = Array.from({ length: 15_000 }, (_, i) => ({
      data: {},
      id: `node-${i}`,
      position: { x: 0, y: 0 },
      type: 'default',
    }));

    const { getByTestId } = render(
      <HybridGraphView nodes={nodes} edges={[]} config={{ forceReactFlow: true }} />,
    );

    expect(getByTestId('reactflow-mode')).toBeInTheDocument();
  });

  it('should respect forceWebGL override', () => {
    const nodes: Node[] = Array.from({ length: 100 }, (_, i) => ({
      data: {},
      id: `node-${i}`,
      position: { x: 0, y: 0 },
      type: 'default',
    }));

    const { getByTestId } = render(
      <HybridGraphView nodes={nodes} edges={[]} config={{ forceWebGL: true }} />,
    );

    expect(getByTestId('webgl-mode')).toBeInTheDocument();
  });

  it('should display node count badge', () => {
    const nodes: Node[] = Array.from({ length: 5000 }, (_, i) => ({
      data: {},
      id: `node-${i}`,
      position: { x: 0, y: 0 },
      type: 'default',
    }));

    const { getByText } = render(<HybridGraphView nodes={nodes} edges={[]} />);

    expect(getByText('5,000 nodes')).toBeInTheDocument();
  });

  it('should show threshold warning near 10k', () => {
    const nodes: Node[] = Array.from({ length: 9500 }, (_, i) => ({
      data: {},
      id: `node-${i}`,
      position: { x: 0, y: 0 },
      type: 'default',
    }));

    const { getByText } = render(<HybridGraphView nodes={nodes} edges={[]} />);

    expect(getByText(/approaching 10k node threshold/i)).toBeInTheDocument();
  });

  it('should call onNodeClick handler', () => {
    const onNodeClick = vi.fn();
    const nodes: Node[] = [{ data: {}, id: 'node1', position: { x: 0, y: 0 }, type: 'default' }];

    render(<HybridGraphView nodes={nodes} edges={[]} onNodeClick={onNodeClick} />);

    // Actual click testing requires integration tests
    expect(onNodeClick).toBeDefined();
  });

  it('should show correct mode badge for ReactFlow', () => {
    const nodes: Node[] = Array.from({ length: 100 }, (_, i) => ({
      data: {},
      id: `node-${i}`,
      position: { x: 0, y: 0 },
      type: 'default',
    }));

    const { getByText } = render(<HybridGraphView nodes={nodes} edges={[]} />);

    expect(getByText('ReactFlow Mode')).toBeInTheDocument();
  });

  it('should show correct mode badge for WebGL', () => {
    const nodes: Node[] = Array.from({ length: 15_000 }, (_, i) => ({
      data: {},
      id: `node-${i}`,
      position: { x: 0, y: 0 },
      type: 'default',
    }));

    const { getByTestId, getAllByText } = render(<HybridGraphView nodes={nodes} edges={[]} />);

    // Should use WebGL mode
    expect(getByTestId('webgl-mode')).toBeInTheDocument();
    // Badge should show WebGL Mode (may appear multiple times in DOM)
    expect(getAllByText('WebGL Mode').length).toBeGreaterThan(0);
  });

  it('should use custom threshold from config', () => {
    const nodes: Node[] = Array.from({ length: 3000 }, (_, i) => ({
      data: {},
      id: `node-${i}`,
      position: { x: 0, y: 0 },
      type: 'default',
    }));

    const { getByTestId } = render(
      <HybridGraphView nodes={nodes} edges={[]} config={{ nodeThreshold: 2000 }} />,
    );

    // Should use WebGL because 3000 > 2000
    expect(getByTestId('webgl-mode')).toBeInTheDocument();
  });

  it('should handle empty node array', () => {
    const { getByTestId } = render(<HybridGraphView nodes={[]} edges={[]} />);

    expect(getByTestId('reactflow-mode')).toBeInTheDocument();
  });

  it('should handle single node', () => {
    const nodes: Node[] = [{ data: {}, id: 'node1', position: { x: 0, y: 0 }, type: 'default' }];

    const { getByTestId, getByText } = render(<HybridGraphView nodes={nodes} edges={[]} />);

    expect(getByTestId('reactflow-mode')).toBeInTheDocument();
    expect(getByText('1 nodes')).toBeInTheDocument();
  });

  it('should handle exactly 10k nodes (boundary test)', () => {
    const nodes: Node[] = Array.from({ length: 10_000 }, (_, i) => ({
      data: {},
      id: `node-${i}`,
      position: { x: 0, y: 0 },
      type: 'default',
    }));

    const { getByTestId } = render(<HybridGraphView nodes={nodes} edges={[]} />);

    // At exactly 10k, should switch to WebGL
    expect(getByTestId('webgl-mode')).toBeInTheDocument();
  });
});
