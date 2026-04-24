import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { toast } from 'sonner';

import { useProjectStore } from '@/stores/project-store';

import type { FilterOption, SidebarGroup, SortOption } from './sidebar-nav';

import { buildSidebarGroups, filterSidebarGroups } from './sidebar-nav';

const SIDEBAR_DEFAULT_WIDTH_PX = 320;
const SIDEBAR_MIN_WIDTH_PX = 280;
const SIDEBAR_MAX_WIDTH_PX = 720;
const RECENT_PROJECTS_DISPLAY_MAX = 5;
const KEYBOARD_HOME_INDEX = 0;
const KEYBOARD_LAST_INDEX_OFFSET = 1;
const NO_INDEX = -1;

interface RecentProject {
  id: string;
  name: string;
  createdAt?: string | undefined;
  updatedAt?: string | undefined;
}

const isSortOption = (value: string): value is SortOption =>
  value === 'recent' || value === 'alphabetical' || value === 'modified';

const isFilterOption = (value: string): value is FilterOption =>
  value === 'all' || value === 'active' || value === 'archived';

const isRecordOfBoolean = (value: unknown): value is Record<string, boolean> => {
  if (!value || typeof value !== 'object') {
    return false;
  }
  return Object.values(value as Record<string, unknown>).every(
    (entry) => typeof entry === 'boolean',
  );
};

const parseStoredCollapsedGroups = (value: string): Record<string, boolean> | undefined => {
  try {
    const parsed = JSON.parse(value);
    if (isRecordOfBoolean(parsed)) {
      return parsed;
    }
  } catch {
    return undefined;
  }
  return undefined;
};

const getActiveProjectId = (
  projectId: string | undefined,
  currentProjectId: string | number | undefined,
): string | undefined => {
  if (typeof projectId === 'string' && projectId.length > 0) {
    return projectId;
  }
  if (typeof currentProjectId === 'string' && currentProjectId.length > 0) {
    return currentProjectId;
  }
  if (typeof currentProjectId === 'number') {
    return String(currentProjectId);
  }
  return undefined;
};

const getProjectTimestamp = (project: RecentProject): number => {
  if (typeof project.updatedAt === 'string' && project.updatedAt.length > 0) {
    return new Date(project.updatedAt).getTime();
  }
  if (typeof project.createdAt === 'string' && project.createdAt.length > 0) {
    return new Date(project.createdAt).getTime();
  }
  return 0;
};

export const useSidebarPreferences = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [collapsedGroups, setCollapsedGroups] = useState<Record<string, boolean>>({});
  const [recentSort, setRecentSort] = useState<SortOption>('recent');
  const [recentFilter, setRecentFilter] = useState<FilterOption>('all');
  const [activeTab, setActiveTab] = useState<Record<string, string>>({
    'Active Registry': 'overview',
    Specifications: 'dashboard',
  });

  useEffect(() => {
    const savedCollapsed = localStorage.getItem('sidebar-collapsed');
    if (typeof savedCollapsed === 'string' && savedCollapsed.length > 0) {
      setIsCollapsed(savedCollapsed === 'true');
    }

    const savedGroups = localStorage.getItem('sidebar-collapsed-groups');
    if (typeof savedGroups === 'string' && savedGroups.length > 0) {
      const parsedGroups = parseStoredCollapsedGroups(savedGroups);
      if (parsedGroups) {
        setCollapsedGroups(parsedGroups);
      }
    }

    const savedSort = localStorage.getItem('sidebar-recent-sort');
    if (typeof savedSort === 'string' && isSortOption(savedSort)) {
      setRecentSort(savedSort);
    }

    const savedFilter = localStorage.getItem('sidebar-recent-filter');
    if (typeof savedFilter === 'string' && isFilterOption(savedFilter)) {
      setRecentFilter(savedFilter);
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('sidebar-collapsed', String(isCollapsed));
  }, [isCollapsed]);

  useEffect(() => {
    localStorage.setItem('sidebar-collapsed-groups', JSON.stringify(collapsedGroups));
  }, [collapsedGroups]);

  useEffect(() => {
    localStorage.setItem('sidebar-recent-sort', recentSort);
  }, [recentSort]);

  useEffect(() => {
    localStorage.setItem('sidebar-recent-filter', recentFilter);
  }, [recentFilter]);

  return {
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
  };
};

