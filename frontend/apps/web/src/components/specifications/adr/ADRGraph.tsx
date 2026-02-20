/**
 * ADRGraph - Relationship visualization for Architecture Decision Records
 * Shows supersession chains, dependencies, and related ADRs using a graph layout
 */

import { ChevronDown, ChevronUp, Download, GitBranch, ZoomIn, ZoomOut } from 'lucide-react';
import { useCallback, useMemo, useState } from 'react';

import type { ADR, ADRStatus } from '@tracertm/types';

import { Badge, Button, Card, CardContent, CardHeader, CardTitle } from '@tracertm/ui';

interface ADRGraphProps {
  adrs: ADR[];
  selectedAdrId?: string;
  onAdrSelect?: (adr: ADR) => void;
  className?: string;
}

interface GraphNode {
  adr: ADR;
  x: number;
  y: number;
  level: number;
  connectedIds: Set<string>;
}

interface GraphEdge {
  source: string;
  target: string;
  type: 'supersedes' | 'related' | 'depends';
}

const STATUS_COLORS: Record<ADRStatus, string> = {
  accepted: 'bg-green-500/20 border-green-500/50 text-green-700',
  deprecated: 'bg-orange-500/20 border-orange-500/50 text-orange-700',
  proposed: 'bg-yellow-500/20 border-yellow-500/50 text-yellow-700',
  rejected: 'bg-red-500/20 border-red-500/50 text-red-700',
  superseded: 'bg-blue-500/20 border-blue-500/50 text-blue-700',
};

