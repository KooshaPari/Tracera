import { Link } from '@tanstack/react-router';
import { Check, ChevronDown, ChevronRight, Copy, Globe, Play } from 'lucide-react';
import { useState } from 'react';

import type { TypedItem } from '@tracertm/types';

import { useItems } from '@/hooks/useItems';
import { Skeleton } from '@tracertm/ui/components/Skeleton';

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

interface ApiViewProps {
  projectId: string;
}

interface Endpoint {
  id: string;
  method: HttpMethod;
  path: string;
  description: string;
  status: 'implemented' | 'planned' | 'deprecated';
  requestBody?: string;
  responseExample?: string;
}

interface ApiGroup {
  id: string;
  name: string;
  baseUrl: string;
  endpoints: Endpoint[];
}

const apiGroups: ApiGroup[] = [
  {
    baseUrl: '/api/v1/projects',
    endpoints: [
      {
        description: 'List all projects',
        id: '1.1',
        method: 'GET',
        path: '/',
        responseExample: '[{"id": "uuid", "name": "Project"}]',
        status: 'implemented',
      },
      {
        description: 'Create a project',
        id: '1.2',
        method: 'POST',
        path: '/',
        requestBody: '{"name": "string"}',
        status: 'implemented',
      },
      {
        description: 'Get project by ID',
        id: '1.3',
        method: 'GET',
        path: '/{id}',
        status: 'implemented',
      },
      {
        description: 'Update project',
        id: '1.4',
        method: 'PATCH',
        path: '/{id}',
        status: 'implemented',
      },
      {
        description: 'Delete project',
        id: '1.5',
        method: 'DELETE',
        path: '/{id}',
        status: 'planned',
      },
    ],
    id: '1',
    name: 'Projects',
  },
  {
    baseUrl: '/api/v1/items',
    endpoints: [
      {
        description: 'List items with filters',
        id: '2.1',
        method: 'GET',
        path: '/',
        status: 'implemented',
      },
      {
        description: 'Create an item',
        id: '2.2',
        method: 'POST',
        path: '/',
        status: 'implemented',
      },
      {
        description: 'Get item by ID',
        id: '2.3',
        method: 'GET',
        path: '/{id}',
        status: 'implemented',
      },
      {
        description: 'Update item',
        id: '2.4',
        method: 'PATCH',
        path: '/{id}',
        status: 'implemented',
      },
      {
        description: 'Get item version history',
        id: '2.5',
        method: 'GET',
        path: '/{id}/history',
        status: 'planned',
      },
    ],
    id: '2',
    name: 'Items',
  },
  {
    baseUrl: '/api/v1/links',
    endpoints: [
      {
        description: 'List all links',
        id: '3.1',
        method: 'GET',
        path: '/',
        status: 'implemented',
      },
      {
        description: 'Create a link',
        id: '3.2',
        method: 'POST',
        path: '/',
        status: 'implemented',
      },
      {
        description: 'Delete a link',
        id: '3.3',
        method: 'DELETE',
        path: '/{id}',
        status: 'implemented',
      },
      {
        description: 'Get full traceability graph',
        id: '3.4',
        method: 'GET',
        path: '/graph',
        status: 'planned',
      },
    ],
    id: '3',
    name: 'Links',
  },
];

const methodColors: Record<HttpMethod, string> = {
  DELETE: 'bg-red-100 text-red-700',
  GET: 'bg-green-100 text-green-700',
  PATCH: 'bg-orange-100 text-orange-700',
  POST: 'bg-blue-100 text-blue-700',
  PUT: 'bg-yellow-100 text-yellow-700',
};

const statusBadge: Record<string, string> = {
  deprecated: 'bg-red-500',
  implemented: 'bg-green-500',
  planned: 'bg-yellow-500',
};

