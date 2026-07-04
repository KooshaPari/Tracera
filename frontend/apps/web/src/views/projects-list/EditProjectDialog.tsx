import { useCallback, useEffect, useState } from 'react';
import { toast } from 'sonner';

import type { Project } from '@tracertm/types';

import { useUpdateProject } from '@/hooks/useProjects';
import { getProjectDisplayName } from '@/lib/project-name-utils';
import { Button, Dialog, DialogContent, Input, Label, Textarea } from '@tracertm/ui';

interface EditProjectDialogProps {
  project?: Project | undefined;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const EMPTY_STRING = '';

interface EditProjectDialogFormProps {
  description: string;
  name: string;
  onCancel: () => void;
  onDescriptionChange: (event: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onNameChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onSubmit: (event: React.SyntheticEvent<HTMLFormElement>) => void;
  submitDisabled: boolean;
  submitLabel: string;
}

const getNonEmptyString = (value: unknown): string => {
  if (typeof value === 'string' && value.length > 0) {
    return value;
  }
  return EMPTY_STRING;
};

const syncEditProjectDialogFields = (
  project: Project | undefined,
  setName: React.Dispatch<React.SetStateAction<string>>,
  setDescription: React.Dispatch<React.SetStateAction<string>>,
): void => {
  if (project) {
    setName(getNonEmptyString(project.name));
    setDescription(getNonEmptyString(project.description));
    return;
  }
  setName(EMPTY_STRING);
  setDescription(EMPTY_STRING);
};

function renderEditProjectDialogHeader(): JSX.Element {
  return (
    <div className='bg-primary text-primary-foreground p-8'>
      <div className='mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-white/20'>
        <span className='text-lg font-black'>✎</span>
      </div>
      <h2 className='text-2xl font-black tracking-tight uppercase'>Edit Registry</h2>
      <p className='text-primary-foreground/70 mt-1 text-xs font-bold tracking-widest uppercase'>
        Modify project container details
      </p>
    </div>
  );
}

function renderEditProjectDialogForm({
  description,
  name,
  onCancel,
  onDescriptionChange,
  onNameChange,
  onSubmit,
  submitDisabled,
  submitLabel,
}: EditProjectDialogFormProps): JSX.Element {
  return (
    <form onSubmit={onSubmit} className='space-y-6 p-8'>
      <div className='space-y-4'>
        <div className='space-y-2'>
          <Label
            htmlFor='edit-project-name'
            className='ml-1 text-[10px] font-black tracking-widest uppercase'
          >
            Project Identifier
          </Label>
          <Input
            id='edit-project-name'
            value={name}
            onChange={onNameChange}
            placeholder='e.g. PROJECT-X-ALPHA'
            className='bg-muted/30 h-12 rounded-xl border-none px-4 font-bold'
          />
        </div>

        <div className='space-y-2'>
          <Label
            htmlFor='edit-project-description'
            className='ml-1 text-[10px] font-black tracking-widest uppercase'
          >
            Technical Brief
          </Label>
          <Textarea
            id='edit-project-description'
            value={description}
            onChange={onDescriptionChange}
            placeholder='Context and scope definition...'
            className='bg-muted/30 min-h-[120px] rounded-xl border-none p-4 font-medium'
          />
        </div>
      </div>

      <div className='flex gap-3 pt-2'>
        <Button
          type='button'
          variant='ghost'
          onClick={onCancel}
          className='flex-1 rounded-xl text-[10px] font-black tracking-widest uppercase'
        >
          Cancel
        </Button>
        <Button
          type='submit'
          disabled={submitDisabled}
          className='shadow-primary/20 h-12 flex-1 rounded-xl text-[10px] font-black tracking-widest uppercase shadow-lg'
        >
          {submitLabel}
        </Button>
      </div>
    </form>
  );
}

interface EditProjectDialogModel {
  description: string;
  isDialogOpen: boolean;
  name: string;
  onCancel: () => void;
  onDescriptionChange: (event: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onNameChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onSubmit: (event: React.SyntheticEvent<HTMLFormElement>) => void;
  submitDisabled: boolean;
  submitLabel: string;
}

function useEditProjectDialogModel({
  onOpenChange,
  open,
  project,
}: EditProjectDialogProps): EditProjectDialogModel {
  const [name, setName] = useState(EMPTY_STRING);
  const [description, setDescription] = useState(EMPTY_STRING);
  const updateProject = useUpdateProject();

  useEffect((): void => {
    syncEditProjectDialogFields(project, setName, setDescription);
  }, [project]);

  const onNameChange = useCallback((event: React.ChangeEvent<HTMLInputElement>): void => {
    setName(event.target.value);
  }, []);

  const onDescriptionChange = useCallback((event: React.ChangeEvent<HTMLTextAreaElement>): void => {
    setDescription(event.target.value);
  }, []);

  const onCancel = useCallback((): void => {
    onOpenChange(false);
  }, [onOpenChange]);

  const onSubmit = useCallback(
    (event: React.SyntheticEvent<HTMLFormElement>): void => {
      event.preventDefault();
      if (!project) {
        toast.error('Project not loaded');
        return;
      }

      const trimmedName = name.trim();
      if (trimmedName === EMPTY_STRING) {
        toast.error('Project identity sequence required');
        return;
      }

      const trimmedDescription = description.trim();
      const payload: { name: string; description?: string } = { name: trimmedName };
      if (trimmedDescription !== EMPTY_STRING) {
        payload.description = trimmedDescription;
      }

      updateProject.mutate(
        { data: payload, id: project.id },
        {
          onError: () => {
            toast.error('Cluster reject: Failed to update project');
          },
          onSuccess: () => {
            toast.success(
              `Project "${getProjectDisplayName({ ...project, name: trimmedName })}" updated`,
            );
            setName(EMPTY_STRING);
            setDescription(EMPTY_STRING);
            onOpenChange(false);
          },
        },
      );
    },
    [description, name, onOpenChange, project, updateProject],
  );

  const isDialogOpen = Boolean(project) && open;
  let submitLabel = 'Update';
  if (updateProject.isPending) {
    submitLabel = 'Syncing...';
  }

  return {
    description,
    isDialogOpen,
    name,
    onCancel,
    onDescriptionChange,
    onNameChange,
    onSubmit,
    submitDisabled: updateProject.isPending,
    submitLabel,
  };
}

export function EditProjectDialog({
  project,
  open,
  onOpenChange,
}: EditProjectDialogProps): JSX.Element {
  const model = useEditProjectDialogModel({ onOpenChange, open, project });

  return (
    <Dialog open={model.isDialogOpen} onOpenChange={onOpenChange}>
      <DialogContent className='bg-card overflow-hidden rounded-[2rem] border-none p-0 shadow-2xl sm:max-w-[500px]'>
        {renderEditProjectDialogHeader()}
        {renderEditProjectDialogForm({
          description: model.description,
          name: model.name,
          onCancel: model.onCancel,
          onDescriptionChange: model.onDescriptionChange,
          onNameChange: model.onNameChange,
          onSubmit: model.onSubmit,
          submitDisabled: model.submitDisabled,
          submitLabel: model.submitLabel,
        })}
      </DialogContent>
    </Dialog>
  );
}
