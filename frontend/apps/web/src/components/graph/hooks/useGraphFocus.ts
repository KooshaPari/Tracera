import { useCallback } from "react";
import { useReactFlow } from "@xyflow/react";
import type { Node } from "@xyflow/react";

/** How long the viewport animates when centring on a node. */
const FOCUS_DURATION_MS = 200;

export interface GraphFocusControls {
  /** Fit the entire graph into the viewport. */
  fitAll: () => void;
  /**
   * Centre the viewport on a single node.
   *
   * Calls `onSelect` first (so the node is marked selected even when the id
   * does not resolve to a laid-out node), then focuses it if it exists.
   */
  focusNode: (nodeId: string) => void;
}

/**
 * Shared fit / centre-on-node controls for the graph views.
 *
 * Extracted because ClusteredGraphView and FlowGraphView had grown identical
 * `handleFit` / `handleFocusNode` bodies. SonarCloud measured the duplication
 * at `new_duplicated_lines_density=4.5` (gate threshold 3) on PR #1289, which
 * is what prompted this.
 *
 * Both callers previously carried a bare `undefined;` where the focus logic
 * belonged, so "focus node" silently did nothing.
 */
export function useGraphFocus(
  nodes: readonly Node[],
  onSelect?: ((nodeId: string) => void) | undefined,
): GraphFocusControls {
  const { fitView } = useReactFlow();

  const fitAll = useCallback(() => {
    void fitView();
  }, [fitView]);

  const focusNode = useCallback(
    (nodeId: string) => {
      onSelect?.(nodeId);

      const node = nodes.find((candidate) => candidate.id === nodeId);
      if (!node) {
        return;
      }

      void fitView({ nodes: [node], duration: FOCUS_DURATION_MS });
    },
    [fitView, nodes, onSelect],
  );

  return { fitAll, focusNode };
}
