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

type MDXContent = FC<{ components?: MDXComponents }>

function getDocPath(slug: string[]): string | null {
  let current: any = DOCS_STRUCTURE
  const pathParts: string[] = []

  for (let i = 0; i < slug.length; i++) {
    const segment = slug[i]

    // Check if segment exists in current level
    if (current[segment]) {
      current = current[segment]
      // Add this item's path to our path parts
      if (current.path) {
        pathParts.push(current.path)
      }
      // If this is not the last segment and current has children, move to children
      if (i < slug.length - 1 && current.children) {
        current = current.children
      }
    } else {
      return null
    }
  }

  // Return the full path by joining all path parts
  return pathParts.length > 0 ? pathParts.join('/') : null
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

const mdxComponents: MDXComponents = {
  code: ({ className, children, ...props }) => {
    const language = className?.replace('language-', '')
    if (language === 'mermaid') {
      return (
        <div className="-mx-8 px-8 my-6">
          <MermaidRenderer chart={String(children).replace(/\n$/, '')} />
        </div>
      )
    }
    return (
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
    if (!docPath) return null

    const filePath = join(process.cwd(), 'content/docs', docPath, 'index.mdx')
    await access(filePath)

    const raw = await readFile(filePath, 'utf-8')
    const match = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/)
    if (!match) return null

    const frontmatter = (yaml.load(match[1]) as Record<string, string | undefined>) ?? {}
    const body = match[2]

    const mdxOptions = applyMdxPreset({
      remarkPlugins: (defaults) => [remarkGfm, ...defaults],
      rehypePlugins: (defaults) => [rehypeHighlight, ...defaults],
    })

    const compiled = await compile(body, {
      outputFormat: 'function-body',
      ...mdxOptions,
      development: false,
    })

    const { default: Content } = await run(compiled, {
      ...runtime,
      useMDXComponents: () => mdxComponents,
      baseUrl: import.meta.url,
    })

    return {
      title: (frontmatter.title as string) ?? 'Untitled',
      description: frontmatter.description as string | undefined,
      Content: Content as MDXContent,
    }
  } catch (error) {
    console.error(`Failed to load doc: ${slug?.join('/')}`, error)
    return null
  }
}

export default async function DocsPage({ params }: { params: { slug?: string[] } }) {
  const docContent = await getDocContent(params.slug)

  return (
    <DocsPageClient
      slug={params.slug}
      heading={docContent ? { title: docContent.title, description: docContent.description } : undefined}
    >
      {docContent?.Content ? (
        <div className="prose prose-sm max-w-none dark:prose-invert">
          <docContent.Content components={mdxComponents} />
        </div>
      ) : null}
    </DocsPageClient>
  )
}
