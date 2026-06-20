import type { FC } from 'react';

import { Filter, Search, Shield } from 'lucide-react';
import { useCallback, useMemo } from 'react';

import type { Contract, ContractStatus } from '@tracertm/types';

import {
  Card,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui';

interface ContractFiltersBarProps {
  readonly searchQuery: string;
  readonly setSearchQuery: (query: string) => void;
  readonly statusFilter: ContractStatus | 'all';
  readonly setStatusFilter: (filter: ContractStatus | 'all') => void;
  readonly typeFilter: string;
  readonly setTypeFilter: (filter: string) => void;
  readonly contracts: readonly Contract[];
}

export const ContractFiltersBar: FC<ContractFiltersBarProps> = ({
  searchQuery,
  setSearchQuery,
  statusFilter,
  setStatusFilter,
  typeFilter,
  setTypeFilter,
  contracts,
}) => {
  const statusCounts = useMemo(
    () => ({
      active: contracts.filter((c) => c.status === 'active').length,
      all: contracts.length,
      deprecated: contracts.filter((c) => c.status === 'deprecated').length,
      draft: contracts.filter((c) => c.status === 'draft').length,
      verified: contracts.filter((c) => c.status === 'verified').length,
      violated: contracts.filter((c) => c.status === 'violated').length,
    }),
    [contracts],
  );

  const typeCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const contract of contracts) {
      const type = contract.contractType;
      counts[type] = (counts[type] ?? 0) + 1;
    }
    return counts;
  }, [contracts]);

  const handleSearchChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      setSearchQuery(event.target.value);
    },
    [setSearchQuery],
  );

  const handleStatusChange = useCallback(
    (value: string) => {
      setStatusFilter(value as ContractStatus | 'all');
    },
    [setStatusFilter],
  );

  const handleTypeChange = useCallback(
    (value: string) => {
      setTypeFilter(value);
    },
    [setTypeFilter],
  );

  return (
    <Card className='bg-muted/30 flex flex-wrap items-center gap-3 rounded-2xl border-none p-3'>
      <div className='relative min-w-[250px] flex-1'>
        <Search className='text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2' />
        <Input
          placeholder='Search by title, number, or description...'
          className='h-10 border-none bg-transparent pl-10 focus-visible:ring-0'
          value={searchQuery}
          onChange={handleSearchChange}
        />
      </div>

      <div className='bg-border/50 hidden h-6 w-px md:block' />

      <Select value={statusFilter} onValueChange={handleStatusChange}>
        <SelectTrigger className='hover:bg-background/50 h-10 w-[140px] border-none bg-transparent'>
          <div className='flex items-center gap-2'>
            <Filter className='text-muted-foreground h-3.5 w-3.5' />
            <SelectValue placeholder='Status' />
          </div>
        </SelectTrigger>
        <SelectContent>
          <SelectItem value='all'>All ({statusCounts.all})</SelectItem>
          <SelectItem value='draft'>Draft ({statusCounts.draft})</SelectItem>
          <SelectItem value='active'>Active ({statusCounts.active})</SelectItem>
          <SelectItem value='verified'>Verified ({statusCounts.verified})</SelectItem>
          <SelectItem value='violated'>Violated ({statusCounts.violated})</SelectItem>
          <SelectItem value='deprecated'>Deprecated ({statusCounts.deprecated})</SelectItem>
        </SelectContent>
      </Select>

      <Select value={typeFilter} onValueChange={handleTypeChange}>
        <SelectTrigger className='hover:bg-background/50 h-10 w-[140px] border-none bg-transparent'>
          <div className='flex items-center gap-2'>
            <Shield className='text-muted-foreground h-3.5 w-3.5' />
            <SelectValue placeholder='Type' />
          </div>
        </SelectTrigger>
        <SelectContent>
          <SelectItem value='all'>All Types ({contracts.length})</SelectItem>
          <SelectItem value='api'>API ({typeCounts['api'] ?? 0})</SelectItem>
          <SelectItem value='function'>Function ({typeCounts['function'] ?? 0})</SelectItem>
          <SelectItem value='invariant'>Invariant ({typeCounts['invariant'] ?? 0})</SelectItem>
          <SelectItem value='data'>Data ({typeCounts['data'] ?? 0})</SelectItem>
          <SelectItem value='integration'>
            Integration ({typeCounts['integration'] ?? 0})
          </SelectItem>
        </SelectContent>
      </Select>
    </Card>
  );
};
