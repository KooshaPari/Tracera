import type { Meta, StoryObj } from '@storybook/react';

import { useState } from 'react';

import { Button } from '@tracertm/ui/components/Button';

import { ErrorState } from '../ErrorState';
import { GraphSkeleton } from '../GraphSkeleton';
import { LoadingProgress } from '../LoadingProgress';
import { LoadingTransition } from '../LoadingTransition';

const meta: Meta = {
  parameters: {
    layout: 'fullscreen',
  },
  title: 'Graph/Loading States',
};

export default meta;

// GraphSkeleton Stories
export const Skeleton: StoryObj = {
  render: () => (
    <div className='h-[600px] w-full'>
      <GraphSkeleton nodeCount={20} edgeCount={30} />
    </div>
  ),
};

export const SkeletonSmall: StoryObj = {
  render: () => (
    <div className='h-[600px] w-full'>
      <GraphSkeleton nodeCount={10} edgeCount={15} />
    </div>
  ),
};

export const SkeletonLarge: StoryObj = {
  render: () => (
    <div className='h-[600px] w-full'>
      <GraphSkeleton nodeCount={30} edgeCount={50} />
    </div>
  ),
};

// ErrorState Stories
export const Error: StoryObj = {
  render: () => (
    <div className='h-[600px] w-full'>
      <ErrorState
        onRetry={() => {
          alert('Retrying...');
        }}
      />
    </div>
  ),
};

export const ErrorCustom: StoryObj = {
  render: () => (
    <div className='h-[600px] w-full'>
      <ErrorState
        title='Network Error'
        message='Unable to connect to the server. Please check your internet connection and try again.'
        onRetry={() => {
          alert('Retrying...');
        }}
      />
    </div>
  ),
};

export const ErrorNoRetry: StoryObj = {
  render: () => (
    <div className='h-[600px] w-full'>
      <ErrorState
        title='Permission Denied'
        message="You don't have permission to view this graph."
      />
    </div>
  ),
};

// LoadingTransition Stories
export const TransitionDemo: StoryObj = {
  render: () => {
    const [isLoading, setIsLoading] = useState(true);

    return (
      <div className='h-[600px] w-full space-y-4'>
        <div className='flex gap-2 p-4'>
          <Button
            onClick={() => {
              setIsLoading(true);
            }}
          >
            Show Loading
          </Button>
          <Button
            onClick={() => {
              setIsLoading(false);
            }}
          >
            Show Content
          </Button>
        </div>
        <div className='h-[500px]'>
          <LoadingTransition isLoading={isLoading}>
            <div className='bg-card flex h-full items-center justify-center rounded-lg border'>
              <div className='space-y-2 text-center'>
                <h2 className='text-2xl font-bold'>Graph Content Loaded</h2>
                <p className='text-muted-foreground'>This is the actual graph content</p>
              </div>
            </div>
          </LoadingTransition>
        </div>
      </div>
    );
  },
};

// LoadingProgress Stories
export const Progress: StoryObj = {
  render: () => {
    const [loaded, setLoaded] = useState(0);
    const total = 100;

    return (
      <div className='h-[600px] w-full p-4'>
        <div className='space-y-4'>
          <Button
            onClick={() => {
              setLoaded(0);
              const interval = setInterval(() => {
                setLoaded((prev) => {
                  if (prev >= total) {
                    clearInterval(interval);
                    return total;
                  }
                  return prev + 10;
                });
              }, 500);
            }}
          >
            Start Loading
          </Button>
          <div className='bg-card relative h-[400px] rounded-lg border'>
            <LoadingProgress loaded={loaded} total={total} />
          </div>
        </div>
      </div>
    );
  },
};

export const ProgressCustomLabel: StoryObj = {
  render: () => (
    <div className='h-[600px] w-full p-4'>
      <div className='bg-card relative h-[400px] rounded-lg border'>
        <LoadingProgress loaded={75} total={100} label='Indexing nodes' />
      </div>
    </div>
  ),
};

export const ProgressLargeNumbers: StoryObj = {
  render: () => (
    <div className='h-[600px] w-full p-4'>
      <div className='bg-card relative h-[400px] rounded-lg border'>
        <LoadingProgress loaded={1234} total={5678} label='Processing large dataset' />
      </div>
    </div>
  ),
};

// Complete Loading Flow
export const CompleteFlow: StoryObj = {
  render: () => {
    const [state, setState] = useState<'loading' | 'error' | 'content'>('loading');
    const [progress, setProgress] = useState(0);

    const startLoading = () => {
      setState('loading');
      setProgress(0);

      const interval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 100) {
            clearInterval(interval);
            // Randomly show error or content
            setState(Math.random() > 0.5 ? 'content' : 'error');
            return 100;
          }
          return prev + 20;
        });
      }, 500);
    };

    return (
      <div className='h-[600px] w-full space-y-4'>
        <div className='flex gap-2 p-4'>
          <Button onClick={startLoading}>Start Loading</Button>
          <Button
            onClick={() => {
              setState('error');
            }}
          >
            Show Error
          </Button>
          <Button
            onClick={() => {
              setState('content');
            }}
          >
            Show Content
          </Button>
        </div>
        <div className='h-[500px]'>
          {state === 'loading' && (
            <div className='relative h-full'>
              <GraphSkeleton />
              {progress > 0 && <LoadingProgress loaded={progress} total={100} />}
            </div>
          )}
          {state === 'error' && <ErrorState onRetry={startLoading} />}
          {state === 'content' && (
            <div className='bg-card flex h-full items-center justify-center rounded-lg border'>
              <div className='space-y-2 text-center'>
                <h2 className='text-2xl font-bold'>✓ Graph Loaded Successfully</h2>
                <p className='text-muted-foreground'>All nodes and edges are ready</p>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  },
};
