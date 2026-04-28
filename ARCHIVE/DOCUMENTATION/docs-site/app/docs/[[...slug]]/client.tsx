'use client'

import Link from 'next/link'
import { useState, useEffect, type ReactNode } from 'react'
import { ChevronDown, ChevronRight, BookOpen, Rocket, FileText, Zap, Wrench, RotateCcw } from 'lucide-react'
import { DOCS_STRUCTURE } from './structure'

const STORAGE_KEY = 'docs-expanded-sections'

interface DocsPageClientProps {
  slug?: string[]
  heading?: {
    title: string
    description?: string
  }
  children?: ReactNode
}

function getIconComponent(iconName?: string) {
  const iconMap: { [key: string]: any } = {
    'Rocket': Rocket,
    'BookOpen': BookOpen,
    'Zap': Zap,
    'Wrench': Wrench,
    'RotateCcw': RotateCcw,
    'FileText': FileText,
  }
  return iconMap[iconName || ''] || null
}

function getPathString(path: string[]): string {
  return path.join('/')
}

interface NavItemProps {
  itemKey: string
  value: any
  path: string[]
  depth: number
  currentSlug?: string[]
  expandedSections: Set<string>
  toggleSection: (path: string) => void
}

function NavItem({
  itemKey,
  value,
  path,
  depth,
  currentSlug,
  expandedSections,
  toggleSection,
}: NavItemProps) {
  const newPath = [...path, itemKey]
  const pathString = getPathString(newPath)
  const isExpanded = expandedSections.has(pathString)
  const hasChildren = value.children && Object.keys(value.children).length > 0
  const isActive = currentSlug?.join('/') === pathString

  return (
    <div>
      <button
        onClick={() => hasChildren && toggleSection(pathString)}
        className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
          isActive ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'
        }`}
        style={{ paddingLeft: `${12 + depth * 16}px` }}
      >
        <div className="flex items-center gap-2">
          {hasChildren && (isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />)}
          {!hasChildren && <div className="w-4" />}
          <Link href={`/docs/${pathString}`} className="flex-1">
            {value.title}
          </Link>
        </div>
      </button>
      {hasChildren && isExpanded && (
        <div>
          {Object.entries(value.children).map(([key, child]: [string, any]) => (
            <NavItem
              key={key}
              itemKey={key}
              value={child}
              path={newPath}
              depth={depth + 1}
              currentSlug={currentSlug}
              expandedSections={expandedSections}
              toggleSection={toggleSection}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function SidebarNav({ slug }: { slug?: string[] }) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(() => {
    if (typeof window === 'undefined') return new Set()
    try {
      const stored = sessionStorage.getItem(STORAGE_KEY)
      return stored ? new Set(JSON.parse(stored)) : new Set()
    } catch {
      return new Set()
    }
  })

  useEffect(() => {
    if (!slug || slug.length === 0) return
    const pathsToExpand = new Set<string>()
    let currentPath: string[] = []
    slug.forEach((segment) => {
      currentPath.push(segment)
      pathsToExpand.add(getPathString(currentPath))
    })
    setExpandedSections((prev) => {
      const newSet = new Set([...prev, ...pathsToExpand])
      if (typeof window !== 'undefined') {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify([...newSet]))
      }
      return newSet
    })
  }, [slug])

  const toggleSection = (path: string) => {
    setExpandedSections((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(path)) {
        newSet.delete(path)
      } else {
        newSet.add(path)
      }
      if (typeof window !== 'undefined') {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify([...newSet]))
      }
      return newSet
    })
  }

  return (
    <nav className="p-4 space-y-1">
      {Object.entries(DOCS_STRUCTURE).map(([key, value]: [string, any]) => (
        <NavItem
          key={key}
          itemKey={key}
          value={value}
          path={[]}
          depth={0}
          currentSlug={slug}
          expandedSections={expandedSections}
          toggleSection={toggleSection}
        />
      ))}
    </nav>
  )
}

export function DocsPageClient({ slug, heading, children }: DocsPageClientProps) {
  return (
    <div className="flex h-screen">
      <aside className="w-80 border-r bg-muted/50 overflow-y-auto">
        <div className="sticky top-0 bg-background border-b p-4 z-10">
          <Link href="/docs" className="flex items-center gap-2 font-bold text-lg hover:opacity-75 transition-opacity">
            <BookOpen className="w-5 h-5" />
            TraceRTM Docs
          </Link>
        </div>
        <SidebarNav slug={slug} />
      </aside>

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto p-8">
          {heading ? (
            <>
              <h1 className="text-4xl font-bold mb-2">{heading.title}</h1>
              {heading.description && <p className="text-lg text-muted-foreground mb-6">{heading.description}</p>}
              {children}
            </>
          ) : (
            <>
              <h1 className="text-4xl font-bold mb-4">Documentation</h1>
              <p className="text-lg text-muted-foreground mb-8">Select a topic from the sidebar to get started.</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(DOCS_STRUCTURE).map(([key, value]: [string, any]) => {
                  const IconComponent = getIconComponent(value.icon)
                  return (
                    <Link
                      key={key}
                      href={`/docs/${key}`}
                      className="p-4 border rounded-lg hover:border-primary hover:bg-muted transition-colors"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        {IconComponent && <IconComponent className="w-5 h-5 text-primary" />}
                        <h2 className="font-bold">{value.title}</h2>
                      </div>
                      <p className="text-sm text-muted-foreground">{value.description}</p>
                    </Link>
                  )
                })}
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  )
}
