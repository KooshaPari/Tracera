import type * as React from 'react';
import type { ArrayPath, Control, FieldArray, FieldValues } from 'react-hook-form';

import { Plus, Trash2 } from 'lucide-react';
import { useFieldArray } from 'react-hook-form';

import { cn } from '@/lib/utils';
import { Button } from '@tracertm/ui';

export interface FormArrayFieldProps<T extends FieldValues> {
  control: Control<T>;
  /** Array path (e.g. "subtasks"). Use string when Control<T> is inferred from a resolver and causes ArrayPath<T> to narrow incorrectly. */
  name: ArrayPath<T> | (string & {});
  label: string;
  helpText?: string;
  renderField: (index: number) => React.ReactNode;
  defaultValue?: FieldArray<T, ArrayPath<T>>;
  addButtonLabel?: string;
  removeButtonLabel?: string;
  minItems?: number;
  maxItems?: number;
  className?: string;
}

export function FormArrayField<T extends FieldValues>({
  control,
  name,
  label,
  helpText,
  renderField,
  defaultValue,
  addButtonLabel = 'Add item',
  removeButtonLabel = 'Remove',
  minItems = 0,
  maxItems,
  className,
}: FormArrayFieldProps<T>) {
  const { fields, append, remove } = useFieldArray({
    control,
    name: name as ArrayPath<T>,
  });

  const canAdd = !maxItems || fields.length < maxItems;
  const canRemove = fields.length > minItems;

  return (
    <div className={cn('space-y-4', className)}>
      <div className='flex items-center justify-between'>
        <div>
          <label className='text-foreground block text-sm font-medium'>{label}</label>
          {helpText && <p className='text-muted-foreground mt-1 text-xs'>{helpText}</p>}
        </div>
        <Button
          type='button'
          variant='outline'
          size='sm'
          onClick={() => {
            if (defaultValue !== undefined) {
              append(defaultValue);
            } else {
              append({} as FieldArray<T, ArrayPath<T>>);
            }
          }}
          disabled={!canAdd}
          aria-label={addButtonLabel}
        >
          <Plus className='mr-1 h-4 w-4' aria-hidden='true' />
          {addButtonLabel}
        </Button>
      </div>

      <div className='space-y-3'>
        {fields.length === 0 ? (
          <p className='text-muted-foreground text-sm italic'>
            No items added yet. Click "{addButtonLabel}" to get started.
          </p>
        ) : (
          fields.map((field, index) => (
            <div
              key={field.id}
              className='bg-muted/50 flex items-start gap-2 rounded-lg border p-3'
            >
              <div className='flex-1'>{renderField(index)}</div>
              <Button
                type='button'
                variant='ghost'
                size='icon'
                onClick={() => {
                  remove(index);
                }}
                disabled={!canRemove}
                aria-label={`${removeButtonLabel} item ${index + 1}`}
                className='mt-1 shrink-0'
              >
                <Trash2 className='text-destructive h-4 w-4' aria-hidden='true' />
              </Button>
            </div>
          ))
        )}
      </div>

      {maxItems && (
        <p className='text-muted-foreground text-xs'>
          {fields.length} / {maxItems} items
        </p>
      )}
    </div>
  );
}

FormArrayField.displayName = 'FormArrayField';
