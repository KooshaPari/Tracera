import { Link } from '@tanstack/react-router';
import { ArrowRight, Box, Command, Layers, Search as SearchIcon } from 'lucide-react';
import { useState } from 'react';

import type { Item } from '@tracertm/types';

import { Button, Separator } from '@tracertm/ui';
import { Badge } from '@tracertm/ui/components/Badge';
import { Card } from '@tracertm/ui/components/Card';
import { Input } from '@tracertm/ui/components/Input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui/components/Select';
import { Skeleton } from '@tracertm/ui/components/Skeleton';

import { useSearch } from '../hooks/useSearch';

export function SearchView() {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState({
    project: '',
    status: '',
    type: '',
  });

  const { results, isLoading } = useSearch({ q: query, ...filters });

  return (
    <div className='animate-in-fade-up mx-auto max-w-5xl space-y-8 p-6'>
      {/* Header */}
      <div className='mb-12 flex flex-col items-center space-y-4 text-center'>
        <div className='bg-primary/10 flex h-16 w-16 items-center justify-center rounded-[2rem] shadow-inner'>
          <Command className='text-primary h-8 w-8 animate-pulse' />
        </div>
        <div>
          <h1 className='text-3xl font-black tracking-tight uppercase'>Omni-Search</h1>
          <p className='text-muted-foreground mx-auto max-w-lg font-medium'>
            Search the entire graph repository for nodes, projects, and metadata links.
          </p>
        </div>
      </div>

      {/* Search Control Bar */}
      <div className='group relative mx-auto max-w-3xl'>
        <div className='bg-primary/20 absolute inset-0 opacity-0 blur-2xl transition-all group-focus-within:opacity-100 group-focus-within:blur-3xl' />
        <Card className='bg-card ring-border relative flex flex-col items-center gap-2 overflow-hidden rounded-[2.5rem] border-none p-2 shadow-2xl ring-1 md:flex-row'>
          <div className='relative w-full flex-1'>
            <SearchIcon className='text-muted-foreground group-focus-within:text-primary absolute top-1/2 left-6 h-5 w-5 -translate-y-1/2 transition-colors' />
            <Input
              type='search'
              placeholder='Type anything to search...'
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
              }}
              className='h-14 border-none bg-transparent pl-14 text-lg font-medium focus-visible:ring-0'
            />
          </div>
          <div className='flex w-full items-center gap-2 px-2 md:w-auto'>
            <Separator orientation='vertical' className='hidden h-8 md:block' />
            <Select
              value={filters.type || 'all'}
              onValueChange={(v) => {
                setFilters({ ...filters, type: v === 'all' ? '' : v });
              }}
            >
              <SelectTrigger className='bg-muted/50 h-10 rounded-2xl border-none md:w-32'>
                <SelectValue placeholder='All Types' />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value='all'>Any Type</SelectItem>
                <SelectItem value='requirement'>Requirement</SelectItem>
                <SelectItem value='feature'>Feature</SelectItem>
                <SelectItem value='test'>Test Case</SelectItem>
              </SelectContent>
            </Select>
            <Button className='shadow-primary/20 h-10 rounded-2xl px-6 text-[10px] font-black tracking-widest uppercase shadow-lg'>
              Query
            </Button>
          </div>
        </Card>
      </div>

      {/* Results Surface */}
      <div className='space-y-6'>
        {isLoading ? (
          <div className='space-y-4'>
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className='h-32 w-full rounded-[2rem]' />
            ))}
          </div>
        ) : results?.items && results.items.length > 0 ? (
          <div className='animate-in slide-in-from-bottom-4 space-y-4 duration-500'>
            <div className='flex items-center justify-between px-2'>
              <h2 className='text-muted-foreground flex items-center gap-2 text-xs font-black tracking-[0.2em] uppercase'>
                <Layers className='h-3 w-3' /> Search Results
              </h2>
              <Badge variant='secondary' className='rounded-full font-bold'>
                {results.items.length} nodes matched
              </Badge>
            </div>

            <div className='stagger-children grid grid-cols-1 gap-4'>
              {results.items.map((item) => {
                const raw = item as Item & {
                  item_view?: string;
                  project_id?: string;
                  view_type?: string;
                };
                const projectId = item.projectId ?? raw.project_id;
                const viewTypeCandidate1 = item.view ?? raw.view_type;
                const viewTypeCandidate2 = viewTypeCandidate1 ?? raw.item_view;
                const viewType = viewTypeCandidate2 ?? 'feature';

                const targetPath = projectId
                  ? `/projects/${projectId}/views/${String(viewType).toLowerCase()}/${item.id}`
                  : '/projects';

                return (
                  <Link key={item.id} to={targetPath}>
                    <Card className='bg-card/50 hover:bg-card group rounded-[2rem] border-none p-6 shadow-sm transition-all duration-200 ease-out hover:shadow-xl active:scale-[0.99]'>
                      <div className='flex flex-col gap-6 md:flex-row md:items-center'>
                        <div className='bg-muted group-hover:bg-primary/10 flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl transition-colors'>
                          <Box className='text-muted-foreground group-hover:text-primary h-6 w-6 transition-colors' />
                        </div>
                        <div className='flex-1 space-y-1'>
                          <div className='flex flex-wrap items-center gap-2'>
                            <h3 className='group-hover:text-primary text-lg leading-none font-bold transition-colors'>
                              {item.title}
                            </h3>
                            <Badge
                              variant='outline'
                              className='border-primary/20 text-primary h-4 text-[8px] font-black tracking-tighter uppercase'
                            >
                              {item.type}
                            </Badge>
                          </div>
                          <p className='text-muted-foreground line-clamp-1 text-sm font-medium'>
                            {item.description ?? 'No registry description provided for this node.'}
                          </p>
                        </div>
                        <div className='flex shrink-0 items-center gap-6'>
                          <div className='hidden text-right sm:block'>
                            <p className='text-muted-foreground text-[9px] font-black tracking-widest uppercase'>
                              Status
                            </p>
                            <div className='mt-0.5 flex items-center justify-end gap-1'>
                              <div className='h-1.5 w-1.5 rounded-full bg-green-500' />
                              <span className='text-[10px] font-bold uppercase'>{item.status}</span>
                            </div>
                          </div>
                          <div className='border-border flex h-10 w-10 -translate-x-4 items-center justify-center rounded-full border opacity-0 transition-all group-hover:translate-x-0 group-hover:opacity-100'>
                            <ArrowRight className='text-primary h-4 w-4' />
                          </div>
                        </div>
                      </div>
                    </Card>
                  </Link>
                );
              })}
            </div>
          </div>
        ) : query ? (
          <div className='flex flex-col items-center justify-center py-32 text-center'>
            <div className='bg-muted mb-6 flex h-20 w-20 items-center justify-center rounded-full'>
              <SearchIcon className='h-10 w-10 opacity-10' />
            </div>
            <h3 className='text-muted-foreground text-sm font-black tracking-[0.2em] uppercase'>
              Zero matches in registry
            </h3>
            <p className='text-muted-foreground/60 mt-2 text-xs font-medium'>
              Adjust your query or check filters for specific projects.
            </p>
          </div>
        ) : (
          <div className='text-muted-foreground/20 flex flex-col items-center justify-center py-32'>
            <Command className='mb-4 h-24 w-24 opacity-5' />
            <p className='text-[10px] font-black tracking-[0.3em] uppercase'>
              Awaiting Input Sequence
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
