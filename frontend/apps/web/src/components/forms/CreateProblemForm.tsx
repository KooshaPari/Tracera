import { zodResolver } from '@hookform/resolvers/zod';
import { X } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import { logger } from '@/lib/logger';

import { useCreateProblem } from '../../hooks/useProblems';

const impactLevels = ['critical', 'high', 'medium', 'low'] as const;

const problemSchema = z.object({
  affectedSystems: z.string().optional(),
  affectedUsersEstimated: z.coerce.number().optional(),
  assignedTeam: z.string().max(255).optional(),
  assignedTo: z.string().max(255).optional(),
  businessImpactDescription: z.string().max(2000).optional(),
  category: z.string().max(100).optional(),
  description: z.string().max(5000).optional(),
  impactLevel: z.enum(impactLevels),
  owner: z.string().max(255).optional(),
  priority: z.enum(impactLevels),
  subCategory: z.string().max(100).optional(),
  title: z.string().min(1, 'Title is required').max(500, 'Title too long'),
  urgency: z.enum(impactLevels),
});

type ProblemFormData = z.infer<typeof problemSchema>;

interface CreateProblemFormProps {
  projectId: string;
  onCancel: () => void;
  onSuccess: () => void;
}

const categoryOptions = [
  'Software Bug',
  'Configuration',
  'Infrastructure',
  'Performance',
  'Security',
  'Integration',
  'Data',
  'User Error',
  'Other',
];

