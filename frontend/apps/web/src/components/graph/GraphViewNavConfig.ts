import type { ComponentType } from 'react';

import {
  Activity,
  BarChart3,
  BookOpen,
  Code,
  Database,
  FileStack,
  Globe,
  LayoutGrid,
  Layers,
  Network,
  Shield,
  TestTube,
  Workflow,
} from 'lucide-react';

interface ProjectViewNavItem {
  label: string;
  viewType: string;
  icon: ComponentType<{ className?: string }>;
}

const PROJECT_VIEW_NAV: ProjectViewNavItem[] = [
  { icon: Layers, label: 'Features', viewType: 'feature' },
  { icon: Network, label: 'Traceability / Graph', viewType: 'graph' },
  { icon: TestTube, label: 'Test Suite', viewType: 'test' },
  { icon: Globe, label: 'API Docs', viewType: 'api' },
  { icon: Database, label: 'Database', viewType: 'database' },
  { icon: LayoutGrid, label: 'Wireframe', viewType: 'wireframe' },
  { icon: BarChart3, label: 'Matrix', viewType: 'matrix' },
  { icon: Activity, label: 'Workflows', viewType: 'workflows' },
  { icon: Code, label: 'Code', viewType: 'code' },
  { icon: TestTube, label: 'Test Cases', viewType: 'test-cases' },
  { icon: Activity, label: 'Test Runs', viewType: 'test-runs' },
  { icon: FileStack, label: 'Test Suites', viewType: 'test-suites' },
  { icon: Shield, label: 'Problem', viewType: 'problem' },
  { icon: Workflow, label: 'Process', viewType: 'process' },
  { icon: BookOpen, label: 'Documentation', viewType: 'documentation' },
];

export { PROJECT_VIEW_NAV, type ProjectViewNavItem };
