import MermaidClient from './MermaidClient'

interface MermaidRendererProps {
  chart: string
}

export default function MermaidRenderer({ chart }: MermaidRendererProps) {
  return (
    <div className="my-6 bg-muted rounded-lg overflow-auto border border-border">
      <div className="flex justify-center p-0 min-h-96">
        <MermaidClient chart={chart} />
      </div>
    </div>
  )
}

