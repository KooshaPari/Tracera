import type Graph from 'graphology';

import { SigmaContainer, useLoadGraph, useSigma } from '@react-sigma/core';
import { memo, useEffect, useRef } from 'react';

interface SigmaGraphViewProps {
  graph: Graph;
  onNodeClick?: (nodeId: string) => void;
  onNodeHover?: (nodeId: string | null) => void;
  onNodeDoubleClick?: (nodeId: string) => void;
  className?: string;
}

function SigmaGraphContent({
  graph,
  onNodeClick,
  onNodeHover,
  onNodeDoubleClick,
}: SigmaGraphViewProps) {
  const loadGraph = useLoadGraph();
  const sigma = useSigma();
  const hoveredNodeRef = useRef<string | null>(null);

  // Load graph data
  useEffect(() => {
    loadGraph(graph);
  }, [graph, loadGraph]);

  // Event handlers
  useEffect(() => {
    if (!sigma) {
      return;
    }

    const handleClick = (event: { node?: string }) => {
      if (event.node && onNodeClick) {
        onNodeClick(event.node);
      }
    };

    const handleDoubleClick = (event: { node?: string }) => {
      if (event.node && onNodeDoubleClick) {
        onNodeDoubleClick(event.node);
      }
    };

    const handleEnterNode = (event: { node?: string }) => {
      if (event.node) {
        hoveredNodeRef.current = event.node;
        if (onNodeHover) {
          onNodeHover(event.node);
        }
      }
    };

    const handleLeaveNode = () => {
      hoveredNodeRef.current = null;
      if (onNodeHover) {
        onNodeHover(null);
      }
    };

    sigma.on('clickNode', handleClick);
    sigma.on('doubleClickNode', handleDoubleClick);
    sigma.on('enterNode', handleEnterNode);
    sigma.on('leaveNode', handleLeaveNode);

    return () => {
      sigma.off('clickNode', handleClick);
      sigma.off('doubleClickNode', handleDoubleClick);
      sigma.off('enterNode', handleEnterNode);
      sigma.off('leaveNode', handleLeaveNode);
    };
  }, [sigma, onNodeClick, onNodeHover, onNodeDoubleClick]);

  return null;
}

export const SigmaGraphView = memo(function SigmaGraphView(props: SigmaGraphViewProps) {
  const { className = '', ...contentProps } = props;

  return (
    <SigmaContainer
      className={`sigma-container ${className}`}
      style={{ height: '100%', width: '100%' }}
      settings={{
        // Performance optimizations
        renderEdgeLabels: false, // Labels only on zoom
        enableEdgeEvents: false,

        // Rendering settings
        defaultNodeType: 'custom',
        defaultEdgeType: 'custom',

        // Camera settings
        minCameraRatio: 0.1,
        maxCameraRatio: 10,

        // Performance
        hideEdgesOnMove: true, // Hide edges during pan/zoom
        hideLabelsOnMove: true,

        // Renderer
        renderLabels: true,
        labelRenderedSizeThreshold: 0.5, // Only show labels when zoomed in
      }}
    >
      <SigmaGraphContent {...contentProps} />
    </SigmaContainer>
  );
});
