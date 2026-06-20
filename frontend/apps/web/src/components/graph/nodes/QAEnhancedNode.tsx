// QA Enhanced Node - Graph node with QA metrics and expandable popup
// Extends RichNodePill with QA-specific features: pass rate, artifacts, demo runner

import type { Node, NodeProps } from '@xyflow/react';

import { Handle, Position } from '@xyflow/react';
import { CheckCircle2, Clock, Image, Link2, Play, XCircle } from 'lucide-react';
import { memo, useCallback, useState } from 'react';

import type { Item } from '@tracertm/types';

import { Badge } from '@tracertm/ui/components/Badge';
import { Card } from '@tracertm/ui/components/Card';
import { Dialog, DialogContent, DialogTrigger } from '@tracertm/ui/components/Dialog';

import { NodeExpandPopup } from './NodeExpandPopup';

// === Types ===

export interface QANodeMetrics {
  passRate: number; // 0-100
  testCount: number;
  passCount: number;
  failCount: number;
  coverage?: number; // 0-100
  avgDuration?: number; // Ms
  flakiness?: number; // 0-100
  lastRunAt?: string;
}

export interface QANodePreview {
  thumbnailUrl?: string;
  screenshotUrl?: string;
  videoUrl?: string;
  gifUrl?: string;
  hasLiveDemo?: boolean;
  demoUrl?: string;
}

export interface QANodeArtifact {
  id: string;
  type: 'screenshot' | 'video' | 'gif' | 'log' | 'trace';
  url: string;
  thumbnailUrl?: string | undefined;
  capturedAt: string;
}

export interface QAEnhancedNodeData {
  id: string;
  item: Item;
  label: string;
  type: string;
  status: string;
  description?: string;
  metrics?: QANodeMetrics;
  preview?: QANodePreview;
  artifacts?: QANodeArtifact[];
  connections: { incoming: number; outgoing: number; total: number };
  onExpandPopup?: (nodeId: string) => void;
  onRunTests?: (nodeId: string) => void;
  [key: string]: unknown; // Index signature for React Flow compatibility
}

// === Main Component ===

function getPassRateColor(rate: number): string {
  if (rate >= 90) {
    return 'text-green-500 bg-green-500/10 border-green-500/30';
  }
  if (rate >= 70) {
    return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/30';
  }
  return 'text-red-500 bg-red-500/10 border-red-500/30';
}

function QAEnhancedNodeComponent({
  data,
  selected,
}: NodeProps<Node<QAEnhancedNodeData, 'qaEnhanced'>>) {
  const [popupOpen, setPopupOpen] = useState(false);

  const hasPreview = Boolean(data.preview?.thumbnailUrl);
  const passRate = data.metrics?.passRate ?? 0;

  const handleImageClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    setPopupOpen(true);
  }, []);

  return (
    <>
      <Handle type='target' position={Position.Left} className='!h-3 !w-3' />

      <Dialog open={popupOpen} onOpenChange={setPopupOpen}>
        <Card
          className={`w-[280px] overflow-hidden transition-all ${
            selected ? 'ring-primary ring-2 ring-offset-2' : ''
          }`}
        >
          {/* Header Row */}
          <div className='bg-muted/30 flex items-center justify-between border-b p-3'>
            <div className='flex min-w-0 flex-1 items-center gap-2'>
              <div className='flex min-w-0 flex-col'>
                <h4 className='truncate text-sm font-semibold'>{data.label}</h4>
                <div className='mt-0.5 flex items-center gap-1.5'>
                  <Badge variant='outline' className='h-4 px-1.5 text-[10px]'>
                    {data.type}
                  </Badge>
                  <Badge variant='secondary' className='h-4 px-1.5 text-[10px]'>
                    {data.status}
                  </Badge>
                </div>
              </div>
            </div>

            {/* Pass Rate Badge */}
            {data.metrics && (
              <div
                className={`flex items-center gap-1 rounded-full border px-2 py-1 text-xs font-semibold ${getPassRateColor(
                  passRate,
                )}`}
              >
                {passRate >= 90 ? (
                  <CheckCircle2 className='h-3.5 w-3.5' />
                ) : passRate >= 70 ? (
                  <Clock className='h-3.5 w-3.5' />
                ) : (
                  <XCircle className='h-3.5 w-3.5' />
                )}
                {passRate}%
              </div>
            )}
          </div>

          {/* Image Pill - Separately Clickable */}
          {hasPreview && (
            <DialogTrigger asChild>
              <div
                className='group hover:border-primary/50 relative mx-3 my-2 cursor-pointer overflow-hidden rounded-xl border-2 border-dashed border-transparent transition-all'
                onClick={handleImageClick}
              >
                <img
                  src={data.preview?.thumbnailUrl}
                  alt={data.label}
                  className='h-28 w-full object-cover transition-transform group-hover:scale-105'
                />

                {/* Hover Overlay */}
                <div className='absolute inset-0 flex flex-col items-center justify-center gap-1 bg-black/60 opacity-0 transition-opacity group-hover:opacity-100'>
                  {data.preview?.hasLiveDemo ? (
                    <>
                      <Play className='h-8 w-8 text-white' />
                      <span className='text-xs font-medium text-white'>Run Demo</span>
                    </>
                  ) : (
                    <>
                      <Image className='h-6 w-6 text-white' />
                      <span className='text-xs font-medium text-white'>Click to Expand</span>
                    </>
                  )}
                </div>

                {/* Artifact Count Badge */}
                {data.artifacts && data.artifacts.length > 0 && (
                  <div className='absolute top-2 right-2 rounded-full bg-black/70 px-1.5 py-0.5 text-[10px] text-white'>
                    {data.artifacts.length} artifacts
                  </div>
                )}
              </div>
            </DialogTrigger>
          )}

          {/* Metrics Footer */}
          <div className='text-muted-foreground bg-muted/20 flex items-center justify-between border-t px-3 py-2 text-[10px]'>
            <div className='flex items-center gap-3'>
              <span className='flex items-center gap-0.5'>
                <Link2 className='h-3 w-3' />
                {data.connections.total}
              </span>

              {data.metrics?.avgDuration && (
                <span className='flex items-center gap-0.5'>
                  <Clock className='h-3 w-3' />
                  {data.metrics.avgDuration}ms
                </span>
              )}

              {data.metrics && (
                <span className='flex items-center gap-0.5'>
                  🧪 {data.metrics.passCount}/{data.metrics.testCount}
                </span>
              )}
            </div>

            {data.metrics?.coverage !== undefined && (
              <span className='font-medium'>📊 {data.metrics.coverage}%</span>
            )}
          </div>
        </Card>

        {/* Expand Popup */}
        <DialogContent className='flex h-[80vh] max-w-4xl overflow-hidden p-0'>
          <NodeExpandPopup
            data={data}
            onClose={() => {
              setPopupOpen(false);
            }}
          />
        </DialogContent>
      </Dialog>

      <Handle type='source' position={Position.Right} className='!h-3 !w-3' />
    </>
  );
}

export const QAEnhancedNode = memo(QAEnhancedNodeComponent);
