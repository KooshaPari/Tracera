import type { MDXComponents } from 'mdx/types';
import Link from 'next/link';
import Image from 'next/image';

// Import MDX components
import {
  Callout,
  InfoCallout,
  WarningCallout,
  ErrorCallout,
  TipCallout,
  SuccessCallout,
  NoteCallout,
} from '@/components/mdx/Callout';
import { Tabs, Tab } from '@/components/mdx/Tabs';
import { CodeGroup } from '@/components/mdx/CodeGroup';
import { FileTree, Folder, File } from '@/components/mdx/FileTree';
import { Steps, Step } from '@/components/mdx/Steps';
import { Card, Cards } from '@/components/mdx/Card';
import { ResponseExample } from '@/components/mdx/ResponseExample';
import { CLICommand } from '@/components/mdx/CLICommand';
import { APIEndpoint } from '@/components/mdx/APIEndpoint';
import { TypeTable } from '@/components/mdx/TypeTable';

/**
 * MDX Components Configuration
 *
 * Maps custom components to be used in MDX files.
 * Also customizes default HTML elements for better styling.
 */
export function useMDXComponents(components: MDXComponents): MDXComponents {
  return {
    // Override default HTML elements
    a: ({ href, children, ...props }) => (
      <Link
        href={href || '#'}
        className="text-primary hover:underline underline-offset-4 font-medium"
        {...props}
      >
        {children}
      </Link>
    ),

    img: ({ src, alt, ...props }) => (
      <Image
        src={src || ''}
        alt={alt || ''}
        width={800}
        height={400}
        className="rounded-lg border my-4"
        {...props}
      />
    ),

    // Tables
    table: ({ children }) => (
      <div className="my-4 overflow-x-auto rounded-lg border">
        <table className="w-full border-collapse text-sm">{children}</table>
      </div>
    ),
    thead: ({ children }) => (
      <thead className="bg-muted/50">{children}</thead>
    ),
    th: ({ children }) => (
      <th className="px-4 py-2 text-left font-semibold border-b">
        {children}
      </th>
    ),
    td: ({ children }) => (
      <td className="px-4 py-2 border-b">{children}</td>
    ),

    // Blockquotes
    blockquote: ({ children }) => (
      <blockquote className="my-4 border-l-4 border-primary pl-4 italic text-muted-foreground">
        {children}
      </blockquote>
    ),

    // Code blocks
    pre: ({ children }) => (
      <pre className="my-4 overflow-x-auto rounded-lg bg-zinc-950 p-4 text-sm">
        {children}
      </pre>
    ),
    code: ({ children, className }) => {
      // Inline code vs code blocks
      const isBlock = className?.includes('language-');
      if (isBlock) {
        return <code className={className}>{children}</code>;
      }
      return (
        <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-sm">
          {children}
        </code>
      );
    },

    // Headings with anchor links
    h1: ({ children, id }) => (
      <h1
        id={id}
        className="scroll-mt-20 text-4xl font-bold tracking-tight mb-4 mt-8"
      >
        {children}
      </h1>
    ),
    h2: ({ children, id }) => (
      <h2
        id={id}
        className="scroll-mt-20 text-3xl font-semibold tracking-tight mb-3 mt-8 border-b pb-2"
      >
        {children}
      </h2>
    ),
    h3: ({ children, id }) => (
      <h3
        id={id}
        className="scroll-mt-20 text-2xl font-semibold tracking-tight mb-2 mt-6"
      >
        {children}
      </h3>
    ),
    h4: ({ children, id }) => (
      <h4
        id={id}
        className="scroll-mt-20 text-xl font-semibold tracking-tight mb-2 mt-4"
      >
        {children}
      </h4>
    ),

    // Lists
    ul: ({ children }) => (
      <ul className="my-4 ml-6 list-disc space-y-2">{children}</ul>
    ),
    ol: ({ children }) => (
      <ol className="my-4 ml-6 list-decimal space-y-2">{children}</ol>
    ),
    li: ({ children }) => <li className="text-muted-foreground">{children}</li>,

    // Paragraphs
    p: ({ children }) => (
      <p className="my-4 text-muted-foreground leading-7">{children}</p>
    ),

    // Horizontal rule
    hr: () => <hr className="my-8 border-border" />,

    // Custom components
    Callout,
    InfoCallout,
    WarningCallout,
    ErrorCallout,
    TipCallout,
    SuccessCallout,
    NoteCallout,
    Tabs,
    Tab,
    CodeGroup,
    FileTree,
    Folder,
    File,
    Steps,
    Step,
    Card,
    Cards,
    ResponseExample,
    CLICommand,
    APIEndpoint,
    TypeTable,

    // Merge with any additional components passed in
    ...components,
  };
}
