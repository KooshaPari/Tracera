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

// Base item fields
const statusOptions = ['todo', 'in_progress', 'done', 'blocked', 'cancelled'] as const;
const priorityOptions = ['low', 'medium', 'high', 'critical'] as const;

// EARS pattern types
const earsPatternTypes = [
  'ubiquitous',
  'event_driven',
  'state_driven',
  'unwanted',
  'optional',
] as const;

// Risk levels
const riskLevels = ['low', 'medium', 'high', 'critical'] as const;

// Constraint types
const constraintTypes = ['hard', 'soft', 'optimizable'] as const;

// Verification status
const verificationStatusOptions = ['unverified', 'pending', 'verified', 'failed'] as const;

const requirementItemSchema = z.object({
  // Base item fields
  title: z.string().min(1, 'Title is required').max(500, 'Title too long'),
  description: z.string().max(5000).optional(),
  status: z.enum(statusOptions),
  priority: z.enum(priorityOptions),
  owner: z.string().max(255).optional(),

  // Requirement specification fields
  ears_pattern_type: z.enum(earsPatternTypes),
  ears_trigger: z.string().max(500).optional(),
  ears_precondition: z.string().max(500).optional(),
  ears_postcondition: z.string().max(500).optional(),

  constraint_type: z.enum(constraintTypes),
  constraint_target: z.coerce.number().optional(),
  constraint_tolerance: z.coerce.number().optional(),
  constraint_unit: z.string().max(50).optional(),

  risk_level: z.enum(riskLevels),
  verification_status: z.enum(verificationStatusOptions),

  // Quality dimensions (0-1 range)
  verifiability: z.coerce.number().min(0).max(1).optional(),
  traceability: z.coerce.number().min(0).max(1).optional(),
  clarity: z.coerce.number().min(0).max(1).optional(),

  // Additional fields
  rationale: z.string().max(1000).optional(),
  source_reference: z.string().max(500).optional(),
});

type RequirementItemFormData = z.infer<typeof requirementItemSchema>;

