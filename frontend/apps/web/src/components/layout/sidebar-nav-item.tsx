import { Link } from '@tanstack/react-router';
import React from 'react';

import { cn } from '@/lib/utils';
import * as UI from '@tracertm/ui';

import type { SidebarNavItem as SidebarItem } from './sidebar-nav';

interface NavItemProps {
  item: SidebarItem;
  isActive: boolean;
  isCollapsed: boolean;
  renderTitle: (title: string) => (string | JSX.Element)[];
}

const SPACE_KEY = ' ';

export const SidebarNavItem = React.forwardRef<HTMLAnchorElement, NavItemProps>(
  ({ item, isActive, isCollapsed, renderTitle }, ref) => {
    const Icon = item.icon;

    const handleKeyDown = React.useCallback((event: React.KeyboardEvent<HTMLAnchorElement>) => {
      if (event.key === SPACE_KEY) {
        event.preventDefault();
        event.currentTarget.click();
      }
    }, []);

    let linkClassName =
      'group flex items-center gap-2 rounded-lg px-3 py-2 transition-all duration-200 ease-out cursor-pointer relative z-10 min-w-0 w-full max-w-full overflow-hidden box-border isolate';
    linkClassName +=
      ' hover:shadow-sm hover:-translate-y-0.5 active:translate-y-0 active:scale-[0.99] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-primary';
    if (isActive) {
      linkClassName +=
        ' bg-primary text-primary-foreground border border-primary/50 ring-2 ring-primary/30 shadow-md shadow-primary/20';
    } else {
      linkClassName +=
        ' text-muted-foreground border border-transparent bg-background/10 hover:bg-background/20 hover:text-foreground';
    }

    const iconClassNameParts = ['h-5 w-5 shrink-0 transition-all duration-150'];
    if (!isActive) {
      iconClassNameParts.push('group-hover:text-primary group-hover:scale-110');
    }

    const ariaCurrent = isActive ? 'page' : undefined;
    const ariaLabel = isCollapsed ? item.title : undefined;

    const linkContent = (
      <Link
        ref={ref}
        to={item.href as never}
        onKeyDown={handleKeyDown}
        className={linkClassName}
        aria-current={ariaCurrent}
        aria-label={ariaLabel}
      >
        <Icon className={cn(...iconClassNameParts)} />
        {isCollapsed ? undefined : (
          <>
            <span className='min-w-0 flex-1 truncate overflow-hidden text-sm font-bold tracking-tight'>
              {renderTitle(item.title)}
            </span>
            {typeof item.badge === 'number' ? (
              <UI.Badge
                variant='secondary'
                className='flex h-5 min-w-[1.25rem] shrink-0 items-center justify-center px-1.5 text-[10px] font-bold'
              >
                {item.badge}
              </UI.Badge>
            ) : undefined}
            {isActive ? (
              <div className='bg-primary-foreground absolute top-1/2 left-0 h-6 w-1 -translate-y-1/2 animate-pulse rounded-r-full' />
            ) : undefined}
          </>
        )}
      </Link>
    );

    if (isCollapsed) {
      return (
        <UI.Tooltip>
          <UI.TooltipTrigger asChild>{linkContent}</UI.TooltipTrigger>
          <UI.TooltipContent>
            <p>{item.title}</p>
          </UI.TooltipContent>
        </UI.Tooltip>
      );
    }

    return linkContent;
  },
);

SidebarNavItem.displayName = 'SidebarNavItem';
