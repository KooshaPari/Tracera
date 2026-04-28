import type React from 'react';

import * as Icons from 'lucide-react';

export type SortOption = 'recent' | 'alphabetical' | 'modified';
export type FilterOption = 'all' | 'active' | 'archived';

export type IconComponent = React.ComponentType<{ className?: string }>;

export interface SidebarNavItem {
  badge?: number | undefined;
  href: string;
  icon: IconComponent;
  title: string;
}

export interface SidebarCategoryView {
  description: string;
  href: string;
  icon: IconComponent;
  title: string;
}

export interface SidebarCategory {
  icon: IconComponent;
  name: string;
  views: SidebarCategoryView[];
}

export type SidebarGroupKey =
  | 'command'
  | 'active-registry'
  | 'specifications'
  | 'all-views'
  | 'system';

interface SidebarGroupBase {
  collapsible: boolean;
  items: SidebarNavItem[];
  key: SidebarGroupKey;
  label: string;
}

interface SidebarGroupWithCategories extends SidebarGroupBase {
  categories: SidebarCategory[];
  key: 'all-views';
}

export type SidebarGroup = SidebarGroupBase | SidebarGroupWithCategories;

interface BuildSidebarGroupsInput {
  activeId?: string | undefined;
  isTestEnv: boolean;
  projectsBadge?: number | undefined;
}

