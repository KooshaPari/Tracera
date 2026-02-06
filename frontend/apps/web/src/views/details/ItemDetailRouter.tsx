/**
 * ItemDetailRouter
 *
 * Routes to type-specific detail views based on item type.
 * Uses type guards to determine the correct view component to render.
 */

import { AlertTriangle } from 'lucide-react';

import type { TypedItem } from '@tracertm/types';

import { ItemDetailView } from '@/views/ItemDetailView';
import {
  isDefectItem,
  isEpicItem,
  isRequirementItem,
  isTaskItem,
  isTestItem,
  isUserStoryItem,
} from '@tracertm/types';
import { Card, CardContent } from '@tracertm/ui';

import { EpicDetailView } from './EpicDetailView';
import { RequirementDetailView } from './RequirementDetailView';
import { TestDetailView } from './TestDetailView';

interface ItemDetailRouterProps {
  item: TypedItem;
  projectId: string;
}

/**
 * Routes item to the appropriate detail view based on type.
 * Falls back to generic ItemDetailView if no specific view exists.
 */
export default function ItemDetailRouter({ item, projectId }: ItemDetailRouterProps) {
  // Route to requirement view
  if (isRequirementItem(item)) {
    return <RequirementDetailView item={item} projectId={projectId} />;
  }

  // Route to test view
  if (isTestItem(item)) {
    return <TestDetailView item={item} projectId={projectId} />;
  }

  // Route to epic view
  if (isEpicItem(item)) {
    return <EpicDetailView item={item} projectId={projectId} />;
  }

  // User story, task, and defect views coming soon
  if (isUserStoryItem(item)) {
    return (
      <div className='p-6'>
        <Card className='border-blue-500/50 bg-blue-500/10'>
          <CardContent className='pt-6'>
            <div className='flex items-center gap-2 text-blue-700'>
              <AlertTriangle className='h-5 w-5' />
              <div>
                <p className='font-medium'>User Story Detail View - Coming Soon</p>
                <p className='mt-1 text-sm'>
                  Enhanced user story view with acceptance criteria and story points tracking is
                  under development.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isTaskItem(item)) {
    return (
      <div className='p-6'>
        <Card className='border-blue-500/50 bg-blue-500/10'>
          <CardContent className='pt-6'>
            <div className='flex items-center gap-2 text-blue-700'>
              <AlertTriangle className='h-5 w-5' />
              <div>
                <p className='font-medium'>Task Detail View - Coming Soon</p>
                <p className='mt-1 text-sm'>
                  Enhanced task view with checklists and time tracking is under development.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isDefectItem(item)) {
    return (
      <div className='p-6'>
        <Card className='border-blue-500/50 bg-blue-500/10'>
          <CardContent className='pt-6'>
            <div className='flex items-center gap-2 text-blue-700'>
              <AlertTriangle className='h-5 w-5' />
              <div>
                <p className='font-medium'>Defect Detail View - Coming Soon</p>
                <p className='mt-1 text-sm'>
                  Enhanced defect view with reproduction steps and severity tracking is under
                  development.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Fallback to generic item detail view for other types
  return <ItemDetailView />;
}
