import type { MouseEvent, ReactElement } from 'react';

import { useCallback } from 'react';

import type { TabConfig, TabId } from '@/pages/projects/views/integrations-view/types';

interface TabsNavProps {
  activeTab: TabId;
  conflictCount: number;
  onSelect: (tabId: TabId) => void;
  tabs: TabConfig[];
}

const TAB_ID_ATTR = 'data-tab-id';

function readTabId(value: string | undefined): TabId | undefined {
  if (value === undefined) {
    return undefined;
  }
  if (
    value === 'overview' ||
    value === 'credentials' ||
    value === 'mappings' ||
    value === 'sync' ||
    value === 'conflicts'
  ) {
    return value;
  }
  return undefined;
}

function tabButtonClassName(isActive: boolean): string {
  const base = 'border-b-2 px-1 py-2 text-sm font-medium';
  if (isActive) {
    return `${base} border-blue-500 text-blue-600 dark:text-blue-400`;
  }
  return `${base} border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400`;
}

function renderConflictBadge(conflictCount: number): ReactElement | undefined {
  if (conflictCount <= 0) {
    return undefined;
  }

  return (
    <span className='ml-2 rounded bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800 dark:bg-red-900 dark:text-red-300'>
      {conflictCount}
    </span>
  );
}

function renderTabButton({
  isActive,
  tab,
  conflictCount,
  onClick,
}: {
  isActive: boolean;
  tab: TabConfig;
  conflictCount: number;
  onClick: (event: MouseEvent<HTMLButtonElement>) => void;
}): ReactElement {
  const shouldShowConflictsBadge = tab.id === 'conflicts';
  let conflictsBadge: ReactElement | undefined = undefined;
  if (shouldShowConflictsBadge) {
    conflictsBadge = renderConflictBadge(conflictCount);
  }

  return (
    <button
      key={tab.id}
      type='button'
      data-tab-id={tab.id}
      onClick={onClick}
      className={tabButtonClassName(isActive)}
    >
      {tab.label}
      {conflictsBadge}
    </button>
  );
}

export default function TabsNav({
  activeTab,
  conflictCount,
  onSelect,
  tabs,
}: TabsNavProps): ReactElement {
  const handleClick = useCallback(
    (event: MouseEvent<HTMLButtonElement>) => {
      const tabId = readTabId(event.currentTarget.getAttribute(TAB_ID_ATTR) ?? undefined);
      if (tabId !== undefined) {
        onSelect(tabId);
      }
    },
    [onSelect],
  );

  return (
    <div className='mb-6 border-b border-gray-200 dark:border-gray-700'>
      <nav className='flex space-x-8'>
        {tabs.map((tab) =>
          renderTabButton({
            isActive: activeTab === tab.id,
            tab,
            conflictCount,
            onClick: handleClick,
          }),
        )}
      </nav>
    </div>
  );
}
