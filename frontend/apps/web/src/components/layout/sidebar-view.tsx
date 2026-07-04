import { Link } from '@tanstack/react-router';
import * as Icons from 'lucide-react';
import React from 'react';

import { cn } from '@/lib/utils';
import * as Ui from '@tracertm/ui';

import type { SidebarGroup, SidebarNavItem, SortOption, FilterOption } from './sidebar-nav';

import { SidebarNavItem as SidebarNavItemRow } from './sidebar-nav-item';

interface RecentProject {
  id: string;
  name: string;
}

interface SidebarViewProps {
  activeTab: Record<string, string>;
  collapsedGroups: Record<string, boolean>;
  currentProjectId?: string | number | undefined;
  filteredNavGroups: SidebarGroup[];
  isCollapsed: boolean;
  isResizing: boolean;
  navItemRefSetter: (element: HTMLAnchorElement | null) => void;
  onActiveTabChange: (groupLabel: string, value: string) => void;
  onCollapseToggle: () => void;
  onFilterChange: (value: FilterOption) => void;
  onGroupToggle: (label: string, isOpen: boolean) => void;
  onProjectAction: (action: 'pin' | 'remove' | 'newtab', projectId: string) => void;
  onResizeStart: (event: React.MouseEvent) => void;
  onSearchChange: (value: string) => void;
  onSearchClear: () => void;
  onSortChange: (value: SortOption) => void;
  onTabValue: (groupLabel: string, fallback: string) => string;
  recentFilter: FilterOption;
  recentProjects: RecentProject[];
  recentSort: SortOption;
  renderTitle: (title: string) => (string | JSX.Element)[];
  searchInputRef: React.Ref<HTMLInputElement>;
  searchQuery: string;
  sidebarWidth: number;
}

const RECENT_BADGE_MAX = '20+';
const RESIZE_HANDLE_STYLE: React.CSSProperties = { cursor: 'ew-resize' };