interface CreateRequirementItemFormProps {
  onSubmit: (data: unknown) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

const earsPatternExamples: Record<string, string> = {
  event_driven: 'When user clicks submit, the system shall validate the form',
  optional: 'Where premium features are enabled, the system shall allow export',
  state_driven: 'While user is logged in, the system shall display dashboard',
  ubiquitous: 'The system shall always validate user input',
  unwanted: 'The system shall not store passwords in plain text',
};

export const CreateRequirementItemForm = ({
  onSubmit,
  onCancel,
  isLoading,
}: CreateRequirementItemFormProps) => {
  const dialogRef = useRef<HTMLDivElement>(null);
  const formRef = useRef<HTMLFormElement>(null);
  const savedFocusRef = useRef<HTMLElement | null>(null);
  const cleanupFocusTrapRef = useRef<(() => void) | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<RequirementItemFormData>({
    defaultValues: {
      clarity: 0.5,
      constraint_type: 'hard',
      ears_pattern_type: 'ubiquitous',
      priority: 'medium',
      risk_level: 'medium',
      status: 'todo',
      traceability: 0.5,
      verifiability: 0.5,
      verification_status: 'unverified',
    },
    mode: 'onBlur',
    resolver: zodResolver(requirementItemSchema) as Resolver<RequirementItemFormData>,
  });

  const selectedEarsPattern = watch('ears_pattern_type');
  const titleError = errors['title'];
  const titleErrorMessage =
    typeof titleError?.message === 'string' ? titleError.message : undefined;

  // Handle form submission with error announcements
  const onSubmitWithAnnouncement = useCallback(
    async (data: RequirementItemFormData) => {
      try {
        await Promise.resolve(onSubmit(data));
        announceToScreenReader('Requirement created successfully', 'polite');
      } catch {
        announceToScreenReader(
          'Error creating requirement. Please check the form and try again.',
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
        'Create requirement dialog opened. Fill in the required fields marked with an asterisk.',
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
            Create Requirement
          </h2>
          <p id='dialog-description' className='sr-only'>
            Fill in the required fields marked with an asterisk and click Create Requirement to
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
          onSubmit={handleSubmit(
            onSubmitWithAnnouncement as SubmitHandler<RequirementItemFormData>,
          )}
          className='mt-6 space-y-6'
        >
          {/* Requirement Details Section */}
          <div className='space-y-4'>
            <h3 className='border-b pb-2 text-sm font-semibold'>Requirement Details</h3>

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
                placeholder='Enter requirement title'
                aria-describedby={titleError ? 'title-error' : 'title-help'}
                aria-required='true'
                aria-invalid={Boolean(titleError)}
                className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
              />
              {titleError ? (
                <p
                  id='title-error'
                  role='alert'
                  className='mt-1 text-sm text-red-500'
                  aria-live='polite'
                  aria-atomic='true'
                >
                  {titleErrorMessage ?? 'Title is required'}
                </p>
              ) : (
                <span id='title-help' className='text-muted-foreground mt-1 block text-xs'>
                  Give this requirement a clear, descriptive title
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
                placeholder='Describe this requirement...'
                aria-describedby='description-help'
                className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
              />
              <span id='description-help' className='text-muted-foreground mt-1 block text-xs'>
                Optional: Provide additional context or details
              </span>
            </div>

            <div className='grid gap-4 sm:grid-cols-3'>
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
                  Current status
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
                  Optional: Assignee
                </span>
              </div>
            </div>
          </div>

          {/* Requirement Specification Section */}
          <div className='space-y-4'>
            <h3 className='border-b pb-2 text-sm font-semibold'>Requirement Specification</h3>

            <div>
              <label htmlFor='ears_pattern_type' className='block text-sm font-medium'>
                EARS Pattern Type{' '}
                <span className='text-red-500' aria-label='required'>
                  *
                </span>
              </label>
              <select
                id='ears_pattern_type'
                aria-describedby='ears-pattern-help'
                {...register('ears_pattern_type')}
                className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
              >
                {earsPatternTypes.map((t) => (
                  <option key={t} value={t}>
                    {t.replace('_', ' ')}
                  </option>
                ))}
              </select>
              <span id='ears-pattern-help' className='text-muted-foreground mt-1 block text-xs'>
                Example: {earsPatternExamples[selectedEarsPattern]}
              </span>
            </div>

            <div className='grid gap-4 sm:grid-cols-2'>
              <div>
                <label htmlFor='ears_trigger' className='block text-sm font-medium'>
                  EARS Trigger
                </label>
                <input
                  id='ears_trigger'
                  {...register('ears_trigger')}
                  placeholder='When...'
                  aria-describedby='trigger-help'
                  className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
                />
                <span id='trigger-help' className='text-muted-foreground mt-1 block text-xs'>
                  Event or condition that triggers this requirement
                </span>
              </div>
              <div>
                <label htmlFor='ears_precondition' className='block text-sm font-medium'>
                  EARS Precondition
                </label>
                <input
                  id='ears_precondition'
                  {...register('ears_precondition')}
                  placeholder='While...'
                  aria-describedby='precondition-help'
                  className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
                />
                <span id='precondition-help' className='text-muted-foreground mt-1 block text-xs'>
                  State that must be true before execution
                </span>
              </div>
            </div>

            <div>
              <label htmlFor='ears_postcondition' className='block text-sm font-medium'>
                EARS Postcondition
              </label>
              <input
                id='ears_postcondition'
                {...register('ears_postcondition')}
                placeholder='The system shall...'
                aria-describedby='postcondition-help'
                className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
              />
              <span id='postcondition-help' className='text-muted-foreground mt-1 block text-xs'>
                The expected behavior or result
              </span>
            </div>

            <div className='grid gap-4 sm:grid-cols-3'>
              <div>
                <label htmlFor='constraint_type' className='block text-sm font-medium'>
                  Constraint Type
                </label>
                <select
                  id='constraint_type'
                  aria-describedby='constraint-type-help'
                  {...register('constraint_type')}
                  className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
                >
                  {constraintTypes.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
                <span
                  id='constraint-type-help'
                  className='text-muted-foreground mt-1 block text-xs'
                >
                  Constraint flexibility
                </span>
              </div>
              <div>
                <label htmlFor='risk_level' className='block text-sm font-medium'>
                  Risk Level
                </label>
                <select
                  id='risk_level'
                  aria-describedby='risk-help'
                  {...register('risk_level')}
                  className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
                >
                  {riskLevels.map((r) => (
                    <option key={r} value={r}>
                      {r}
                    </option>
                  ))}
                </select>
                <span id='risk-help' className='text-muted-foreground mt-1 block text-xs'>
                  Risk assessment
                </span>
              </div>
              <div>
                <label htmlFor='verification_status' className='block text-sm font-medium'>
                  Verification Status
                </label>
                <select
                  id='verification_status'
                  aria-describedby='verification-help'
                  {...register('verification_status')}
                  className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
                >
                  {verificationStatusOptions.map((v) => (
                    <option key={v} value={v}>
                      {v}
                    </option>
                  ))}
                </select>
                <span id='verification-help' className='text-muted-foreground mt-1 block text-xs'>
                  Current verification state
                </span>
              </div>
            </div>

            <div className='grid gap-4 sm:grid-cols-3'>
              <div>
                <label htmlFor='constraint_target' className='block text-sm font-medium'>
                  Constraint Target
                </label>
                <input
                  id='constraint_target'
                  type='number'
                  step='0.01'
                  {...register('constraint_target')}
                  placeholder='0'
                  aria-describedby='target-help'
                  className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
                />
                <span id='target-help' className='text-muted-foreground mt-1 block text-xs'>
                  Target value
                </span>
              </div>
              <div>
                <label htmlFor='constraint_tolerance' className='block text-sm font-medium'>
                  Tolerance
                </label>
                <input
                  id='constraint_tolerance'
                  type='number'
                  step='0.01'
                  {...register('constraint_tolerance')}
                  placeholder='0'
                  aria-describedby='tolerance-help'
                  className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
                />
                <span id='tolerance-help' className='text-muted-foreground mt-1 block text-xs'>
                  Acceptable variance
                </span>
              </div>
              <div>
                <label htmlFor='constraint_unit' className='block text-sm font-medium'>
                  Unit
                </label>
                <input
                  id='constraint_unit'
                  {...register('constraint_unit')}
                  placeholder='ms, MB, etc.'
                  aria-describedby='unit-help'
                  className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
                />
                <span id='unit-help' className='text-muted-foreground mt-1 block text-xs'>
                  Unit of measurement
                </span>
              </div>
            </div>

            <div className='space-y-3'>
              <label className='block text-sm font-medium'>Quality Dimensions (0-1 scale)</label>
              <div className='grid gap-4 sm:grid-cols-3'>
                <div>
                  <label htmlFor='verifiability' className='mb-1 block text-xs font-medium'>
                    Verifiability
                  </label>
                  <input
                    id='verifiability'
                    type='number'
                    step='0.1'
                    min='0'
                    max='1'
                    {...register('verifiability')}
                    aria-describedby='verifiability-help'
                    className='bg-background focus-visible:ring-primary w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
                  />
                  <span
                    id='verifiability-help'
                    className='text-muted-foreground mt-1 block text-xs'
                  >
                    How testable is this?
                  </span>
                </div>
                <div>
                  <label htmlFor='traceability' className='mb-1 block text-xs font-medium'>
                    Traceability
                  </label>
                  <input
                    id='traceability'
                    type='number'
                    step='0.1'
                    min='0'
                    max='1'
                    {...register('traceability')}
                    aria-describedby='traceability-help'
                    className='bg-background focus-visible:ring-primary w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
                  />
                  <span id='traceability-help' className='text-muted-foreground mt-1 block text-xs'>
                    How traceable is this?
                  </span>
                </div>
                <div>
                  <label htmlFor='clarity' className='mb-1 block text-xs font-medium'>
                    Clarity
                  </label>
                  <input
                    id='clarity'
                    type='number'
                    step='0.1'
                    min='0'
                    max='1'
                    {...register('clarity')}
                    aria-describedby='clarity-help'
                    className='bg-background focus-visible:ring-primary w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
                  />
                  <span id='clarity-help' className='text-muted-foreground mt-1 block text-xs'>
                    How clear/unambiguous?
                  </span>
                </div>
              </div>
            </div>

            <div>
              <label htmlFor='rationale' className='block text-sm font-medium'>
                Rationale
              </label>
              <textarea
                id='rationale'
                {...register('rationale')}
                rows={2}
                placeholder='Why is this requirement needed?'
                aria-describedby='rationale-help'
                className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
              />
              <span id='rationale-help' className='text-muted-foreground mt-1 block text-xs'>
                Optional: Explain the reasoning behind this requirement
              </span>
            </div>

            <div>
              <label htmlFor='source_reference' className='block text-sm font-medium'>
                Source Reference
              </label>
              <input
                id='source_reference'
                {...register('source_reference')}
                placeholder='Document, stakeholder, or system reference'
                aria-describedby='source-help'
                className='bg-background focus-visible:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus-visible:ring-2'
              />
              <span id='source-help' className='text-muted-foreground mt-1 block text-xs'>
                Optional: Where did this requirement originate?
              </span>
            </div>
          </div>

          <div className='flex gap-3 border-t pt-4'>
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
                isLoading || isSubmitting ? 'Creating requirement...' : 'Create requirement'
              }
              className='bg-primary text-primary-foreground focus-visible:ring-primary flex-1 rounded-lg px-4 py-2 focus:outline-none focus-visible:ring-2 disabled:opacity-50'
            >
              {isLoading || isSubmitting ? 'Creating...' : 'Create Requirement'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
