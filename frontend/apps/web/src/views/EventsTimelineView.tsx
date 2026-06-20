import { useNavigate } from '@tanstack/react-router';
import {
  ArrowRight,
  Calendar,
  Clock,
  Edit,
  ExternalLink,
  Folder,
  GitCommit,
  History,
  Link2,
  Plus,
  Search,
  User,
  Zap,
} from 'lucide-react';
import { useCallback, useMemo, useState } from 'react';

import { cn } from '@/lib/utils';
import {
  Button,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui';
import { Badge } from '@tracertm/ui/components/Badge';
import { Card } from '@tracertm/ui/components/Card';
import { Input } from '@tracertm/ui/components/Input';

interface Event {
  id: string;
  type: 'item_created' | 'item_updated' | 'link_created' | 'project_created';
  title: string;
  description: string;
  timestamp: Date;
  user: string;
  projectId?: string;
  itemId?: string;
  commitHash?: string;
}

const eventConfigs = {
  item_created: { color: 'bg-green-500', icon: Plus, text: 'Created node' },
  item_updated: { color: 'bg-blue-500', icon: Edit, text: 'Modified node' },
  link_created: { color: 'bg-purple-500', icon: Link2, text: 'Mapped link' },
  project_created: {
    color: 'bg-orange-500',
    icon: Folder,
    text: 'Initialized project',
  },
};

export function EventsTimelineView() {
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const navigate = useNavigate();

  // Mock events - replace with actual API call (stable reference for hook deps)
  const events = useMemo<Event[]>(
    () => [
      {
        commitHash: 'a1b2c3d',
        description: 'New security requirement initialized in Project Alpha.',
        id: '1',
        itemId: 'req-auth-001',
        projectId: 'alpha-1',
        timestamp: new Date(),
        title: 'User Authentication',
        type: 'item_created',
        user: 'Admin',
      },
      {
        commitHash: 'e4f5g6h',
        description: "Connected 'Auth Logic' to 'Security Spec v1'.",
        id: '2',
        itemId: 'link-001',
        projectId: 'alpha-1',
        timestamp: new Date(Date.now() - 3_600_000),
        title: 'Traceability Link',
        type: 'link_created',
        user: 'Jane Doe',
      },
      {
        commitHash: 'i7j8k9l',
        description: "Field 'user_id' updated to UUID for higher integrity.",
        id: '3',
        itemId: 'schema-db-001',
        projectId: 'beta-2',
        timestamp: new Date(Date.now() - 86_400_000),
        title: 'Database Schema',
        type: 'item_updated',
        user: 'System',
      },
    ],
    [],
  );

  const handleEventClick = useCallback(
    (event: Event) => {
      if (event.itemId) {
        void navigate({ to: '/items/$itemId', params: { itemId: event.itemId } });
      }
    },
    [navigate],
  );

  const filteredEvents = useMemo(
    () =>
      events.filter((e) => {
        const matchesQuery =
          e.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          e.description.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesType = typeFilter === 'all' || e.type === typeFilter;
        return matchesQuery && matchesType;
      }),
    [events, searchQuery, typeFilter],
  );

  return (
    <div className='animate-in fade-in mx-auto max-w-4xl space-y-8 p-6 duration-500'>
      {/* Header */}
      <div className='flex flex-col justify-between gap-4 text-center md:flex-row md:items-center md:text-left'>
        <div>
          <h1 className='text-2xl font-black tracking-tight uppercase'>Audit Timeline</h1>
          <p className='text-muted-foreground text-sm font-medium'>
            Immutable record of system activity and entity transitions.
          </p>
        </div>
        <Button
          variant='outline'
          size='sm'
          className='gap-2 rounded-xl text-[10px] font-bold tracking-widest uppercase'
        >
          <History className='h-3 w-3' /> Export Logs
        </Button>
      </div>

      {/* Filters Bar */}
      <Card className='bg-muted/30 flex flex-wrap items-center gap-2 rounded-2xl border-none p-2'>
        <div className='relative min-w-[200px] flex-1'>
          <Search className='text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2' />
          <Input
            placeholder='Search audit trail...'
            className='h-10 border-none bg-transparent pl-10 focus-visible:ring-0'
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
            }}
          />
        </div>
        <div className='bg-border/50 mx-2 hidden h-6 w-px md:block' />
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className='hover:bg-background/50 h-10 w-[160px] border-none bg-transparent transition-colors'>
            <SelectValue placeholder='Event Type' />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value='all'>All Events</SelectItem>
            {Object.keys(eventConfigs).map((t) => (
              <SelectItem key={t} value={t} className='capitalize'>
                {t.replace('_', ' ')}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </Card>

      {/* Timeline Content */}
      <div className='before:bg-border/50 relative space-y-8 before:absolute before:top-2 before:bottom-2 before:left-[19px] before:w-px'>
        {filteredEvents.length > 0 ? (
          filteredEvents.map((event) => {
            const config = eventConfigs[event.type];
            return (
              <div
                key={event.id}
                className='group relative pl-12'
                role='button'
                tabIndex={0}
                onClick={() => {
                  handleEventClick(event);
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') handleEventClick(event);
                }}
              >
                {/* Timeline Node */}
                <div
                  className={cn(
                    'absolute left-0 top-1.5 h-10 w-10 rounded-2xl flex items-center justify-center shadow-lg transition-transform group-hover:scale-110',
                    config.color,
                    'shadow-current/20',
                  )}
                >
                  <config.icon className='h-5 w-5 text-white' />
                </div>

                <Card className='bg-card/50 group-hover:bg-card hover:border-primary/20 cursor-pointer border-none p-6 shadow-sm transition-all group-hover:shadow-md'>
                  <div className='flex flex-col justify-between gap-4 md:flex-row md:items-start'>
                    <div className='flex-1 space-y-2'>
                      <div className='flex flex-wrap items-center gap-2'>
                        <h3 className='text-sm font-black tracking-tight'>{event.title}</h3>
                        <Badge
                          variant='secondary'
                          className='h-4 text-[8px] font-black tracking-tighter uppercase'
                        >
                          {config.text}
                        </Badge>
                        {event.projectId && (
                          <span className='text-primary bg-primary/5 rounded px-1.5 py-0.5 text-[9px] font-bold uppercase'>
                            {event.projectId}
                          </span>
                        )}
                        {event.commitHash && (
                          <span className='text-muted-foreground bg-muted/40 flex items-center gap-1 rounded px-1.5 py-0.5 font-mono text-[9px] font-bold'>
                            <GitCommit className='h-2.5 w-2.5' />
                            {event.commitHash}
                          </span>
                        )}
                      </div>
                      <p className='text-muted-foreground text-sm leading-relaxed font-medium'>
                        {event.description}
                      </p>
                    </div>
                    <div className='shrink-0 text-right'>
                      <div className='text-muted-foreground mb-1 flex items-center justify-end gap-1.5 text-[10px] font-black uppercase'>
                        <Clock className='h-3 w-3' />
                        {new Date(event.timestamp).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </div>
                      <div className='text-muted-foreground/60 flex items-center justify-end gap-1.5 text-[10px] font-bold'>
                        <User className='h-2.5 w-2.5' />
                        {event.user}
                      </div>
                    </div>
                  </div>

                  <div className='mt-4 flex items-center justify-between border-t border-dashed pt-4'>
                    <div className='flex items-center gap-4'>
                      <div className='flex items-center gap-1'>
                        <Calendar className='text-muted-foreground h-3 w-3' />
                        <span className='text-muted-foreground text-[9px] font-bold uppercase'>
                          {new Date(event.timestamp).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                    <Button
                      variant='ghost'
                      size='xs'
                      className='group/btn gap-1 text-[9px] font-black uppercase'
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEventClick(event);
                      }}
                    >
                      View Context{' '}
                      <ExternalLink className='h-2.5 w-2.5 opacity-60 transition-opacity group-hover/btn:opacity-100' />
                      <ArrowRight className='h-2.5 w-2.5 transition-transform group-hover/btn:translate-x-1' />
                    </Button>
                  </div>
                </Card>
              </div>
            );
          })
        ) : (
          <div className='text-muted-foreground/30 flex flex-col items-center justify-center py-32'>
            <Zap className='mb-4 h-16 w-16 opacity-10' />
            <p className='text-xs font-black tracking-[0.2em] uppercase'>End of Audit Trail</p>
          </div>
        )}
      </div>
    </div>
  );
}
