import type { FieldErrors, UseFormRegister } from 'react-hook-form';

import { zodResolver } from '@hookform/resolvers/zod';
import { X } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

const MAX_DESCRIPTION_LENGTH = 2000;
const MAX_NAME_LENGTH = 255;

const projectSchema = z.object({
  description: z.string().max(MAX_DESCRIPTION_LENGTH).optional(),
  name: z.string().min(1, 'Name is required').max(MAX_NAME_LENGTH, 'Name too long'),
});

type ProjectFormData = z.infer<typeof projectSchema>;

interface CreateProjectFormProps {
  isLoading?: boolean | undefined;
  onCancel: () => void;
  onSubmit: (data: ProjectFormData) => void;
}

const createProjectFormProps = ({
  onSubmit: _onSubmit,
  onCancel,
  isLoading,
}: CreateProjectFormProps) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
  });

  return {
    errors,
    handleSubmit,
    isLoading,
    onCancel,
    register,
  };
};

const CreateProjectHeader = ({ onCancel }: { onCancel: () => void }) => (
  <div className='flex items-center justify-between'>
    <h2 className='text-lg font-semibold'>Create Project</h2>
    <button onClick={onCancel} className='hover:bg-accent rounded-lg p-1'>
      <X className='h-5 w-5' />
    </button>
  </div>
);

const ProjectNameField = ({
  errors,
  register,
}: {
  errors: FieldErrors<ProjectFormData>;
  register: UseFormRegister<ProjectFormData>;
}) => (
  <div>
    <label htmlFor='name' className='block text-sm font-medium'>
      Project Name <span className='text-red-500'>*</span>
    </label>
    <input
      id='name'
      {...register('name')}
      placeholder='My Awesome Project'
      className='bg-background focus:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:ring-2 focus:outline-none'
    />
    {errors.name && <p className='mt-1 text-sm text-red-500'>{errors.name.message}</p>}
  </div>
);

const DescriptionField = ({
  errors,
  register,
}: {
  errors: FieldErrors<ProjectFormData>;
  register: UseFormRegister<ProjectFormData>;
}) => (
  <div>
    <label htmlFor='description' className='block text-sm font-medium'>
      Description
    </label>
    <textarea
      id='description'
      {...register('description')}
      rows={4}
      placeholder='What is this project about?'
      className='bg-background focus:ring-primary mt-1 w-full rounded-lg border px-3 py-2 focus:ring-2 focus:outline-none'
    />
    {errors.description && (
      <p className='mt-1 text-sm text-red-500'>{errors.description.message}</p>
    )}
  </div>
);

const CreateProjectFormActions = ({
  isLoading,
  onCancel,
}: {
  isLoading?: boolean | undefined;
  onCancel: () => void;
}) => (
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
      disabled={isLoading}
      className='bg-primary text-primary-foreground flex-1 rounded-lg px-4 py-2 disabled:opacity-50'
    >
      {isLoading ? 'Creating...' : 'Create Project'}
    </button>
  </div>
);

const CreateProjectContent = ({
  errors,
  handleSubmit,
  isLoading,
  onCancel,
  onSubmit,
  register,
}: ReturnType<typeof createProjectFormProps> & { onSubmit: (data: ProjectFormData) => void }) => (
  <form onSubmit={handleSubmit(onSubmit)} className='mt-6 space-y-4'>
    <ProjectNameField errors={errors} register={register} />
    <DescriptionField errors={errors} register={register} />
    <CreateProjectFormActions isLoading={isLoading} onCancel={onCancel} />
  </form>
);

export function CreateProjectForm({ onSubmit, onCancel, isLoading }: CreateProjectFormProps) {
  const props = createProjectFormProps({
    isLoading,
    onCancel,
    onSubmit,
  });

  return (
    <div className='fixed inset-0 z-50 flex items-center justify-center'>
      <div
        className='fixed inset-0 bg-black/50 backdrop-blur-sm'
        onClick={onCancel}
        role='presentation'
      />
      <div className='bg-background relative w-full max-w-md rounded-xl border p-6 shadow-2xl'>
        <CreateProjectHeader onCancel={onCancel} />
        <CreateProjectContent {...props} onSubmit={onSubmit} />
      </div>
    </div>
  );
}
