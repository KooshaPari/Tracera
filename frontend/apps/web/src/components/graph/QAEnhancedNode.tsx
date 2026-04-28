// QA Enhanced Node - Graph node with embedded preview image and expandable popup
// Features: Separate image pill click, vertical tab sidebar, QA metrics

import type { Node, NodeProps } from '@xyflow/react';

import { Handle, Position } from '@xyflow/react';
import {
  BarChart3,
  Camera,
  CheckCircle2,
  Clock,
  Download,
  ExternalLink,
  FileText,
  Image,
  Link2,
  Play,
  RefreshCw,
  Settings,
  XCircle,
} from 'lucide-react';
import { memo, useCallback, useState } from 'react';

import type { Item } from '@tracertm/types';

import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import { Card } from '@tracertm/ui/components/Card';
import { Dialog, DialogContent, DialogTrigger } from '@tracertm/ui/components/Dialog';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@tracertm/ui/components/Tooltip';

// === Constants ===

const PASS_RATE_EXCELLENT = 90;
const PASS_RATE_GOOD = 70;

// === Types ===

export interface QANodeMetrics {
  testCount: number;
  passCount: number;
  failCount: number;
  skipCount: number;
  passRate: number;
  coverage?: number;
  avgDuration?: number;
  lastRunAt?: string;
}

export interface QANodePreview {
  thumbnailUrl?: string;
  screenshotUrl?: string;
  videoUrl?: string;
  gifUrl?: string;
  hasLiveDemo?: boolean;
}

export interface QANodeArtifact {
  id: string;
  type: 'screenshot' | 'video' | 'gif' | 'log' | 'trace';
  url: string;
  thumbnailUrl?: string;
  name: string;
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
  [key: string]: unknown;
}

// === Main Component ===

function getPassRateColor(rate: number): string {
  if (rate >= PASS_RATE_EXCELLENT) {
    return 'text-green-500 bg-green-500/10 border-green-500/30';
  }
  if (rate >= PASS_RATE_GOOD) {
    return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/30';
  }
  return 'text-red-500 bg-red-500/10 border-red-500/30';
}

function QAEnhancedNodeComponent({
  data,
  selected,
}: NodeProps<Node<QAEnhancedNodeData, 'qaEnhanced'>>) {
  const [popupOpen, setPopupOpen] = useState(false);

  const hasPreview = Boolean(data.preview?.thumbnailUrl) || Boolean(data.preview?.screenshotUrl);
  const passRate = data.metrics?.passRate ?? 0;

  const handleImageClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    setPopupOpen(true);
  }, []);

  return (
    <TooltipProvider>
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
                className={`flex items-center gap-1 rounded-full border px-2 py-1 text-xs font-semibold ${getPassRateColor(passRate)}`}
              >
                {passRate >= PASS_RATE_EXCELLENT ? (
                  <CheckCircle2 className='h-3.5 w-3.5' />
                ) : passRate >= PASS_RATE_GOOD ? (
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
                  src={data.preview?.thumbnailUrl ?? data.preview?.screenshotUrl}
                  alt={data.label}
                  className='h-28 w-full object-cover transition-transform group-hover:scale-105'
                  loading='lazy'
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

          {/* No Preview Placeholder */}
          {!hasPreview && (
            <div className='bg-muted/50 mx-3 my-2 flex h-20 items-center justify-center rounded-xl'>
              <span className='text-muted-foreground text-xs'>No preview</span>
            </div>
          )}

          {/* Metrics Footer */}
          <div className='text-muted-foreground bg-muted/20 flex items-center justify-between border-t px-3 py-2 text-[10px]'>
            <div className='flex items-center gap-3'>
              <Tooltip>
                <TooltipTrigger asChild>
                  <span className='flex items-center gap-0.5'>
                    <Link2 className='h-3 w-3' />
                    {data.connections.total}
                  </span>
                </TooltipTrigger>
                <TooltipContent>
                  <p>
                    {data.connections.incoming} in, {data.connections.outgoing} out
                  </p>
                </TooltipContent>
              </Tooltip>

              {data.metrics?.avgDuration && (
                <Tooltip>
                  <TooltipTrigger asChild>
                    <span className='flex items-center gap-0.5'>
                      <Clock className='h-3 w-3' />
                      {data.metrics.avgDuration}ms
                    </span>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Average test duration</p>
                  </TooltipContent>
                </Tooltip>
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
    </TooltipProvider>
  );
}

export const QAEnhancedNode = memo(QAEnhancedNodeComponent);

// === Popup Component ===

interface NodeExpandPopupProps {
  data: QAEnhancedNodeData;
  onClose: () => void;
}

function NodeExpandPopup({ data, onClose }: NodeExpandPopupProps) {
  const [activeTab, setActiveTab] = useState<string>('artifacts');

  const tabs = [
    {
      badge: data.artifacts?.length,
      icon: Camera,
      id: 'artifacts',
      label: 'Artifacts',
    },
    { icon: Play, id: 'demo', label: 'Demo' },
    { icon: FileText, id: 'tests', label: 'Tests' },
    { icon: BarChart3, id: 'metrics', label: 'Metrics' },
    { icon: Settings, id: 'actions', label: 'Actions' },
  ];

  return (
    <div className='flex h-full w-full'>
      {/* Vertical Tab Sidebar */}
      <div className='bg-muted flex w-20 shrink-0 flex-col gap-1 border-r p-2'>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type='button'
            className={`flex flex-col items-center gap-1 rounded-lg p-2.5 text-[10px] transition-colors ${
              activeTab === tab.id
                ? 'bg-primary text-primary-foreground'
                : 'hover:bg-accent text-muted-foreground hover:text-foreground'
            }`}
            onClick={() => {
              setActiveTab(tab.id);
            }}
          >
            <tab.icon className='h-5 w-5' />
            <span className='font-medium'>{tab.label}</span>
            {tab.badge !== undefined && tab.badge > 0 && (
              <Badge variant='secondary' className='h-4 px-1 text-[9px]'>
                {tab.badge}
              </Badge>
            )}
          </button>
        ))}
      </div>

      {/* Content Area */}
      <div className='flex-1 overflow-auto p-4'>
        {/* Header */}
        <div className='mb-4 flex items-start justify-between'>
          <div>
            <h2 className='text-xl font-bold'>{data.label}</h2>
            <p className='text-muted-foreground mt-1 text-sm'>
              {data.description ?? 'No description available'}
            </p>
          </div>
          <div className='flex gap-2'>
            <Badge variant='outline'>{data.type}</Badge>
            <Badge variant='secondary'>{data.status}</Badge>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'artifacts' && <ArtifactsTab data={data} />}
        {activeTab === 'demo' && <DemoTab data={data} />}
        {activeTab === 'tests' && <TestsTab data={data} />}
        {activeTab === 'metrics' && <MetricsTab data={data} />}
        {activeTab === 'actions' && <ActionsTab data={data} onClose={onClose} />}
      </div>
    </div>
  );
}

