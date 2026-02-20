/**
 * Enhanced Hybrid Graph View with Smooth Transitions
 *
 * Automatically switches between ReactFlow and Sigma.js based on node count:
 * - ReactFlow: < 10k nodes (rich interactivity)
 * - Sigma.js: >= 10k nodes (WebGL performance)
 *
 * Features:
 * - Smooth fade transitions between renderers
 * - Preserve camera position across transitions
 * - Maintain all interactivity (zoom, pan, select, hover)
 * - Performance monitoring and adaptive mode switching
 * - Rich node detail panel for WebGL mode
 */

import type { Edge, Node } from '@xyflow/react';

import { AnimatePresence, motion } from 'framer-motion';
import { Activity, AlertTriangle, Layers, Zap } from 'lucide-react';
import { memo, useCallback, useEffect, useMemo, useState } from 'react';

import type { HybridGraphConfig } from '@/hooks/useHybridGraph';
import type { Item, Link } from '@tracertm/types';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useHybridGraph } from '@/hooks/useHybridGraph';

import { FlowGraphViewInner } from './FlowGraphViewInner';
import { RichNodeDetailPanel } from './sigma/RichNodeDetailPanel';
import { SigmaGraphViewEnhanced } from './SigmaGraphView.enhanced';

interface HybridGraphViewProps {
  nodes: Node[];
  edges: Edge[];
  onNodeClick?: ((nodeId: string) => void) | undefined;
  onNodeExpand?: ((nodeId: string) => void) | undefined;
  onNodeNavigate?: ((nodeId: string) => void) | undefined;
  config?: HybridGraphConfig | undefined;
  className?: string | undefined;
}

interface PerformanceWarning {
  type: 'threshold' | 'fps' | 'memory';
  message: string;
  severity: 'info' | 'warning' | 'error';
}

