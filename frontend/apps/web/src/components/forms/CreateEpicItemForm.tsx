import type { Resolver } from 'react-hook-form';

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

const statusOptions = ['todo', 'in_progress', 'done', 'blocked', 'cancelled'] as const;
const priorityOptions = ['low', 'medium', 'high', 'critical'] as const;

const epicSchema = z.object({
  business_value: z
    .union([z.number(), z.string()])
    .transform((val) => (typeof val === 'string' ? Number.parseFloat(val) : val))
    .pipe(z.number().min(0, 'Business value must be non-negative'))
    .optional(),
  completed_story_count: z
    .union([z.number(), z.string()])
    .transform((val) => (typeof val === 'string' ? Number.parseFloat(val) : val))
    .pipe(z.number().min(0, 'Completed story count must be non-negative'))
    .optional(),
  description: z.string().max(5000).optional(),
  priority: z.enum(priorityOptions),
  status: z.enum(statusOptions),
  story_count: z
    .union([z.number(), z.string()])
    .transform((val) => (typeof val === 'string' ? Number.parseFloat(val) : val))
    .pipe(z.number().min(0, 'Story count must be non-negative'))
    .optional(),
  timeline_end: z.string().optional(),
  timeline_start: z.string().optional(),
  title: z.string().min(1, 'Title is required').max(500, 'Title too long'),
});

type EpicFormData = z.infer<typeof epicSchema>;

