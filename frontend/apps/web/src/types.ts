// Re-export types from packages
export type {
  Agent,
  ApiError,
  Item,
  ItemStatus,
  Link,
  LinkType,
  Mutation,
  PaginatedResponse,
  Priority,
  Project,
  ViewType,
} from '@tracertm/types';

// Import for local use
import type { Item, Link, ViewType } from '@tracertm/types';

// Application-specific types

export interface Route {
  path: string;
  name: string;
  icon?: string;
  component?: React.ComponentType;
  children?: Route[];
}

export interface MenuItem {
  id: string;
  label: string;
  icon?: string;
  action?: () => void;
  shortcut?: string;
  separator?: boolean;
  disabled?: boolean;
  children?: MenuItem[];
}

export interface CommandItem extends MenuItem {
  keywords?: string[];
  category?: string;
}

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message?: string;
  timestamp: Date;
  read: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export interface FilterOption {
  label: string;
  value: string;
  count?: number;
}

export interface SortOption {
  label: string;
  value: string;
  order: 'asc' | 'desc';
}

export interface ViewConfig {
  id: ViewType;
  name: string;
  icon: string;
  description: string;
  color: string;
  itemTypes: string[];
}

export interface GraphNode {
  id: string;
  data: Item;
  x?: number;
  y?: number;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  data: Link;
}

export interface GraphLayout {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface KeyboardShortcut {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  meta?: boolean;
  description: string;
  action: () => void;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  language: string;
  dateFormat: string;
  timeFormat: '12h' | '24h';
  notifications: {
    enabled: boolean;
    desktop: boolean;
    email: boolean;
  };
  editor: {
    fontSize: number;
    tabSize: number;
    wordWrap: boolean;
    minimap: boolean;
  };
}

export interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: string;
}

export interface TableColumn<T = unknown> {
  id: string;
  header: string;
  accessor: keyof T | ((row: T) => unknown);
  width?: number;
  sortable?: boolean;
  filterable?: boolean;
  cell?: (value: unknown, row: T) => React.ReactNode;
}

export interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: string;
  custom?: (value: unknown) => boolean | string;
  [key: string]: unknown;
}

export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'textarea' | 'select' | 'checkbox' | 'radio' | 'date' | 'number' | 'email';
  placeholder?: string;
  required?: boolean;
  options?: { label: string; value: string }[];
  validation?: ValidationRule;
  helpText?: string;
}

export interface ContextMenuConfig {
  items: MenuItem[];
  position: { x: number; y: number };
  targetId?: string;
}

export interface DragDropItem<T = unknown> {
  id: string;
  type: string;
  data: T;
}

export interface UploadFile {
  id: string;
  name: string;
  size: number;
  type: string;
  status: 'pending' | 'uploading' | 'success' | 'error';
  progress: number;
  error?: string;
  url?: string;
}

export type ExportFilter = Record<string, string | number | boolean | string[] | undefined>;

export interface ApiErrorResponse {
  message: string;
  code?: string;
  details?: unknown;
  statusCode?: number;
}

export interface ExportConfig {
  format: 'json' | 'csv' | 'xlsx' | 'pdf';
  filename: string;
  includeMetadata?: boolean;
  filters?: ExportFilter;
}

// Utility types

export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type ValueOf<T> = T[keyof T];

export type NonNullableFields<T> = {
  [P in keyof T]: NonNullable<T[P]>;
};

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

export type OptionalFields<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

// Component prop types

export interface BaseComponentProps {
  className?: string;
  style?: React.CSSProperties;
  children?: React.ReactNode;
}

export interface LoadingProps extends BaseComponentProps {
  loading: boolean;
  fallback?: React.ReactNode;
}

export interface ErrorBoundaryProps extends BaseComponentProps {
  fallback?: (error: Error) => React.ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

// API request/response types

export type SearchFilter = Record<string, string | number | boolean | string[] | undefined>;

export interface SearchParams {
  query: string;
  filters?: SearchFilter;
  sort?: string;
  order?: 'asc' | 'desc';
  page?: number;
  pageSize?: number;
}

export type BulkOperationData = Record<string, string | number | boolean | null | undefined>;

export interface BulkOperation {
  operation: 'update' | 'delete';
  ids: string[];
  data?: BulkOperationData;
}

export interface ImportResult {
  total: number;
  success: number;
  failed: number;
  errors: {
    row: number;
    message: string;
  }[];
}
