import type { Resolver, SubmitHandler } from 'react-hook-form';

import { zodResolver } from '@hookform/resolvers/zod';
import { Plus, Trash2, X } from 'lucide-react';
import { useFieldArray, useForm } from 'react-hook-form';
import { z } from 'zod';

import { logger } from '@/lib/logger';

import { useCreateProcess } from '../../hooks/useProcesses';

// Constants
const MAX_DESCRIPTION_LENGTH = 5000;
const MAX_NAME_LENGTH = 500;
const MAX_OWNER_LENGTH = 255;
const MAX_PURPOSE_LENGTH = 2000;
const MAX_RESPONSIBLE_TEAM_LENGTH = 255;

const categoryOptions = [
  'compliance',
  'development',
  'integration',
  'management',
  'operational',
  'other',
  'support',
] as const;

const stageSchema = z.object({
  assignedRole: z.string().optional(),
  description: z.string().optional(),
  estimatedDurationMinutes: z.coerce.number().optional(),
  id: z.string(),
  name: z.string().min(1, 'Stage name required'),
  order: z.number(),
  required: z.boolean().default(true),
});

const swimlaneSchema = z.object({
  description: z.string().optional(),
  id: z.string(),
  name: z.string().min(1, 'Swimlane name required'),
  role: z.string().optional(),
});

const processSchema = z.object({
  category: z.enum(categoryOptions).optional(),
  description: z.string().max(MAX_DESCRIPTION_LENGTH).optional(),
  exitCriteria: z.string().optional(),
  expectedDurationHours: z.coerce.number().optional(),
  name: z.string().min(1, 'Name is required').max(MAX_NAME_LENGTH, 'Name too long'),
  owner: z.string().max(MAX_OWNER_LENGTH).optional(),
  purpose: z.string().max(MAX_PURPOSE_LENGTH).optional(),
  responsibleTeam: z.string().max(MAX_RESPONSIBLE_TEAM_LENGTH).optional(),
  slaHours: z.coerce.number().optional(),
  stages: z.array(stageSchema).optional(),
  swimlanes: z.array(swimlaneSchema).optional(),
});

type ProcessFormData = z.infer<typeof processSchema>;

interface CreateProcessFormProps {
  onCancel: () => void;
  onSuccess: () => void;
  projectId: string;
}

// Helper function to build process payload
const buildProcessPayload = (
  data: ProcessFormData,
  projectId: string,
): {
  name: string;
  projectId: string;
  category?: string | undefined;
  description?: string | undefined;
  expectedDurationHours?: number | undefined;
  exitCriteria?: string[] | undefined;
  owner?: string | undefined;
  purpose?: string | undefined;
  responsibleTeam?: string | undefined;
  slaHours?: number | undefined;
  stages?: {
    id: string;
    name: string;
    order: number;
    required: boolean;
    description?: string | undefined;
    estimatedDurationMinutes?: number | undefined;
    assignedRole?: string | undefined;
  }[];
  swimlanes?: {
    id: string;
    name: string;
    role?: string | undefined;
    description?: string | undefined;
  }[];
} => {
  const payload: {
    name: string;
    projectId: string;
    category?: string | undefined;
    description?: string | undefined;
    expectedDurationHours?: number | undefined;
    exitCriteria?: string[] | undefined;
    owner?: string | undefined;
    purpose?: string | undefined;
    responsibleTeam?: string | undefined;
    slaHours?: number | undefined;
    stages?: {
      id: string;
      name: string;
      order: number;
      required: boolean;
      description?: string | undefined;
      estimatedDurationMinutes?: number | undefined;
      assignedRole?: string | undefined;
    }[];
    swimlanes?: {
      id: string;
      name: string;
      role?: string | undefined;
      description?: string | undefined;
    }[];
  } = {
    name: data.name,
    projectId,
  };

  if (data.description) {
    payload.description = data.description;
  }
  if (data.purpose) {
    payload.purpose = data.purpose;
  }
  if (data.category) {
    payload.category = data.category;
  }
  if (data.owner) {
    payload.owner = data.owner;
  }
  if (data.responsibleTeam) {
    payload.responsibleTeam = data.responsibleTeam;
  }
  if (data.expectedDurationHours) {
    payload.expectedDurationHours = data.expectedDurationHours;
  }
  if (data.slaHours) {
    payload.slaHours = data.slaHours;
  }
  if (data.exitCriteria) {
    payload.exitCriteria = data.exitCriteria.split('\n').filter((c) => c.trim());
  }
  if (data.stages?.length) {
    payload.stages = data.stages.map((s) => ({
      id: s.id,
      name: s.name,
      order: s.order,
      required: s.required,
      ...(s.description && { description: s.description }),
      ...(s.estimatedDurationMinutes && {
        estimatedDurationMinutes: s.estimatedDurationMinutes,
      }),
      ...(s.assignedRole && { assignedRole: s.assignedRole }),
    }));
  }
  if (data.swimlanes?.length) {
    payload.swimlanes = data.swimlanes.map((sw) => ({
      id: sw.id,
      name: sw.name,
      ...(sw.role && { role: sw.role }),
      ...(sw.description && { description: sw.description }),
    }));
  }

  return payload;
};

