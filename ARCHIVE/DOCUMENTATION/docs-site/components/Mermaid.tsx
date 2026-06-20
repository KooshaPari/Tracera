'use client'

import { useEffect, useRef } from 'react'
import mermaid from 'mermaid'

interface MermaidProps {
  chart: string
}

export default function Mermaid({ chart }: MermaidProps) {
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
      className="flex justify-center my-8 p-4 bg-muted rounded-lg overflow-x-auto"
    >
      <div className="mermaid">
        {chart}
      </div>
    </div>
  )
}

