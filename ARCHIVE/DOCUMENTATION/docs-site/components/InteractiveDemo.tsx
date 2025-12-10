'use client'

import { useState } from 'react'

export interface DemoPane {
  label: string
  icon: string
  gifUrl?: string
  gifAlt?: string
  description?: string
  code?: string
}

export function InteractiveDemo({ 
  title, 
  description, 
  panes 
}: { 
  title: string
  description?: string
  panes: DemoPane[]
}) {
  const [activePane, setActivePane] = useState(0)
  const activeDemo = panes[activePane]

  return (
    <div className="my-8 border rounded-lg overflow-hidden bg-muted/30">
      <div className="p-4 border-b bg-muted/50">
        <h3 className="font-semibold text-lg mb-2">{title}</h3>
        {description && <p className="text-sm text-foreground/75">{description}</p>}
      </div>

      {/* Pane Selector */}
      <div className="flex border-b bg-muted/20">
        {panes.map((pane, idx) => (
          <button
            key={idx}
            onClick={() => setActivePane(idx)}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activePane === idx
                ? 'bg-primary text-primary-foreground border-b-2 border-primary'
                : 'hover:bg-muted text-foreground/75'
            }`}
          >
            <span className="mr-2">{pane.icon}</span>
            {pane.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="p-6">
        {activeDemo.gifUrl && (
          <div className="mb-4">
            <img 
              src={activeDemo.gifUrl} 
              alt={activeDemo.gifAlt || activeDemo.label}
              className="w-full rounded-lg border border-muted"
            />
          </div>
        )}
        {activeDemo.description && (
          <p className="text-sm text-foreground/80 mb-4">{activeDemo.description}</p>
        )}
        {activeDemo.code && (
          <pre className="bg-muted p-4 rounded text-sm overflow-x-auto">
            <code>{activeDemo.code}</code>
          </pre>
        )}
      </div>
    </div>
  )
}

