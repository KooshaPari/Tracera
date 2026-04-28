'use client'

import { useEffect, useRef } from 'react'
import mermaid from 'mermaid'

interface MermaidClientProps {
  chart: string
}

export default function MermaidClient({ chart }: MermaidClientProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (containerRef.current) {
      mermaid.contentLoaded()
      mermaid.run()
    }
  }, [chart])

  return (
    <div
      ref={containerRef}
      className="mermaid w-full flex items-center justify-center"
      style={{ minHeight: '400px' }}
    >
      {chart}
    </div>
  )
}

