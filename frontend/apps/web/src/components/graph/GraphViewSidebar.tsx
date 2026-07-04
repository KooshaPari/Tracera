import { Link as RouterLink } from '@tanstack/react-router';
import { ChevronLeft, ChevronRight, Layers } from 'lucide-react';

import { cn } from '@tracertm/ui';
import { Button } from '@tracertm/ui/components/Button';
import { ScrollArea } from '@tracertm/ui/components/ScrollArea';

import { PROJECT_VIEW_NAV } from './GraphViewNavConfig';

interface GraphViewSidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  projectId?: string | undefined;
  itemsCount: number;
  linksCount: number;
}

const GraphViewSidebar = ({
  collapsed,
  onToggle,
  projectId,
  itemsCount,
  linksCount,
}: GraphViewSidebarProps): JSX.Element => {
  let sidebarWidthClass = 'w-48 sm:w-52 md:w-56';
  if (collapsed) {
    sidebarWidthClass = 'w-12 sm:w-14';
  }

  let toggleIcon = <ChevronLeft className='h-4 w-4' />;
  if (collapsed) {
    toggleIcon = <ChevronRight className='h-4 w-4' />;
  }

  return (
    <div
      className={cn(
        'border-r bg-muted/30 transition-all duration-300 flex flex-col shrink-0',
        sidebarWidthClass,
      )}
    >
      {/* Sidebar header */}
      <div className='flex min-w-0 items-center justify-between border-b p-2 sm:p-3'>
        {!collapsed && (
          <div className='flex min-w-0 items-center gap-1.5'>
            <Layers className='text-primary h-4 w-4 shrink-0 sm:h-[1.1rem]' />
            <span className='truncate text-xs font-semibold sm:text-sm'>Views</span>
          </div>
        )}
        <Button variant='ghost' size='sm' className='h-8 w-8 p-0' onClick={onToggle}>
          {toggleIcon}
        </Button>
      </div>

      {/* Sidebar content: project views (Feature, API, Test, Graph, etc.) */}
      <ScrollArea className='flex-1'>
        <div className='space-y-1 p-2'>
          {!collapsed && (
            <div className='text-muted-foreground truncate px-2 py-1.5 text-[10px] font-medium tracking-wide uppercase sm:text-[11px]'>
              Project views
            </div>
          )}
          {PROJECT_VIEW_NAV.map((nav) => {
            const isActive = nav.viewType === 'graph';
            const Icon = nav.icon;
            let title: string | undefined;
            if (collapsed) {
              title = nav.label;
            }

            if (!projectId) {
              return (
                <div
                  key={nav.viewType}
                  className={cn(
                    'flex items-center gap-2 sm:gap-3 h-9 sm:h-10 px-2 sm:px-3 rounded-md min-w-0 w-full opacity-60',
                    collapsed && 'justify-center px-2',
                  )}
                  title={title}
                >
                  <Icon className='h-3.5 w-3.5 shrink-0 sm:h-4 sm:w-4' />
                  {!collapsed && (
                    <span className='min-w-0 flex-1 truncate text-left text-xs sm:text-sm'>
                      {nav.label}
                    </span>
                  )}
                </div>
              );
            }

            return (
              <RouterLink
                key={nav.viewType}
                to='/projects/$projectId/views/$viewType'
                params={{ projectId, viewType: nav.viewType }}
                className={cn(
                  'flex items-center gap-2 sm:gap-3 h-9 sm:h-10 px-2 sm:px-3 rounded-md transition-all min-w-0 w-full',
                  collapsed && 'justify-center px-2',
                  isActive && 'bg-primary/10 text-primary hover:bg-primary/15',
                  !isActive && 'hover:bg-muted/50',
                )}
                title={title}
              >
                <Icon
                  className={cn('h-3.5 w-3.5 sm:h-4 sm:w-4 shrink-0', isActive && 'text-primary')}
                />
                {!collapsed && (
                  <span className='min-w-0 flex-1 truncate text-left text-xs sm:text-sm'>
                    {nav.label}
                  </span>
                )}
              </RouterLink>
            );
          })}
        </div>
      </ScrollArea>

      {/* Sidebar footer */}
      {!collapsed && (
        <div className='min-w-0 border-t p-2 sm:p-3'>
          <div className='text-muted-foreground truncate text-[10px] sm:text-[11px]'>
            {itemsCount} items · {linksCount} links
          </div>
        </div>
      )}
    </div>
  );
};

export { GraphViewSidebar };