export function ADRGraph({ adrs, selectedAdrId, onAdrSelect, className }: ADRGraphProps) {
  const [zoom, setZoom] = useState(1);
  const [showDetails, setShowDetails] = useState(false);

  // Calculate graph layout
  const { nodes, edges } = useMemo(() => {
    if (!adrs || adrs.length === 0) {
      return { edges: [], nodes: [] };
    }

    const edges: GraphEdge[] = [];
    const visited = new Set<string>();
    const levelMap = new Map<string, number>();

    // Build relationships
    for (const adr of adrs) {
      if (adr.supersedes) {
        edges.push({
          source: adr.id,
          target: adrs.find((a) => a.adrNumber === adr.supersedes)?.id ?? adr.id,
          type: 'supersedes',
        });
      }

      if (adr.relatedAdrs) {
        for (const relatedNum of adr.relatedAdrs) {
          const relatedAdr = adrs.find((a) => a.adrNumber === relatedNum);
          if (relatedAdr) {
            edges.push({
              source: adr.id,
              target: relatedAdr.id,
              type: 'related',
            });
          }
        }
      }

      if (adr.relatedRequirements && adr.relatedRequirements.length > 0) {
        edges.push({
          source: adr.id,
          target: adr.id,
          type: 'depends',
        });
      }
    }

    // Assign levels using topological sort
    const assignLevel = (adrId: string, level = 0): number => {
      if (levelMap.has(adrId)) {
        return levelMap.get(adrId) ?? 0;
      }

      visited.add(adrId);
      let maxChildLevel = level;

      for (const edge of edges) {
        if (edge.source === adrId && edge.target !== adrId) {
          const childLevel = assignLevel(edge.target, level + 1);
          maxChildLevel = Math.max(maxChildLevel, childLevel);
        }
      }

      levelMap.set(adrId, maxChildLevel);
      return maxChildLevel;
    };

    for (const adr of adrs) {
      assignLevel(adr.id);
    }

    // Calculate positions based on levels
    const levelCounts = new Map<number, number>();
    const levelPositions = new Map<number, number>();

    for (const [, level] of levelMap) {
      levelCounts.set(level, (levelCounts.get(level) ?? 0) + 1);
    }

    const nodes: GraphNode[] = adrs.map((adr) => {
      const level = levelMap.get(adr.id) ?? 0;
      const count = levelCounts.get(level) ?? 1;
      const position = levelPositions.get(level) ?? 0;

      const x = (position - count / 2) * 200;
      const y = level * 150;

      levelPositions.set(level, position + 1);

      const connectedIds = new Set<string>();
      for (const edge of edges) {
        if (edge.source === adr.id) {
          connectedIds.add(edge.target);
        }
        if (edge.target === adr.id) {
          connectedIds.add(edge.source);
        }
      }

      return { adr, connectedIds, level, x, y };
    });

    return { edges, nodes };
  }, [adrs]);

  // Calculate bounds for auto-fit
  const bounds = useMemo(() => {
    if (nodes.length === 0) {
      return { maxX: 800, maxY: 600, minX: 0, minY: 0 };
    }

    let minX = Infinity,
      maxX = -Infinity,
      minY = Infinity,
      maxY = -Infinity;

    for (const node of nodes) {
      minX = Math.min(minX, node.x - 60);
      maxX = Math.max(maxX, node.x + 60);
      minY = Math.min(minY, node.y - 40);
      maxY = Math.max(maxY, node.y + 40);
    }

    return { maxX, maxY, minX, minY };
  }, [nodes]);

  const canvasWidth = bounds.maxX - bounds.minX + 100;
  const canvasHeight = bounds.maxY - bounds.minY + 100;

  const handleZoom = useCallback((direction: 'in' | 'out') => {
    setZoom((prev) => {
      const newZoom = direction === 'in' ? prev * 1.2 : prev / 1.2;
      return Math.max(0.5, Math.min(newZoom, 3));
    });
  }, []);

  const handleExport = useCallback(() => {
    const data = {
      edges: edges.map((e) => ({
        source: adrs.find((a) => a.id === e.source)?.adrNumber,
        target: adrs.find((a) => a.id === e.target)?.adrNumber,
        type: e.type,
      })),
      nodes: nodes.map((n) => ({
        id: n.adr.id,
        level: n.level,
        number: n.adr.adrNumber,
        status: n.adr.status,
        title: n.adr.title,
      })),
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'adr-graph.json';
    a.click();
    URL.revokeObjectURL(url);
  }, [nodes, edges, adrs]);

  if (adrs.length === 0) {
    return (
      <Card className={className}>
        <CardContent className='flex h-64 items-center justify-center'>
          <div className='text-muted-foreground text-center'>
            <GitBranch className='mx-auto mb-3 h-12 w-12 opacity-20' />
            <p className='text-sm'>No ADRs to visualize</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader className='flex flex-row items-center justify-between pb-3'>
        <div>
          <CardTitle>ADR Relationship Graph</CardTitle>
          <p className='text-muted-foreground mt-1 text-xs'>
            {nodes.length} decisions · {edges.length} relationships
          </p>
        </div>

        <div className='flex items-center gap-2'>
          <Button
            variant='outline'
            size='sm'
            className='h-8 gap-1'
            onClick={() => {
              handleZoom('out');
            }}
            disabled={zoom <= 0.5}
          >
            <ZoomOut className='h-3 w-3' />
          </Button>
          <span className='w-12 text-center text-xs font-medium'>{Math.round(zoom * 100)}%</span>
          <Button
            variant='outline'
            size='sm'
            className='h-8 gap-1'
            onClick={() => {
              handleZoom('in');
            }}
            disabled={zoom >= 3}
          >
            <ZoomIn className='h-3 w-3' />
          </Button>

          <div className='bg-border mx-1 h-5 w-px' />

          <Button variant='outline' size='sm' className='h-8 gap-1' onClick={handleExport}>
            <Download className='h-3 w-3' />
          </Button>

          <Button
            variant='outline'
            size='sm'
            className='h-8 gap-1'
            onClick={() => {
              setShowDetails(!showDetails);
            }}
          >
            {showDetails ? (
              <>
                <ChevronUp className='h-3 w-3' />
                Hide
              </>
            ) : (
              <>
                <ChevronDown className='h-3 w-3' />
                Show
              </>
            )}
          </Button>
        </div>
      </CardHeader>

      <CardContent className='space-y-4'>
        {/* Graph Canvas */}
        <div className='bg-muted/20 border-border relative overflow-auto rounded-lg border'>
          <svg
            width={canvasWidth * zoom}
            height={canvasHeight * zoom}
            className='min-h-[400px] min-w-full'
          >
            <g transform='translate(50, 50)'>
              {/* Edges */}
              {edges.map((edge, idx) => {
                const sourceNode = nodes.find((n) => n.adr.id === edge.source);
                const targetNode = nodes.find((n) => n.adr.id === edge.target);

                if (!sourceNode || !targetNode) {
                  return null;
                }

                const isSupersedes = edge.type === 'supersedes';
                const strokeDasharray = isSupersedes ? '5,5' : '0';
                const stroke = isSupersedes ? '#3b82f6' : '#cbd5e1';

                return (
                  <g key={`edge-${idx}`}>
                    <line
                      x1={sourceNode.x}
                      y1={sourceNode.y}
                      x2={targetNode.x}
                      y2={targetNode.y}
                      stroke={stroke}
                      strokeWidth={2}
                      strokeDasharray={strokeDasharray}
                      markerEnd='url(#arrowhead)'
                    />
                    {isSupersedes && (
                      <text
                        x={(sourceNode.x + targetNode.x) / 2}
                        y={(sourceNode.y + targetNode.y) / 2 - 5}
                        fontSize='10'
                        fill='#3b82f6'
                        className='pointer-events-none'
                      >
                        supersedes
                      </text>
                    )}
                  </g>
                );
              })}

              {/* Arrow marker */}
              <defs>
                <marker
                  id='arrowhead'
                  markerWidth='10'
                  markerHeight='10'
                  refX='9'
                  refY='3'
                  orient='auto'
                >
                  <polygon points='0 0, 10 3, 0 6' fill='#cbd5e1' />
                </marker>
              </defs>

              {/* Nodes */}
              {nodes.map((node) => {
                const isSelected = node.adr.id === selectedAdrId;
                const isConnected = node.connectedIds.has(selectedAdrId ?? '');

                return (
                  <g
                    key={node.adr.id}
                    transform={`translate(${node.x * zoom}, ${node.y * zoom})`}
                    onClick={() => onAdrSelect?.(node.adr)}
                    className='group cursor-pointer'
                  >
                    {/* Node background */}
                    <rect
                      x={-50}
                      y={-30}
                      width={100}
                      height={60}
                      fill={STATUS_COLORS[node.adr.status].split(' ')[0]}
                      stroke={isSelected ? '#ef4444' : isConnected ? '#3b82f6' : '#e2e8f0'}
                      strokeWidth={isSelected ? 3 : isConnected ? 2 : 1}
                      rx={8}
                      className='transition-all group-hover:shadow-lg'
                    />

                    {/* Node content */}
                    <text
                      x={0}
                      y={-10}
                      textAnchor='middle'
                      fontSize='11'
                      fontWeight='bold'
                      fill='currentColor'
                      className='pointer-events-none'
                    >
                      {node.adr.adrNumber}
                    </text>
                    <text
                      x={0}
                      y={8}
                      textAnchor='middle'
                      fontSize='9'
                      fill='currentColor'
                      className='pointer-events-none line-clamp-1'
                    >
                      {node.adr.title.slice(0, 15)}
                    </text>
                  </g>
                );
              })}
            </g>
          </svg>
        </div>

        {/* Details */}
        {showDetails && (
          <div className='bg-muted/20 grid grid-cols-2 gap-4 rounded-lg p-4'>
            <div>
              <h4 className='text-muted-foreground mb-2 text-xs font-semibold tracking-wider uppercase'>
                Legend
              </h4>
              <div className='space-y-2'>
                <div className='flex items-center gap-2 text-xs'>
                  <div className='h-3 w-3 rounded border border-green-500/50 bg-green-500/30' />
                  <span>Accepted</span>
                </div>
                <div className='flex items-center gap-2 text-xs'>
                  <div className='h-3 w-3 rounded border border-yellow-500/50 bg-yellow-500/30' />
                  <span>Proposed</span>
                </div>
                <div className='flex items-center gap-2 text-xs'>
                  <div className='h-3 w-3 rounded border border-blue-500/50 bg-blue-500/30' />
                  <span>Superseded</span>
                </div>
                <div className='flex items-center gap-2 text-xs'>
                  <div className='h-3 w-3 rounded border border-red-500/50 bg-red-500/30' />
                  <span>Rejected</span>
                </div>
              </div>
            </div>

            <div>
              <h4 className='text-muted-foreground mb-2 text-xs font-semibold tracking-wider uppercase'>
                Edge Types
              </h4>
              <div className='space-y-2'>
                <div className='flex items-center gap-2 text-xs'>
                  <div className='h-px w-8 bg-blue-500' style={{ borderTop: '1px dashed' }} />
                  <span>Supersedes</span>
                </div>
                <div className='flex items-center gap-2 text-xs'>
                  <div className='h-px w-8 bg-slate-300' />
                  <span>Related</span>
                </div>
                <div className='flex items-center gap-2 text-xs'>
                  <GitBranch className='h-3 w-3' />
                  <span>Dependency</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Relationship Summary */}
        {selectedAdrId && (
          <div className='bg-muted/50 border-border rounded-lg border p-3'>
            <div className='text-muted-foreground mb-2 text-xs font-semibold tracking-wider uppercase'>
              Related ADRs
            </div>
            <div className='flex flex-wrap gap-1'>
              {(() => {
                const selectedNode = nodes.find((n) => n.adr.id === selectedAdrId);
                if (!selectedNode || selectedNode.connectedIds.size === 0) {
                  return <span className='text-muted-foreground text-xs'>No relationships</span>;
                }
                return [...selectedNode.connectedIds].map((id) => {
                  const related = nodes.find((n) => n.adr.id === id);
                  if (related) {
                    return (
                      <Badge key={id} variant='secondary' className='text-xs'>
                        {related.adr.adrNumber}
                      </Badge>
                    );
                  }
                  return null;
                });
              })()}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