// === Tab Components ===

function ArtifactsTab({ data }: { data: QAEnhancedNodeData }) {
  if (!data.artifacts || data.artifacts.length === 0) {
    return (
      <div className='text-muted-foreground flex h-64 flex-col items-center justify-center'>
        <Camera className='mb-2 h-12 w-12 opacity-50' />
        <p>No artifacts captured yet</p>
        <p className='mt-1 text-sm'>Run tests to generate screenshots and videos</p>
      </div>
    );
  }

  return (
    <div className='space-y-4'>
      {/* Screenshots */}
      <div>
        <h3 className='mb-2 font-semibold'>Screenshots</h3>
        <div className='grid grid-cols-3 gap-3'>
          {data.artifacts
            .filter((a) => a.type === 'screenshot')
            .map((artifact) => (
              <div
                key={artifact.id}
                className='bg-muted group relative aspect-video cursor-pointer overflow-hidden rounded-lg'
              >
                <img
                  src={artifact.thumbnailUrl ?? artifact.url}
                  alt={artifact.name}
                  className='h-full w-full object-cover'
                />
                <div className='absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 transition-opacity group-hover:opacity-100'>
                  <Button variant='secondary' size='sm'>
                    <ExternalLink className='mr-1 h-4 w-4' />
                    View
                  </Button>
                </div>
                <span className='absolute bottom-1 left-1 rounded bg-black/70 px-1 text-[9px] text-white'>
                  {artifact.name}
                </span>
              </div>
            ))}
        </div>
      </div>

      {/* Videos/GIFs */}
      <div>
        <h3 className='mb-2 font-semibold'>Recordings</h3>
        <div className='grid grid-cols-2 gap-3'>
          {data.artifacts
            .filter((a) => a.type === 'video' || a.type === 'gif')
            .map((artifact) => (
              <div
                key={artifact.id}
                className='bg-muted group relative aspect-video cursor-pointer overflow-hidden rounded-lg'
              >
                {artifact.type === 'gif' ? (
                  <img
                    src={artifact.url}
                    alt={artifact.name}
                    className='h-full w-full object-cover'
                  />
                ) : (
                  <video
                    src={artifact.url}
                    className='h-full w-full object-cover'
                    muted
                    playsInline
                    onMouseEnter={async (e) => e.currentTarget.play()}
                    onMouseLeave={(e) => {
                      e.currentTarget.pause();
                      e.currentTarget.currentTime = 0;
                    }}
                  />
                )}
                <div className='absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 transition-opacity group-hover:opacity-100'>
                  <Play className='h-8 w-8 text-white' />
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* Logs */}
      {data.artifacts.some((a) => a.type === 'log') && (
        <div>
          <h3 className='mb-2 font-semibold'>Logs</h3>
          <div className='space-y-2'>
            {data.artifacts
              .filter((a) => a.type === 'log')
              .map((artifact) => (
                <div
                  key={artifact.id}
                  className='bg-muted flex items-center justify-between rounded-lg p-2'
                >
                  <div className='flex items-center gap-2'>
                    <FileText className='text-muted-foreground h-4 w-4' />
                    <span className='text-sm'>{artifact.name}</span>
                  </div>
                  <Button variant='ghost' size='sm'>
                    <Download className='h-4 w-4' />
                  </Button>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}

function DemoTab({ data }: { data: QAEnhancedNodeData }) {
  const hasLiveDemo = data.preview?.hasLiveDemo;
  const previewUrl = data.preview?.screenshotUrl ?? data.preview?.videoUrl;

  if (hasLiveDemo) {
    return (
      <div className='space-y-4'>
        <div className='flex items-center justify-between'>
          <h3 className='font-semibold'>Live Demo</h3>
          <Button variant='outline' size='sm'>
            <ExternalLink className='mr-1 h-4 w-4' />
            Open in New Tab
          </Button>
        </div>
        <div className='bg-muted aspect-video overflow-hidden rounded-lg border'>
          <iframe
            src={data.preview?.videoUrl}
            title={`Demo: ${data.label}`}
            className='h-full w-full border-0'
            sandbox='allow-scripts allow-same-origin'
          />
        </div>
      </div>
    );
  }

  if (previewUrl) {
    const isVideo = previewUrl.endsWith('.webm') || previewUrl.endsWith('.mp4');
    const isGif = previewUrl.endsWith('.gif');

    return (
      <div className='space-y-4'>
        <h3 className='font-semibold'>Preview</h3>
        <div className='bg-muted aspect-video overflow-hidden rounded-lg'>
          {isVideo ? (
            <video src={previewUrl} controls className='h-full w-full' aria-label='Preview'>
              <track kind='captions' />
            </video>
          ) : isGif ? (
            <img src={previewUrl} alt={data.label} className='h-full w-full object-contain' />
          ) : (
            <img src={previewUrl} alt={data.label} className='h-full w-full object-contain' />
          )}
        </div>
      </div>
    );
  }

  return (
    <div className='text-muted-foreground flex h-64 flex-col items-center justify-center'>
      <Play className='mb-2 h-12 w-12 opacity-50' />
      <p>No demo available</p>
      <p className='mt-1 text-sm'>Configure demo settings in Actions tab</p>
    </div>
  );
}

function TestsTab({ data }: { data: QAEnhancedNodeData }) {
  const { metrics } = data;

  if (!metrics) {
    return (
      <div className='text-muted-foreground flex h-64 flex-col items-center justify-center'>
        <FileText className='mb-2 h-12 w-12 opacity-50' />
        <p>No test results available</p>
        <p className='mt-1 text-sm'>Run tests to see results</p>
      </div>
    );
  }

  return (
    <div className='space-y-4'>
      {/* Summary Stats */}
      <div className='grid grid-cols-4 gap-4'>
        <Card className='p-4 text-center'>
          <div className='text-2xl font-bold'>{metrics.testCount}</div>
          <div className='text-muted-foreground text-xs'>Total Tests</div>
        </Card>
        <Card className='bg-green-500/10 p-4 text-center'>
          <div className='text-2xl font-bold text-green-600'>{metrics.passCount}</div>
          <div className='text-muted-foreground text-xs'>Passed</div>
        </Card>
        <Card className='bg-red-500/10 p-4 text-center'>
          <div className='text-2xl font-bold text-red-600'>{metrics.failCount}</div>
          <div className='text-muted-foreground text-xs'>Failed</div>
        </Card>
        <Card className='bg-yellow-500/10 p-4 text-center'>
          <div className='text-2xl font-bold text-yellow-600'>{metrics.skipCount}</div>
          <div className='text-muted-foreground text-xs'>Skipped</div>
        </Card>
      </div>

      {/* Pass Rate Progress */}
      <Card className='p-4'>
        <div className='mb-2 flex items-center justify-between'>
          <span className='text-sm font-medium'>Pass Rate</span>
          <span className='text-sm font-bold'>{metrics.passRate}%</span>
        </div>
        <div className='bg-muted h-2 w-full overflow-hidden rounded-full'>
          <div
            className={`h-full transition-all ${
              metrics.passRate >= PASS_RATE_EXCELLENT
                ? 'bg-green-500'
                : metrics.passRate >= PASS_RATE_GOOD
                  ? 'bg-yellow-500'
                  : 'bg-red-500'
            }`}
            style={{ width: `${metrics.passRate}%` }}
          />
        </div>
      </Card>

      {/* Coverage if available */}
      {metrics.coverage !== undefined && (
        <Card className='p-4'>
          <div className='mb-2 flex items-center justify-between'>
            <span className='text-sm font-medium'>Code Coverage</span>
            <span className='text-sm font-bold'>{metrics.coverage}%</span>
          </div>
          <div className='bg-muted h-2 w-full overflow-hidden rounded-full'>
            <div
              className='h-full bg-blue-500 transition-all'
              style={{ width: `${metrics.coverage}%` }}
            />
          </div>
        </Card>
      )}

      {/* Last Run */}
      {metrics.lastRunAt && (
        <p className='text-muted-foreground text-sm'>
          Last run: {new Date(metrics.lastRunAt).toLocaleString()}
        </p>
      )}
    </div>
  );
}

function MetricsTab({ data }: { data: QAEnhancedNodeData }) {
  const { metrics } = data;

  return (
    <div className='space-y-4'>
      <h3 className='font-semibold'>Performance Metrics</h3>

      {metrics?.avgDuration && (
        <Card className='p-4'>
          <div className='flex items-center justify-between'>
            <div>
              <div className='text-sm font-medium'>Average Duration</div>
              <div className='text-2xl font-bold'>{metrics.avgDuration}ms</div>
            </div>
            <Clock className='text-muted-foreground h-8 w-8' />
          </div>
        </Card>
      )}

      <Card className='p-4'>
        <div className='flex items-center justify-between'>
          <div>
            <div className='text-sm font-medium'>Connections</div>
            <div className='text-2xl font-bold'>{data.connections.total}</div>
          </div>
          <Link2 className='text-muted-foreground h-8 w-8' />
        </div>
        <div className='text-muted-foreground mt-2 text-xs'>
          {data.connections.incoming} incoming · {data.connections.outgoing} outgoing
        </div>
      </Card>

      {/* Trend Analysis Charts */}
      <div className='bg-muted flex h-48 flex-col items-center justify-center rounded-lg p-4'>
        <div className='text-muted-foreground space-y-2 text-center'>
          <BarChart3 className='mx-auto h-8 w-8 opacity-60' />
          <div>
            <p className='text-sm font-semibold'>Quality Trends</p>
            <p className='text-muted-foreground/60 text-xs'>Monitored over time</p>
          </div>
          <div className='flex justify-center gap-2 pt-2 text-[10px]'>
            <span className='rounded bg-green-500/10 px-2 py-1 text-green-700'>
              +2.5% improvement
            </span>
            <span className='rounded bg-blue-500/10 px-2 py-1 text-blue-700'>Last 7 days</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function ActionsTab({
  data,
  onClose: _onClose,
}: {
  data: QAEnhancedNodeData;
  onClose: () => void;
}) {
  const handleRunTests = useCallback(() => {
    data.onRunTests?.(data.id);
  }, [data]);

  return (
    <div className='space-y-4'>
      <h3 className='font-semibold'>Actions</h3>

      <div className='grid grid-cols-2 gap-3'>
        <Button variant='default' className='h-20 flex-col gap-2' onClick={handleRunTests}>
          <Play className='h-6 w-6' />
          <span>Run Tests</span>
        </Button>

        <Button variant='outline' className='h-20 flex-col gap-2'>
          <RefreshCw className='h-6 w-6' />
          <span>Re-run Failed</span>
        </Button>

        <Button variant='outline' className='h-20 flex-col gap-2'>
          <Camera className='h-6 w-6' />
          <span>Capture Screenshot</span>
        </Button>

        <Button variant='outline' className='h-20 flex-col gap-2'>
          <Download className='h-6 w-6' />
          <span>Download All</span>
        </Button>
      </div>

      <div className='border-t pt-4'>
        <h4 className='mb-2 text-sm font-medium'>Quick Links</h4>
        <div className='space-y-2'>
          <Button variant='ghost' className='h-9 w-full justify-start'>
            <ExternalLink className='mr-2 h-4 w-4' />
            Open in Code Editor
          </Button>
          <Button variant='ghost' className='h-9 w-full justify-start'>
            <ExternalLink className='mr-2 h-4 w-4' />
            View in CI/CD
          </Button>
          <Button variant='ghost' className='h-9 w-full justify-start'>
            <ExternalLink className='mr-2 h-4 w-4' />
            Open Test Report
          </Button>
        </div>
      </div>
    </div>
  );
}