export const SidebarView = ({
  activeTab: _activeTab,
  collapsedGroups,
  currentProjectId,
  filteredNavGroups,
  isCollapsed,
  isResizing,
  navItemRefSetter,
  onActiveTabChange,
  onCollapseToggle,
  onFilterChange,
  onGroupToggle,
  onProjectAction,
  onResizeStart,
  onSearchChange,
  onSearchClear,
  onSortChange,
  onTabValue,
  recentFilter,
  recentProjects,
  recentSort,
  renderTitle,
  searchInputRef,
  searchQuery,
  sidebarWidth,
}: SidebarViewProps): JSX.Element => {
  const showSearch = !isCollapsed;
  const showRecent = !isCollapsed && recentProjects.length > 0;
  const showNoResults =
    searchQuery.length > 0 && filteredNavGroups.length === 0 && recentProjects.length === 0;

  const navStyle = React.useMemo<React.CSSProperties | undefined>(
    () =>
      !isCollapsed
        ? {
            maxWidth: `min(${sidebarWidth}px, 90vw)`,
            minWidth: `${sidebarWidth}px`,
            transition: isResizing ? 'none' : undefined,
            width: `${sidebarWidth}px`,
          }
        : undefined,
    [isCollapsed, isResizing, sidebarWidth],
  );

  const handleSearchInputChange = React.useCallback(
    (event: React.ChangeEvent<HTMLInputElement>): void => {
      onSearchChange(event.target.value);
    },
    [onSearchChange],
  );
  const handleOpenRecentInNewTab = React.useCallback(
    (projectId: string): void => {
      onProjectAction('newtab', projectId);
    },
    [onProjectAction],
  );
  const handleRemoveRecent = React.useCallback(
    (projectId: string): void => {
      onProjectAction('remove', projectId);
    },
    [onProjectAction],
  );

  const navClassName = cn(
    'geist-sidebar relative flex h-full max-h-screen flex-col shrink-0 overflow-x-auto overflow-y-auto box-border',
    isResizing ? 'transition-none' : 'transition-all duration-300 ease-in-out',
    isCollapsed ? 'w-20 min-w-[5rem] max-w-[5rem]' : undefined,
  );

  return (
    <Ui.TooltipProvider delayDuration={200}>
      <div className='relative flex h-full max-h-screen min-w-0 shrink-0 flex-col overflow-visible'>
        <nav className={navClassName} style={navStyle} aria-label='Main navigation'>
          <div className='flex h-16 min-w-0 shrink-0 items-center justify-center border-b px-4'>
            <div className='flex min-w-0 flex-1 items-center justify-center gap-3'>
              <div className='bg-primary border-primary/30 shadow-primary/20 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl border shadow-md transition-all duration-200 ease-out hover:-translate-y-0.5 hover:scale-105 hover:shadow-lg active:translate-y-0 active:scale-100'>
                <Icons.GitBranch className='text-primary-foreground h-5 w-5' />
              </div>
              {isCollapsed ? undefined : (
                <span className='animate-in fade-in slide-in-from-left-2 text-center text-lg font-black tracking-tighter uppercase'>
                  Trace<span className='text-primary'>RTM</span>
                </span>
              )}
            </div>
          </div>

          {showSearch ? (
            <div className='min-w-0 shrink-0 border-b px-4 py-3'>
              <div className='relative min-w-0'>
                <Icons.Search className='text-muted-foreground pointer-events-none absolute top-1/2 left-3 z-10 h-4 w-4 shrink-0 -translate-y-1/2' />
                <Ui.Input
                  ref={searchInputRef}
                  type='text'
                  placeholder='Search navigation...'
                  value={searchQuery}
                  onChange={handleSearchInputChange}
                  className='bg-background/10 focus-visible:ring-primary focus-visible:border-primary/30 h-9 w-full min-w-0 rounded-lg border border-transparent pr-9 pl-9 text-sm transition-all duration-200 ease-out focus-visible:ring-2 focus-visible:ring-inset'
                  aria-label='Search navigation items'
                  aria-describedby='search-hint'
                  tabIndex={-1}
                />
                <span id='search-hint' className='sr-only'>
                  Use arrow keys to navigate results, Escape to clear
                </span>
                {searchQuery.length > 0 ? (
                  <Ui.Button
                    variant='ghost'
                    size='icon'
                    className='bg-background/10 hover:bg-background/20 absolute top-1/2 right-1 h-7 w-7 -translate-y-1/2 rounded-md border border-transparent transition-all duration-200 ease-out'
                    onClick={onSearchClear}
                    tabIndex={-1}
                  >
                    <Icons.X className='h-3 w-3' />
                  </Ui.Button>
                ) : undefined}
              </div>
            </div>
          ) : undefined}

          <div className='flex min-h-0 w-full max-w-full min-w-0 flex-1 flex-col overflow-x-auto overflow-y-hidden px-4 py-4'>
            <Ui.ScrollArea className='h-full min-h-0 w-full min-w-0 overflow-auto [&>[data-radix-scroll-area-viewport]]:box-border [&>[data-radix-scroll-area-viewport]]:w-full [&>[data-radix-scroll-area-viewport]]:max-w-full [&>[data-radix-scroll-area-viewport]]:min-w-0 [&>[data-radix-scroll-area-viewport]]:overflow-x-auto [&>[data-radix-scroll-area-viewport]]:overflow-y-auto'>
              <div className='w-full max-w-full min-w-0 space-y-4'>
                {filteredNavGroups.map((group) => {
                  const isGroupCollapsed = collapsedGroups[group.label] ?? false;
                  const groupKey = group.key;
                  const handleGroupOpenChange = (open: boolean): void => {
                    onGroupToggle(group.label, open);
                  };

                  if (groupKey === 'active-registry' && !isCollapsed) {
                    const overviewItem = group.items[0];
                    const viewsItems = group.items.slice(1, -1);
                    const settingsItem = group.items.at(-1);
                    const handleRegistryTabChange = (value: string): void => {
                      onActiveTabChange(group.label, value);
                    };

                    return (
                      <Ui.Collapsible
                        key={group.label}
                        open={!isGroupCollapsed}
                        onOpenChange={handleGroupOpenChange}
                        className='w-full max-w-full min-w-0 space-y-1 overflow-hidden'
                      >
                        <Ui.CollapsibleTrigger className='bg-background/10 hover:bg-background/20 box-border w-full max-w-full min-w-0 rounded-lg border border-transparent px-3 py-1.5 text-center transition-all duration-200 ease-out hover:no-underline hover:shadow-sm'>
                          <h3 className='text-muted-foreground/60 min-w-0 truncate text-center text-[10px] font-black tracking-[0.2em] uppercase'>
                            {group.label}
                          </h3>
                        </Ui.CollapsibleTrigger>
                        <Ui.CollapsibleContent className='isolate w-full max-w-full min-w-0 overflow-hidden pt-1'>
                          <Ui.Tabs
                            value={onTabValue(group.label, 'overview')}
                            onValueChange={handleRegistryTabChange}
                            className='w-full max-w-full min-w-0'
                          >
                            <Ui.TabsList className='bg-background/10 mb-1.5 box-border grid h-auto w-full max-w-full min-w-0 shrink-0 grid-cols-3 gap-0.5 rounded-lg border border-transparent p-1'>
                              <Ui.TabsTrigger
                                value='overview'
                                className='data-[state=inactive]:hover:bg-background/20 data-[state=active]:border-primary/40 data-[state=active]:ring-primary/20 data-[state=active]:bg-primary/10 min-w-0 truncate rounded-md border border-transparent bg-transparent px-2 py-1 text-center text-[10px] transition-all duration-200 ease-out data-[state=active]:border data-[state=active]:ring-2'
                              >
                                Overview
                              </Ui.TabsTrigger>
                              <Ui.TabsTrigger
                                value='views'
                                className='data-[state=inactive]:hover:bg-background/20 data-[state=active]:border-primary/40 data-[state=active]:ring-primary/20 data-[state=active]:bg-primary/10 min-w-0 truncate rounded-md border border-transparent bg-transparent px-2 py-1 text-center text-[10px] transition-all duration-200 ease-out data-[state=active]:border data-[state=active]:ring-2'
                              >
                                Views
                              </Ui.TabsTrigger>
                              <Ui.TabsTrigger
                                value='settings'
                                className='data-[state=inactive]:hover:bg-background/20 data-[state=active]:border-primary/40 data-[state=active]:ring-primary/20 data-[state=active]:bg-primary/10 min-w-0 truncate rounded-md border border-transparent bg-transparent px-2 py-1 text-center text-[10px] transition-all duration-200 ease-out data-[state=active]:border data-[state=active]:ring-2'
                              >
                                Settings
                              </Ui.TabsTrigger>
                            </Ui.TabsList>
                            <Ui.TabsContent
                              value='overview'
                              className='isolate mt-0 max-h-[280px] w-full max-w-full min-w-0 space-y-1 overflow-x-hidden overflow-y-auto'
                            >
                              {overviewItem ? (
                                <SidebarNavItemRow
                                  ref={navItemRefSetter}
                                  item={overviewItem}
                                  isActive={onTabValue(group.label, 'overview') === 'overview'}
                                  isCollapsed={false}
                                  renderTitle={renderTitle}
                                />
                              ) : undefined}
                            </Ui.TabsContent>
                            <Ui.TabsContent
                              value='views'
                              className='isolate mt-0 max-h-[280px] w-full max-w-full min-w-0 space-y-1 overflow-x-hidden overflow-y-auto'
                            >
                              {viewsItems.map((item: SidebarNavItem) => (
                                <SidebarNavItemRow
                                  key={item.href}
                                  ref={navItemRefSetter}
                                  item={item}
                                  isActive={onTabValue(group.label, 'overview') === item.title}
                                  isCollapsed={false}
                                  renderTitle={renderTitle}
                                />
                              ))}
                            </Ui.TabsContent>
                            <Ui.TabsContent
                              value='settings'
                              className='isolate mt-0 max-h-[280px] w-full max-w-full min-w-0 space-y-1 overflow-x-hidden overflow-y-auto'
                            >
                              {settingsItem ? (
                                <SidebarNavItemRow
                                  ref={navItemRefSetter}
                                  item={settingsItem}
                                  isActive={onTabValue(group.label, 'overview') === 'settings'}
                                  isCollapsed={false}
                                  renderTitle={renderTitle}
                                />
                              ) : undefined}
                            </Ui.TabsContent>
                          </Ui.Tabs>
                        </Ui.CollapsibleContent>
                      </Ui.Collapsible>
                    );
                  }

                  if (groupKey === 'specifications' && !isCollapsed) {
                    const handleSpecificationsTabChange = (value: string): void => {
                      onActiveTabChange(group.label, value);
                    };

                    return (
                      <Ui.Collapsible
                        key={group.label}
                        open={!isGroupCollapsed}
                        onOpenChange={handleGroupOpenChange}
                        className='w-full max-w-full min-w-0 space-y-1 overflow-hidden'
                      >
                        <Ui.CollapsibleTrigger className='bg-background/10 hover:bg-background/20 w-full min-w-0 rounded-lg border border-transparent px-3 py-1.5 text-center transition-all duration-200 ease-out hover:no-underline hover:shadow-sm'>
                          <h3 className='text-muted-foreground/60 min-w-0 truncate text-center text-[10px] font-black tracking-[0.2em] uppercase'>
                            {group.label}
                          </h3>
                        </Ui.CollapsibleTrigger>
                        <Ui.CollapsibleContent className='isolate w-full max-w-full min-w-0 overflow-hidden pt-1'>
                          <Ui.Tabs
                            value={onTabValue(group.label, 'dashboard')}
                            onValueChange={handleSpecificationsTabChange}
                            className='w-full min-w-0'
                          >
                            <Ui.TabsList className='bg-background/10 mb-1.5 grid h-auto w-full max-w-full min-w-0 shrink-0 grid-cols-2 gap-0.5 rounded-lg border border-transparent p-1'>
                              <Ui.TabsTrigger
                                value='dashboard'
                                className='data-[state=inactive]:hover:bg-background/20 data-[state=active]:border-primary/40 data-[state=active]:ring-primary/20 data-[state=active]:bg-primary/10 min-w-0 truncate rounded-md border border-transparent bg-transparent px-2 py-1 text-center text-[10px] transition-all duration-200 ease-out data-[state=active]:border data-[state=active]:ring-2'
                              >
                                Dashboard
                              </Ui.TabsTrigger>
                              <Ui.TabsTrigger
                                value='specs'
                                className='data-[state=inactive]:hover:bg-background/20 data-[state=active]:border-primary/40 data-[state=active]:ring-primary/20 data-[state=active]:bg-primary/10 min-w-0 truncate rounded-md border border-transparent bg-transparent px-2 py-1 text-center text-[10px] transition-all duration-200 ease-out data-[state=active]:border data-[state=active]:ring-2'
                              >
                                Specs
                              </Ui.TabsTrigger>
                            </Ui.TabsList>
                            <Ui.TabsContent
                              value='dashboard'
                              className='isolate mt-0 max-h-[280px] w-full max-w-full min-w-0 space-y-1 overflow-x-hidden overflow-y-auto'
                            >
                              {group.items[0] ? (
                                <SidebarNavItemRow
                                  item={group.items[0]}
                                  isActive={false}
                                  isCollapsed={false}
                                  renderTitle={renderTitle}
                                />
                              ) : undefined}
                            </Ui.TabsContent>
                            <Ui.TabsContent
                              value='specs'
                              className='isolate mt-0 max-h-[280px] w-full max-w-full min-w-0 space-y-1 overflow-x-hidden overflow-y-auto'
                            >
                              {group.items.slice(1).map((item) => (
                                <SidebarNavItemRow
                                  key={item.href}
                                  item={item}
                                  isActive={false}
                                  isCollapsed={false}
                                  renderTitle={renderTitle}
                                />
                              ))}
                            </Ui.TabsContent>
                          </Ui.Tabs>
                        </Ui.CollapsibleContent>
                      </Ui.Collapsible>
                    );
                  }

                  if (group.collapsible && !isCollapsed) {
                    if (groupKey === 'all-views' && 'categories' in group) {
                      return (
                        <Ui.Collapsible
                          key={group.label}
                          open={!isGroupCollapsed}
                          onOpenChange={handleGroupOpenChange}
                          className='w-full max-w-full min-w-0 space-y-1 overflow-hidden'
                        >
                          <Ui.CollapsibleTrigger
                            className='group/trigger bg-background/10 hover:bg-background/20 box-border flex w-full max-w-full min-w-0 items-center justify-center rounded-lg border border-transparent px-3 py-1.5 text-center transition-all duration-200 ease-out hover:no-underline hover:shadow-sm'
                            aria-label={`Toggle ${group.label} section`}
                          >
                            <div className='flex max-w-full min-w-0 flex-1 items-center justify-center gap-2 overflow-hidden'>
                              <Icons.LayoutGrid className='text-muted-foreground/70 h-4 w-4 shrink-0' />
                              <h3 className='text-muted-foreground/60 min-w-0 truncate text-center text-[10px] font-black tracking-[0.2em] uppercase'>
                                {group.label}
                              </h3>
                              {isGroupCollapsed ? (
                                <Ui.Badge
                                  variant='secondary'
                                  className='h-4 shrink-0 px-1.5 text-[9px]'
                                >
                                  {RECENT_BADGE_MAX}
                                </Ui.Badge>
                              ) : undefined}
                            </div>
                          </Ui.CollapsibleTrigger>
                          <Ui.CollapsibleContent className='isolate max-h-[500px] w-full max-w-full min-w-0 space-y-2 overflow-x-hidden overflow-y-auto pt-1'>
                            {group.categories.map((category, categoryIndex) => {
                              const CategoryIcon = category.icon;

                              return (
                                <div
                                  key={`${category.name}-${categoryIndex}`}
                                  className='w-full max-w-full min-w-0 space-y-1 overflow-hidden'
                                >
                                  <div className='bg-background/10 flex max-w-full min-w-0 items-center justify-center gap-2 overflow-hidden rounded-md border border-transparent px-3 py-1'>
                                    <CategoryIcon className='text-primary/60 h-3 w-3 shrink-0' />
                                    <h4 className='text-muted-foreground/70 min-w-0 truncate text-center text-[9px] font-bold tracking-widest uppercase'>
                                      {category.name}
                                    </h4>
                                  </div>
                                  <div className='w-full max-w-full min-w-0 space-y-0.5 overflow-hidden pl-0'>
                                    {category.views.map((view) => {
                                      const ViewIcon = view.icon;

                                      return (
                                        <Ui.Tooltip key={view.href}>
                                          <Ui.TooltipTrigger asChild>
                                            <Link
                                              to={view.href as never}
                                              className={cn(
                                                'group flex items-center gap-2 rounded-lg px-3 py-1.5 border transition-all duration-200 ease-out cursor-pointer relative min-w-0 w-full max-w-full text-xs overflow-hidden box-border',
                                                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-primary',
                                                'hover:shadow-sm hover:-translate-y-0.5 active:translate-y-0 active:scale-[0.99]',
                                                'text-muted-foreground border border-transparent bg-background/10 hover:bg-background/20 hover:text-foreground',
                                              )}
                                              aria-current='page'
                                            >
                                              <ViewIcon className='h-4 w-4 shrink-0' />
                                              <span className='min-w-0 flex-1 truncate overflow-hidden font-medium'>
                                                {view.title}
                                              </span>
                                            </Link>
                                          </Ui.TooltipTrigger>
                                          <Ui.TooltipContent side='right'>
                                            <p className='text-xs'>{view.description}</p>
                                          </Ui.TooltipContent>
                                        </Ui.Tooltip>
                                      );
                                    })}
                                  </div>
                                </div>
                              );
                            })}
                          </Ui.CollapsibleContent>
                        </Ui.Collapsible>
                      );
                    }

                    return (
                      <Ui.Collapsible
                        key={group.label}
                        open={!isGroupCollapsed}
                        onOpenChange={handleGroupOpenChange}
                        className='w-full min-w-0 space-y-1'
                      >
                        <Ui.CollapsibleTrigger
                          className='group/trigger bg-background/10 hover:bg-background/20 flex w-full min-w-0 items-center justify-center rounded-lg border border-transparent px-3 py-1.5 text-center transition-all duration-200 ease-out hover:no-underline hover:shadow-sm'
                          aria-label={`Toggle ${group.label} section`}
                        >
                          <div className='flex max-w-full min-w-0 flex-1 items-center justify-center gap-2 overflow-hidden'>
                            <h3 className='text-muted-foreground/60 min-w-0 truncate text-center text-[10px] font-black tracking-[0.2em] uppercase'>
                              {group.label}
                            </h3>
                            {isGroupCollapsed ? (
                              <Ui.Badge
                                variant='secondary'
                                className='h-4 shrink-0 px-1.5 text-[9px]'
                              >
                                {group.items.length}
                              </Ui.Badge>
                            ) : undefined}
                          </div>
                        </Ui.CollapsibleTrigger>
                        <Ui.CollapsibleContent className='isolate max-h-[360px] w-full max-w-full min-w-0 space-y-1 overflow-x-hidden overflow-y-auto pt-1'>
                          {group.items.map((item: SidebarNavItem) => (
                            <SidebarNavItemRow
                              key={item.href}
                              ref={navItemRefSetter}
                              item={item}
                              isActive={false}
                              isCollapsed={false}
                              renderTitle={renderTitle}
                            />
                          ))}
                        </Ui.CollapsibleContent>
                      </Ui.Collapsible>
                    );
                  }

                  return (
                    <div
                      key={group.label}
                      className='w-full max-w-full min-w-0 space-y-1 overflow-hidden'
                    >
                      {isCollapsed ? undefined : (
                        <h3 className='text-muted-foreground/60 bg-background/10 min-w-0 truncate rounded-lg border border-transparent px-3 py-1.5 text-center text-[10px] font-black tracking-[0.2em] uppercase'>
                          {group.label}
                        </h3>
                      )}
                      <div className='w-full min-w-0 space-y-0.5' role='list'>
                        {group.items.map((item: SidebarNavItem) => (
                          <SidebarNavItemRow
                            key={item.href}
                            ref={navItemRefSetter}
                            item={item}
                            isActive={false}
                            isCollapsed={isCollapsed}
                            renderTitle={renderTitle}
                          />
                        ))}
                      </div>
                    </div>
                  );
                })}

                {showRecent ? (
                  <div className='w-full min-w-0 space-y-1'>
                    <div className='bg-background/10 flex w-full max-w-full min-w-0 items-center justify-center gap-2 overflow-hidden rounded-lg border border-transparent px-3 py-1.5'>
                      <h3 className='text-muted-foreground/60 min-w-0 flex-1 truncate text-center text-[10px] font-black tracking-[0.2em] uppercase'>
                        Recent
                      </h3>
                      <div className='flex shrink-0 items-center gap-1'>
                        <Ui.Select value={recentSort} onValueChange={onSortChange}>
                          <Ui.SelectTrigger className='bg-background/10 hover:bg-background/20 h-6 w-6 rounded-md border border-transparent p-0 transition-all duration-200 ease-out'>
                            <Icons.ArrowUpDown className='h-3 w-3' />
                          </Ui.SelectTrigger>
                          <Ui.SelectContent>
                            <Ui.SelectItem value='recent'>Recently Viewed</Ui.SelectItem>
                            <Ui.SelectItem value='alphabetical'>Alphabetical</Ui.SelectItem>
                            <Ui.SelectItem value='modified'>Last Modified</Ui.SelectItem>
                          </Ui.SelectContent>
                        </Ui.Select>
                        <Ui.Select value={recentFilter} onValueChange={onFilterChange}>
                          <Ui.SelectTrigger className='bg-background/10 hover:bg-background/20 h-6 w-6 rounded-md border border-transparent p-0 transition-all duration-200 ease-out'>
                            <Icons.Filter className='h-3 w-3' />
                          </Ui.SelectTrigger>
                          <Ui.SelectContent>
                            <Ui.SelectItem value='all'>All Projects</Ui.SelectItem>
                            <Ui.SelectItem value='active'>Active Only</Ui.SelectItem>
                            <Ui.SelectItem value='archived'>Archived</Ui.SelectItem>
                          </Ui.SelectContent>
                        </Ui.Select>
                      </div>
                    </div>
                    <div className='max-h-[260px] w-full max-w-full min-w-0 space-y-0.5 overflow-x-hidden overflow-y-auto'>
                      {recentProjects.map((project) => {
                        const handleNewTabClick = (): void => {
                          handleOpenRecentInNewTab(project.id);
                        };
                        const handleRemoveClick = (): void => {
                          handleRemoveRecent(project.id);
                        };

                        return (
                          <Ui.Tooltip key={project.id}>
                            <Ui.TooltipTrigger asChild>
                              <div className='group relative flex w-full min-w-0 items-center overflow-hidden'>
                                <Link
                                  to={`/projects/${project.id}` as never}
                                  className='bg-background/10 text-muted-foreground hover:bg-background/20 hover:text-foreground group/item flex max-w-full min-w-0 flex-1 cursor-pointer items-center gap-2 overflow-hidden rounded-lg border border-transparent px-3 py-1.5 transition-all duration-200 ease-out hover:-translate-y-0.5 hover:shadow-sm active:translate-y-0 active:scale-[0.99]'
                                >
                                  <div className='bg-primary/40 group-hover/item:bg-primary h-2 w-2 shrink-0 rounded-full transition-colors' />
                                  <span className='min-w-0 flex-1 truncate text-xs font-bold'>
                                    {renderTitle(project.name)}
                                  </span>
                                </Link>
                                <Ui.DropdownMenu>
                                  <Ui.DropdownMenuTrigger asChild>
                                    <span>
                                      <Ui.Button
                                        variant='ghost'
                                        size='icon'
                                        className='h-6 w-6 shrink-0 opacity-0 transition-opacity group-hover:opacity-100'
                                      >
                                        <Icons.MoreVertical className='h-3 w-3' />
                                      </Ui.Button>
                                    </span>
                                  </Ui.DropdownMenuTrigger>
                                  <Ui.DropdownMenuContent align='end'>
                                    <Ui.DropdownMenuItem onClick={handleNewTabClick}>
                                      <Icons.ExternalLink className='mr-2 h-4 w-4' />
                                      Open in new tab
                                    </Ui.DropdownMenuItem>
                                    <Ui.DropdownMenuItem onClick={handleRemoveClick}>
                                      <Icons.X className='mr-2 h-4 w-4' />
                                      Remove from recent
                                    </Ui.DropdownMenuItem>
                                  </Ui.DropdownMenuContent>
                                </Ui.DropdownMenu>
                              </div>
                            </Ui.TooltipTrigger>
                            <Ui.TooltipContent>
                              <p>{project.name}</p>
                            </Ui.TooltipContent>
                          </Ui.Tooltip>
                        );
                      })}
                    </div>
                  </div>
                ) : undefined}

                {showNoResults ? (
                  <div
                    className='flex flex-col items-center justify-center py-8 text-center'
                    role='status'
                    aria-live='polite'
                  >
                    <Icons.Search
                      className='text-muted-foreground/50 mb-2 h-8 w-8'
                      aria-hidden='true'
                    />
                    <p className='text-muted-foreground text-sm'>No results found</p>
                    <p className='text-muted-foreground/70 mt-1 text-xs'>
                      Try a different search term
                    </p>
                  </div>
                ) : undefined}
              </div>
            </Ui.ScrollArea>
          </div>

          <div className='bg-muted/20 min-w-0 shrink-0 border-t px-4 py-3'>
            {isCollapsed || currentProjectId === undefined ? undefined : (
              <div className='bg-background/20 hover:bg-background/30 mb-3 min-w-0 overflow-hidden rounded-xl border border-transparent p-2.5 shadow-sm transition-all duration-200 ease-out hover:-translate-y-0.5 hover:shadow-md active:translate-y-0'>
                <div className='text-muted-foreground mb-2 flex min-w-0 items-center justify-center text-[9px] font-black tracking-widest uppercase'>
                  <span className='text-center'>Integrity 84%</span>
                </div>
                <Ui.Progress value={84} className='h-1 w-full min-w-0' />
              </div>
            )}

            <div className='flex items-center justify-center'>
              <Ui.Button
                variant='ghost'
                size='icon'
                onClick={onCollapseToggle}
                className='bg-background/10 hover:bg-primary/15 hover:text-primary focus-visible:ring-primary focus-visible:border-primary/40 h-10 w-10 shrink-0 rounded-xl border border-transparent transition-all duration-200 ease-out hover:-translate-y-0.5 hover:shadow-md focus-visible:ring-2 focus-visible:ring-inset active:translate-y-0 active:scale-[0.98]'
                aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                aria-expanded={!isCollapsed}
              >
                {isCollapsed ? (
                  <Icons.ChevronRight className='h-5 w-5 transition-transform' />
                ) : (
                  <Icons.ChevronLeft className='h-5 w-5 transition-transform' />
                )}
              </Ui.Button>
            </div>
          </div>
        </nav>

        {isCollapsed ? undefined : (
          <div
            onMouseDown={onResizeStart}
            className={cn(
              'absolute right-0 top-0 h-full w-2 cursor-ew-resize bg-transparent hover:bg-primary/30 transition-all flex items-center justify-center group z-10',
              'active:cursor-ew-resize',
              isResizing ? 'bg-primary/50 cursor-ew-resize' : undefined,
            )}
            role='separator'
            aria-label='Resize sidebar'
            aria-orientation='vertical'
            style={RESIZE_HANDLE_STYLE}
          >
            <div className='bg-muted-foreground/10 group-hover:bg-primary/40 h-full w-0.5 rounded-full transition-all' />
            <div className='bg-primary/0 group-hover:bg-primary/60 absolute top-1/2 left-1/2 h-8 w-1 -translate-x-1/2 -translate-y-1/2 rounded-full opacity-0 transition-all group-hover:opacity-100' />
          </div>
        )}
      </div>
    </Ui.TooltipProvider>
  );
};
