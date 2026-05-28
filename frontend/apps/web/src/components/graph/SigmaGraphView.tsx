import type Graph from 'graphology';

import { SigmaContainer, useLoadGraph, useSigma } from '@react-sigma/core';
import { memo, useEffect, useMemo, useRef } from 'react';
import { EdgeArrowProgram, NodeCircleProgram } from 'sigma/rendering';

interface SigmaGraphViewProps {
  graph: Graph;
  onNodeClick?: (nodeId: string) => void;
  onNodeHover?: (nodeId: string | null) => void;
  onNodeDoubleClick?: (nodeId: string) => void;
  className?: string;
}

type SigmaGraphContentProps = {
  graph: Graph;
  onNodeClick: SigmaGraphViewProps['onNodeClick'];
  onNodeHover: SigmaGraphViewProps['onNodeHover'];
  onNodeDoubleClick: SigmaGraphViewProps['onNodeDoubleClick'];
};

function SigmaGraphContent({
  graph,
  onNodeClick,
  onNodeHover,
  onNodeDoubleClick,
}: SigmaGraphContentProps) {
  const loadGraph = useLoadGraph();
  const sigma = useSigma();
  const hoveredNodeRef = useRef<string | null>(null);

  useEffect(() => {
    loadGraph(graph);
  }, [graph, loadGraph]);

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
        onNodeHover?.(event.node);
      }
    };

    const handleLeaveNode = () => {
      hoveredNodeRef.current = null;
      onNodeHover?.(null);
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

export const SigmaGraphView = memo(function SigmaGraphView({
  graph,
  onNodeClick,
  onNodeHover,
  onNodeDoubleClick,
  className = '',
}: SigmaGraphViewProps) {
  const sigmaSettings = useMemo(
    () => ({
      allowInvalidContainer: false,
      defaultEdgeType: 'line',
      defaultNodeType: 'circle',
      nodeProgramClasses: {
        circle: NodeCircleProgram,
      },
      edgeProgramClasses: {
        line: EdgeArrowProgram,
      },
      doubleClickZoomingDuration: 220,
      doubleClickZoomingRatio: 1.9,
      enableCameraPanning: true,
      enableCameraRotation: false,
      enableCameraZooming: true,
      enableEdgeEvents: false,
      hideEdgesOnMove: true,
      hideLabelsOnMove: true,
      labelRenderedSizeThreshold: 0.75,
      maxCameraRatio: 14,
      minCameraRatio: 0.08,
      renderEdgeLabels: false,
      renderLabels: true,
      zoomDuration: 260,
      zoomToSizeRatioFunction: (x: number) => x,
      zoomingRatio: 1.25,
    }),
    [],
  );

  return (
    <SigmaContainer
      className={`sigma-container graph-glass-panel graph-glass-motion ${className}`}
      style={{
        background:
          'radial-gradient(circle at top, rgba(148, 163, 184, 0.12), transparent 42%), linear-gradient(180deg, rgba(15, 23, 42, 0.42), rgba(15, 23, 42, 0.2))',
        height: '100%',
        width: '100%',
      }}
      settings={sigmaSettings}
      graph={graph}
    >
      <SigmaGraphContent
        graph={graph}
        onNodeClick={onNodeClick}
        onNodeHover={onNodeHover}
        onNodeDoubleClick={onNodeDoubleClick}
      />
    </SigmaContainer>
  );
});
