/**
 * CreateDefectItemForm Component
 *
 * Specialized form for creating defect items with defect-specific fields:
 * - Base fields: title, description, status, priority, owner
 * - Spec fields: severity, reproduction_steps, root_cause, cvss_score, affected_versions
 *
 * Uses FormArrayField pattern for array inputs (reproduction_steps, affected_versions)
 */

import { zodResolver } from '@hookform/resolvers/zod';
import { Plus, Trash2, X } from 'lucide-react';
import { useCallback, useEffect, useRef } from 'react';
import { useFieldArray, useForm } from 'react-hook-form';
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
const severityOptions = ['low', 'medium', 'high', 'critical'] as const;

const defectItemSchema = z.object({
  title: z.string().min(1, 'Title is required').max(500, 'Title too long'),
  description: z.string().max(5000).optional(),
  status: z.enum(statusOptions),
  priority: z.enum(priorityOptions),
  owner: z.string().max(255).optional(),
  // Defect-specific spec fields
  severity: z.enum(severityOptions),
  reproduction_steps: z
    .array(
      z.object({
        value: z.string().min(1, 'Step cannot be empty'),
      }),
    )
    .min(1, 'At least one reproduction step is required'),
  root_cause: z.string().max(1000).optional(),
  cvss_score: z.number().min(0).max(10).optional(),
  affected_versions: z
    .array(
      z.object({
        value: z.string().min(1, 'Version cannot be empty'),
      }),
    )
    .optional(),
});

type DefectItemFormData = z.infer<typeof defectItemSchema>;

