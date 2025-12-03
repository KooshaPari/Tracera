'use client';

import {
  useState,
  ReactNode,
  Children,
  isValidElement,
  cloneElement,
  ReactElement,
} from 'react';
import { cn } from '@/lib/utils';
import { Copy, Check, FileCode } from 'lucide-react';

interface CodeGroupProps {
  /** Code block children with data-title or filename props */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
}

interface CodeBlockMeta {
  title: string;
  language?: string;
  index: number;
}

/**
 * CodeGroup - Group related code blocks with tabbed navigation
 *
 * Usage in MDX:
 * ```mdx
 * <CodeGroup>
 * ```bash title="npm"
 * npm install tracertm
 * ```
 * ```bash title="yarn"
 * yarn add tracertm
 * ```
 * ```bash title="pnpm"
 * pnpm add tracertm
 * ```
 * </CodeGroup>
 * ```
 */
export function CodeGroup({ children, className }: CodeGroupProps) {
  const [activeIndex, setActiveIndex] = useState(0);
  const [copied, setCopied] = useState(false);

  // Extract code blocks and their metadata
  const childArray = Children.toArray(children).filter(isValidElement);
  const codeBlocks: CodeBlockMeta[] = childArray.map((child, index) => {
    const props = child.props as Record<string, unknown>;
    // Look for title in various places
    const title =
      (props['data-title'] as string) ||
      (props.title as string) ||
      (props.filename as string) ||
      (props['data-language'] as string) ||
      extractLanguage(child) ||
      `Code ${index + 1}`;

    const language = (props['data-language'] as string) || extractLanguage(child);

    return { title, language, index };
  });

  // Get the active code block's raw content for copying
  const getCodeContent = (): string => {
    const activeChild = childArray[activeIndex];
    if (!activeChild) return '';

    // Try to extract text content from the code block
    const props = activeChild.props as Record<string, unknown>;

    // Handle pre > code structure
    const children = props.children as { props?: { children?: unknown } } | undefined;
    if (children?.props?.children) {
      const codeContent = children.props.children;
      if (typeof codeContent === 'string') {
        return codeContent;
      }
    }

    // Handle direct children
    if (typeof props.children === 'string') {
      return props.children;
    }

    return '';
  };

  const handleCopy = async () => {
    const content = getCodeContent();
    if (content) {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (childArray.length === 0) {
    return null;
  }

  return (
    <div
      className={cn(
        'my-6 rounded-lg border overflow-hidden',
        'bg-zinc-900 dark:bg-zinc-950',
        className
      )}
    >
      {/* Tab Header */}
      <div className="flex items-center justify-between bg-zinc-800 dark:bg-zinc-900 border-b border-zinc-700">
        <div className="flex overflow-x-auto scrollbar-none">
          {codeBlocks.map((block, index) => (
            <button
              key={index}
              onClick={() => setActiveIndex(index)}
              className={cn(
                'px-4 py-2 text-sm font-medium whitespace-nowrap',
                'border-b-2 -mb-px transition-colors',
                activeIndex === index
                  ? 'border-primary text-zinc-100 bg-zinc-900/50'
                  : 'border-transparent text-zinc-400 hover:text-zinc-200'
              )}
            >
              <span className="flex items-center gap-2">
                <FileCode className="w-3.5 h-3.5" />
                {block.title}
              </span>
            </button>
          ))}
        </div>

        {/* Copy Button */}
        <button
          onClick={handleCopy}
          className={cn(
            'p-2 mr-2 rounded-md transition-colors',
            'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700'
          )}
          title="Copy code"
          aria-label="Copy code to clipboard"
        >
          {copied ? (
            <Check className="w-4 h-4 text-green-400" />
          ) : (
            <Copy className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Code Content */}
      <div className="[&>pre]:m-0 [&>pre]:rounded-none [&>pre]:border-0">
        {childArray[activeIndex]}
      </div>
    </div>
  );
}

/**
 * Extract language from a code block element
 */
function extractLanguage(element: ReactElement): string | undefined {
  const props = element.props as Record<string, unknown>;
  const className = (props?.className as string) || '';
  const match = className.match(/language-(\w+)/);
  return match ? match[1] : undefined;
}

/**
 * CodeFile - Display a file with its path and content
 */
interface CodeFileProps {
  /** File path to display */
  path: string;
  /** Code content */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
  /** Show line numbers */
  showLineNumbers?: boolean;
}

export function CodeFile({
  path,
  children,
  className,
  showLineNumbers,
}: CodeFileProps) {
  const [copied, setCopied] = useState(false);

  const getCodeContent = (): string => {
    if (typeof children === 'string') return children;
    // Try to extract from nested structure
    const childArray = Children.toArray(children);
    const firstChild = childArray[0];
    if (isValidElement(firstChild)) {
      const props = firstChild.props as Record<string, unknown>;
      if (typeof props.children === 'string') {
        return props.children;
      }
    }
    return '';
  };

  const handleCopy = async () => {
    const content = getCodeContent();
    if (content) {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div
      className={cn(
        'my-6 rounded-lg border overflow-hidden',
        'bg-zinc-900 dark:bg-zinc-950',
        className
      )}
    >
      {/* File Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-zinc-800 dark:bg-zinc-900 border-b border-zinc-700">
        <span className="text-sm font-mono text-zinc-300">{path}</span>
        <button
          onClick={handleCopy}
          className={cn(
            'p-1.5 rounded-md transition-colors',
            'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700'
          )}
          title="Copy code"
          aria-label="Copy code to clipboard"
        >
          {copied ? (
            <Check className="w-4 h-4 text-green-400" />
          ) : (
            <Copy className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Code Content */}
      <div
        className={cn(
          '[&>pre]:m-0 [&>pre]:rounded-none [&>pre]:border-0',
          showLineNumbers && '[&>pre]:pl-12'
        )}
      >
        {children}
      </div>
    </div>
  );
}

export default CodeGroup;
