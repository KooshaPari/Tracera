import { readFile, access } from 'fs/promises'
import { join } from 'path'
import { DocsPageClient } from './client'
import { DOCS_STRUCTURE } from './structure'
import { compile, run } from '@mdx-js/mdx'
import * as runtime from 'react/jsx-runtime'
import MermaidRenderer from '@/components/MermaidRenderer'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import { applyMdxPreset } from 'fumadocs-mdx/config'
import yaml from 'js-yaml'
import type { MDXComponents } from 'mdx/types'
import type { FC } from 'react'
import { useMDXComponents } from '@/mdx-components'

type MDXContent = FC<{ components?: MDXComponents }>

function getDocPath(slug: string[]): string | null {
  let current: any = DOCS_STRUCTURE
  const pathSegments: string[] = []
  
  for (let i = 0; i < slug.length; i++) {
    const segment = slug[i]

    // Check if segment exists in current level
    if (current[segment]) {
      current = current[segment]
      
      // Add path segment if it exists
      if (current.path) {
        pathSegments.push(current.path)
      }
      
      // If this is not the last segment and current has children, move to children
      if (i < slug.length - 1 && current.children) {
        current = current.children
      }
    } else {
      return null
    }
  }

  // Return the full path by joining all segments
  return pathSegments.join('/')
}

export async function generateStaticParams() {
  const params: { slug: string[] }[] = [{ slug: [] }]

  async function fileExists(filePath: string) {
    try {
      await access(filePath)
      return true
    } catch {
      return false
    }
  }

  async function collectPaths(items: any, path: string[] = []) {
    for (const [key, value] of Object.entries(items)) {
      const newPath = [...path, key]
      const docPath = getDocPath(newPath)
      if (docPath) {
        const filePath = join(process.cwd(), 'content/docs', docPath, 'index.mdx')
        if (await fileExists(filePath)) {
          params.push({ slug: newPath })
        }
      }
      if (value && typeof value === 'object' && 'children' in value) {
        await collectPaths((value as any).children, newPath)
      }
    }
  }

  await collectPaths(DOCS_STRUCTURE)
  return params
}

// Get the full MDX components from mdx-components.tsx
const baseMdxComponents = useMDXComponents({})

// Extend with Mermaid support
const mdxComponents: MDXComponents = {
  ...baseMdxComponents,
  code: ({ className, children, ...props }) => {
    const language = className?.replace('language-', '')
    if (language === 'mermaid') {
      return (
        <div className="-mx-8 px-8 my-6">
          <MermaidRenderer chart={String(children).replace(/\n$/, '')} />
        </div>
      )
    }
    // Use the base code component for non-mermaid code
    return baseMdxComponents.code ? baseMdxComponents.code({ className, children, ...props } as any) : (
      <code className={className} {...props}>
        {children}
      </code>
    )
  },
}