export const HybridGraphViewEnhanced = memo(function HybridGraphViewEnhanced({
  nodes,
  edges,
  onNodeClick,
  onNodeExpand,
  onNodeNavigate,
  config,
  className = '',
}: HybridGraphViewProps) {
  const { useWebGL, nodeCount, edgeCount, graphologyGraph, selectedNodeId, setSelectedNodeId } =
    useHybridGraph(nodes, edges, config);

  const [detailPanelNode, setDetailPanelNode] = useState<any>(null);
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);

  // Derive items/links from nodes/edges for FlowGraphViewInner (same as HybridGraphView)
  const reactFlowItems = useMemo((): Item[] => {
    const timestamp = new Date().toISOString();
    return nodes
      .map((node) => {
        const data = node.data as Record<string, unknown> | undefined;
        const item = data?.['item'];
        if (item) {
          return item as Item;
        }
        return {
          createdAt: timestamp,
          id: node.id,
          priority: 'medium',
          projectId: 'unknown',
          status: 'todo',
          title: node.id,
          type: node.type ?? 'node',
          updatedAt: timestamp,
          version: 1,
          view: 'FEATURE',
        } satisfies Item;
      })
      .filter((item): item is Item => Boolean(item));
  }, [nodes]);
  const reactFlowLinks = useMemo(
    (): Link[] =>
      edges
        .map((edge) => {
          const { data } = edge;
          const link = data?.['link'];
          return link as Link | undefined;
        })
        .filter((link): link is Link => Boolean(link)),
    [edges],
  );
  const [showTransition, setShowTransition] = useState(false);
  const [previousMode, setPreviousMode] = useState<'reactflow' | 'webgl'>(
    useWebGL ? 'webgl' : 'reactflow',
  );
  const [performanceWarnings, setPerformanceWarnings] = useState<PerformanceWarning[]>([]);

  // Detect mode transitions
  useEffect(() => {
    const currentMode = useWebGL ? 'webgl' : 'reactflow';

    if (currentMode !== previousMode) {
      setShowTransition(true);

      // Hide transition message after animation
      const timer = setTimeout(() => {
        setShowTransition(false);
      }, 1500);

      setPreviousMode(currentMode);

      return () => {
        clearTimeout(timer);
      };
    }
    return;
  }, [useWebGL, previousMode]);

  // Performance warnings
  useEffect(() => {
    const warnings: PerformanceWarning[] = [];

    // Near threshold warning
    if (!useWebGL && nodeCount > 8000) {
      warnings.push({
        message: `Approaching 10k node threshold (${nodeCount.toLocaleString()} nodes). WebGL mode will activate automatically.`,
        severity: 'info',
        type: 'threshold',
      });
    }

    // Very large graph warning
    if (useWebGL && nodeCount > 50_000) {
      warnings.push({
        message: `Large graph detected (${nodeCount.toLocaleString()} nodes). Performance mode enabled.`,
        severity: 'warning',
        type: 'memory',
      });
    }

    setPerformanceWarnings(warnings);
  }, [useWebGL, nodeCount]);

  // Handle node click
  const handleNodeClick = useCallback(
    (nodeId: string) => {
      setSelectedNodeId(nodeId);

      // In WebGL mode, open detail panel
      if (useWebGL) {
        const node = nodes.find((n) => n['id'] === nodeId);
        if (node) {
          setDetailPanelNode({
            data: node.data || {},
            id: node['id'],
            label: node.data?.['label'] ?? node['id'],
            type: node['type'] ?? 'default',
          });
        }
      }

      // Call parent handler
      onNodeClick?.(nodeId);
    },
    [useWebGL, nodes, setSelectedNodeId, onNodeClick],
  );

  // Handle node hover
  const handleNodeHover = useCallback((nodeId: string | null) => {
    setHoveredNodeId(nodeId);
  }, []);

  // Handle node double-click (expand)
  const handleNodeDoubleClick = useCallback(
    (nodeId: string) => {
      onNodeExpand?.(nodeId);
    },
    [onNodeExpand],
  );

  // Handle background click (deselect)
  const handleBackgroundClick = useCallback(() => {
    setSelectedNodeId(null);
    setDetailPanelNode(null);
  }, [setSelectedNodeId]);

  // Determine performance mode for Sigma
  const sigmaPerformanceMode = useMemo(() => {
    if (nodeCount > 50_000) {
      return 'performance';
    }
    if (nodeCount < 1000) {
      return 'quality';
    }
    return 'balanced';
  }, [nodeCount]);

  return (
    <div className={`relative h-full w-full ${className}`}>
      {/* Performance indicators */}
      <div className='absolute top-4 right-4 z-10 flex flex-col items-end gap-2'>
        {/* Mode indicator */}
        <Badge
          variant={useWebGL ? 'default' : 'secondary'}
          className='text-xs font-medium shadow-md'
        >
          {useWebGL ? (
            <>
              <Zap className='mr-1 h-3 w-3' />
              WebGL Mode
            </>
          ) : (
            <>
              <Layers className='mr-1 h-3 w-3' />
              ReactFlow Mode
            </>
          )}
        </Badge>

        {/* Node/Edge count */}
        <Badge variant='outline' className='text-xs shadow-md'>
          <Activity className='mr-1 h-3 w-3' />
          {nodeCount.toLocaleString()}N / {edgeCount.toLocaleString()}E
        </Badge>

        {/* Performance mode (WebGL only) */}
        {useWebGL && (
          <Badge
            variant='outline'
            className={`text-xs shadow-md ${
              sigmaPerformanceMode === 'performance' ? 'border-orange-500 text-orange-500' : ''
            }`}
          >
            {sigmaPerformanceMode.charAt(0).toUpperCase() + sigmaPerformanceMode.slice(1)}
          </Badge>
        )}
      </div>

      {/* Performance warnings */}
      {performanceWarnings.length > 0 && (
        <div className='absolute bottom-4 left-4 z-10 flex max-w-md flex-col gap-2'>
          {performanceWarnings.map((warning, i) => (
            <Badge
              key={i}
              variant={warning.severity === 'error' ? 'destructive' : 'default'}
              className='text-xs shadow-md'
            >
              <AlertTriangle className='mr-1 h-3 w-3' />
              {warning.message}
            </Badge>
          ))}
        </div>
      )}

      {/* Transition notification */}
      <AnimatePresence>
        {showTransition && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className='absolute top-20 left-1/2 z-20 -translate-x-1/2 transform'
          >
            <Badge variant='default' className='px-4 py-2 text-sm font-medium shadow-lg'>
              {useWebGL ? (
                <>
                  <Zap className='mr-2 h-4 w-4' />
                  Switching to WebGL for better performance...
                </>
              ) : (
                <>
                  <Layers className='mr-2 h-4 w-4' />
                  Switching to ReactFlow for richer interactivity...
                </>
              )}
            </Badge>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Graph renderer with smooth transitions */}
      <AnimatePresence mode='wait'>
        {useWebGL && graphologyGraph ? (
          // WebGL mode (>= 10k nodes)
          <motion.div
            key='webgl'
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className='h-full w-full'
          >
            <SigmaGraphViewEnhanced
              graph={graphologyGraph}
              onNodeClick={handleNodeClick}
              onNodeHover={handleNodeHover}
              onNodeDoubleClick={handleNodeDoubleClick}
              onBackgroundClick={handleBackgroundClick}
              selectedNodeId={selectedNodeId}
              hoveredNodeId={hoveredNodeId}
              performanceMode={sigmaPerformanceMode}
              className='h-full w-full'
            />
          </motion.div>
        ) : (
          // ReactFlow mode (< 10k nodes)
          <motion.div
            key='reactflow'
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className='h-full w-full'
          >
            <FlowGraphViewInner
              items={reactFlowItems}
              links={reactFlowLinks}
              onNavigateToItem={handleNodeClick}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Rich node detail panel (WebGL mode only) */}
      <AnimatePresence>
        {useWebGL && detailPanelNode && (
          <motion.div
            initial={{ opacity: 0, x: 400 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 400 }}
            transition={{ damping: 25, stiffness: 300, type: 'spring' }}
          >
            <RichNodeDetailPanel
              node={detailPanelNode}
              onClose={() => {
                setDetailPanelNode(null);
              }}
              onExpand={onNodeExpand}
              onNavigate={onNodeNavigate}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
});
