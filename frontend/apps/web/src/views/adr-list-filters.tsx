import { Calendar, Filter, Search } from 'lucide-react';

import type { ADRStatus } from '@tracertm/types';

import {
  Card,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui';

interface StatusCounts {
  all: number;
  proposed: number;
  accepted: number;
  deprecated: number;
  superseded: number;
  rejected: number;
}

interface ADRListFiltersProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  statusFilter: ADRStatus | 'all';
  onStatusChange: (status: ADRStatus | 'all') => void;
  dateRange: 'all' | 'week' | 'month' | 'quarter';
  onDateRangeChange: (range: 'all' | 'week' | 'month' | 'quarter') => void;
  statusCounts: StatusCounts;
}

export function ADRListFilters({
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusChange,
  dateRange,
  onDateRangeChange,
  statusCounts,
}: ADRListFiltersProps): React.JSX.Element {
  return (
    <Card className='bg-muted/30 flex flex-wrap items-center gap-3 rounded-2xl border-none p-3'>
      <div className='relative min-w-[250px] flex-1'>
        <Search className='text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2' />
        <Input
          placeholder='Search by title, number, or context...'
          className='h-10 border-none bg-transparent pl-10 focus-visible:ring-0'
          value={searchQuery}
          onChange={(event) => {
            onSearchChange(event.target.value);
          }}
        />
      </div>

      <div className='bg-border/50 hidden h-6 w-px md:block' />

      <Select
        value={statusFilter}
        onValueChange={(value) => {
          onStatusChange(value as ADRStatus | 'all');
        }}
      >
        <SelectTrigger className='hover:bg-background/50 h-10 w-[160px] border-none bg-transparent'>
          <div className='flex items-center gap-2'>
            <Filter className='text-muted-foreground h-3.5 w-3.5' />
            <SelectValue placeholder='Status' />
          </div>
        </SelectTrigger>
        <SelectContent>
          <SelectItem value='all'>All Statuses ({statusCounts.all})</SelectItem>
          <SelectItem value='proposed'>Proposed ({statusCounts.proposed})</SelectItem>
          <SelectItem value='accepted'>Accepted ({statusCounts.accepted})</SelectItem>
          <SelectItem value='deprecated'>Deprecated ({statusCounts.deprecated})</SelectItem>
          <SelectItem value='superseded'>Superseded ({statusCounts.superseded})</SelectItem>
          <SelectItem value='rejected'>Rejected ({statusCounts.rejected})</SelectItem>
        </SelectContent>
      </Select>

      <Select
        value={dateRange}
        onValueChange={(value) => {
          onDateRangeChange(value as typeof dateRange);
        }}
      >
        <SelectTrigger className='hover:bg-background/50 h-10 w-[140px] border-none bg-transparent'>
          <div className='flex items-center gap-2'>
            <Calendar className='text-muted-foreground h-3.5 w-3.5' />
            <SelectValue placeholder='Date' />
          </div>
        </SelectTrigger>
        <SelectContent>
          <SelectItem value='all'>Any Time</SelectItem>
          <SelectItem value='week'>This Week</SelectItem>
          <SelectItem value='month'>This Month</SelectItem>
          <SelectItem value='quarter'>This Quarter</SelectItem>
        </SelectContent>
      </Select>
    </Card>
  );
}