export function CreateProcessForm({ projectId, onCancel, onSuccess }: CreateProcessFormProps) {
  const createProcess = useCreateProcess();

  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<ProcessFormData>({
    defaultValues: {
      stages: [],
      swimlanes: [],
    },
    resolver: zodResolver(processSchema) as Resolver<ProcessFormData>,
  });

  const {
    fields: stageFields,
    append: appendStage,
    remove: removeStage,
  } = useFieldArray({
    control,
    name: 'stages',
  });

  const {
    fields: swimlaneFields,
    append: appendSwimlane,
    remove: removeSwimlane,
  } = useFieldArray({
    control,
    name: 'swimlanes',
  });

  const onSubmit: SubmitHandler<ProcessFormData> = async (data) => {
    try {
      const payload = buildProcessPayload(data, projectId);
      await createProcess.mutateAsync(payload as Parameters<typeof createProcess.mutateAsync>[0]);
      onSuccess();
    } catch (error) {
      logger.error('Failed to create process:', error);
    }
  };

  const addStage = () => {
    appendStage({
      id: crypto.randomUUID(),
      name: '',
      order: stageFields.length + 1,
      required: true,
    });
  };

  const addSwimlane = () => {
    appendSwimlane({
      id: crypto.randomUUID(),
      name: '',
    });
  };

  return (
    <div className='fixed inset-0 z-50 flex items-center justify-center'>
      <div
        className='fixed inset-0 bg-black/50 backdrop-blur-sm'
        onClick={onCancel}
        role='presentation'
      />
      <div
        className='bg-background relative max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-xl border p-6 shadow-2xl'
        role='dialog'
        aria-modal='true'
        aria-labelledby='create-process-title'
      >
        <div className='flex items-center justify-between'>
          <h2 id='create-process-title' className='text-lg font-semibold'>
            Create Process
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

        <form onSubmit={handleSubmit(onSubmit)} className='mt-6 space-y-6'>
          {/* Basic Info */}
          <div className='space-y-4'>
            <h3 className='font-medium'>Basic Information</h3>

            <div>
              <label htmlFor='name' className='block text-sm font-medium'>
                Name <span className='text-red-500'>*</span>
              </label>
              <input
                id='name'
                {...register('name')}
                placeholder='Process name'
                className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
              />
              {errors.name && <p className='mt-1 text-sm text-red-500'>{errors.name.message}</p>}
            </div>

            <div>
              <label className='block text-sm font-medium'>Description</label>
              <textarea
                {...register('description')}
                rows={3}
                placeholder='Describe this process...'
                className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
              />
            </div>

            <div>
              <label className='block text-sm font-medium'>Purpose</label>
              <textarea
                {...register('purpose')}
                rows={2}
                placeholder='What is the purpose of this process?'
                className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
              />
            </div>

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
                      {cat.charAt(0).toUpperCase() + cat.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className='block text-sm font-medium'>Owner</label>
                <input
                  {...register('owner')}
                  placeholder='Process owner...'
                  className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
                />
              </div>
            </div>

            <div className='grid gap-4 sm:grid-cols-3'>
              <div>
                <label className='block text-sm font-medium'>Responsible Team</label>
                <input
                  {...register('responsibleTeam')}
                  placeholder='Team...'
                  className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
                />
              </div>
              <div>
                <label className='block text-sm font-medium'>Expected Duration (hours)</label>
                <input
                  {...register('expectedDurationHours')}
                  type='number'
                  min={0}
                  placeholder='Hours...'
                  className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
                />
              </div>
              <div>
                <label className='block text-sm font-medium'>SLA (hours)</label>
                <input
                  {...register('slaHours')}
                  type='number'
                  min={0}
                  placeholder='Hours...'
                  className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
                />
              </div>
            </div>
          </div>

          {/* Stages */}
          <div className='space-y-4'>
            <div className='flex items-center justify-between'>
              <h3 className='font-medium'>Stages</h3>
              <button
                type='button'
                onClick={addStage}
                className='text-primary flex items-center gap-1 text-sm hover:underline'
              >
                <Plus className='h-4 w-4' /> Add Stage
              </button>
            </div>

            {stageFields.length === 0 ? (
              <p className='text-muted-foreground text-sm'>
                No stages defined. Click "Add Stage" to define process steps.
              </p>
            ) : (
              <div className='space-y-3'>
                {stageFields.map((field, index) => (
                  <div key={field.id} className='flex items-start gap-3 rounded-lg border p-3'>
                    <span className='text-muted-foreground mt-2 text-sm font-medium'>
                      {index + 1}.
                    </span>
                    <div className='grid flex-1 gap-3 sm:grid-cols-2'>
                      <input
                        {...register(`stages.${index}.name`)}
                        placeholder='Stage name'
                        className='bg-background rounded-lg border px-3 py-2'
                      />
                      <input
                        {...register(`stages.${index}.assignedRole`)}
                        placeholder='Assigned role'
                        className='bg-background rounded-lg border px-3 py-2'
                      />
                      <input
                        {...register(`stages.${index}.description`)}
                        placeholder='Description'
                        className='bg-background rounded-lg border px-3 py-2 sm:col-span-2'
                      />
                    </div>
                    <button
                      type='button'
                      onClick={() => {
                        removeStage(index);
                      }}
                      className='mt-2 text-red-500 hover:text-red-700'
                    >
                      <Trash2 className='h-4 w-4' />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Swimlanes */}
          <div className='space-y-4'>
            <div className='flex items-center justify-between'>
              <h3 className='font-medium'>Swimlanes (Actors/Roles)</h3>
              <button
                type='button'
                onClick={addSwimlane}
                className='text-primary flex items-center gap-1 text-sm hover:underline'
              >
                <Plus className='h-4 w-4' /> Add Swimlane
              </button>
            </div>

            {swimlaneFields.length === 0 ? (
              <p className='text-muted-foreground text-sm'>
                No swimlanes defined. Click "Add Swimlane" to define actors.
              </p>
            ) : (
              <div className='space-y-3'>
                {swimlaneFields.map((field, index) => (
                  <div key={field.id} className='flex items-center gap-3 rounded-lg border p-3'>
                    <div className='grid flex-1 gap-3 sm:grid-cols-2'>
                      <input
                        {...register(`swimlanes.${index}.name`)}
                        placeholder='Swimlane name'
                        className='bg-background rounded-lg border px-3 py-2'
                      />
                      <input
                        {...register(`swimlanes.${index}.role`)}
                        placeholder='Role'
                        className='bg-background rounded-lg border px-3 py-2'
                      />
                    </div>
                    <button
                      type='button'
                      onClick={() => {
                        removeSwimlane(index);
                      }}
                      className='text-red-500 hover:text-red-700'
                    >
                      <Trash2 className='h-4 w-4' />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Exit Criteria */}
          <div>
            <label className='block text-sm font-medium'>Exit Criteria (one per line)</label>
            <textarea
              {...register('exitCriteria')}
              rows={3}
              placeholder='Conditions that must be met to complete the process...'
              className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
            />
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
              disabled={createProcess.isPending}
              className='bg-primary text-primary-foreground flex-1 rounded-lg px-4 py-2 disabled:opacity-50'
            >
              {createProcess.isPending ? 'Creating...' : 'Create Process'}
            </button>
          </div>

          {createProcess.isError && (
            <p className='text-sm text-red-500'>
              Error:{' '}
              {createProcess.error instanceof Error
                ? createProcess.error.message
                : String(createProcess.error)}
            </p>
          )}
        </form>
      </div>
    </div>
  );
}