interface CreateDefectItemFormProps {
  onSubmit: (data: DefectItemFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function CreateDefectItemForm({ onSubmit, onCancel, isLoading }: CreateDefectItemFormProps) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const formRef = useRef<HTMLFormElement>(null);
  const savedFocusRef = useRef<HTMLElement | null>(null);
  const cleanupFocusTrapRef = useRef<(() => void) | null>(null);

  const {
    register,
    handleSubmit,
    control,
    formState: { errors, isSubmitting },
  } = useForm<DefectItemFormData>({
    defaultValues: {
      affected_versions: [{ value: '' }],
      priority: 'high',
      reproduction_steps: [{ value: '' }],
      severity: 'medium',
      status: 'todo',
    },
    mode: 'onBlur',
    resolver: zodResolver(defectItemSchema),
  });

  // Field arrays for reproduction steps and affected versions
  const {
    fields: reproductionStepsFields,
    append: appendReproductionStep,
    remove: removeReproductionStep,
  } = useFieldArray({
    control,
    name: 'reproduction_steps',
  });

  const {
    fields: affectedVersionsFields,
    append: appendAffectedVersion,
    remove: removeAffectedVersion,
  } = useFieldArray({
    control,
    name: 'affected_versions',
  });

  // Handle form submission with error announcements
  const onSubmitWithAnnouncement = useCallback(
    async (data: DefectItemFormData) => {
      try {
        await Promise.resolve(onSubmit(data));
        announceToScreenReader('Defect item created successfully', 'polite');
      } catch {
        announceToScreenReader(
          'Error creating defect item. Please check the form and try again.',
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
        'Create defect item dialog opened. Fill in the required fields marked with an asterisk.',
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
  }, [handleKeyDown, onCancel]);

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
        className='bg-background focus-visible:ring-primary relative max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-xl border p-6 shadow-2xl focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2'
        tabIndex={-1}
      >
        <div className='flex items-center justify-between'>
          <h2 id='dialog-title' className='text-lg font-semibold'>
            Create Defect Item
          </h2>
          <p id='dialog-description' className='sr-only'>
            Fill in the required fields marked with an asterisk and click Create Defect to submit.
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
          className='mt-6 space-y-6'
        >
          {/* Defect Details Section */}
          <div className='space-y-4'>
            <h3 className='text-foreground border-b pb-2 text-sm font-semibold'>Defect Details</h3>

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
                placeholder='Enter defect title'
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
                  Give this defect a clear, descriptive title
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
                placeholder='Describe this defect...'
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
                  Current status of this defect
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
                Optional: Person responsible for this defect
              </span>
            </div>
          </div>

          {/* Defect Specification Section */}
          <div className='space-y-4'>
            <h3 className='text-foreground border-b pb-2 text-sm font-semibold'>
              Defect Specification
            </h3>

            <div>
              <label htmlFor='severity' className='block text-sm font-medium'>
                Severity{' '}
                <span className='text-red-500' aria-label='required'>
                  *
                </span>
              </label>
              <select
                id='severity'
                aria-describedby='severity-help'
                aria-required='true'
                {...register('severity')}
                className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
              >
                {severityOptions.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
              <span id='severity-help' className='text-muted-foreground mt-1 block text-xs'>
                Impact severity of the defect
              </span>
            </div>

            {/* Reproduction Steps Array */}
            <div>
              <label className='mb-2 block text-sm font-medium'>
                Reproduction Steps{' '}
                <span className='text-red-500' aria-label='required'>
                  *
                </span>
              </label>
              <div className='space-y-2'>
                {reproductionStepsFields.map((field, index) => (
                  <div key={field.id} className='flex gap-2'>
                    <div className='flex-1'>
                      <input
                        {...register(`reproduction_steps.${index}.value`)}
                        placeholder={`Step ${index + 1}`}
                        aria-label={`Reproduction step ${index + 1}`}
                        aria-describedby={
                          errors.reproduction_steps?.[index]?.value
                            ? `step-${index}-error`
                            : undefined
                        }
                        aria-invalid={Boolean(errors.reproduction_steps?.[index]?.value)}
                        className='bg-background focus-visible:ring-primary w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
                      />
                      {errors.reproduction_steps?.[index]?.value && (
                        <p
                          id={`step-${index}-error`}
                          role='alert'
                          className='mt-1 text-sm text-red-500'
                          aria-live='polite'
                        >
                          {errors.reproduction_steps[index]?.value?.message}
                        </p>
                      )}
                    </div>
                    {reproductionStepsFields.length > 1 && (
                      <button
                        type='button'
                        onClick={() => {
                          removeReproductionStep(index);
                        }}
                        aria-label={`Remove step ${index + 1}`}
                        className='hover:bg-destructive/10 text-destructive focus-visible:ring-primary rounded-lg p-2 focus:outline-none focus-visible:ring-2'
                      >
                        <Trash2 className='h-4 w-4' aria-hidden='true' />
                      </button>
                    )}
                  </div>
                ))}
                <button
                  type='button'
                  onClick={() => {
                    appendReproductionStep({ value: '' });
                  }}
                  className='text-primary focus-visible:ring-primary flex items-center gap-2 rounded text-sm hover:underline focus:outline-none focus-visible:ring-2'
                >
                  <Plus className='h-4 w-4' aria-hidden='true' />
                  Add Step
                </button>
              </div>
              <span className='text-muted-foreground mt-1 block text-xs'>
                Steps to reproduce the defect
              </span>
            </div>

            <div>
              <label htmlFor='root_cause' className='block text-sm font-medium'>
                Root Cause
              </label>
              <textarea
                id='root_cause'
                {...register('root_cause')}
                rows={3}
                placeholder='Describe the root cause if known...'
                aria-describedby='root-cause-help'
                className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
              />
              <span id='root-cause-help' className='text-muted-foreground mt-1 block text-xs'>
                Optional: Identified root cause of the defect
              </span>
            </div>

            <div>
              <label htmlFor='cvss_score' className='block text-sm font-medium'>
                CVSS Score
              </label>
              <input
                id='cvss_score'
                type='number'
                step='0.1'
                min='0'
                max='10'
                {...register('cvss_score', { valueAsNumber: true })}
                placeholder='0.0 - 10.0'
                aria-describedby='cvss-score-help'
                className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
              />
              <span id='cvss-score-help' className='text-muted-foreground mt-1 block text-xs'>
                Optional: CVSS score from 0 (lowest) to 10 (highest severity)
              </span>
            </div>

            {/* Affected Versions Array */}
            <div>
              <label className='mb-2 block text-sm font-medium'>Affected Versions</label>
              <div className='space-y-2'>
                {affectedVersionsFields.map((field, index) => (
                  <div key={field.id} className='flex gap-2'>
                    <div className='flex-1'>
                      <input
                        {...register(`affected_versions.${index}.value`)}
                        placeholder={`Version ${index + 1}`}
                        aria-label={`Affected version ${index + 1}`}
                        className='bg-background focus-visible:ring-primary w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
                      />
                    </div>
                    {affectedVersionsFields.length > 1 && (
                      <button
                        type='button'
                        onClick={() => {
                          removeAffectedVersion(index);
                        }}
                        aria-label={`Remove version ${index + 1}`}
                        className='hover:bg-destructive/10 text-destructive focus-visible:ring-primary rounded-lg p-2 focus:outline-none focus-visible:ring-2'
                      >
                        <Trash2 className='h-4 w-4' aria-hidden='true' />
                      </button>
                    )}
                  </div>
                ))}
                <button
                  type='button'
                  onClick={() => {
                    appendAffectedVersion({ value: '' });
                  }}
                  className='text-primary focus-visible:ring-primary flex items-center gap-2 rounded text-sm hover:underline focus:outline-none focus-visible:ring-2'
                >
                  <Plus className='h-4 w-4' aria-hidden='true' />
                  Add Version
                </button>
              </div>
              <span className='text-muted-foreground mt-1 block text-xs'>
                Optional: Versions affected by this defect
              </span>
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
              aria-label={isLoading || isSubmitting ? 'Creating defect...' : 'Create defect'}
              className='bg-primary text-primary-foreground focus-visible:ring-primary flex-1 rounded-lg px-4 py-2 focus:outline-none focus-visible:ring-2 disabled:opacity-50'
            >
              {isLoading || isSubmitting ? 'Creating...' : 'Create Defect'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