export const useSidebarWidth = () => {
  const [sidebarWidth, setSidebarWidth] = useState(() => {
    const saved = localStorage.getItem('sidebar-width');
    let parsed = SIDEBAR_DEFAULT_WIDTH_PX;
    if (typeof saved === 'string' && saved.length > 0) {
      parsed = Number.parseInt(saved, 10);
    }
    return Math.max(SIDEBAR_MIN_WIDTH_PX, parsed);
  });
  const [isResizing, setIsResizing] = useState(false);

  const handleResizeStart = useCallback(
    (event: React.MouseEvent): void => {
      event.preventDefault();
      event.stopPropagation();
      setIsResizing(true);
      const startX = event.clientX;
      const startWidth = sidebarWidth;

      document.body.style.userSelect = 'none';
      document.body.style.cursor = 'ew-resize';

      const handleMouseMove = (moveEvent: MouseEvent): void => {
        moveEvent.preventDefault();
        const delta = moveEvent.clientX - startX;
        const newWidth = Math.max(
          SIDEBAR_MIN_WIDTH_PX,
          Math.min(SIDEBAR_MAX_WIDTH_PX, startWidth + delta),
        );
        setSidebarWidth(newWidth);
        localStorage.setItem('sidebar-width', newWidth.toString());
      };

      const handleMouseUp = (): void => {
        setIsResizing(false);
        document.body.style.userSelect = '';
        document.body.style.cursor = '';
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };

      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    },
    [sidebarWidth],
  );

  return { handleResizeStart, isResizing, sidebarWidth };
};

export const useSidebarKeyboardNavigation = ({
  isCollapsed,
  navItemsRef,
  searchInputRef,
  setFocusedIndex,
  setSearchQuery,
}: {
  isCollapsed: boolean;
  navItemsRef: React.RefObject<(HTMLAnchorElement | undefined)[]>;
  searchInputRef: React.RefObject<HTMLInputElement | undefined>;
  setFocusedIndex: React.Dispatch<React.SetStateAction<number>>;
  setSearchQuery: React.Dispatch<React.SetStateAction<string>>;
}) => {
  const handleSearchShortcut = useCallback(
    (event: KeyboardEvent): boolean => {
      const isShortcut = (event.metaKey || event.ctrlKey) && event.key === 'f';
      if (!isShortcut || isCollapsed) {
        return false;
      }
      event.preventDefault();
      searchInputRef.current?.focus();
      return true;
    },
    [isCollapsed, searchInputRef],
  );

  const handleEscapeClear = useCallback(
    (event: KeyboardEvent): boolean => {
      if (event.key !== 'Escape') {
        return false;
      }
      const { activeElement } = document;
      if (activeElement !== searchInputRef.current) {
        return false;
      }
      setSearchQuery('');
      searchInputRef.current?.blur();
      return true;
    },
    [searchInputRef, setSearchQuery],
  );

  const handleArrowNavigation = useCallback(
    (event: KeyboardEvent): void => {
      const { activeElement } = document;
      const isSidebarFocused =
        Boolean(activeElement?.closest('aside')) || activeElement === searchInputRef.current;
      if (!isSidebarFocused || isCollapsed) {
        return;
      }

      const allNavItems = navItemsRef.current?.filter(Boolean) ?? [];
      const lastIndex = allNavItems.length - KEYBOARD_LAST_INDEX_OFFSET;

      if (event.key === 'ArrowDown') {
        event.preventDefault();
        const nextIndex = lastIndex > KEYBOARD_HOME_INDEX ? KEYBOARD_HOME_INDEX + 1 : lastIndex;
        setFocusedIndex(nextIndex);
        allNavItems[nextIndex]?.focus();
        return;
      }

      if (event.key === 'ArrowUp') {
        event.preventDefault();
        const prevIndex = lastIndex > KEYBOARD_HOME_INDEX ? lastIndex - 1 : KEYBOARD_HOME_INDEX;
        setFocusedIndex(prevIndex);
        allNavItems[prevIndex]?.focus();
        return;
      }

      if (event.key === 'Home') {
        event.preventDefault();
        setFocusedIndex(KEYBOARD_HOME_INDEX);
        allNavItems[KEYBOARD_HOME_INDEX]?.focus();
        return;
      }

      if (event.key === 'End') {
        event.preventDefault();
        setFocusedIndex(lastIndex);
        allNavItems[lastIndex]?.focus();
      }
    },
    [isCollapsed, navItemsRef, searchInputRef, setFocusedIndex],
  );

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent): void => {
      if (handleSearchShortcut(event)) {
        return;
      }
      if (handleEscapeClear(event)) {
        return;
      }
      handleArrowNavigation(event);
    };

    globalThis.addEventListener('keydown', handleKeyDown);
    return () => {
      globalThis.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleArrowNavigation, handleEscapeClear, handleSearchShortcut]);
};

