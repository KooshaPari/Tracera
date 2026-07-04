import type { Core } from 'cytoscape';
import type { RefObject } from 'react';

import cytoscape from 'cytoscape';
import { useCallback, useEffect, useRef } from 'react';

import type { EnhancedNodeData, GraphPerspective } from '@/components/graph/types';
import type { LayoutType, Link } from '@tracertm/types';

import { PERSPECTIVE_CONFIGS } from '@/components/graph/types';

import { createEnhancedCytoscapeStyle } from './cytoscapeStyle';

interface UseCytoscapeEnhancedGraphArgs {
  filteredLinks: Link[];
  filteredNodes: EnhancedNodeData[];
  layout: LayoutType;
  onClearSelection: () => void;
  onSelectNodeId: (nodeId: string) => void;
  onShowDetailPanel: (show: boolean) => void;
  perspective: GraphPerspective;
}

interface CytoscapeEnhancedGraphControls {
  clearHighlights: () => void;
  containerRef: RefObject<HTMLDivElement | null>;
  cyRef: RefObject<Core | null>;
  exportPng: () => void;
  fit: () => void;
  focusNode: (nodeId: string) => void;
  zoomIn: () => void;
  zoomOut: () => void;
}

export function useCytoscapeEnhancedGraph({
  filteredNodes,
  filteredLinks,
  layout,
  perspective,
  onSelectNodeId,
  onShowDetailPanel,
  onClearSelection,
}: UseCytoscapeEnhancedGraphArgs): CytoscapeEnhancedGraphControls {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  const clearHighlights = useCallback((): void => {
    cyRef.current?.elements().removeClass('faded highlighted');
  }, []);

  const initCytoscape = useCallback((): void => {
    if (!containerRef.current || filteredNodes.length === 0) {
      return;
    }

    // Destroy existing instance
    if (cyRef.current) {
      cyRef.current.destroy();
    }

    // Convert to Cytoscape format
    const cytoscapeNodes = filteredNodes.map((node) => ({
      data: {
        connectionCount: node.connections.total,
        id: node.id,
        label: node.label,
        status: node.status,
        type: node.type,
      },
    }));

    const cytoscapeEdges = filteredLinks.map((link) => ({
      data: {
        id: link.id,
        label: link.type.replaceAll('_', ' '),
        source: link.sourceId,
        target: link.targetId,
        type: link.type,
      },
    }));

    // Get perspective color for active perspective
    const perspectiveConfig = PERSPECTIVE_CONFIGS.find((c) => c.id === perspective);

    cyRef.current = cytoscape({
      container: containerRef.current,
      elements: [...cytoscapeNodes, ...cytoscapeEdges],
      layout: {
        name: layout === 'elk' ? 'breadthfirst' : layout,
        animate: true,
        animationDuration: 500,
        ...(layout === 'breadthfirst' || layout === 'elk'
          ? {
              directed: true,
              padding: 50,
              spacingFactor: 1.5,
            }
          : {}),
        ...(layout === 'cose'
          ? {
              edgeElasticity: (): number => 100,
              gravity: 0.25,
              idealEdgeLength: (): number => 100,
              nodeRepulsion: (): number => 8000,
            }
          : {}),
      },
      maxZoom: 4,
      minZoom: 0.1,
      style: createEnhancedCytoscapeStyle(perspectiveConfig?.color),
      wheelSensitivity: 0.3,
    });

    // Event handlers
    cyRef.current.on('tap', 'node', (evt) => {
      const nodeId = String(evt.target.id());
      onSelectNodeId(nodeId);
      onShowDetailPanel(true);

      // Highlight connected nodes and edges
      const node = evt.target;
      const neighborhood = node.closedNeighborhood();

      const cy = cyRef.current;
      if (!cy) {
        return;
      }

      cy.elements().addClass('faded');
      neighborhood.removeClass('faded');
      neighborhood.addClass('highlighted');
    });

    cyRef.current.on('tap', (evt) => {
      if (evt.target === cyRef.current) {
        onClearSelection();
        clearHighlights();
      }
    });

    // Fit to viewport
    cyRef.current.fit(undefined, 50);
  }, [
    clearHighlights,
    filteredLinks,
    filteredNodes,
    layout,
    onClearSelection,
    onSelectNodeId,
    onShowDetailPanel,
    perspective,
  ]);

  useEffect((): (() => void) => {
    initCytoscape();
    return (): void => {
      cyRef.current?.destroy();
    };
  }, [initCytoscape]);

  const zoomIn = useCallback((): void => {
    const cy = cyRef.current;
    if (!cy) {
      return;
    }
    cy.zoom(cy.zoom() * 1.3);
  }, []);

  const zoomOut = useCallback((): void => {
    const cy = cyRef.current;
    if (!cy) {
      return;
    }
    cy.zoom(cy.zoom() / 1.3);
  }, []);

  const fit = useCallback((): void => {
    const cy = cyRef.current;
    if (!cy) {
      return;
    }
    cy.fit(undefined, 50);
    cy.elements().removeClass('faded highlighted');
  }, []);

  const focusNode = useCallback(
    (nodeId: string) => {
      const cy = cyRef.current;
      if (!cy) {
        return;
      }
      const node = cy.$id(nodeId);
      if (node.length === 0) {
        return;
      }

      onSelectNodeId(nodeId);

      // Center on node
      cy.animate({
        center: { eles: node },
        duration: 300,
        zoom: 1.5,
      });

      // Highlight
      cy.elements().addClass('faded');
      const neighborhood = node.closedNeighborhood();
      neighborhood.removeClass('faded');
      neighborhood.addClass('highlighted');
    },
    [onSelectNodeId],
  );

  const exportPng = useCallback((): void => {
    const cy = cyRef.current;
    if (!cy) {
      return;
    }
    const png = cy.png({ bg: '#1a1a2e', full: true, scale: 2 });
    const link = document.createElement('a');
    link.download = `graph-${perspective}-${new Date().toISOString()}.png`;
    link.href = png;
    link.click();
  }, [perspective]);

  return {
    clearHighlights,
    containerRef,
    cyRef,
    exportPng,
    fit,
    focusNode,
    zoomIn,
    zoomOut,
  };
}
