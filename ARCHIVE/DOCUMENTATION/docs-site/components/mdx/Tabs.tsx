'use client';

import {
  createContext,
  useContext,
  useState,
  ReactNode,
  Children,
  isValidElement,
  useId,
} from 'react';
import { cn } from '@/lib/utils';

/**
 * Tabs context for sharing state between Tabs and Tab components
 */
interface TabsContextValue {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  tabsId: string;
}

const TabsContext = createContext<TabsContextValue | null>(null);

function useTabsContext() {
  const context = useContext(TabsContext);
  if (!context) {
    throw new Error('Tab must be used within a Tabs component');
  }
  return context;
}

interface TabsProps {
  /** Default active tab value */
  defaultValue?: string;
  /** Array of tab names */
  items?: string[];
  /** Tab content */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
  /** Persist selected tab across page navigation */
  persist?: string;
}

/**
 * Tabs - Tabbed content container for documentation
 *
 * Usage in MDX:
 * ```mdx
 * <Tabs items={["npm", "yarn", "pnpm"]}>
 *   <Tab value="npm">
 *     ```bash
 *     npm install tracertm
 *     ```
 *   </Tab>
 *   <Tab value="yarn">
 *     ```bash
 *     yarn add tracertm
 *     ```
 *   </Tab>
 *   <Tab value="pnpm">
 *     ```bash
 *     pnpm add tracertm
 *     ```
 *   </Tab>
 * </Tabs>
 * ```
 */
export function Tabs({
  defaultValue,
  items = [],
  children,
  className,
  persist,
}: TabsProps) {
  const tabsId = useId();

  // Extract items from children if not provided
  const tabItems = items.length > 0 ? items : extractTabItems(children);

  // Initialize active tab from localStorage if persist is set
  const getInitialTab = () => {
    if (typeof window !== 'undefined' && persist) {
      const stored = localStorage.getItem(`tabs-${persist}`);
      if (stored && tabItems.includes(stored)) {
        return stored;
      }
    }
    return defaultValue || tabItems[0] || '';
  };

  const [activeTab, setActiveTab] = useState(getInitialTab);

  // Persist tab selection
  const handleSetActiveTab = (tab: string) => {
    setActiveTab(tab);
    if (typeof window !== 'undefined' && persist) {
      localStorage.setItem(`tabs-${persist}`, tab);
    }
  };

  return (
    <TabsContext.Provider
      value={{ activeTab, setActiveTab: handleSetActiveTab, tabsId }}
    >
      <div className={cn('my-6', className)}>
        {/* Tab List */}
        <div
          className="flex border-b overflow-x-auto scrollbar-none"
          role="tablist"
          aria-orientation="horizontal"
        >
          {tabItems.map((item, index) => (
            <button
              key={item}
              onClick={() => handleSetActiveTab(item)}
              className={cn(
                'px-4 py-2 text-sm font-medium whitespace-nowrap',
                'border-b-2 -mb-px transition-colors',
                'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary',
                activeTab === item
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground hover:border-muted-foreground/30'
              )}
              role="tab"
              aria-selected={activeTab === item}
              aria-controls={`${tabsId}-panel-${index}`}
              id={`${tabsId}-tab-${index}`}
              tabIndex={activeTab === item ? 0 : -1}
            >
              {item}
            </button>
          ))}
        </div>

        {/* Tab Panels */}
        <div className="mt-4">{children}</div>
      </div>
    </TabsContext.Provider>
  );
}

interface TabProps {
  /** Tab identifier - must match one of the items in Tabs */
  value: string;
  /** Tab content */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Tab - Individual tab panel content
 */
export function Tab({ value, children, className }: TabProps) {
  const { activeTab, tabsId } = useTabsContext();

  if (activeTab !== value) {
    return null;
  }

  return (
    <div
      className={cn('animate-in fade-in-50 duration-200', className)}
      role="tabpanel"
      aria-labelledby={`${tabsId}-tab-${value}`}
      id={`${tabsId}-panel-${value}`}
      tabIndex={0}
    >
      {children}
    </div>
  );
}

/**
 * Extract tab values from Tab children
 */
function extractTabItems(children: ReactNode): string[] {
  const items: string[] = [];

  Children.forEach(children, (child) => {
    if (isValidElement<{ value?: string }>(child)) {
      if (child.props.value) {
        items.push(child.props.value);
      }
    }
  });

  return items;
}

/**
 * LanguageTabs - Pre-configured tabs for programming languages
 */
export function LanguageTabs({
  children,
  ...props
}: Omit<TabsProps, 'items'> & { items?: string[] }) {
  return (
    <Tabs
      items={props.items || ['Python', 'JavaScript', 'Go', 'cURL']}
      persist="language"
      {...props}
    >
      {children}
    </Tabs>
  );
}

/**
 * PackageManagerTabs - Pre-configured tabs for package managers
 */
export function PackageManagerTabs({
  children,
  ...props
}: Omit<TabsProps, 'items'>) {
  return (
    <Tabs items={['npm', 'yarn', 'pnpm', 'bun']} persist="packageManager" {...props}>
      {children}
    </Tabs>
  );
}

export default Tabs;
