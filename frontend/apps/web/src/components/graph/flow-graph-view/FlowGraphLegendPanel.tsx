interface FlowGraphLegendPanelProps {
  visibleLegendEntries: Array<[string, string]>;
  legendColorStyles: Map<string, { backgroundColor: string }>;
}

export function FlowGraphLegendPanel({
  visibleLegendEntries,
  legendColorStyles,
}: FlowGraphLegendPanelProps) {
  return (
    <div className='bg-card/90 flex max-w-[90vw] flex-wrap gap-1 rounded-md border p-1.5 text-[9px] backdrop-blur-sm sm:gap-2 sm:rounded-lg sm:p-2 sm:text-[10px]'>
      {visibleLegendEntries.map(([type]) => (
        <div key={type} className='flex min-w-0 items-center gap-0.5 sm:gap-1'>
          <div
            className='h-2 w-4 shrink-0 rounded sm:h-2.5 sm:w-5'
            style={legendColorStyles.get(type)}
          />
          <span className='truncate capitalize'>{type.replaceAll('_', ' ')}</span>
        </div>
      ))}
    </div>
  );
}