async function getDocContent(slug?: string[]) {
  if (!slug || slug.length === 0) return null

  try {
    const docPath = getDocPath(slug)
    if (!docPath) {
      console.warn(`No doc path found for slug: ${slug.join('/')}`)
      return null
    }

    const filePath = join(process.cwd(), 'content/docs', docPath, 'index.mdx')
    
    // Check if file exists
    try {
      await access(filePath)
    } catch (accessError) {
      console.warn(`File not found: ${filePath}`, accessError)
      return null
    }

    const raw = await readFile(filePath, 'utf-8')
    const match = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/)
    if (!match) {
      console.warn(`Invalid frontmatter format in: ${filePath}`)
      return null
    }

    let frontmatter: Record<string, string | undefined> = {}
    try {
      frontmatter = (yaml.load(match[1]) as Record<string, string | undefined>) ?? {}
    } catch (yamlError) {
      console.warn(`Failed to parse YAML frontmatter in: ${filePath}`, yamlError)
      // Continue with empty frontmatter
    }

    const body = match[2]

    const mdxOptions = applyMdxPreset({
      remarkPlugins: (defaults) => [remarkGfm, ...defaults],
      rehypePlugins: (defaults) => [rehypeHighlight, ...defaults],
    })

    let compiled
    try {
      compiled = await compile(body, {
        outputFormat: 'function-body',
        ...mdxOptions,
        development: false,
      })
    } catch (compileError) {
      console.error(`MDX compilation failed for: ${filePath}`, compileError)
      throw new Error(`Failed to compile MDX: ${compileError instanceof Error ? compileError.message : String(compileError)}`)
    }

    let Content: MDXContent
    try {
      const result = await run(compiled, {
        ...runtime,
        useMDXComponents: () => mdxComponents,
        baseUrl: import.meta.url,
      })
      Content = result.default as MDXContent
    } catch (runError) {
      console.error(`MDX execution failed for: ${filePath}`, runError)
      throw new Error(`Failed to execute MDX: ${runError instanceof Error ? runError.message : String(runError)}`)
    }

    return {
      title: (frontmatter.title as string) ?? 'Untitled',
      description: frontmatter.description as string | undefined,
      Content: Content as MDXContent,
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error)
    console.error(`Failed to load doc: ${slug?.join('/')}`, {
      error: errorMessage,
      stack: error instanceof Error ? error.stack : undefined,
    })
    // Re-throw the error so Next.js error boundary can handle it
    throw new Error(`Failed to load documentation page "${slug?.join('/') || 'home'}": ${errorMessage}`)
  }
}

// Fallback function for testing
function getFallbackContent(slug?: string[]) {
  if (!slug || slug.length === 0) {
    return {
      title: "Documentation",
      description: "Multi-View Requirements Traceability System - Official Documentation",
      Content: () => <div>Documentation home page</div>
    }
  }
  
  return {
    title: `Debug: ${slug?.join('/')}`,
    description: `Debug page for ${slug?.join('/')}`,
    Content: () => <div>Debug content for {slug?.join('/')}. Slug parameter working but content loading failed.</div>
  }
}

export default async function DocsPage({ params }: { params: Promise<{ slug?: string[] }> }) {
  const resolvedParams = await params
  
  // For empty slug, show fallback content
  if (!resolvedParams.slug || resolvedParams.slug.length === 0) {
    const fallbackContent = getFallbackContent()
    return (
      <DocsPageClient
        slug={resolvedParams.slug}
        heading={{ title: fallbackContent.title, description: fallbackContent.description }}
      >
        <div className="prose prose-sm max-w-none dark:prose-invert prose-headings:font-bold prose-headings:text-foreground prose-p:text-foreground prose-strong:text-foreground prose-code:text-foreground prose-pre:bg-zinc-950 prose-pre:text-zinc-50">
          <fallbackContent.Content components={mdxComponents} />
        </div>
      </DocsPageClient>
    )
  }

  // Try to load the actual content
  const docContent = await getDocContent(resolvedParams.slug)
  
  // If content loading failed, show fallback with warning
  if (!docContent) {
    const fallbackContent = getFallbackContent(resolvedParams.slug)
    return (
      <DocsPageClient
        slug={resolvedParams.slug}
        heading={{ title: fallbackContent.title, description: fallbackContent.description }}
      >
        <div className="prose prose-sm max-w-none dark:prose-invert prose-headings:font-bold prose-headings:text-foreground prose-p:text-foreground prose-strong:text-foreground prose-code:text-foreground prose-pre:bg-zinc-950 prose-pre:text-zinc-50">
          <fallbackContent.Content components={mdxComponents} />
        </div>
      </DocsPageClient>
    )
  }

  return (
    <DocsPageClient
      slug={resolvedParams.slug}
      heading={{ title: docContent.title, description: docContent.description }}
    >
      <div className="prose prose-sm max-w-none dark:prose-invert prose-headings:font-bold prose-headings:text-foreground prose-p:text-foreground prose-strong:text-foreground prose-code:text-foreground prose-pre:bg-zinc-950 prose-pre:text-zinc-50">
        <docContent.Content components={mdxComponents} />
      </div>
    </DocsPageClient>
  )
}
