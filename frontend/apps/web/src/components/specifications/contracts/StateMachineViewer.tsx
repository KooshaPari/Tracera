import { motion } from 'framer-motion';
import { Circle, Play } from 'lucide-react';
import { useState } from 'react';

import type { ContractTransition } from '@tracertm/types';

import { Card } from '@tracertm/ui';

interface StateMachineViewerProps {
  states?: string[] | undefined;
  initialState?: string | undefined;
  currentState?: string | undefined;
  transitions?: ContractTransition[] | undefined;
  onStateSelect?: ((state: string) => void) | undefined;
  onTransitionTrigger?: ((transition: ContractTransition) => Promise<void>) | undefined;
  isExecutable?: boolean | undefined;
  className?: string | undefined;
}

interface StateNodePosition {
  state: string;
  x: number;
  y: number;
}

function calculatePositions(states: string[], centerX = 300, centerY = 150): StateNodePosition[] {
  if (!states || states.length === 0) {
    return [];
  }

  const radius = Math.min(250, 50 * states.length);
  const angleSlice = (2 * Math.PI) / Math.max(states.length, 1);

  return states.map((state, index) => ({
    state,
    x: centerX + radius * Math.cos(angleSlice * index - Math.PI / 2),
    y: centerY + radius * Math.sin(angleSlice * index - Math.PI / 2),
  }));
}

