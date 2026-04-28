import { createFileRoute } from '@tanstack/react-router';
import { BookOpen, ClipboardList, FileText, LayoutGrid, Shield } from 'lucide-react';

import { ItemSpecsOverview } from '@/components/specifications/items/ItemSpecsOverview';
import { requireAuth } from '@/lib/route-guards';
import { ADRListView } from '@/views/adr-list-view';
import { ComplianceView } from '@/views/ComplianceView';
import { ContractListView } from '@/views/ContractListView';
import { FeatureListView } from '@/views/FeatureListView';
import { SpecificationsDashboardView } from '@/views/SpecificationsDashboardView';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@tracertm/ui';

export const Route = createFileRoute('/projects/$projectId/specifications')({
  beforeLoad: async () => {
    await requireAuth();
  },
  component: SpecificationsRoute,
  validateSearch: (search: Record<string, unknown>) => ({
    tab: typeof search['tab'] === 'string' ? search['tab'] : 'overview',
  }),
});

function SpecificationsRoute() {
  const { projectId } = Route.useParams();
  const { tab } = Route.useSearch();
  const allowedTabs = new Set([
    'overview',
    'item-specs',
    'adrs',
    'contracts',
    'features',
    'compliance',
  ]);
  const currentTab = allowedTabs.has(tab) ? tab : 'overview';

  const handleTabChange = (_value: string) => {
    // Tab change handled by Tabs component via value/onValueChange
  };

  return (
    <div className='p-6'>
      <Tabs value={currentTab} onValueChange={handleTabChange} className='w-full'>
        <TabsList className='bg-muted/50 mb-6 w-full justify-start p-1'>
          <TabsTrigger value='overview' className='gap-2'>
            <LayoutGrid className='h-4 w-4' />
            Overview Dashboard
          </TabsTrigger>
          <TabsTrigger value='item-specs' className='gap-2'>
            <ClipboardList className='h-4 w-4' />
            Item Specs
          </TabsTrigger>
          <TabsTrigger value='adrs' className='gap-2'>
            <FileText className='h-4 w-4' />
            ADRs
          </TabsTrigger>
          <TabsTrigger value='contracts' className='gap-2'>
            <Shield className='h-4 w-4' />
            Contracts
          </TabsTrigger>
          <TabsTrigger value='features' className='gap-2'>
            <BookOpen className='h-4 w-4' />
            Features
          </TabsTrigger>
          <TabsTrigger value='compliance' className='gap-2'>
            <Shield className='h-4 w-4' />
            Compliance
          </TabsTrigger>
        </TabsList>

        {/* Overview Dashboard */}
        <TabsContent value='overview'>
          <SpecificationsDashboardView projectId={projectId} />
        </TabsContent>

        {/* Item Specifications */}
        <TabsContent value='item-specs'>
          <ItemSpecsOverview projectId={projectId} />
        </TabsContent>

        {/* ADRs */}
        <TabsContent value='adrs'>
          <ADRListView projectId={projectId} />
        </TabsContent>

        {/* Contracts */}
        <TabsContent value='contracts'>
          <ContractListView projectId={projectId} />
        </TabsContent>

        {/* Features */}
        <TabsContent value='features'>
          <FeatureListView projectId={projectId} />
        </TabsContent>

        {/* Compliance */}
        <TabsContent value='compliance'>
          <ComplianceView />
        </TabsContent>
      </Tabs>
    </div>
  );
}
