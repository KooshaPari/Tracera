import { zodResolver } from '@hookform/resolvers/zod';
import { X } from 'lucide-react';
import { useCallback, useEffect, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import {
  announceToScreenReader,
  createFocusTrap,
  focusFirst,
  restoreFocus,
  saveFocus,
} from '@/lib/focus-management';

const viewTypes = [
  'FEATURE',
  'CODE',
  'TEST',
  'API',
  'DATABASE',
  'WIREFRAME',
  'DOCUMENTATION',
  'DEPLOYMENT',
] as const;
const statusOptions = ['todo', 'in_progress', 'done', 'blocked', 'cancelled'] as const;
const priorityOptions = ['low', 'medium', 'high', 'critical'] as const;

const itemSchema = z.object({
  description: z.string().max(5000).optional(),
  owner: z.string().max(255).optional(),
  parentId: z.string().uuid().optional().or(z.literal('')),
  priority: z.enum(priorityOptions),
  status: z.enum(statusOptions),
  title: z.string().min(1, 'Title is required').max(500, 'Title too long'),
  type: z.string().min(1, 'Type is required'),
  view: z.enum(viewTypes),
});

type ItemFormData = z.infer<typeof itemSchema>;

interface CreateItemFormProps {
  onSubmit: (data: ItemFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
  defaultView?: (typeof viewTypes)[number];
  /** Modal title (e.g. "Create Feature"). Default: "Create Item" */
  title?: string;
  /** Submit button label (e.g. "Create Feature"). Default: "Create Item" */
  submitLabel?: string;
  /** Submit button label when loading (e.g. "Creating..."). Default: "Creating..." */
  submitBusyLabel?: string;
}

export function CreateItemForm({
  onSubmit,
  onCancel,
  isLoading,
  defaultView = 'FEATURE',
  title: titleProp = 'Create Item',
  submitLabel = 'Create Item',
  submitBusyLabel = 'Creating...',
}: CreateItemFormProps) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const formRef = useRef<HTMLFormElement>(null);
  const savedFocusRef = useRef<HTMLElement | null>(null);
  const cleanupFocusTrapRef = useRef<(() => void) | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<ItemFormData>({
    defaultValues: { priority: 'medium', status: 'todo', view: defaultView },
    mode: 'onBlur',
    resolver: zodResolver(itemSchema),
  });

  const selectedView = watch('view');
  const typeOptions: Record<string, string[]> = {
    API: ['endpoint', 'schema', 'model'],
    CODE: ['module', 'file', 'function', 'class'],
    DATABASE: ['table', 'column', 'index'],
    DEPLOYMENT: ['environment', 'release', 'config'],
    DOCUMENTATION: ['guide', 'reference', 'tutorial', 'changelog'],
    FEATURE: ['epic', 'feature', 'story', 'task'],
    TEST: ['suite', 'case', 'scenario'],
    WIREFRAME: ['screen', 'component', 'flow'],
  };

  // Handle form submission with error announcements
  const onSubmitWithAnnouncement = useCallback(
    async (data: ItemFormData) => {
      try {
        await Promise.resolve(onSubmit(data));
        announceToScreenReader('Item created successfully', 'polite');
      } catch {
        announceToScreenReader(
          'Error creating item. Please check the form and try again.',
          'assertive',
        );
      }
    },
    [onSubmit],
  );

  // Handle Escape key to close dialog
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onCancel();
      }
    },
    [onCancel],
  );

  useEffect(() => {
    // Save current focus
    savedFocusRef.current = saveFocus();

    // Setup event listeners
    document.addEventListener('keydown', handleKeyDown);

    // Create focus trap
    if (dialogRef.current) {
      cleanupFocusTrapRef.current = createFocusTrap(dialogRef.current, onCancel);

      // Focus first input on mount
      focusFirst(dialogRef.current);

      // Announce dialog opened
      announceToScreenReader(
        `${titleProp} dialog opened. Fill in the required fields marked with an asterisk.`,
        'polite',
      );
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      if (cleanupFocusTrapRef.current) {
        cleanupFocusTrapRef.current();
      }
      // Restore focus when closing
      if (savedFocusRef.current) {
        restoreFocus(savedFocusRef.current);
      }
    };
  }, [handleKeyDown, onCancel, titleProp]);

  return (
    <div className='fixed inset-0 z-50 flex items-center justify-center'>
      {/* Backdrop */}
      <div
        className='fixed inset-0 bg-black/50 backdrop-blur-sm'
        onClick={onCancel}
        aria-hidden='true'
      />

      {/* Dialog */}
      <div
        ref={dialogRef}
        role='dialog'
        aria-modal='true'
        aria-labelledby='dialog-title'
        aria-describedby='dialog-description'
        className='bg-background focus-visible:ring-primary relative max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-xl border p-6 shadow-2xl focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2'
        tabIndex={-1}
      >
        <div className='flex items-center justify-between'>
          <h2 id='dialog-title' className='text-lg font-semibold'>
            {titleProp}
          </h2>
          <p id='dialog-description' className='sr-only'>
            Fill in the required fields marked with an asterisk and click {submitLabel} to submit.
          </p>
          <button
            onClick={onCancel}
            aria-label='Close dialog'
            className='hover:bg-accent focus-visible:ring-primary rounded-lg p-1 focus:outline-none focus-visible:ring-2'
          >
            <X className='h-5 w-5' aria-hidden='true' />
          </button>
        </div>

        <form
          ref={formRef}
          onSubmit={handleSubmit(onSubmitWithAnnouncement)}
          className='mt-6 space-y-4'
        >
          <div className='grid gap-4 sm:grid-cols-2'>
            <div>
              <label htmlFor='view' className='block text-sm font-medium'>
                View{' '}
                <span className='text-red-500' aria-label='required'>
                  *
                </span>
              </label>
              <select
                id='view'
                aria-describedby='view-help'
                aria-required='true'
                {...register('view')}
                className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
              >
                {viewTypes.map((v) => (
                  <option key={v} value={v}>
                    {v}
                  </option>
                ))}
              </select>
              <span id='view-help' className='text-muted-foreground mt-1 block text-xs'>
                Select the view type for this item
              </span>
            </div>
            <div>
              <label htmlFor='type' className='block text-sm font-medium'>
                Type{' '}
                <span className='text-red-500' aria-label='required'>
                  *
                </span>
              </label>
              <select
                id='type'
                aria-describedby={errors.type ? 'type-error' : 'type-help'}
                aria-required='true'
                aria-invalid={Boolean(errors.type)}
                {...register('type')}
                className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
              >
                {typeOptions[selectedView]?.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
              {errors.type ? (
                <p
                  id='type-error'
                  role='alert'
                  className='mt-1 text-sm text-red-500'
                  aria-live='polite'
                  aria-atomic='true'
                >
                  {errors.type.message}
                </p>
              ) : (
                <span id='type-help' className='text-muted-foreground mt-1 block text-xs'>
                  Select from options based on your chosen view
                </span>
              )}
            </div>
          </div>

          <div>
            <label htmlFor='title' className='block text-sm font-medium'>
              Title{' '}
              <span className='text-red-500' aria-label='required'>
                *
              </span>
            </label>
            <input
              id='title'
              {...register('title')}
              placeholder='Enter item title'
              aria-describedby={errors.title ? 'title-error' : 'title-help'}
              aria-required='true'
              aria-invalid={Boolean(errors.title)}
              className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
            />
            {errors.title ? (
              <p
                id='title-error'
                role='alert'
                className='mt-1 text-sm text-red-500'
                aria-live='polite'
                aria-atomic='true'
              >
                {errors.title.message}
              </p>
            ) : (
              <span id='title-help' className='text-muted-foreground mt-1 block text-xs'>
                Give this item a clear, descriptive title
              </span>
            )}
          </div>

          <div>
            <label htmlFor='description' className='block text-sm font-medium'>
              Description
            </label>
            <textarea
              id='description'
              {...register('description')}
              rows={3}
              placeholder='Describe this item...'
              aria-describedby='description-help'
              className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
            />
            <span id='description-help' className='text-muted-foreground mt-1 block text-xs'>
              Optional: Provide additional context or details
            </span>
          </div>

          <div className='grid gap-4 sm:grid-cols-2'>
            <div>
              <label htmlFor='status' className='block text-sm font-medium'>
                Status
              </label>
              <select
                id='status'
                aria-describedby='status-help'
                {...register('status')}
                className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
              >
                {statusOptions.map((s) => (
                  <option key={s} value={s}>
                    {s.replace('_', ' ')}
                  </option>
                ))}
              </select>
              <span id='status-help' className='text-muted-foreground mt-1 block text-xs'>
                Current status of this item
              </span>
            </div>
            <div>
              <label htmlFor='priority' className='block text-sm font-medium'>
                Priority
              </label>
              <select
                id='priority'
                aria-describedby='priority-help'
                {...register('priority')}
                className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
              >
                {priorityOptions.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
              <span id='priority-help' className='text-muted-foreground mt-1 block text-xs'>
                Importance level
              </span>
            </div>
          </div>

          <div>
            <label htmlFor='owner' className='block text-sm font-medium'>
              Owner
            </label>
            <input
              id='owner'
              {...register('owner')}
              placeholder='Assigned to...'
              aria-describedby='owner-help'
              className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
            />
            <span id='owner-help' className='text-muted-foreground mt-1 block text-xs'>
              Optional: Person responsible for this item
            </span>
          </div>

          <div className='flex gap-3 pt-4'>
            <button
              type='button'
              onClick={onCancel}
              aria-label='Discard changes and close dialog'
              className='hover:bg-accent focus-visible:ring-primary flex-1 rounded-lg border px-4 py-2 focus:outline-none focus-visible:ring-2'
            >
              Cancel
            </button>
            <button
              type='submit'
              disabled={isLoading ?? isSubmitting}
              aria-busy={isLoading ?? isSubmitting}
              aria-label={isLoading || isSubmitting ? submitBusyLabel : submitLabel}
              className='bg-primary text-primary-foreground focus-visible:ring-primary flex-1 rounded-lg px-4 py-2 focus:outline-none focus-visible:ring-2 disabled:opacity-50'
            >
              {isLoading || isSubmitting ? submitBusyLabel : submitLabel}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
