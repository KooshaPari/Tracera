/**
 * ItemTypeSelector Component
 *
 * Displays available item types for a given view as selectable cards.
 * Shows icon, label, description, and spec requirement status.
 */

import type { LucideIcon } from 'lucide-react';

import {
  BookOpen,
  Box,
  Bug,
  CheckSquare,
  Code,
  Database,
  FileCode,
  FileText,
  FlaskConical,
  Layers,
  Layout,
  Shield,
  Sparkles,
  Zap,
} from 'lucide-react';

import type { ItemTypeConfig } from '@/lib/itemTypeConfig';
import type { ViewType } from '@tracertm/types';

import { getItemTypesForView } from '@/lib/itemTypeConfig';

// Icon mapping for item types
const ICON_MAP: Record<string, LucideIcon> = {
  api: Code,
  architecture: Box,
  bug: Bug,
  code: FileCode,
  database: Database,
  document: FileText,
  epic: Layers,
  feature: Sparkles,
  generic: Box,
  performance: Zap,
  requirement: FileText,
  security: Shield,
  story: BookOpen,
  task: CheckSquare,
  test: FlaskConical,
  wireframe: Layout,
};

interface ItemTypeSelectorProps {
  view: ViewType;
  selectedType?: string | undefined;
  onSelect: (type: string) => void;
}

export function ItemTypeSelector({ view, selectedType, onSelect }: ItemTypeSelectorProps) {
  const types = getItemTypesForView(view);

  if (types.length === 0) {
    return (
      <div className='text-muted-foreground text-sm'>No item types available for this view.</div>
    );
  }

  return (
    <div className='grid grid-cols-2 gap-3 md:grid-cols-3'>
      {types.map((config: ItemTypeConfig) => {
        const IconComponent = ICON_MAP[config.icon] ?? Box;
        const isSelected = selectedType === config.type;

        return (
          <button
            key={config.type}
            type='button'
            onClick={() => {
              onSelect(config.type);
            }}
            aria-pressed={isSelected}
            className={`group relative flex flex-col items-start gap-2 rounded-lg border-2 p-4 text-left transition-all ${
              isSelected
                ? 'border-primary bg-primary/5 shadow-sm'
                : 'border-border hover:border-primary/50 hover:bg-accent'
            } focus-visible:ring-primary focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2`}
          >
            {/* Icon */}
            <div
              className={`rounded-md p-2 transition-colors ${isSelected ? 'bg-primary/10' : 'bg-muted group-hover:bg-primary/10'} `}
            >
              <IconComponent
                className={`h-5 w-5 ${isSelected ? 'text-primary' : 'text-muted-foreground'}`}
                aria-hidden='true'
              />
            </div>

            {/* Label */}
            <div className='flex-1'>
              <div className={`font-medium ${isSelected ? 'text-primary' : 'text-foreground'}`}>
                {config.label}
              </div>
              <div className='text-muted-foreground mt-1 text-xs'>{config.description}</div>
            </div>

            {/* Spec Required Badge */}
            {config.requiresSpec && (
              <div className='absolute top-2 right-2'>
                <span className='inline-flex items-center rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'>
                  Spec Required
                </span>
              </div>
            )}
          </button>
        );
      })}
    </div>
  );
}
