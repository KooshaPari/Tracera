import {
  BarChart,
  ExternalLink,
  FileText,
  Folder,
  Layout,
  Link as LinkIcon,
  Monitor,
  Plus,
  Settings,
  Smartphone,
  Tablet,
} from 'lucide-react';
import { useState } from 'react';

interface Wireframe {
  id: string;
  name: string;
  description: string;
  screen: 'desktop' | 'tablet' | 'mobile';
  status: 'draft' | 'review' | 'approved';
  thumbnail: React.ComponentType<{ className?: string }>;
  linkedFeatures: string[];
}

const wireframes: Wireframe[] = [
  {
    description: 'Main dashboard with stats and quick actions',
    id: '1',
    linkedFeatures: ['Dashboard Feature', 'Analytics'],
    name: 'Dashboard',
    screen: 'desktop',
    status: 'approved',
    thumbnail: BarChart,
  },
  {
    description: 'Grid view of all projects',
    id: '2',
    linkedFeatures: ['Project Management'],
    name: 'Project List',
    screen: 'desktop',
    status: 'approved',
    thumbnail: Folder,
  },
  {
    description: 'Traceability visualization',
    id: '3',
    linkedFeatures: ['Graph Visualization', 'Traceability'],
    name: 'Graph View',
    screen: 'desktop',
    status: 'review',
    thumbnail: LinkIcon,
  },
  {
    description: 'Single item view with metadata',
    id: '4',
    linkedFeatures: ['Item CRUD'],
    name: 'Item Detail',
    screen: 'desktop',
    status: 'draft',
    thumbnail: FileText,
  },
  {
    description: 'Responsive dashboard for mobile',
    id: '5',
    linkedFeatures: ['Mobile Support'],
    name: 'Mobile Dashboard',
    screen: 'mobile',
    status: 'draft',
    thumbnail: Smartphone,
  },
  {
    description: 'User and project settings',
    id: '6',
    linkedFeatures: ['Settings Management'],
    name: 'Settings',
    screen: 'desktop',
    status: 'approved',
    thumbnail: Settings,
  },
];

const screenIcons = { desktop: Monitor, mobile: Smartphone, tablet: Tablet };
const statusColors = {
  approved: 'bg-green-100 text-green-600',
  draft: 'bg-gray-100 text-gray-600',
  review: 'bg-yellow-100 text-yellow-600',
};

export function WireframeView() {
  const [filter, setFilter] = useState<string | null>(null);
  const [selected, setSelected] = useState<Wireframe | null>(null);

  const filtered = filter ? wireframes.filter((w) => w.screen === filter) : wireframes;

  return (
    <div className='space-y-4'>
      <div className='flex items-center justify-between'>
        <h3 className='text-lg font-semibold'>Wireframe View</h3>
        <div className='flex items-center gap-2'>
          <div className='flex rounded-lg border p-1'>
            <button
              onClick={() => {
                setFilter(null);
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  setFilter(null);
                }
              }}
              type='button'
              className={`rounded px-2 py-1 text-sm ${!filter ? 'bg-accent' : ''}`}
            >
              All
            </button>
            <button
              onClick={() => {
                setFilter('desktop');
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  setFilter('desktop');
                }
              }}
              type='button'
              className={`rounded px-2 py-1 text-sm ${filter === 'desktop' ? 'bg-accent' : ''}`}
            >
              <Monitor className='h-4 w-4' />
            </button>
            <button
              onClick={() => {
                setFilter('tablet');
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  setFilter('tablet');
                }
              }}
              type='button'
              className={`rounded px-2 py-1 text-sm ${filter === 'tablet' ? 'bg-accent' : ''}`}
            >
              <Tablet className='h-4 w-4' />
            </button>
            <button
              onClick={() => {
                setFilter('mobile');
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  setFilter('mobile');
                }
              }}
              type='button'
              className={`rounded px-2 py-1 text-sm ${filter === 'mobile' ? 'bg-accent' : ''}`}
            >
              <Smartphone className='h-4 w-4' />
            </button>
          </div>
          <button
            className='bg-primary text-primary-foreground flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm'
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                // Add wireframe handler would go here
              }
            }}
            type='button'
          >
            <Plus className='h-4 w-4' /> Add Wireframe
          </button>
        </div>
      </div>

      <div className='flex gap-4'>
        <div className='grid flex-1 gap-4 md:grid-cols-2 lg:grid-cols-3'>
          {filtered.map((wf) => {
            const Icon = screenIcons[wf.screen];
            const ThumbnailIcon = wf.thumbnail;
            return (
              <div
                key={wf.id}
                onClick={() => {
                  setSelected(wf);
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    setSelected(wf);
                  }
                }}
                tabIndex={0}
                className={`cursor-pointer rounded-lg border p-4 transition-all hover:shadow-md ${selected?.id === wf.id ? 'ring-primary ring-2' : ''}`}
              >
                <div className='bg-muted flex aspect-video items-center justify-center rounded-lg'>
                  <ThumbnailIcon className='text-muted-foreground h-16 w-16' />
                </div>
                <div className='mt-3 flex items-center gap-2'>
                  <Icon className='text-muted-foreground h-4 w-4' />
                  <span className='font-medium'>{wf.name}</span>
                  <span
                    className={`ml-auto rounded-full px-2 py-0.5 text-xs ${statusColors[wf.status]}`}
                  >
                    {wf.status}
                  </span>
                </div>
                <p className='text-muted-foreground mt-1 text-sm'>{wf.description}</p>
              </div>
            );
          })}
        </div>

        {selected && (
          <div className='bg-card w-72 rounded-lg border p-4'>
            <div className='flex items-center justify-between'>
              <h4 className='font-semibold'>{selected.name}</h4>
              <button
                className='hover:bg-accent rounded p-1'
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    // Open external link handler would go here
                  }
                }}
                type='button'
              >
                <ExternalLink className='h-4 w-4' />
              </button>
            </div>
            <p className='text-muted-foreground mt-2 text-sm'>{selected.description}</p>
            <div className='mt-4 space-y-3 text-sm'>
              <div>
                <span className='text-muted-foreground'>Screen:</span>{' '}
                <span className='capitalize'>{selected.screen}</span>
              </div>
              <div>
                <span className='text-muted-foreground'>Status:</span>{' '}
                <span
                  className={`ml-2 rounded-full px-2 py-0.5 text-xs ${statusColors[selected.status]}`}
                >
                  {selected.status}
                </span>
              </div>
              <div>
                <span className='text-muted-foreground'>Linked Features:</span>
                <ul className='mt-1 space-y-1'>
                  {selected.linkedFeatures.map((f) => (
                    <li key={f} className='text-primary flex items-center gap-2'>
                      <Layout className='h-3 w-3' /> {f}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            <div className='mt-4 flex gap-2'>
              <button
                className='hover:bg-accent flex-1 rounded-lg border px-3 py-1.5 text-sm'
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    // Edit handler would go here
                  }
                }}
                type='button'
              >
                Edit
              </button>
              <button
                className='bg-primary text-primary-foreground flex-1 rounded-lg px-3 py-1.5 text-sm'
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    // Preview handler would go here
                  }
                }}
                type='button'
              >
                Preview
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