export const buildSidebarGroups = ({
  activeId,
  isTestEnv,
  projectsBadge,
}: BuildSidebarGroupsInput): SidebarGroup[] => {
  const groups: SidebarGroup[] = [
    {
      collapsible: false,
      items: [
        { badge: undefined, href: '/', icon: Icons.Home, title: 'Dashboard' },
        {
          badge: projectsBadge,
          href: '/projects',
          icon: Icons.FolderOpen,
          title: 'Projects',
        },
        { badge: undefined, href: '/items', icon: Icons.ListTodo, title: 'Items' },
        { badge: undefined, href: '/agents', icon: Icons.Bot, title: 'Agents' },
      ],
      key: 'command',
      label: 'Command',
    },
  ];

  if (isTestEnv) {
    return groups;
  }

  if (typeof activeId === 'string' && activeId.length > 0) {
    groups.push({
      collapsible: true,
      items: [
        {
          badge: undefined,
          href: `/projects/${activeId}`,
          icon: Icons.Activity,
          title: 'Overview',
        },
        {
          badge: undefined,
          href: `/projects/${activeId}/views/feature`,
          icon: Icons.Layers,
          title: 'Feature Layer',
        },
        {
          badge: undefined,
          href: `/projects/${activeId}/views/code`,
          icon: Icons.Code,
          title: 'Source Map',
        },
        {
          badge: undefined,
          href: `/projects/${activeId}/views/test`,
          icon: Icons.Shield,
          title: 'Validation',
        },
        {
          badge: undefined,
          href: `/projects/${activeId}/views/workflows`,
          icon: Icons.Activity,
          title: 'Workflow Runs',
        },
        {
          badge: undefined,
          href: `/projects/${activeId}/settings`,
          icon: Icons.Link2,
          title: 'Project Settings',
        },
      ],
      key: 'active-registry',
      label: 'Active Registry',
    });

    groups.push({
      collapsible: true,
      items: [
        {
          badge: undefined,
          href: `/projects/${activeId}/specifications`,
          icon: Icons.FileCode,
          title: 'Dashboard',
        },
        {
          badge: undefined,
          href: `/projects/${activeId}/scenario-activity`,
          icon: Icons.Activity,
          title: 'Scenario Activity',
        },
        {
          badge: undefined,
          href: `/projects/${activeId}/specifications?tab=adrs`,
          icon: Icons.FileText,
          title: 'ADRs',
        },
        {
          badge: undefined,
          href: `/projects/${activeId}/specifications?tab=contracts`,
          icon: Icons.ClipboardCheck,
          title: 'Contracts',
        },
        {
          badge: undefined,
          href: `/projects/${activeId}/specifications?tab=compliance`,
          icon: Icons.Shield,
          title: 'Compliance',
        },
      ],
      key: 'specifications',
      label: 'Specifications',
    });

    const categories: SidebarCategory[] = [
      {
        icon: Icons.Target,
        name: 'Planning & Requirements',
        views: [
          {
            description: 'Manage product features and requirements',
            href: `/projects/${activeId}/views/feature`,
            icon: Icons.Layers,
            title: 'Features',
          },
          {
            description: 'Visualize domain entities and relationships',
            href: `/projects/${activeId}/views/domain`,
            icon: Icons.Network,
            title: 'Domain Model',
          },
          {
            description: 'Track identified problems and issues',
            href: `/projects/${activeId}/views/problem`,
            icon: Icons.AlertCircle,
            title: 'Problem Analysis',
          },
          {
            description: 'UI/UX design and layout specifications',
            href: `/projects/${activeId}/views/wireframe`,
            icon: Icons.Eye,
            title: 'Wireframes',
          },
        ],
      },
      {
        icon: Icons.Code,
        name: 'Development',
        views: [
          {
            description: 'Source code structure and organization',
            href: `/projects/${activeId}/views/code`,
            icon: Icons.Code,
            title: 'Code View',
          },
          {
            description: 'System architecture and design patterns',
            href: `/projects/${activeId}/views/architecture`,
            icon: Icons.Network,
            title: 'Architecture',
          },
          {
            description: 'API endpoints and specifications',
            href: `/projects/${activeId}/views/api`,
            icon: Icons.Package,
            title: 'API Documentation',
          },
          {
            description: 'Database structure and relationships',
            href: `/projects/${activeId}/views/database`,
            icon: Icons.Database,
            title: 'Database Schema',
          },
          {
            description: 'Data pipeline and processing flows',
            href: `/projects/${activeId}/views/dataflow`,
            icon: Icons.Zap,
            title: 'Data Flow',
          },
        ],
      },
      {
        icon: Icons.TestTube,
        name: 'Testing & Quality',
        views: [
          {
            description: 'Test case definitions and scenarios',
            href: `/projects/${activeId}/views/test-cases`,
            icon: Icons.ClipboardCheck,
            title: 'Test Cases',
          },
          {
            description: 'Organized test suites and execution',
            href: `/projects/${activeId}/views/test-suites`,
            icon: Icons.TestTube,
            title: 'Test Suites',
          },
          {
            description: 'Test execution history and results',
            href: `/projects/${activeId}/views/test-runs`,
            icon: Icons.Activity,
            title: 'Test Runs',
          },
          {
            description: 'Quality metrics and coverage analysis',
            href: `/projects/${activeId}/views/qa-dashboard`,
            icon: Icons.BarChart3,
            title: 'QA Dashboard',
          },
          {
            description: 'Code coverage and test statistics',
            href: `/projects/${activeId}/views/coverage`,
            icon: Icons.TrendingUp,
            title: 'Coverage Report',
          },
        ],
      },
      {
        icon: Icons.Calendar,
        name: 'Project Management',
        views: [
          {
            description: 'User journeys and workflows',
            href: `/projects/${activeId}/views/journey`,
            icon: Icons.Calendar,
            title: 'Journey Map',
          },
          {
            description: 'Business process definitions',
            href: `/projects/${activeId}/views/process`,
            icon: Icons.Workflow,
            title: 'Process Flow',
          },
          {
            description: 'Project timeline and milestones',
            href: `/projects/${activeId}/views/monitoring`,
            icon: Icons.Activity,
            title: 'Timeline',
          },
          {
            description: 'Project metrics and analytics',
            href: `/projects/${activeId}/views/performance`,
            icon: Icons.BarChart3,
            title: 'Reports',
          },
        ],
      },
      {
        icon: Icons.TrendingUp,
        name: 'Analysis & Tracking',
        views: [
          {
            description: 'Change impact and dependency analysis',
            href: `/projects/${activeId}/views/impact-analysis`,
            icon: Icons.Network,
            title: 'Impact Analysis',
          },
          {
            description: 'Requirements to implementation tracing',
            href: `/projects/${activeId}/views/traceability`,
            icon: Icons.BarChart3,
            title: 'Traceability Matrix',
          },
          {
            description: 'System and code dependencies',
            href: `/projects/${activeId}/views/dependency`,
            icon: Icons.Network,
            title: 'Dependency Graph',
          },
          {
            description: 'Performance benchmarks and metrics',
            href: `/projects/${activeId}/views/performance`,
            icon: Icons.TrendingUp,
            title: 'Performance Metrics',
          },
        ],
      },
      {
        icon: Icons.Lock,
        name: 'Security & Monitoring',
        views: [
          {
            description: 'Security vulnerabilities and threats',
            href: `/projects/${activeId}/views/security`,
            icon: Icons.Lock,
            title: 'Security Analysis',
          },
          {
            description: 'System health and alerts',
            href: `/projects/${activeId}/views/monitoring`,
            icon: Icons.Activity,
            title: 'Monitoring Dashboard',
          },
          {
            description: 'Reported bugs and issues',
            href: `/projects/${activeId}/views/problem`,
            icon: Icons.Bug,
            title: 'Bug Tracking',
          },
        ],
      },
      {
        icon: Icons.Settings,
        name: 'Configuration',
        views: [
          {
            description: 'Third-party integrations and webhooks',
            href: `/projects/${activeId}/views/integrations`,
            icon: Icons.Zap,
            title: 'Integrations',
          },
          {
            description: 'Webhook configurations and events',
            href: `/projects/${activeId}/views/webhooks`,
            icon: Icons.Workflow,
            title: 'Webhooks',
          },
          {
            description: 'Project configuration and preferences',
            href: `/projects/${activeId}/settings`,
            icon: Icons.Settings,
            title: 'Settings',
          },
        ],
      },
    ];

    groups.push({
      categories,
      collapsible: true,
      items: [],
      key: 'all-views',
      label: 'All Views',
    });
  }

  groups.push({
    collapsible: false,
    items: [{ badge: undefined, href: '/settings', icon: Icons.Settings, title: 'Settings' }],
    key: 'system',
    label: 'System',
  });

  return groups;
};

export const filterSidebarGroups = (
  navGroups: SidebarGroup[],
  searchQuery: string,
): SidebarGroup[] => {
  if (searchQuery.trim().length === 0) {
    return navGroups;
  }

  const query = searchQuery.toLowerCase();
  return navGroups
    .map((group) => {
      if (group.key === 'all-views' && 'categories' in group) {
        const filteredCategories = group.categories
          .map((category) => {
            const filteredViews = category.views.filter((view) =>
              view.title.toLowerCase().includes(query),
            );
            return { ...category, views: filteredViews };
          })
          .filter((category) => category.views.length > 0);
        return { ...group, categories: filteredCategories };
      }

      const filteredItems = group.items.filter((item) => item.title.toLowerCase().includes(query));
      return { ...group, items: filteredItems };
    })
    .filter((group) => {
      if (group.key === 'all-views' && 'categories' in group) {
        return group.categories.length > 0;
      }
      return group.items.length > 0;
    });
};