interface CreateEpicItemFormProps {
  onSubmit: (data: EpicFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function CreateEpicItemForm({ onSubmit, onCancel, isLoading }: CreateEpicItemFormProps) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const formRef = useRef<HTMLFormElement>(null);
  const savedFocusRef = useRef<HTMLElement | null>(null);
  const cleanupFocusTrapRef = useRef<(() => void) | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<EpicFormData>({
    defaultValues: { priority: 'medium', status: 'todo' },
    mode: 'onBlur',
    resolver: zodResolver(epicSchema) as Resolver<EpicFormData>,
  });

  const onSubmitWithAnnouncement = useCallback(
    async (data: EpicFormData) => {
      try {
        await Promise.resolve(onSubmit(data));
        announceToScreenReader('Epic created successfully', 'polite');
      } catch {
        announceToScreenReader(
          'Error creating epic. Please check the form and try again.',
          'assertive',
        );
      }
    },
    [onSubmit],
  );

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
    savedFocusRef.current = saveFocus();
    document.addEventListener('keydown', handleKeyDown);

    if (dialogRef.current) {
      cleanupFocusTrapRef.current = createFocusTrap(dialogRef.current, onCancel);
      focusFirst(dialogRef.current);
      announceToScreenReader(
        'Create epic dialog opened. Fill in the required fields marked with an asterisk.',
        'polite',
      );
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      if (cleanupFocusTrapRef.current) {
        cleanupFocusTrapRef.current();
      }
      if (savedFocusRef.current) {
        restoreFocus(savedFocusRef.current);
      }
    };
  }, [handleKeyDown, onCancel]);

  return (
    <div className='fixed inset-0 z-50 flex items-center justify-center'>
      <div
        className='fixed inset-0 bg-black/50 backdrop-blur-sm'
        onClick={onCancel}
        aria-hidden='true'
      />

      <div
        ref={dialogRef}
        role='dialog'
        aria-modal='true'
        aria-labelledby='dialog-title'
        aria-describedby='dialog-description'
        className='bg-background focus-visible:ring-primary relative max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-xl border p-6 shadow-2xl focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2'
        tabIndex={-1}
      >
        <div className='flex items-center justify-between'>
          <h2 id='dialog-title' className='text-lg font-semibold'>
            Create Epic
          </h2>
          <p id='dialog-description' className='sr-only'>
            Fill in the required fields marked with an asterisk and click Create Epic to submit.
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
          onSubmit={handleSubmit(onSubmitWithAnnouncement as (data: EpicFormData) => void)}
          className='mt-6 space-y-6'
        >
          {/* Epic Details Section */}
          <div className='space-y-4'>
            <h3 className='text-md border-b pb-2 font-medium'>Epic Details</h3>

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
                placeholder='Enter epic title'
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
                  Give this epic a clear, descriptive title
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
                placeholder='Describe this epic...'
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
                  Current status of this epic
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
          </div>

          {/* Epic Specification Section */}
          <div className='space-y-4'>
            <h3 className='text-md border-b pb-2 font-medium'>Epic Specification</h3>

            <div>
              <label htmlFor='business_value' className='block text-sm font-medium'>
                Business Value
              </label>
              <input
                id='business_value'
                type='number'
                min={0}
                {...register('business_value')}
                placeholder='e.g., 1000'
                aria-describedby={
                  errors.business_value ? 'business_value-error' : 'business_value-help'
                }
                aria-invalid={Boolean(errors.business_value)}
                className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
              />
              {errors.business_value ? (
                <p
                  id='business_value-error'
                  role='alert'
                  className='mt-1 text-sm text-red-500'
                  aria-live='polite'
                  aria-atomic='true'
                >
                  {errors.business_value.message}
                </p>
              ) : (
                <span id='business_value-help' className='text-muted-foreground mt-1 block text-xs'>
                  Optional: Estimated business value
                </span>
              )}
            </div>

            <div className='grid gap-4 sm:grid-cols-2'>
              <div>
                <label htmlFor='timeline_start' className='block text-sm font-medium'>
                  Timeline Start
                </label>
                <input
                  id='timeline_start'
                  type='date'
                  {...register('timeline_start')}
                  aria-describedby='timeline_start-help'
                  className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
                />
                <span id='timeline_start-help' className='text-muted-foreground mt-1 block text-xs'>
                  Optional: Start date for this epic
                </span>
              </div>
              <div>
                <label htmlFor='timeline_end' className='block text-sm font-medium'>
                  Timeline End
                </label>
                <input
                  id='timeline_end'
                  type='date'
                  {...register('timeline_end')}
                  aria-describedby='timeline_end-help'
                  className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
                />
                <span id='timeline_end-help' className='text-muted-foreground mt-1 block text-xs'>
                  Optional: Target completion date
                </span>
              </div>
            </div>

            <div className='grid gap-4 sm:grid-cols-2'>
              <div>
                <label htmlFor='story_count' className='block text-sm font-medium'>
                  Story Count
                </label>
                <input
                  id='story_count'
                  type='number'
                  min={0}
                  {...register('story_count')}
                  placeholder='e.g., 10'
                  aria-describedby={errors.story_count ? 'story_count-error' : 'story_count-help'}
                  aria-invalid={Boolean(errors.story_count)}
                  className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
                />
                {errors.story_count ? (
                  <p
                    id='story_count-error'
                    role='alert'
                    className='mt-1 text-sm text-red-500'
                    aria-live='polite'
                    aria-atomic='true'
                  >
                    {errors.story_count.message}
                  </p>
                ) : (
                  <span id='story_count-help' className='text-muted-foreground mt-1 block text-xs'>
                    Optional: Total number of user stories
                  </span>
                )}
              </div>
              <div>
                <label htmlFor='completed_story_count' className='block text-sm font-medium'>
                  Completed Story Count
                </label>
                <input
                  id='completed_story_count'
                  type='number'
                  min={0}
                  {...register('completed_story_count')}
                  placeholder='e.g., 3'
                  aria-describedby={
                    errors.completed_story_count
                      ? 'completed_story_count-error'
                      : 'completed_story_count-help'
                  }
                  aria-invalid={Boolean(errors.completed_story_count)}
                  className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
                />
                {errors.completed_story_count ? (
                  <p
                    id='completed_story_count-error'
                    role='alert'
                    className='mt-1 text-sm text-red-500'
                    aria-live='polite'
                    aria-atomic='true'
                  >
                    {errors.completed_story_count.message}
                  </p>
                ) : (
                  <span
                    id='completed_story_count-help'
                    className='text-muted-foreground mt-1 block text-xs'
                  >
                    Optional: Number of completed stories
                  </span>
                )}
              </div>
            </div>
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
              aria-label={isLoading || isSubmitting ? 'Creating epic...' : 'Create epic'}
              className='bg-primary text-primary-foreground focus-visible:ring-primary flex-1 rounded-lg px-4 py-2 focus:outline-none focus-visible:ring-2 disabled:opacity-50'
            >
              {isLoading || isSubmitting ? 'Creating...' : 'Create Epic'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
