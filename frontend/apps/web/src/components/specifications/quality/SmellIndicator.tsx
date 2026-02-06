import type { ReactElement } from 'react';

import { ShieldAlert } from 'lucide-react';

import type { SmellType } from '@tracertm/types';

import { Badge, Tooltip, TooltipContent, TooltipTrigger } from '@tracertm/ui';

interface SmellIndicatorProps {
  smells: SmellType[];
  className?: string;
}

const smellLabels: Record<SmellType, string> = {
  ambiguous_adverbs: 'Ambiguous Adverb',
  comparative: 'Comparative',
  incomplete_references: 'Incomplete Ref',
  loopholes: 'Loophole',
  negative_statements: 'Negative',
  open_ended: 'Open Ended',
  subjective: 'Subjective',
  superlative: 'Superlative',
  vague_pronouns: 'Vague Pronoun',
};

const smellDescriptions: Record<SmellType, string> = {
  ambiguous_adverbs: "Avoid vague qualifiers like 'usually', 'often', 'significantly'.",
  comparative: "Avoid relative terms like 'better', 'faster' without baseline.",
  incomplete_references: "Avoid 'see documentation' without specific link/ID.",
  loopholes: "Avoid optionality terms like 'if possible', 'as appropriate'.",
  negative_statements: 'Avoid negative constraints; state what the system SHALL do.',
  open_ended: "Avoid unquantifiable terms like 'et cetera', 'and so on'.",
  subjective: "Avoid user-dependent terms like 'user-friendly', 'easy'.",
  superlative: "Avoid absolute terms like 'best', 'fastest', 'highest'.",
  vague_pronouns: "Avoid 'it', 'this', 'that' without clear antecedent.",
};

const SmellIndicator = ({
  smells,
  className = '',
}: SmellIndicatorProps): ReactElement | undefined => {
  if (smells.length === 0) {
    return undefined;
  }

  return (
    <div className={`flex flex-wrap gap-2 ${className}`}>
      {smells.map((smell) => (
        <Tooltip key={smell}>
          <TooltipTrigger asChild>
            <Badge
              variant='destructive'
              className='cursor-help gap-1 border-red-200 bg-red-50 pr-2 pl-1.5 text-red-600 hover:bg-red-100'
            >
              <ShieldAlert className='h-3 w-3' />
              {smellLabels[smell] || smell}
            </Badge>
          </TooltipTrigger>
          <TooltipContent className='max-w-xs'>
            <p className='mb-1 font-semibold'>{smellLabels[smell]}</p>
            <p className='text-muted-foreground text-xs'>{smellDescriptions[smell]}</p>
          </TooltipContent>
        </Tooltip>
      ))}
    </div>
  );
};

export { SmellIndicator };