export const ApiView = ({ projectId }: ApiViewProps) => {
  const [expanded, setExpanded] = useState<Set<string>>(new Set(['1']));
  const [copied, setCopied] = useState<string | null>(null);

  const { data: projectData, isLoading: projectLoading } = useItems({
    projectId,
    view: 'api',
  });
  const projectItems = projectData?.items ?? [];

  const toggle = (id: string) => {
    const next = new Set(expanded);
    if (next.has(id)) {
      next.delete(id);
    } else {
      next.add(id);
    }
    setExpanded(next);
  };

  const copyPath = async (endpoint: Endpoint, group: ApiGroup) => {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(group.baseUrl + endpoint.path);
    }
    setCopied(endpoint.id);
    setTimeout(() => {
      setCopied(null);
    }, 2000);
  };

  return (
    <div className='flex-1 space-y-6 p-6'>
      <div>
        <h1 className='text-3xl font-bold tracking-tight'>API Endpoints</h1>
        <p className='text-muted-foreground'>
          REST API contracts and specifications for this project
        </p>
      </div>

      {projectLoading ? (
        <div className='space-y-2'>
          <Skeleton className='h-10 w-full rounded-lg' />
          <Skeleton className='h-10 w-full rounded-lg' />
          <Skeleton className='h-10 w-full rounded-lg' />
        </div>
      ) : projectItems.length > 0 ? (
        <div className='space-y-2'>
          <h2 className='text-lg font-semibold'>Project API items</h2>
          <div className='rounded-lg border'>
            {projectItems.map((item: TypedItem) => {
              const method = (item.metadata as { method?: string })?.method ?? 'GET';
              const path = item.title ?? item.id;
              return (
                <Link
                  key={item.id}
                  to='/projects/$projectId/views/$viewType/$itemId'
                  params={{
                    itemId: item.id,
                    projectId,
                    viewType: 'api',
                  }}
                  className='hover:bg-muted/50 flex items-center gap-3 border-b p-3 last:border-b-0'
                >
                  <span
                    className={`rounded px-2 py-0.5 font-mono text-xs font-bold ${methodColors[method as HttpMethod] ?? methodColors.GET}`}
                  >
                    {method}
                  </span>
                  <code className='text-sm'>{path}</code>
                  <span className='text-muted-foreground flex-1 truncate text-sm'>
                    {item.description ?? item.type}
                  </span>
                </Link>
              );
            })}
          </div>
        </div>
      ) : null}

      <div className='space-y-2'>
        <h2 className='text-lg font-semibold'>Reference</h2>
        <div className='rounded-lg border'>
          {apiGroups.map((group) => (
            <div key={group.id} className='border-b last:border-b-0'>
              <div
                className='hover:bg-accent/50 flex cursor-pointer items-center gap-3 p-4'
                onClick={() => {
                  toggle(group.id);
                }}
              >
                {expanded.has(group.id) ? (
                  <ChevronDown className='h-4 w-4' />
                ) : (
                  <ChevronRight className='h-4 w-4' />
                )}
                <Globe className='h-5 w-5 text-blue-500' />
                <span className='font-medium'>{group.name}</span>
                <code className='text-muted-foreground ml-2 text-xs'>{group.baseUrl}</code>
                <span className='text-muted-foreground ml-auto text-xs'>
                  {group.endpoints.length} endpoints
                </span>
              </div>
              {expanded.has(group.id) && (
                <div className='bg-muted/20 border-t'>
                  {group.endpoints.map((endpoint) => (
                    <div
                      key={endpoint.id}
                      className='flex items-center gap-3 border-b p-3 pl-12 last:border-b-0'
                    >
                      <span
                        className={`rounded px-2 py-0.5 font-mono text-xs font-bold ${methodColors[endpoint.method]}`}
                      >
                        {endpoint.method}
                      </span>
                      <code className='text-sm'>{endpoint.path}</code>
                      <span className='text-muted-foreground flex-1 text-sm'>
                        {endpoint.description}
                      </span>
                      <span
                        className={`h-2 w-2 rounded-full ${statusBadge[endpoint.status]}`}
                        title={endpoint.status}
                      />
                      <button
                        onClick={async () => copyPath(endpoint, group)}
                        className='hover:bg-accent rounded p-1'
                      >
                        {copied === endpoint.id ? (
                          <Check className='h-4 w-4 text-green-500' />
                        ) : (
                          <Copy className='h-4 w-4' />
                        )}
                      </button>
                      <button className='hover:bg-accent rounded p-1' title='Try it'>
                        <Play className='h-4 w-4' />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
