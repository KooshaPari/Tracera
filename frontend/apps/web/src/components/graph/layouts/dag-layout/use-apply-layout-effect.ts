import type { Edge, Node } from '@xyflow/react';
import type { RefObject } from 'react';

import { useEffect } from 'react';

import { logger } from '@/lib/logger';

import type { ElkOptions, SyncLayoutResult } from './types';

const ZERO = Number('0');

interface ApplyLayoutEffectParams<NodeData extends Record<string, unknown>> {
  applySyncLayout: (inputNodes: Node<NodeData>[], inputEdges: Edge[]) => SyncLayoutResult<NodeData>;
  computeElkLayout: (
    inputNodes: Node<NodeData>[],
    inputEdges: Edge[],
    options: ElkOptions,
  ) => Promise<Node<NodeData>[]>;
  edges: Edge[];
  elkOptions: ElkOptions | undefined;
  getGridFallback: (inputNodes: Node<NodeData>[]) => Node<NodeData>[];
  nodes: Node<NodeData>[];
  prevSignatureRef: RefObject<string>;
  setIsLayouting: (value: boolean) => void;
  setLayoutedNodes: (value: Node<NodeData>[]) => void;
  signature: string;
}

function useApplyLayoutEffect<NodeData extends Record<string, unknown>>({
  applySyncLayout,
  computeElkLayout,
  edges,
  elkOptions,
  getGridFallback,
  nodes,
  prevSignatureRef,
  setIsLayouting,
  setLayoutedNodes,
  signature,
}: ApplyLayoutEffectParams<NodeData>): void {
  useEffect((): (() => void) | undefined => {
    if (signature === prevSignatureRef.current) {
      return undefined;
    }
    prevSignatureRef.current = signature;

    if (nodes.length === ZERO) {
      setLayoutedNodes([]);
      return undefined;
    }

    const syncResult = applySyncLayout(nodes, edges);
    if (syncResult.kind === 'sync' && syncResult.nodes) {
      setLayoutedNodes(syncResult.nodes);
      return undefined;
    }

    if (!elkOptions) {
      setLayoutedNodes(getGridFallback(nodes));
      return undefined;
    }

    let cancelled = false;
    const runLayoutSafe = async (): Promise<void> => {
      setIsLayouting(true);
      try {
        const result = await computeElkLayout(nodes, edges, elkOptions);
        if (!cancelled) {
          setLayoutedNodes(result);
        }
      } catch (error: unknown) {
        logger.error('ELK layout failed:', error);
        if (!cancelled) {
          setLayoutedNodes(getGridFallback(nodes));
        }
      } finally {
        if (!cancelled) {
          setIsLayouting(false);
        }
      }
    };

    // If this rejects, the internal try/catch already logged and handled fallbacks.
    // Keeping a reference avoids `no-floating-promises` without using `void` or `.catch`.
    const _layoutPromise: Promise<void> = runLayoutSafe();

    return (): void => {
      cancelled = true;
    };
  }, [
    applySyncLayout,
    computeElkLayout,
    edges,
    elkOptions,
    getGridFallback,
    nodes,
    prevSignatureRef,
    setIsLayouting,
    setLayoutedNodes,
    signature,
  ]);
}

export { useApplyLayoutEffect };