export const useRecentProjects = ({
  allProjects,
  currentProjectId,
  recentProjects,
  recentSort,
  searchQuery,
}: {
  allProjects: RecentProject[] | undefined;
  currentProjectId?: string | number | undefined;
  recentProjects: string[];
  recentSort: SortOption;
  searchQuery: string;
}) => {
  const recentProjectObjects = useMemo(() => {
    if (!Array.isArray(allProjects)) {
      return [];
    }
    return recentProjects
      .map((projectIdValue) => allProjects.find((project) => project.id === projectIdValue))
      .filter(
        (project): project is RecentProject =>
          project !== undefined && project.id !== currentProjectId,
      );
  }, [allProjects, currentProjectId, recentProjects]);

  const sortedRecentProjects = useMemo(() => {
    const sorted = [...recentProjectObjects].toSorted((firstProject, secondProject) => {
      if (recentSort === 'alphabetical') {
        return firstProject.name.localeCompare(secondProject.name);
      }
      if (recentSort === 'modified') {
        const firstTime = getProjectTimestamp(firstProject);
        const secondTime = getProjectTimestamp(secondProject);
        return secondTime - firstTime;
      }
      const firstIndex = recentProjects.indexOf(firstProject.id);
      const secondIndex = recentProjects.indexOf(secondProject.id);
      return firstIndex - secondIndex;
    });

    if (searchQuery.trim().length > 0) {
      const query = searchQuery.toLowerCase();
      return sorted.filter((project) => project.name.toLowerCase().includes(query));
    }

    return sorted.slice(0, RECENT_PROJECTS_DISPLAY_MAX);
  }, [recentProjectObjects, recentSort, recentProjects, searchQuery]);

  return sortedRecentProjects;
};

export const useSidebarNavGroups = ({
  allProjects,
  isTestEnv,
  projectId,
  currentProjectId,
  searchQuery,
}: {
  allProjects: RecentProject[] | undefined;
  currentProjectId?: string | number | undefined;
  isTestEnv: boolean;
  projectId?: string | undefined;
  searchQuery: string;
}) => {
  const navGroups = useMemo<SidebarGroup[]>(() => {
    let projectsBadge: number | undefined;
    if (Array.isArray(allProjects) && allProjects.length > 0) {
      projectsBadge = allProjects.length;
    }
    return buildSidebarGroups({
      activeId: getActiveProjectId(projectId, currentProjectId),
      isTestEnv,
      projectsBadge,
    });
  }, [allProjects, currentProjectId, isTestEnv, projectId]);

  const filteredNavGroups = useMemo<SidebarGroup[]>(
    () => filterSidebarGroups(navGroups, searchQuery),
    [navGroups, searchQuery],
  );

  return filteredNavGroups;
};

export const useSidebarRefs = () => {
  const initialSearchInput =
    typeof document === 'undefined' ? undefined : document.createElement('input');
  const searchInputRef = useRef<HTMLInputElement | undefined>(initialSearchInput);
  const navItemsRef = useRef<(HTMLAnchorElement | undefined)[]>([]);
  const nextNavItemIndexRef = useRef(0);

  const setNavItemRef = useCallback((element: HTMLAnchorElement | null): void => {
    const nextIndex = (nextNavItemIndexRef.current += 1);
    navItemsRef.current[nextIndex] = element ?? undefined;
  }, []);

  const handleSearchInputRef = useCallback((element: HTMLInputElement | null): void => {
    if (element) {
      searchInputRef.current = element;
    }
  }, []);

  const resetNavItemRefs = useCallback((): void => {
    nextNavItemIndexRef.current = 0;
    navItemsRef.current = [];
  }, []);

  return { handleSearchInputRef, navItemsRef, resetNavItemRefs, searchInputRef, setNavItemRef };
};

