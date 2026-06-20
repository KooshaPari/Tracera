import type { Resolver, SubmitHandler } from 'react-hook-form';

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
const storyPointOptions = [1, 2, 3, 5, 8, 13] as const;

const userStorySchema = z.object({
  acceptance_criteria: z.array(z.string().min(1, 'Criteria cannot be empty')),
  as_a: z.string().max(255).optional(),
  description: z.string().max(5000).optional(),
  i_want: z.string().max(500).optional(),
  priority: z.enum(priorityOptions),
  so_that: z.string().max(500).optional(),
  status: z.enum(statusOptions),
  story_points: z
    .union([z.number(), z.string()])
    .transform((val) => (typeof val === 'string' ? Number.parseFloat(val) : val))
    .pipe(
      z.number().min(1, 'Story points must be at least 1').max(13, 'Story points cannot exceed 13'),
    )
    .optional(),
  title: z.string().min(1, 'Title is required').max(500, 'Title too long'),
});

type UserStoryFormData = z.infer<typeof userStorySchema>;

interface CreateUserStoryItemFormProps {
  onSubmit: (data: UserStoryFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export const CreateUserStoryItemForm = ({
  onSubmit,
  onCancel,
  isLoading,
}: CreateUserStoryItemFormProps) => {
  const dialogRef = useRef<HTMLDivElement>(null);
  const formRef = useRef<HTMLFormElement>(null);
  const savedFocusRef = useRef<HTMLElement | null>(null);
  const cleanupFocusTrapRef = useRef<(() => void) | null>(null);

  const {
    register,
    handleSubmit,
    control,
    formState: { errors, isSubmitting },
  } = useForm<UserStoryFormData>({
    defaultValues: {
      acceptance_criteria: [],
      priority: 'medium',
      status: 'todo',
    },
    mode: 'onBlur',
    resolver: zodResolver(userStorySchema) as Resolver<UserStoryFormData>,
  });

  const onSubmitWithAnnouncement = useCallback(
    async (data: UserStoryFormData) => {
      try {
        await Promise.resolve(onSubmit(data));
        announceToScreenReader('User story created successfully', 'polite');
      } catch {
        announceToScreenReader(
          'Error creating user story. Please check the form and try again.',
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
        'Create user story dialog opened. Fill in the required fields marked with an asterisk.',
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
            Create User Story
          </h2>
          <p id='dialog-description' className='sr-only'>
            Fill in the required fields marked with an asterisk and click Create User Story to
            submit.
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
          onSubmit={handleSubmit(onSubmitWithAnnouncement as SubmitHandler<UserStoryFormData>)}
          className='mt-6 space-y-6'
        >
          {/* User Story Details Section */}
          <div className='space-y-4'>
            <h3 className='text-md border-b pb-2 font-medium'>User Story Details</h3>

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
                placeholder='Enter user story title'
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
                  Give this user story a clear, descriptive title
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
                placeholder='Describe this user story...'
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
                  Current status of this story
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

          {/* Story Specification Section */}
          <div className='space-y-4'>
            <h3 className='text-md border-b pb-2 font-medium'>Story Specification</h3>

            <div>
              <label htmlFor='as_a' className='block text-sm font-medium'>
                As a...
              </label>
              <input
                id='as_a'
                {...register('as_a')}
                placeholder='e.g., logged-in user'
                aria-describedby='as_a-help'
                className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
              />
              <span id='as_a-help' className='text-muted-foreground mt-1 block text-xs'>
                Optional: User role or persona
              </span>
            </div>

            <div>
              <label htmlFor='i_want' className='block text-sm font-medium'>
                I want...
              </label>
              <input
                id='i_want'
                {...register('i_want')}
                placeholder='e.g., to reset my password'
                aria-describedby='i_want-help'
                className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
              />
              <span id='i_want-help' className='text-muted-foreground mt-1 block text-xs'>
                Optional: What the user wants to do
              </span>
            </div>

            <div>
              <label htmlFor='so_that' className='block text-sm font-medium'>
                So that...
              </label>
              <input
                id='so_that'
                {...register('so_that')}
                placeholder='e.g., I can regain access to my account'
                aria-describedby='so_that-help'
                className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
              />
              <span id='so_that-help' className='text-muted-foreground mt-1 block text-xs'>
                Optional: The benefit or value
              </span>
            </div>

            <FormArrayField<UserStoryFormData>
              control={control}
              name='acceptance_criteria'
              label='Acceptance Criteria'
              helpText='Define the conditions that must be met for this story to be complete'
              defaultValue={'' as UserStoryFormData['acceptance_criteria'][number]}
              addButtonLabel='Add Criterion'
              renderField={(index) => (
                <input
                  {...register(`acceptance_criteria.${index}`)}
                  placeholder='Enter acceptance criterion...'
                  aria-label={`Acceptance criterion ${index + 1}`}
                  className='bg-background focus-visible:ring-primary w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus-visible:ring-2'
                />
              )}
            />
            {errors.acceptance_criteria && (
              <p className='text-sm text-red-500' role='alert'>
                {errors.acceptance_criteria.message}
              </p>
            )}

            <div>
              <label htmlFor='story_points' className='block text-sm font-medium'>
                Story Points
              </label>
              <select
                id='story_points'
                {...register('story_points')}
                aria-describedby={errors.story_points ? 'story_points-error' : 'story_points-help'}
                aria-invalid={Boolean(errors.story_points)}
                className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
              >
                <option value=''>Select points...</option>
                {storyPointOptions.map((points) => (
                  <option key={points} value={points}>
                    {points}
                  </option>
                ))}
              </select>
              {errors.story_points ? (
                <p
                  id='story_points-error'
                  role='alert'
                  className='mt-1 text-sm text-red-500'
                  aria-live='polite'
                  aria-atomic='true'
                >
                  {errors.story_points.message}
                </p>
              ) : (
                <span id='story_points-help' className='text-muted-foreground mt-1 block text-xs'>
                  Optional: Estimated effort (Fibonacci scale: 1, 2, 3, 5, 8, 13)
                </span>
              )}
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
              aria-label={
                isLoading || isSubmitting ? 'Creating user story...' : 'Create user story'
              }
              className='bg-primary text-primary-foreground focus-visible:ring-primary flex-1 rounded-lg px-4 py-2 focus:outline-none focus-visible:ring-2 disabled:opacity-50'
            >
              {isLoading || isSubmitting ? 'Creating...' : 'Create User Story'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
