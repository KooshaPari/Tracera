/**
 * ModelSelector - Combobox for selecting AI provider and model
 */

import { Sparkles } from 'lucide-react';
import { useCallback, useMemo } from 'react';

import type { AIModel } from '@/lib/ai/types';

import { getEnabledProviders, getModel } from '@/lib/ai/modelRegistry';
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, cn } from '@tracertm/ui';

interface ModelSelectorProps {
  value: AIModel;
  onChange: (model: AIModel) => void;
  disabled?: boolean;
  className?: string;
}

const ProviderGroup = ({ models, name }: { models: AIModel[]; name: string }) => (
  <SelectGroup>
    <div className='text-muted-foreground px-2 py-1.5 text-xs font-semibold'>{name}</div>
    {models.map((model) => (
      <SelectItem key={model.id} value={model.id} className='text-xs'>
        <span className='block truncate'>{model.name}</span>
      </SelectItem>
    ))}
  </SelectGroup>
);

export const ModelSelector = ({ value, onChange, disabled, className }: ModelSelectorProps) => {
  const providers = useMemo(() => getEnabledProviders(), []);

  const handleValueChange = useCallback(
    (modelId: string) => {
      const model = getModel(modelId);
      if (model) {
        onChange(model);
      }
    },
    [onChange],
  );

  return (
    <Select value={value.id} onValueChange={handleValueChange} disabled={disabled ?? false}>
      <SelectTrigger
        className={cn('h-8 min-w-0 text-xs gap-1.5 bg-background/50 border-muted', className)}
      >
        <div className='flex min-w-0 flex-1 items-center gap-1.5'>
          <Sparkles className='text-primary h-3 w-3 flex-shrink-0' />
          <span className='min-w-0 flex-1 truncate'>{value.name}</span>
        </div>
      </SelectTrigger>
      <SelectContent>
        {providers.map((provider) => (
          <ProviderGroup key={provider.id} models={provider.models} name={provider.name} />
        ))}
      </SelectContent>
    </Select>
  );
};
