import { ReactNode } from 'react';
import {
  Folder as FolderIcon,
  File as FileIcon,
  ChevronRight,
  ChevronDown,
  FileJson,
  FileText,
  FileCode,
  FileType,
  Package,
  Settings,
  Database,
  Image,
  Film,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface FileTreeProps {
  /** Tree content (Folder and File components) */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
}

/**
 * FileTree - Display a file system tree structure
 *
 * Usage in MDX:
 * ```mdx
 * <FileTree>
 *   <Folder name="src" open>
 *     <Folder name="components">
 *       <File name="Button.tsx" />
 *       <File name="Card.tsx" />
 *     </Folder>
 *     <File name="index.ts" highlight />
 *   </Folder>
 *   <File name="package.json" />
 * </FileTree>
 * ```
 */
export function FileTree({ children, className }: FileTreeProps) {
  return (
    <div
      className={cn(
        'my-6 rounded-lg border bg-muted/30 p-4',
        'font-mono text-sm',
        className
      )}
      role="tree"
      aria-label="File tree"
    >
      <ul className="space-y-0.5">{children}</ul>
    </div>
  );
}

interface FolderProps {
  /** Folder name */
  name: string;
  /** Whether the folder is expanded */
  open?: boolean;
  /** Folder contents */
  children?: ReactNode;
  /** Highlight this folder */
  highlight?: boolean;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Folder - A folder node in the file tree
 */
export function Folder({
  name,
  open = false,
  children,
  highlight,
  className,
}: FolderProps) {
  const hasChildren = Boolean(children);
  const ChevronIcon = open ? ChevronDown : ChevronRight;

  return (
    <li className={cn('', className)} role="treeitem" aria-expanded={open}>
      <div
        className={cn(
          'flex items-center gap-1.5 py-1 rounded-md',
          'hover:bg-accent/50 px-1 -mx-1',
          highlight && 'text-primary font-medium'
        )}
      >
        {hasChildren ? (
          <ChevronIcon className="w-4 h-4 text-muted-foreground flex-shrink-0" />
        ) : (
          <span className="w-4" />
        )}
        <FolderIcon
          className={cn(
            'w-4 h-4 flex-shrink-0',
            open ? 'text-primary' : 'text-muted-foreground'
          )}
        />
        <span className={cn(highlight ? 'text-primary' : 'text-foreground')}>
          {name}
        </span>
      </div>
      {open && children && (
        <ul
          className="ml-[22px] border-l border-border pl-2 space-y-0.5"
          role="group"
        >
          {children}
        </ul>
      )}
    </li>
  );
}

interface FileProps {
  /** File name */
  name: string;
  /** Highlight this file */
  highlight?: boolean;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Get the appropriate icon for a file based on its extension
 */
function getFileIcon(filename: string) {
  const ext = filename.split('.').pop()?.toLowerCase();

  const iconMap: Record<string, typeof FileIcon> = {
    json: FileJson,
    md: FileText,
    mdx: FileText,
    txt: FileText,
    ts: FileCode,
    tsx: FileCode,
    js: FileCode,
    jsx: FileCode,
    py: FileCode,
    go: FileCode,
    rs: FileCode,
    yaml: Settings,
    yml: Settings,
    toml: Settings,
    config: Settings,
    sql: Database,
    db: Database,
    png: Image,
    jpg: Image,
    jpeg: Image,
    gif: Image,
    svg: Image,
    webp: Image,
    mp4: Film,
    webm: Film,
    lock: Package,
  };

  return iconMap[ext || ''] || FileIcon;
}

/**
 * File - A file node in the file tree
 */
export function File({ name, highlight, className }: FileProps) {
  const Icon = getFileIcon(name);

  return (
    <li
      className={cn(
        'flex items-center gap-1.5 py-1 ml-5 rounded-md',
        'hover:bg-accent/50 px-1 -mx-1',
        className
      )}
      role="treeitem"
    >
      <Icon
        className={cn(
          'w-4 h-4 flex-shrink-0',
          highlight ? 'text-primary' : 'text-muted-foreground'
        )}
      />
      <span className={cn(highlight && 'text-primary font-medium')}>{name}</span>
    </li>
  );
}

/**
 * Pre-built file tree for common project structures
 */
export function NextJsFileTree() {
  return (
    <FileTree>
      <Folder name="app" open>
        <File name="layout.tsx" />
        <File name="page.tsx" highlight />
        <File name="globals.css" />
        <Folder name="api">
          <Folder name="route">
            <File name="route.ts" />
          </Folder>
        </Folder>
      </Folder>
      <Folder name="components">
        <File name="Button.tsx" />
        <File name="Card.tsx" />
      </Folder>
      <Folder name="lib">
        <File name="utils.ts" />
      </Folder>
      <File name="package.json" />
      <File name="tsconfig.json" />
      <File name="next.config.ts" />
    </FileTree>
  );
}

/**
 * Documentation file tree
 */
export function DocsFileTree() {
  return (
    <FileTree>
      <Folder name="content" open>
        <Folder name="docs" open>
          <Folder name="user">
            <File name="index.mdx" />
            <Folder name="getting-started">
              <File name="index.mdx" />
            </Folder>
          </Folder>
          <Folder name="developer">
            <File name="index.mdx" />
          </Folder>
          <Folder name="api">
            <File name="index.mdx" />
          </Folder>
        </Folder>
      </Folder>
      <File name="source.config.ts" highlight />
    </FileTree>
  );
}

export default FileTree;
