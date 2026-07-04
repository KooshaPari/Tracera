import type { Resolver } from 'react-hook-form';

import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

// Status and Priority options (matching Item model) – mutable for FormSelectOption[]
const statusOptions: { label: string; value: string }[] = [
  { label: 'Todo', value: 'todo' },
  { label: 'In Progress', value: 'in_progress' },
  { label: 'Done', value: 'done' },
  { label: 'Blocked', value: 'blocked' },
  { label: 'Cancelled', value: 'cancelled' },
];

const priorityOptions: { label: string; value: string }[] = [
  { label: 'Low', value: 'low' },
  { label: 'Medium', value: 'medium' },
  { label: 'High', value: 'high' },
  { label: 'Critical', value: 'critical' },
];

const testTypeOptions: { label: string; value: string }[] = [
  { label: 'Unit', value: 'unit' },
  { label: 'Integration', value: 'integration' },
  { label: 'End-to-End', value: 'e2e' },
  { label: 'Performance', value: 'performance' },
  { label: 'Security', value: 'security' },
  { label: 'Smoke', value: 'smoke' },
  { label: 'Regression', value: 'regression' },
  { label: 'Acceptance', value: 'acceptance' },
];

const oracleTypeOptions: { label: string; value: string }[] = [
  { label: 'Assertion', value: 'assertion' },
  { label: 'Golden (Reference)', value: 'golden' },
  { label: 'Metamorphic', value: 'metamorphic' },
  { label: 'Property-Based', value: 'property' },
  { label: 'Differential', value: 'differential' },
];

const coverageTypeOptions: { label: string; value: string }[] = [
  { label: 'Statement', value: 'statement' },
  { label: 'Branch', value: 'branch' },
  { label: 'MC/DC', value: 'mcdc' },
  { label: 'Path', value: 'path' },
  { label: 'Condition', value: 'condition' },
];

const safetyLevelOptions: { label: string; value: string }[] = [
  { label: 'DAL-A (Catastrophic)', value: 'DAL-A' },
  { label: 'DAL-B (Hazardous)', value: 'DAL-B' },
  { label: 'DAL-C (Major)', value: 'DAL-C' },
  { label: 'DAL-D (Minor)', value: 'DAL-D' },
  { label: 'DAL-E (No Effect)', value: 'DAL-E' },
];

const testItemSchema = z.object({
  title: z.string().min(1, 'Title is required').max(500, 'Title too long'),
  description: z.string().max(5000).optional(),
  status: z.enum(['todo', 'in_progress', 'done', 'blocked', 'cancelled']),
  priority: z.enum(['low', 'medium', 'high', 'critical']),
  owner: z.string().max(255).optional(),
  test_type: z.enum([
    'unit',
    'integration',
    'e2e',
    'performance',
    'security',
    'smoke',
    'regression',
    'acceptance',
  ]),
  test_framework: z.string().max(100).optional(),
  language: z.string().max(50).optional(),
  oracle_type: z
    .enum(['assertion', 'golden', 'metamorphic', 'property', 'differential'])
    .optional(),
  coverage_type: z.enum(['statement', 'branch', 'mcdc', 'path', 'condition']).optional(),
  safety_level: z.enum(['DAL-A', 'DAL-B', 'DAL-C', 'DAL-D', 'DAL-E']).optional(),
  expected_duration_ms: z.coerce.number().int().positive().optional(),
  is_critical_path: z.boolean().optional(),
});

type TestItemFormData = z.infer<typeof testItemSchema>;

