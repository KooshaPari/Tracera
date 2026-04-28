import type { ArrayPath, Resolver, SubmitHandler } from 'react-hook-form';

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

import { FormArrayField } from './FormArrayField';

const statusOptions = ['todo', 'in_progress', 'done', 'blocked', 'cancelled'] as const;
const priorityOptions = ['low', 'medium', 'high', 'critical'] as const;

const taskSchema = z.object({
  actual_hours: z
    .union([z.number(), z.string()])
    .transform((val) => (typeof val === 'string' ? Number.parseFloat(val) : val))
    .pipe(z.number().min(0, 'Actual hours must be non-negative'))
    .optional(),
  completion_percentage: z
    .union([z.number(), z.string()])
    .transform((val) => (typeof val === 'string' ? Number.parseFloat(val) : val))
    .pipe(
      z
        .number()
        .min(0, 'Completion percentage must be at least 0')
        .max(100, 'Completion percentage cannot exceed 100'),
    )
    .optional(),
  description: z.string().max(5000).optional(),
  estimated_hours: z
    .union([z.number(), z.string()])
    .transform((val) => (typeof val === 'string' ? Number.parseFloat(val) : val))
    .pipe(z.number().min(0, 'Estimated hours must be non-negative'))
    .optional(),
  owner: z.string().max(255).optional(),
  priority: z.enum(priorityOptions),
  status: z.enum(statusOptions),
  subtasks: z.array(z.string().min(1, 'Subtask cannot be empty')),
  title: z.string().min(1, 'Title is required').max(500, 'Title too long'),
});

type TaskFormData = z.infer<typeof taskSchema>;

interface CreateTaskItemFormProps {
  onSubmit: (data: TaskFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export const CreateTaskItemForm = ({ onSubmit, onCancel, isLoading }: CreateTaskItemFormProps) => {
  const dialogRef = useRef<HTMLDivElement>(null);
  const formRef = useRef<HTMLFormElement>(null);
  const savedFocusRef = useRef<HTMLElement | null>(null);
  const cleanupFocusTrapRef = useRef<(() => void) | null>(null);

  const {
    register,
    handleSubmit,
    control,
    formState: { errors, isSubmitting },
  } = useForm<TaskFormData>({
    defaultValues: {
      priority: 'medium',
      status: 'todo',
      subtasks: [],
    },
    mode: 'onBlur',
    resolver: zodResolver(taskSchema) as Resolver<TaskFormData>,
  });

  const onSubmitWithAnnouncement = useCallback(
    async (data: TaskFormData) => {
      try {
        await Promise.resolve(onSubmit(data));
        announceToScreenReader('Task created successfully', 'polite');
      } catch {
        announceToScreenReader(
          'Error creating task. Please check the form and try again.',
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
        'Create task dialog opened. Fill in the required fields marked with an asterisk.',
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
            Create Task
          </h2>
          <p id='dialog-description' className='sr-only'>
            Fill in the required fields marked with an asterisk and click Create Task to submit.
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
          onSubmit={handleSubmit(onSubmitWithAnnouncement as SubmitHandler<TaskFormData>)}
          className='mt-6 space-y-6'
        >
          {/* Task Details Section */}
          <div className='space-y-4'>
            <h3 className='text-md border-b pb-2 font-medium'>Task Details</h3>

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
                placeholder='Enter task title'
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
                  Give this task a clear, descriptive title
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
                placeholder='Describe this task...'
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
                  Current status of this task
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
                Optional: Person responsible for this task
              </span>
            </div>
          </div>

          {/* Task Specification Section */}
          <div className='space-y-4'>
            <h3 className='text-md border-b pb-2 font-medium'>Task Specification</h3>

            <div className='grid gap-4 sm:grid-cols-2'>
              <div>
                <label htmlFor='estimated_hours' className='block text-sm font-medium'>
                  Estimated Hours
                </label>
                <input
                  id='estimated_hours'
                  type='number'
                  min={0}
                  step={0.5}
                  {...register('estimated_hours')}
                  placeholder='e.g., 8'
                  aria-describedby={
                    errors.estimated_hours ? 'estimated_hours-error' : 'estimated_hours-help'
                  }
                  aria-invalid={Boolean(errors.estimated_hours)}
                  className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
                />
                {errors.estimated_hours ? (
                  <p
                    id='estimated_hours-error'
                    role='alert'
                    className='mt-1 text-sm text-red-500'
                    aria-live='polite'
                    aria-atomic='true'
                  >
                    {errors.estimated_hours.message}
                  </p>
                ) : (
                  <span
                    id='estimated_hours-help'
                    className='text-muted-foreground mt-1 block text-xs'
                  >
                    Optional: Expected time to complete
                  </span>
                )}
              </div>
              <div>
                <label htmlFor='actual_hours' className='block text-sm font-medium'>
                  Actual Hours
                </label>
                <input
                  id='actual_hours'
                  type='number'
                  min={0}
                  step={0.5}
                  {...register('actual_hours')}
                  placeholder='e.g., 6.5'
                  aria-describedby={
                    errors.actual_hours ? 'actual_hours-error' : 'actual_hours-help'
                  }
                  aria-invalid={Boolean(errors.actual_hours)}
                  className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
                />
                {errors.actual_hours ? (
                  <p
                    id='actual_hours-error'
                    role='alert'
                    className='mt-1 text-sm text-red-500'
                    aria-live='polite'
                    aria-atomic='true'
                  >
                    {errors.actual_hours.message}
                  </p>
                ) : (
                  <span id='actual_hours-help' className='text-muted-foreground mt-1 block text-xs'>
                    Optional: Time spent so far
                  </span>
                )}
              </div>
            </div>

            <div>
              <label htmlFor='completion_percentage' className='block text-sm font-medium'>
                Completion Percentage
              </label>
              <input
                id='completion_percentage'
                type='number'
                min={0}
                max={100}
                {...register('completion_percentage')}
                placeholder='e.g., 50'
                aria-describedby={
                  errors.completion_percentage
                    ? 'completion_percentage-error'
                    : 'completion_percentage-help'
                }
                aria-invalid={Boolean(errors.completion_percentage)}
                className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
              />
              {errors.completion_percentage ? (
                <p
                  id='completion_percentage-error'
                  role='alert'
                  className='mt-1 text-sm text-red-500'
                  aria-live='polite'
                  aria-atomic='true'
                >
                  {errors.completion_percentage.message}
                </p>
              ) : (
                <span
                  id='completion_percentage-help'
                  className='text-muted-foreground mt-1 block text-xs'
                >
                  Optional: Progress from 0 to 100
                </span>
              )}
            </div>

            <FormArrayField<TaskFormData>
              control={control}
              name='subtasks'
              label='Subtasks'
              helpText='Break down this task into smaller actionable items'
              defaultValue=''
              addButtonLabel='Add Subtask'
              renderField={(index) => (
                <input
                  {...register(`subtasks.${index}`)}
                  placeholder='Enter subtask...'
                  aria-label={`Subtask ${index + 1}`}
                  className='bg-background focus-visible:ring-primary w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus-visible:ring-2'
                />
              )}
            />
            {errors.subtasks && (
              <p className='text-sm text-red-500' role='alert'>
                {errors.subtasks.message}
              </p>
            )}
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
              aria-label={isLoading || isSubmitting ? 'Creating task...' : 'Create task'}
              className='bg-primary text-primary-foreground focus-visible:ring-primary flex-1 rounded-lg px-4 py-2 focus:outline-none focus-visible:ring-2 disabled:opacity-50'
            >
              {isLoading || isSubmitting ? 'Creating...' : 'Create Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