export const useProjectActionHandler = (recentProjects: string[]) =>
  useCallback(
    (action: 'pin' | 'remove' | 'newtab', targetProjectId: string): void => {
      if (action === 'newtab') {
        window.open(`/projects/${targetProjectId}`, '_blank');
        return;
      }
      if (action === 'remove') {
        const updated = recentProjects.filter(
          (projectIdValue) => projectIdValue !== targetProjectId,
        );
        useProjectStore.getState().setRecentProjects(updated);
        toast.success('Removed from recent');
      }
    },
    [recentProjects],
  );

export const useSidebarViewData = ({
  allProjects,
  currentProjectId,
  isTestEnv,
  projectId,
  recentProjects,
  recentSort,
  searchQuery,
}: {
  allProjects: RecentProject[] | undefined;
  currentProjectId?: string | number | undefined;
  isTestEnv: boolean;
  projectId?: string | undefined;
  recentProjects: string[];
  recentSort: SortOption;
  searchQuery: string;
}) => {
  const filteredNavGroups = useSidebarNavGroups({
    allProjects,
    currentProjectId,
    isTestEnv,
    projectId,
    searchQuery,
  });

  const sortedRecentProjects = useRecentProjects({
    allProjects,
    currentProjectId,
    recentProjects,
    recentSort,
    searchQuery,
  });

  return { filteredNavGroups, sortedRecentProjects };
};

export const useSidebarHandlers = ({
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
}: {
  activeTab: Record<string, string>;
  highlightText: (title: string, query: string) => (string | JSX.Element)[];
  searchQuery: string;
  setActiveTab: React.Dispatch<React.SetStateAction<Record<string, string>>>;
  setCollapsedGroups: React.Dispatch<React.SetStateAction<Record<string, boolean>>>;
  setFocusedIndex: React.Dispatch<React.SetStateAction<number>>;
  setIsCollapsed: React.Dispatch<React.SetStateAction<boolean>>;
  setRecentFilter: React.Dispatch<React.SetStateAction<FilterOption>>;
  setRecentSort: React.Dispatch<React.SetStateAction<SortOption>>;
  setSearchQuery: React.Dispatch<React.SetStateAction<string>>;
}) => {
  const handleSearchChange = useCallback(
    (value: string): void => {
      setSearchQuery(value);
      setFocusedIndex(NO_INDEX);
    },
    [setFocusedIndex, setSearchQuery],
  );

  const handleSearchClear = useCallback((): void => {
    setSearchQuery('');
    setFocusedIndex(NO_INDEX);
  }, [setFocusedIndex, setSearchQuery]);

  const handleCollapseToggle = useCallback((): void => {
    setIsCollapsed((prev) => !prev);
  }, [setIsCollapsed]);

  const handleGroupToggle = useCallback(
    (label: string, open: boolean): void => {
      setCollapsedGroups((prev) => ({
        ...prev,
        [label]: !open,
      }));
    },
    [setCollapsedGroups],
  );

  const handleActiveTabChange = useCallback(
    (label: string, value: string): void => {
      setActiveTab((prev) => ({
        ...prev,
        [label]: value,
      }));
    },
    [setActiveTab],
  );

  const handleRecentSortChange = useCallback(
    (value: SortOption): void => {
      setRecentSort(value);
    },
    [setRecentSort],
  );

  const handleRecentFilterChange = useCallback(
    (value: FilterOption): void => {
      setRecentFilter(value);
    },
    [setRecentFilter],
  );

  const getActiveTabValue = useCallback(
    (label: string, fallback: string): string => {
      const activeValue = activeTab[label];
      if (typeof activeValue === 'string' && activeValue.length > 0) {
        return activeValue;
      }
      return fallback;
    },
    [activeTab],
  );

  const renderHighlightedTitle = useCallback(
    (title: string): (string | JSX.Element)[] => highlightText(title, searchQuery),
    [highlightText, searchQuery],
  );

  return {
    getActiveTabValue,
    handleActiveTabChange,
    handleCollapseToggle,
    handleGroupToggle,
    handleRecentFilterChange,
    handleRecentSortChange,
    handleSearchChange,
    handleSearchClear,
    renderHighlightedTitle,
  };
};