interface CreateTestItemFormProps {
  onSubmit: (data: TestItemFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

const inputClass =
  'mt-1 w-full rounded-lg border bg-background px-3 py-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary';
const labelClass = 'block text-sm font-medium';

export function CreateTestItemForm({ onSubmit, onCancel, isLoading }: CreateTestItemFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<TestItemFormData>({
    defaultValues: {
      is_critical_path: false,
      priority: 'medium',
      status: 'todo',
      test_type: 'unit',
    },
    mode: 'onBlur',
    resolver: zodResolver(testItemSchema) as Resolver<TestItemFormData>,
  });

  return (
    <div className='fixed inset-0 z-50 flex items-center justify-center'>
      <div
        className='fixed inset-0 bg-black/50 backdrop-blur-sm'
        onClick={onCancel}
        aria-hidden='true'
      />
      <div
        role='dialog'
        aria-modal='true'
        aria-labelledby='dialog-title'
        className='bg-background relative max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-xl border p-6 shadow-2xl'
      >
        <div className='mb-6'>
          <h2 id='dialog-title' className='text-lg font-semibold'>
            Create Test Item
          </h2>
          <p className='text-muted-foreground mt-1 text-sm'>
            Create a new test specification with detailed configuration
          </p>
        </div>
        <form
          onSubmit={handleSubmit((data) => {
            onSubmit(data);
          })}
          className='space-y-6'
        >
          <div className='space-y-4'>
            <h3 className='border-b pb-2 text-sm font-medium'>Test Details</h3>
            <div>
              <label htmlFor='title' className={labelClass}>
                Title{' '}
                <span className='text-red-500' aria-label='required'>
                  *
                </span>
              </label>
              <input
                id='title'
                {...register('title')}
                placeholder='Enter test title'
                aria-invalid={Boolean(errors.title)}
                className={inputClass}
              />
              {errors.title && (
                <p className='mt-1 text-sm text-red-500' role='alert'>
                  {errors.title.message}
                </p>
              )}
            </div>
            <div>
              <label htmlFor='description' className={labelClass}>
                Description
              </label>
              <textarea
                id='description'
                {...register('description')}
                rows={3}
                placeholder='Describe this test...'
                className={inputClass}
              />
              {errors.description && (
                <p className='mt-1 text-sm text-red-500' role='alert'>
                  {errors.description.message}
                </p>
              )}
            </div>
            <div className='grid gap-4 sm:grid-cols-2'>
              <div>
                <label htmlFor='status' className={labelClass}>
                  Status{' '}
                  <span className='text-red-500' aria-label='required'>
                    *
                  </span>
                </label>
                <select
                  id='status'
                  {...register('status')}
                  aria-invalid={Boolean(errors.status)}
                  className={inputClass}
                >
                  {statusOptions.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
                {errors.status && (
                  <p className='mt-1 text-sm text-red-500' role='alert'>
                    {errors.status.message}
                  </p>
                )}
              </div>
              <div>
                <label htmlFor='priority' className={labelClass}>
                  Priority{' '}
                  <span className='text-red-500' aria-label='required'>
                    *
                  </span>
                </label>
                <select
                  id='priority'
                  {...register('priority')}
                  aria-invalid={Boolean(errors.priority)}
                  className={inputClass}
                >
                  {priorityOptions.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
                {errors.priority && (
                  <p className='mt-1 text-sm text-red-500' role='alert'>
                    {errors.priority.message}
                  </p>
                )}
              </div>
            </div>
            <div>
              <label htmlFor='owner' className={labelClass}>
                Owner
              </label>
              <input
                id='owner'
                {...register('owner')}
                placeholder='Assigned to...'
                className={inputClass}
              />
              {errors.owner && (
                <p className='mt-1 text-sm text-red-500' role='alert'>
                  {errors.owner.message}
                </p>
              )}
            </div>
          </div>
          <div className='space-y-4'>
            <h3 className='border-b pb-2 text-sm font-medium'>Test Specification</h3>
            <div className='grid gap-4 sm:grid-cols-2'>
              <div>
                <label htmlFor='test_type' className={labelClass}>
                  Test Type{' '}
                  <span className='text-red-500' aria-label='required'>
                    *
                  </span>
                </label>
                <select
                  id='test_type'
                  {...register('test_type')}
                  aria-invalid={Boolean(errors.test_type)}
                  className={inputClass}
                >
                  {testTypeOptions.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
                {errors.test_type && (
                  <p className='mt-1 text-sm text-red-500' role='alert'>
                    {errors.test_type.message}
                  </p>
                )}
              </div>
              <div>
                <label htmlFor='test_framework' className={labelClass}>
                  Test Framework
                </label>
                <input
                  id='test_framework'
                  {...register('test_framework')}
                  placeholder='e.g., Vitest, Jest, Pytest'
                  className={inputClass}
                />
                {errors.test_framework && (
                  <p className='mt-1 text-sm text-red-500' role='alert'>
                    {errors.test_framework.message}
                  </p>
                )}
              </div>
            </div>
            <div className='grid gap-4 sm:grid-cols-2'>
              <div>
                <label htmlFor='language' className={labelClass}>
                  Language
                </label>
                <input
                  id='language'
                  {...register('language')}
                  placeholder='e.g., TypeScript, Python'
                  className={inputClass}
                />
                {errors.language && (
                  <p className='mt-1 text-sm text-red-500' role='alert'>
                    {errors.language.message}
                  </p>
                )}
              </div>
              <div>
                <label htmlFor='oracle_type' className={labelClass}>
                  Oracle Type
                </label>
                <select id='oracle_type' {...register('oracle_type')} className={inputClass}>
                  <option value=''>—</option>
                  {oracleTypeOptions.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
                {errors.oracle_type && (
                  <p className='mt-1 text-sm text-red-500' role='alert'>
                    {errors.oracle_type.message}
                  </p>
                )}
              </div>
            </div>
            <div className='grid gap-4 sm:grid-cols-2'>
              <div>
                <label htmlFor='coverage_type' className={labelClass}>
                  Coverage Type
                </label>
                <select id='coverage_type' {...register('coverage_type')} className={inputClass}>
                  <option value=''>—</option>
                  {coverageTypeOptions.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
                {errors.coverage_type && (
                  <p className='mt-1 text-sm text-red-500' role='alert'>
                    {errors.coverage_type.message}
                  </p>
                )}
              </div>
              <div>
                <label htmlFor='safety_level' className={labelClass}>
                  Safety Level (DO-178C)
                </label>
                <select id='safety_level' {...register('safety_level')} className={inputClass}>
                  <option value=''>—</option>
                  {safetyLevelOptions.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
                {errors.safety_level && (
                  <p className='mt-1 text-sm text-red-500' role='alert'>
                    {errors.safety_level.message}
                  </p>
                )}
              </div>
            </div>
            <div className='grid gap-4 sm:grid-cols-2'>
              <div>
                <label htmlFor='expected_duration_ms' className={labelClass}>
                  Expected Duration (ms)
                </label>
                <input
                  id='expected_duration_ms'
                  type='number'
                  {...register('expected_duration_ms', { valueAsNumber: true })}
                  placeholder='Expected execution time'
                  className={inputClass}
                />
                {errors.expected_duration_ms && (
                  <p className='mt-1 text-sm text-red-500' role='alert'>
                    {errors.expected_duration_ms.message}
                  </p>
                )}
              </div>
              <div className='flex items-center pt-6'>
                <input
                  type='checkbox'
                  id='is_critical_path'
                  {...register('is_critical_path')}
                  className='text-primary focus:ring-primary h-4 w-4 rounded border-gray-300'
                />
                <label htmlFor='is_critical_path' className='ml-2 text-sm font-medium'>
                  Critical Path Test
                </label>
              </div>
            </div>
          </div>
          <div className='flex gap-3 border-t pt-4'>
            <button
              type='button'
              onClick={onCancel}
              className='hover:bg-accent focus-visible:ring-primary flex-1 rounded-lg border px-4 py-2 focus:outline-none focus-visible:ring-2'
            >
              Cancel
            </button>
            <button
              type='submit'
              disabled={isLoading ?? isSubmitting}
              className='bg-primary text-primary-foreground focus-visible:ring-primary flex-1 rounded-lg px-4 py-2 focus:outline-none focus-visible:ring-2 disabled:opacity-50'
            >
              {isLoading || isSubmitting ? 'Creating...' : 'Create Test Item'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