export function StateMachineViewer({
  states = [],
  initialState,
  currentState,
  transitions = [],
  onStateSelect,
  onTransitionTrigger,
  isExecutable = false,
  className = '',
}: StateMachineViewerProps) {
  const [isTransitioning, setIsTransitioning] = useState(false);

  const positions = calculatePositions(states);
  const positionMap = Object.fromEntries(positions.map((p) => [p.state, { x: p.x, y: p.y }]));

  if (states.length === 0) {
    return (
      <Card className={`text-muted-foreground p-6 text-center ${className}`}>
        <Circle className='mx-auto mb-2 h-8 w-8 opacity-50' />
        <p className='text-sm'>No state machine defined.</p>
        <p className='text-xs'>Define states and transitions to visualize the state machine.</p>
      </Card>
    );
  }

  const handleTransitionClick = async (transition: ContractTransition) => {
    if (!isExecutable || !onTransitionTrigger) {
      return;
    }
    setIsTransitioning(true);
    try {
      await onTransitionTrigger(transition);
    } finally {
      setIsTransitioning(false);
    }
  };

  // Calculate viewBox based on positions
  const allX = positions.map((p) => p.x);
  const allY = positions.map((p) => p.y);
  const minX = Math.min(...allX) - 60;
  const maxX = Math.max(...allX) + 60;
  const minY = Math.min(...allY) - 60;
  const maxY = Math.max(...allY) + 60;
  const width = maxX - minX;
  const height = maxY - minY;

  // Get available transitions from each state
  const transitionsBySource: Record<string, ContractTransition[]> = Object.fromEntries(
    states.map((state) => [state, transitions.filter((t) => t.fromState === state)]),
  );

  return (
    <div className={`space-y-4 ${className}`}>
      <Card className='bg-muted/30 p-4'>
        <svg
          viewBox={`${minX} ${minY} ${width} ${height}`}
          className='border-border bg-background h-auto w-full rounded-lg border'
          style={{ minHeight: '400px' }}
        >
          <defs>
            <marker
              id='arrowhead'
              markerWidth='10'
              markerHeight='10'
              refX='9'
              refY='3'
              orient='auto'
            >
              <polygon points='0 0, 10 3, 0 6' fill='#888' />
            </marker>
          </defs>

          {/* Draw Transitions as Curved Lines */}
          {transitions.map((transition) => {
            const fromPos = positionMap[transition.fromState];
            const toPos = positionMap[transition.toState];

            if (!fromPos || !toPos) {
              return null;
            }

            const isSelfLoop = transition.fromState === transition.toState;
            const midX = (fromPos.x + toPos.x) / 2;
            const midY = (fromPos.y + toPos.y) / 2;

            // For self-loops, create a circular path
            if (isSelfLoop) {
              const pathData = `
								M ${fromPos.x + 40} ${fromPos.y}
								Q ${fromPos.x + 60} ${fromPos.y - 50}
								T ${fromPos.x + 40} ${fromPos.y - 80}
							`;
              return (
                <g key={`transition-${transition.id}`}>
                  <path
                    d={pathData}
                    fill='none'
                    stroke='#888'
                    strokeWidth='2'
                    markerEnd='url(#arrowhead)'
                    className='opacity-60'
                  />
                  <text
                    x={fromPos.x + 60}
                    y={fromPos.y - 60}
                    className='fill-muted-foreground pointer-events-none font-mono text-xs'
                    textAnchor='middle'
                  >
                    {transition.trigger}
                  </text>
                </g>
              );
            }

            // Calculate control point for curve (Bezier)
            const distance = Math.sqrt((toPos.x - fromPos.x) ** 2 + (toPos.y - fromPos.y) ** 2);
            const offsetX = ((toPos.y - fromPos.y) / distance) * 40;
            const offsetY = -((toPos.x - fromPos.x) / distance) * 40;

            const pathData = `
							M ${fromPos.x} ${fromPos.y}
							Q ${midX + offsetX} ${midY + offsetY}
							T ${toPos.x} ${toPos.y}
						`;

            return (
              <g key={`transition-${transition.id}`}>
                <path
                  d={pathData}
                  fill='none'
                  stroke='#888'
                  strokeWidth='2'
                  markerEnd='url(#arrowhead)'
                  className='hover:stroke-primary opacity-60 transition-opacity hover:opacity-100'
                  style={{ cursor: isExecutable ? 'pointer' : 'default' }}
                  onClick={async () => handleTransitionClick(transition)}
                />
                <text
                  x={midX + offsetX + 5}
                  y={midY + offsetY - 5}
                  className='fill-muted-foreground pointer-events-none font-mono text-xs'
                  textAnchor='middle'
                  style={{
                    background: 'white',
                    padding: '0 4px',
                  }}
                >
                  {transition.trigger}
                </text>
              </g>
            );
          })}

          {/* Draw State Nodes */}
          {positions.map((pos) => {
            const isInitial = pos.state === initialState;
            const isCurrent = pos.state === currentState;
            const availableTransitions = transitionsBySource[pos.state] ?? [];

            return (
              <g key={`state-${pos.state}`}>
                {/* Node Circle */}
                <motion.circle
                  cx={pos.x}
                  cy={pos.y}
                  r={40}
                  className={`cursor-pointer transition-all ${
                    isCurrent
                      ? 'fill-primary stroke-primary'
                      : isInitial
                        ? 'fill-green-500/20 stroke-green-600'
                        : 'fill-background stroke-border hover:fill-muted'
                  }`}
                  strokeWidth={isCurrent ? 3 : 2}
                  onClick={() => onStateSelect?.(pos.state)}
                  whileHover={{ scale: 1.1 }}
                  animate={{
                    scale: isCurrent ? 1.15 : 1,
                  }}
                  transition={{ duration: 0.2 }}
                />

                {/* Initial State Indicator (inner circle) */}
                {isInitial && (
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r={28}
                    fill='none'
                    stroke='#22c55e'
                    strokeWidth='1'
                    strokeDasharray='4,4'
                  />
                )}

                {/* Current State Indicator */}
                {isCurrent && (
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r={50}
                    fill='none'
                    stroke='#2563eb'
                    strokeWidth='1'
                    strokeDasharray='4,4'
                    opacity='0.5'
                  />
                )}

                {/* State Label */}
                <text
                  x={pos.x}
                  y={pos.y}
                  className='fill-foreground pointer-events-none text-xs font-semibold'
                  textAnchor='middle'
                  dominantBaseline='middle'
                  style={{ maxWidth: '80px', wordWrap: 'break-word' }}
                >
                  {pos.state}
                </text>

                {/* Available Transitions Indicator */}
                {isExecutable && availableTransitions.length > 0 && (
                  <circle cx={pos.x + 35} cy={pos.y - 35} r={4} fill='#f59e0b' opacity={0.8} />
                )}
              </g>
            );
          })}
        </svg>
      </Card>

      {/* State Information */}
      {currentState && (
        <div className='grid gap-2'>
          <h4 className='text-sm font-semibold'>Current State Details</h4>
          <Card className='space-y-2 p-3'>
            <div>
              <p className='text-muted-foreground text-xs'>State</p>
              <p className='font-mono font-semibold'>{currentState}</p>
            </div>

            {/* Available Transitions from Current State */}
            {currentState && (transitionsBySource[currentState]?.length ?? 0) > 0 && (
              <div>
                <p className='text-muted-foreground mb-2 text-xs'>Available Transitions</p>
                <div className='space-y-1'>
                  {(transitionsBySource[currentState] ?? []).map((transition) => (
                    <motion.div
                      key={transition.id}
                      className='bg-muted flex items-center justify-between rounded p-2 text-xs'
                      whileHover={{ backgroundColor: 'rgba(0,0,0,0.1)' }}
                    >
                      <div>
                        <p className='font-mono font-semibold'>{transition.trigger}</p>
                        <p className='text-muted-foreground'>→ {transition.toState}</p>
                      </div>
                      {isExecutable && (
                        <motion.button
                          type='button'
                          onClick={async () => handleTransitionClick(transition)}
                          disabled={isTransitioning}
                          className='hover:bg-primary/10 rounded p-1.5 transition-colors disabled:opacity-50'
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          <Play className='h-3 w-3' />
                        </motion.button>
                      )}
                    </motion.div>
                  ))}
                </div>
              </div>
            )}
          </Card>
        </div>
      )}

      {/* Initial State Info */}
      {initialState && (
        <div className='text-muted-foreground flex items-center gap-2 text-xs'>
          <Circle className='h-3 w-3 fill-green-600 text-green-600' />
          <span>
            Initial State: <span className='font-mono font-semibold'>{initialState}</span>
          </span>
        </div>
      )}
    </div>
  );
}
