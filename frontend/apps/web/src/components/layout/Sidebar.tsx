import { useParams } from '@tanstack/react-router';
import React, { memo, useState } from 'react';

import { useProjects } from '@/hooks/useProjects';
import { useProjectStore } from '@/stores/project-store';

import {
  useProjectActionHandler,
  useSidebarHandlers,
  useSidebarKeyboardNavigation,
  useSidebarPreferences,
  useSidebarRefs,
  useSidebarViewData,
  useSidebarWidth,
} from './sidebar-hooks';
import { SidebarView } from './sidebar-view';

const NO_INDEX = -1;
const HIGHLIGHT_KEY_SLICE = 8;

const highlightText = (text: string, query: string): (string | JSX.Element)[] => {
  const trimmedQuery = query.trim();
  if (!trimmedQuery) {
    return [text];
  }
  const queryLower = trimmedQuery.toLowerCase();
  const parts = text.split(new RegExp(`(${trimmedQuery})`, 'gi'));
  return parts.map((part, index) => {
    if (part.toLowerCase() === queryLower) {
      return (
        <mark
          key={`${index}-${part.slice(0, HIGHLIGHT_KEY_SLICE)}`}
          className='bg-primary/20 text-primary rounded px-0.5 font-medium'
        >
          {part}
        </mark>
      );
    }
    return part;
  });
};

const SidebarComponent = function SidebarComponent(): JSX.Element {
  const [searchQuery, setSearchQuery] = useState('');
  const [, setFocusedIndex] = useState<number>(NO_INDEX);
  const { currentProject, recentProjects } = useProjectStore();
  const { data: allProjects } = useProjects();
  const { projectId } = useParams({ strict: false });
  const isTestEnv = Boolean(globalThis.navigator?.webdriver);

  const {
    activeTab,
    collapsedGroups,
    isCollapsed,
    recentFilter,
    recentSort,
    setActiveTab,
    setCollapsedGroups,
    setIsCollapsed,
    setRecentFilter,
    setRecentSort,
  } = useSidebarPreferences();
  const { handleResizeStart, isResizing, sidebarWidth } = useSidebarWidth();
  const { handleSearchInputRef, navItemsRef, resetNavItemRefs, searchInputRef, setNavItemRef } =
    useSidebarRefs();

  useSidebarKeyboardNavigation({
    isCollapsed,
    navItemsRef,
    searchInputRef,
    setFocusedIndex,
    setSearchQuery,
  });

  const { filteredNavGroups, sortedRecentProjects } = useSidebarViewData({
    allProjects,
    currentProjectId: currentProject?.id,
    isTestEnv,
    projectId,
    recentProjects,
    recentSort,
    searchQuery,
  });

  resetNavItemRefs();

  const handleProjectAction = useProjectActionHandler(recentProjects);

  const {
    getActiveTabValue,
    handleActiveTabChange,
    handleCollapseToggle,
    handleGroupToggle,
    handleRecentFilterChange,
    handleRecentSortChange,
    handleSearchChange,
    handleSearchClear,
    renderHighlightedTitle,
  } = useSidebarHandlers({
    activeTab,
    highlightText,
    searchQuery,
    setActiveTab,
    setCollapsedGroups,
    setFocusedIndex,
    setIsCollapsed,
    setRecentFilter,
    setRecentSort,
    setSearchQuery,
  });

  return (
    <SidebarView
      activeTab={activeTab}
      collapsedGroups={collapsedGroups}
      currentProjectId={currentProject?.id}
      filteredNavGroups={filteredNavGroups}
      isCollapsed={isCollapsed}
      isResizing={isResizing}
      navItemRefSetter={setNavItemRef}
      onActiveTabChange={handleActiveTabChange}
      onCollapseToggle={handleCollapseToggle}
      onFilterChange={handleRecentFilterChange}
      onGroupToggle={handleGroupToggle}
      onProjectAction={handleProjectAction}
      onResizeStart={handleResizeStart}
      onSearchChange={handleSearchChange}
      onSearchClear={handleSearchClear}
      onSortChange={handleRecentSortChange}
      onTabValue={getActiveTabValue}
      recentFilter={recentFilter}
      recentProjects={sortedRecentProjects}
      recentSort={recentSort}
      renderTitle={renderHighlightedTitle}
      searchInputRef={handleSearchInputRef}
      searchQuery={searchQuery}
      sidebarWidth={sidebarWidth}
    />
  );
};

export const Sidebar = memo(SidebarComponent);