export function CreateProblemForm({ projectId, onCancel, onSuccess }: CreateProblemFormProps) {
  const createProblem = useCreateProblem();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProblemFormData>({
    defaultValues: {
      impactLevel: 'medium',
      priority: 'medium',
      urgency: 'medium',
    },
    resolver: zodResolver(problemSchema) as any,
  });

  const onSubmit = async (data: ProblemFormData) => {
    try {
      const payload: Parameters<typeof createProblem.mutateAsync>[0] = {
        impactLevel: data.impactLevel,
        priority: data.priority,
        projectId,
        title: data.title,
        urgency: data.urgency,
      };
      if (data.description) {
        payload.description = data.description;
      }
      if (data.category) {
        payload.category = data.category;
      }
      if (data.subCategory) {
        payload.subCategory = data.subCategory;
      }
      if (data.affectedSystems) {
        payload.affectedSystems = data.affectedSystems.split(',').map((s) => s.trim());
      }
      if (data.affectedUsersEstimated) {
        payload.affectedUsersEstimated = data.affectedUsersEstimated;
      }
      if (data.businessImpactDescription) {
        payload.businessImpactDescription = data.businessImpactDescription;
      }
      if (data.assignedTo) {
        payload.assignedTo = data.assignedTo;
      }
      if (data.assignedTeam) {
        payload.assignedTeam = data.assignedTeam;
      }
      if (data.owner) {
        payload.owner = data.owner;
      }

      await createProblem.mutateAsync(payload);
      onSuccess();
    } catch (error) {
      logger.error('Failed to create problem:', error);
    }
  };

  return (
    <div className='fixed inset-0 z-50 flex items-center justify-center'>
      <div className='fixed inset-0 bg-black/50 backdrop-blur-sm' onClick={onCancel} />
      <div
        className='bg-background relative max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-xl border p-6 shadow-2xl'
        role='dialog'
        aria-modal='true'
        aria-labelledby='report-problem-title'
      >
        <div className='flex items-center justify-between'>
          <h2 id='report-problem-title' className='text-lg font-semibold'>
            Report Problem
          </h2>
          <button
            type='button'
            onClick={onCancel}
            aria-label='Close dialog'
            className='hover:bg-accent rounded-lg p-1'
          >
            <X className='h-5 w-5' />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className='mt-6 space-y-4'>
          {/* Title */}
          <div>
            <label className='block text-sm font-medium'>
              Title <span className='text-red-500'>*</span>
            </label>
            <input
              {...register('title')}
              placeholder='Brief description of the problem'
              className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
            />
            {errors.title && <p className='mt-1 text-sm text-red-500'>{errors.title.message}</p>}
          </div>

          {/* Description */}
          <div>
            <label className='block text-sm font-medium'>Description</label>
            <textarea
              {...register('description')}
              rows={4}
              placeholder='Detailed description of the problem, symptoms, and when it occurs...'
              className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
            />
          </div>

          {/* Category */}
          <div className='grid gap-4 sm:grid-cols-2'>
            <div>
              <label className='block text-sm font-medium'>Category</label>
              <select
                {...register('category')}
                className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
              >
                <option value=''>Select category...</option>
                {categoryOptions.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className='block text-sm font-medium'>Sub-Category</label>
              <input
                {...register('subCategory')}
                placeholder='Sub-category...'
                className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
              />
            </div>
          </div>

          {/* Impact, Urgency, Priority */}
          <div className='grid gap-4 sm:grid-cols-3'>
            <div>
              <label className='block text-sm font-medium'>
                Impact Level <span className='text-red-500'>*</span>
              </label>
              <select
                {...register('impactLevel')}
                className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
              >
                {impactLevels.map((level) => (
                  <option key={level} value={level}>
                    {level.charAt(0).toUpperCase() + level.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className='block text-sm font-medium'>
                Urgency <span className='text-red-500'>*</span>
              </label>
              <select
                {...register('urgency')}
                className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
              >
                {impactLevels.map((level) => (
                  <option key={level} value={level}>
                    {level.charAt(0).toUpperCase() + level.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className='block text-sm font-medium'>
                Priority <span className='text-red-500'>*</span>
              </label>
              <select
                {...register('priority')}
                className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
              >
                {impactLevels.map((level) => (
                  <option key={level} value={level}>
                    {level.charAt(0).toUpperCase() + level.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Affected Systems & Users */}
          <div className='grid gap-4 sm:grid-cols-2'>
            <div>
              <label className='block text-sm font-medium'>Affected Systems</label>
              <input
                {...register('affectedSystems')}
                placeholder='Comma-separated list...'
                className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
              />
              <p className='text-muted-foreground mt-1 text-xs'>e.g., API, Database, Frontend</p>
            </div>
            <div>
              <label className='block text-sm font-medium'>Affected Users (estimated)</label>
              <input
                {...register('affectedUsersEstimated')}
                type='number'
                min={0}
                placeholder='Number of users...'
                className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
              />
            </div>
          </div>

          {/* Business Impact */}
          <div>
            <label className='block text-sm font-medium'>Business Impact Description</label>
            <textarea
              {...register('businessImpactDescription')}
              rows={2}
              placeholder='Describe the business impact...'
              className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
            />
          </div>

          {/* Assignment */}
          <div className='grid gap-4 sm:grid-cols-3'>
            <div>
              <label className='block text-sm font-medium'>Assigned To</label>
              <input
                {...register('assignedTo')}
                placeholder='Person...'
                className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
              />
            </div>
            <div>
              <label className='block text-sm font-medium'>Assigned Team</label>
              <input
                {...register('assignedTeam')}
                placeholder='Team...'
                className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
              />
            </div>
            <div>
              <label className='block text-sm font-medium'>Owner</label>
              <input
                {...register('owner')}
                placeholder='Problem owner...'
                className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
              />
            </div>
          </div>

          {/* Actions */}
          <div className='flex gap-3 pt-4'>
            <button
              type='button'
              onClick={onCancel}
              className='hover:bg-accent flex-1 rounded-lg border px-4 py-2'
            >
              Cancel
            </button>
            <button
              type='submit'
              disabled={createProblem.isPending}
              className='bg-primary text-primary-foreground flex-1 rounded-lg px-4 py-2 disabled:opacity-50'
            >
              {createProblem.isPending ? 'Creating...' : 'Report Problem'}
            </button>
          </div>

          {createProblem.isError && (
            <p className='text-sm text-red-500'>
              Error:{' '}
              {createProblem.error instanceof Error
                ? createProblem.error.message
                : String(createProblem.error)}
            </p>
          )}
        </form>
      </div>
    </div>
  );
}
