import { Link } from '@tanstack/react-router';
import { FolderOpen, MoreVertical, Plus, Search } from 'lucide-react';

const projects = [
  {
    description: 'Desktop App + Website',
    id: '1',
    items: 44,
    links: 5,
    name: 'TraceRTM Frontend',
    status: 'active',
  },
  {
    description: 'Sample project demonstration',
    id: '2',
    items: 28,
    links: 12,
    name: 'Pokemon Go Demo',
    status: 'active',
  },
  {
    description: 'Full-stack e-commerce',
    id: '3',
    items: 156,
    links: 234,
    name: 'E-Commerce Platform',
    status: 'active',
  },
  {
    description: 'React Native banking',
    id: '4',
    items: 89,
    links: 145,
    name: 'Mobile Banking App',
    status: 'archived',
  },
];

export function ProjectList() {
  return (
    <div className='space-y-6'>
      {/* Header */}
      <div className='flex items-center justify-between'>
        <div>
          <h2 className='text-2xl font-bold'>Projects</h2>
          <p className='text-muted-foreground'>Manage your TraceRTM projects</p>
        </div>
        <button className='bg-primary text-primary-foreground hover:bg-primary/90 flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium'>
          <Plus className='h-4 w-4' />
          New Project
        </button>
      </div>

      {/* Search & Filter */}
      <div className='flex gap-4'>
        <div className='relative flex-1'>
          <Search className='text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2' />
          <input
            type='text'
            placeholder='Search projects...'
            className='bg-background focus:ring-primary h-10 w-full rounded-lg border pr-4 pl-9 text-sm focus:ring-2 focus:outline-none'
          />
        </div>
        <select className='bg-background h-10 rounded-lg border px-4 text-sm'>
          <option>All Status</option>
          <option>Active</option>
          <option>Archived</option>
        </select>
      </div>

      {/* Project Grid */}
      <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
        {projects.map((project) => (
          <Link
            key={project.id}
            to={`/projects/${project.id}`}
            className='group bg-card rounded-xl border p-6 shadow-sm transition-all hover:shadow-md'
          >
            <div className='flex items-start justify-between'>
              <div className='bg-primary/10 flex h-12 w-12 items-center justify-center rounded-lg'>
                <FolderOpen className='text-primary h-6 w-6' />
              </div>
              <button
                onClick={(e) => {
                  e.preventDefault();
                  // Handle menu
                }}
                className='hover:bg-accent rounded-lg p-1 opacity-0 group-hover:opacity-100'
              >
                <MoreVertical className='text-muted-foreground h-4 w-4' />
              </button>
            </div>
            <div className='mt-4'>
              <h3 className='font-semibold'>{project.name}</h3>
              <p className='text-muted-foreground mt-1 text-sm'>{project.description}</p>
            </div>
            <div className='text-muted-foreground mt-4 flex items-center gap-4 text-sm'>
              <span>{project.items} items</span>
              <span>·</span>
              <span>{project.links} links</span>
            </div>
            <div className='mt-4'>
              <span
                className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                  project.status === 'active'
                    ? 'bg-green-500/10 text-green-500'
                    : 'bg-gray-500/10 text-gray-500'
                }`}
              >
                {project.status}
              </span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
