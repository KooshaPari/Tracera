// Node Expand Popup - Modal with vertical tabs for artifacts, demo, tests, metrics, actions

import {
  BarChart3,
  Camera,
  Download,
  ExternalLink,
  FileText,
  Play,
  RefreshCw,
  Settings,
  Video,
} from 'lucide-react';
import { useState } from 'react';

import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';

import type {
  QAEnhancedNodeData,
  QANodeArtifact,
  QANodeMetrics,
  QANodePreview,
} from './QAEnhancedNode';

interface NodeExpandPopupProps {
  data: QAEnhancedNodeData;
  onClose?: () => void;
}

export function NodeExpandPopup({ data }: NodeExpandPopupProps) {
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
            className={`flex cursor-pointer flex-col items-center gap-1 rounded-lg p-2.5 text-[10px] transition-colors ${
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
      <div className='flex-1 overflow-auto p-6'>
        {activeTab === 'artifacts' && (
          <ArtifactsTab {...(data.artifacts ? { artifacts: data.artifacts } : {})} />
        )}
        {activeTab === 'demo' && <DemoTab {...(data.preview ? { preview: data.preview } : {})} />}
        {activeTab === 'tests' && <TestsTab {...(data.metrics ? { metrics: data.metrics } : {})} />}
        {activeTab === 'metrics' && (
          <MetricsTab {...(data.metrics ? { metrics: data.metrics } : {})} />
        )}
        {activeTab === 'actions' && <ActionsTab nodeId={data.id} />}
      </div>
    </div>
  );
}

// === Tab Components ===

function ArtifactsTab({ artifacts }: { artifacts?: QANodeArtifact[] }) {
  if (!artifacts || artifacts.length === 0) {
    return (
      <div className='text-muted-foreground flex h-full flex-col items-center justify-center'>
        <Camera className='mb-4 h-12 w-12 opacity-50' />
        <p>No artifacts available</p>
      </div>
    );
  }

  return (
    <div className='space-y-4'>
      <h2 className='text-xl font-semibold'>Artifacts</h2>
      <div className='grid grid-cols-2 gap-4 md:grid-cols-3'>
        {artifacts.map((artifact) => (
          <div
            key={artifact.id}
            className='hover:bg-muted/30 cursor-pointer overflow-hidden rounded-lg border transition-all hover:shadow-md'
          >
            {artifact.type === 'screenshot' || artifact.type === 'gif' ? (
              <img
                src={artifact.thumbnailUrl ?? artifact.url}
                alt={artifact.type}
                className='h-32 w-full object-cover'
              />
            ) : artifact.type === 'video' ? (
              <div className='bg-muted flex h-32 w-full items-center justify-center'>
                <Video className='text-muted-foreground h-8 w-8' />
              </div>
            ) : (
              <div className='bg-muted flex h-32 w-full items-center justify-center'>
                <FileText className='text-muted-foreground h-8 w-8' />
              </div>
            )}
            <div className='p-2'>
              <div className='flex items-center justify-between'>
                <Badge variant='outline' className='text-xs'>
                  {artifact.type}
                </Badge>
                <Button
                  variant='ghost'
                  size='sm'
                  className='hover:bg-muted/50 h-6 w-6 p-0 transition-colors'
                >
                  <Download className='h-3 w-3' />
                </Button>
              </div>
              <p className='text-muted-foreground mt-1 text-xs'>
                {new Date(artifact.capturedAt).toLocaleString()}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function DemoTab({ preview }: { preview?: QANodePreview }) {
  if (!preview) {
    return (
      <div className='text-muted-foreground flex h-full flex-col items-center justify-center'>
        <Play className='mb-4 h-12 w-12 opacity-50' />
        <p>No demo available</p>
      </div>
    );
  }

  return (
    <div className='space-y-4'>
      <h2 className='text-xl font-semibold'>Demo</h2>
      {preview.hasLiveDemo && preview.demoUrl ? (
        <div className='overflow-hidden rounded-lg border'>
          <iframe
            src={preview.demoUrl}
            className='h-[600px] w-full'
            title='Demo'
            sandbox='allow-scripts allow-same-origin'
          />
        </div>
      ) : preview.gifUrl ? (
        <div className='overflow-hidden rounded-lg border'>
          <img src={preview.gifUrl} alt='Demo GIF' className='w-full' />
        </div>
      ) : preview.videoUrl ? (
        <div className='overflow-hidden rounded-lg border'>
          <video src={preview.videoUrl} controls className='w-full'>
            <track kind='captions' />
          </video>
        </div>
      ) : (
        <p className='text-muted-foreground'>No demo media available</p>
      )}
    </div>
  );
}

function TestsTab({ metrics }: { metrics?: QANodeMetrics }) {
  if (!metrics) {
    return (
      <div className='text-muted-foreground flex h-full flex-col items-center justify-center'>
        <FileText className='mb-4 h-12 w-12 opacity-50' />
        <p>No test data available</p>
      </div>
    );
  }

  return (
    <div className='space-y-4'>
      <h2 className='text-xl font-semibold'>Test Results</h2>
      <div className='grid grid-cols-2 gap-4'>
        <div className='rounded-lg border p-4'>
          <div className='text-muted-foreground text-sm'>Total Tests</div>
          <div className='text-2xl font-bold'>{metrics.testCount}</div>
        </div>
        <div className='rounded-lg border p-4'>
          <div className='text-muted-foreground text-sm'>Passed</div>
          <div className='text-2xl font-bold text-green-500'>{metrics.passCount}</div>
        </div>
        <div className='rounded-lg border p-4'>
          <div className='text-muted-foreground text-sm'>Failed</div>
          <div className='text-2xl font-bold text-red-500'>{metrics.failCount}</div>
        </div>
        {metrics.coverage !== undefined && (
          <div className='rounded-lg border p-4'>
            <div className='text-muted-foreground text-sm'>Coverage</div>
            <div className='text-2xl font-bold'>{metrics.coverage}%</div>
          </div>
        )}
      </div>
      {metrics.flakiness !== undefined && (
        <div className='rounded-lg border p-4'>
          <div className='text-muted-foreground mb-2 text-sm'>Flakiness</div>
          <div className='bg-muted h-2 w-full rounded-full'>
            <div
              className='h-2 rounded-full bg-yellow-500'
              style={{ width: `${metrics.flakiness}%` }}
            />
          </div>
          <div className='text-muted-foreground mt-1 text-xs'>{metrics.flakiness}% flaky tests</div>
        </div>
      )}
    </div>
  );
}

function MetricsTab({ metrics }: { metrics?: QANodeMetrics }) {
  if (!metrics) {
    return (
      <div className='text-muted-foreground flex h-full flex-col items-center justify-center'>
        <BarChart3 className='mb-4 h-12 w-12 opacity-50' />
        <p>No metrics available</p>
      </div>
    );
  }

  return (
    <div className='space-y-4'>
      <h2 className='text-xl font-semibold'>Metrics</h2>
      <div className='space-y-4'>
        <div className='rounded-lg border p-4'>
          <div className='text-muted-foreground mb-2 text-sm'>Pass Rate</div>
          <div className='text-3xl font-bold'>{metrics.passRate}%</div>
          <div className='bg-muted mt-2 h-2 w-full rounded-full'>
            <div
              className={`h-2 rounded-full ${
                metrics.passRate >= 90
                  ? 'bg-green-500'
                  : metrics.passRate >= 70
                    ? 'bg-yellow-500'
                    : 'bg-red-500'
              }`}
              style={{ width: `${metrics.passRate}%` }}
            />
          </div>
        </div>
        {metrics.avgDuration !== undefined && (
          <div className='rounded-lg border p-4'>
            <div className='text-muted-foreground text-sm'>Avg Duration</div>
            <div className='text-2xl font-bold'>{metrics.avgDuration}ms</div>
          </div>
        )}
        {metrics.lastRunAt && (
          <div className='rounded-lg border p-4'>
            <div className='text-muted-foreground text-sm'>Last Run</div>
            <div className='text-sm'>{new Date(metrics.lastRunAt).toLocaleString()}</div>
          </div>
        )}
      </div>
    </div>
  );
}

function ActionsTab({ nodeId: _nodeId }: { nodeId: string }) {
  return (
    <div className='space-y-4'>
      <h2 className='text-xl font-semibold'>Actions</h2>
      <div className='space-y-2'>
        <Button
          className='hover:bg-accent w-full justify-start transition-colors'
          variant='outline'
        >
          <RefreshCw className='mr-2 h-4 w-4' />
          Re-run Tests
        </Button>
        <Button
          className='hover:bg-accent w-full justify-start transition-colors'
          variant='outline'
        >
          <Download className='mr-2 h-4 w-4' />
          Download Artifacts
        </Button>
        <Button
          className='hover:bg-accent w-full justify-start transition-colors'
          variant='outline'
        >
          <ExternalLink className='mr-2 h-4 w-4' />
          Open in Browser
        </Button>
      </div>
    </div>
  );
}
