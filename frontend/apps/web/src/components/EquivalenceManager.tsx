import { Download, Link2, Upload } from 'lucide-react';
import { useState } from 'react';

import type { CanonicalConcept, CanonicalProjection, EquivalenceLink, Item } from '@tracertm/types';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

import { EquivalenceExport } from './graph/EquivalenceExport';
import { EquivalenceImport } from './graph/EquivalenceImport';
import { EquivalencePanel } from './graph/EquivalencePanel';

interface EquivalenceManagerProps {
  projectId: string;
}

/**
 * Equivalence Management UI
 * Provides export, import, and equivalence mapping management
 */
export function EquivalenceManager({ projectId }: EquivalenceManagerProps) {
  const [activeTab, setActiveTab] = useState<'panel' | 'export' | 'import'>('panel');

  // Mock data for equivalence components (would be loaded from API)
  const mockEquivalenceLinks: EquivalenceLink[] = [];
  const mockCanonicalConcepts: CanonicalConcept[] = [];
  const mockCanonicalProjections: CanonicalProjection[] = [];
  const mockItems: Item[] = [];
  const selectedItem: Item | null = null;

  return (
    <div className='space-y-6'>
      <div className='flex items-center justify-between'>
        <div>
          <h2 className='flex items-center gap-2 text-2xl font-bold tracking-tight'>
            <Link2 className='h-6 w-6' />
            Equivalence Management
          </h2>
          <p className='text-muted-foreground'>
            Manage concept equivalence mappings and canonical relationships
          </p>
        </div>
      </div>

      <Tabs
        value={activeTab}
        onValueChange={(tab: string) => {
          setActiveTab(tab as typeof activeTab);
        }}
        className='w-full'
      >
        <TabsList>
          <TabsTrigger value='panel' className='flex items-center gap-2'>
            <Link2 className='h-4 w-4' />
            Equivalence Map
          </TabsTrigger>
          <TabsTrigger value='export' className='flex items-center gap-2'>
            <Download className='h-4 w-4' />
            Export
          </TabsTrigger>
          <TabsTrigger value='import' className='flex items-center gap-2'>
            <Upload className='h-4 w-4' />
            Import
          </TabsTrigger>
        </TabsList>

        <TabsContent value='panel' className='space-y-4'>
          <div className='rounded-lg border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-900/20'>
            <p className='text-sm text-blue-900 dark:text-blue-100'>
              View and manage equivalence relationships between items across different perspectives.
              Mark items as representing the same concept with confidence levels.
            </p>
          </div>
          <EquivalencePanel
            selectedItem={selectedItem}
            equivalenceLinks={mockEquivalenceLinks}
            items={mockItems}
            onViewItem={(): void => {}}
          />
        </TabsContent>

        <TabsContent value='export' className='space-y-4'>
          <div className='rounded-lg border border-green-200 bg-green-50 p-4 dark:border-green-800 dark:bg-green-900/20'>
            <p className='text-sm text-green-900 dark:text-green-100'>
              Export equivalence mappings and canonical concepts to JSON or CSV format. Useful for
              sharing with other projects or archiving.
            </p>
          </div>
          <EquivalenceExport
            projectId={projectId}
            equivalenceLinks={mockEquivalenceLinks}
            canonicalConcepts={mockCanonicalConcepts}
            canonicalProjections={mockCanonicalProjections}
          />
        </TabsContent>

        <TabsContent value='import' className='space-y-4'>
          <div className='rounded-lg border border-amber-200 bg-amber-50 p-4 dark:border-amber-800 dark:bg-amber-900/20'>
            <p className='text-sm text-amber-900 dark:text-amber-100'>
              Import equivalence mappings from JSON or CSV files. Merge with existing mappings or
              overwrite based on your preferences.
            </p>
          </div>
          <EquivalenceImport
            projectId={projectId}
            existingLinks={mockEquivalenceLinks}
            existingConcepts={mockCanonicalConcepts}
            existingProjections={mockCanonicalProjections}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}
