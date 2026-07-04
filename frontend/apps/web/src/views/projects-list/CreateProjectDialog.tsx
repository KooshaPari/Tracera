import { useCallback, useState } from 'react';
import { toast } from 'sonner';

import type { Project } from '@tracertm/types';

import { useCreateProject } from '@/hooks/useProjects';
import { getProjectDisplayName } from '@/lib/project-name-utils';
import { Button, Dialog, DialogContent, Input, Label, Textarea } from '@tracertm/ui';

interface CreateProjectDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreated?: (project: Project) => void;
}

const EMPTY_STRING = '';

interface CreateProjectDialogFormProps {
  createPending: boolean;
  description: string;
  name: string;
  onCancel: () => void;
  onDescriptionChange: (event: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onIntegrationsChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onNameChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onSubmit: (event: React.SyntheticEvent<HTMLFormElement>) => void;
  openIntegrations: boolean;
}

function renderCreateProjectDialogHeader(): JSX.Element {
  return (
    <div className='bg-primary text-primary-foreground p-8'>
      <div className='mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-white/20'>
        <span className='text-lg font-black'>+</span>
      </div>
      <h2 className='text-2xl font-black tracking-tight uppercase'>New Registry</h2>
      <p className='text-primary-foreground/70 mt-1 text-xs font-bold tracking-widest uppercase'>
        Initialize a new project container
      </p>
    </div>
  );
}

function renderCreateProjectDialogForm({
  createPending,
  description,
  name,
  onCancel,
  onDescriptionChange,
  onIntegrationsChange,
  onNameChange,
  onSubmit,
  openIntegrations,
}: CreateProjectDialogFormProps): JSX.Element {
  let submitLabel = 'Initialize';
  if (createPending) {
    submitLabel = 'Syncing...';
  }

  return (
    <form onSubmit={onSubmit} className='space-y-6 p-8'>
      <div className='space-y-4'>
        <div className='space-y-2'>
          <Label
            htmlFor='project-name'
            className='ml-1 text-[10px] font-black tracking-widest uppercase'
          >
            Project Identifier
          </Label>
          <Input
            id='project-name'
            value={name}
            onChange={onNameChange}
            placeholder='e.g. PROJECT-X-ALPHA'
            className='bg-muted/30 h-12 rounded-xl border-none px-4 font-bold'
          />
        </div>

        <div className='space-y-2'>
          <Label
            htmlFor='project-description'
            className='ml-1 text-[10px] font-black tracking-widest uppercase'
          >
            Technical Brief
          </Label>
          <Textarea
            id='project-description'
            value={description}
            onChange={onDescriptionChange}
            placeholder='Context and scope definition...'
            className='bg-muted/30 min-h-[120px] rounded-xl border-none p-4 font-medium'
          />
        </div>
      </div>

      <div className='flex gap-3 pt-4'>
        <label className='text-muted-foreground flex items-center gap-2 text-[10px] font-bold tracking-widest uppercase'>
          <input type='checkbox' checked={openIntegrations} onChange={onIntegrationsChange} />
          Open integrations after create
        </label>
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
          disabled={createPending}
          className='shadow-primary/20 h-12 flex-1 rounded-xl text-[10px] font-black tracking-widest uppercase shadow-lg'
        >
          {submitLabel}
        </Button>
      </div>
    </form>
  );
}

export function CreateProjectDialog({
  open,
  onOpenChange,
  onCreated,
}: CreateProjectDialogProps): JSX.Element {
  const [name, setName] = useState(EMPTY_STRING);
  const [description, setDescription] = useState(EMPTY_STRING);
  const [openIntegrations, setOpenIntegrations] = useState(true);
  const createProject = useCreateProject();

  const handleNameChange = useCallback((event: React.ChangeEvent<HTMLInputElement>): void => {
    setName(event.target.value);
  }, []);

  const handleDescriptionChange = useCallback(
    (event: React.ChangeEvent<HTMLTextAreaElement>): void => {
      setDescription(event.target.value);
    },
    [],
  );

  const handleIntegrationsChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>): void => {
      setOpenIntegrations(event.target.checked);
    },
    [],
  );

  const handleCancel = useCallback((): void => {
    onOpenChange(false);
  }, [onOpenChange]);

  const handleSubmit = useCallback(
    (event: React.SyntheticEvent<HTMLFormElement>): void => {
      event.preventDefault();
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

      createProject.mutate(payload, {
        onError: () => {
          toast.error('Cluster reject: Failed to initialize project');
        },
        onSuccess: (project) => {
          toast.success(`Project "${getProjectDisplayName(project)}" initialized`);
          setName(EMPTY_STRING);
          setDescription(EMPTY_STRING);
          onOpenChange(false);
          if (openIntegrations) {
            onCreated?.(project);
          }
        },
      });
    },
    [createProject, description, name, onCreated, onOpenChange, openIntegrations],
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className='bg-card overflow-hidden rounded-[2rem] border-none p-0 shadow-2xl sm:max-w-[500px]'>
        {renderCreateProjectDialogHeader()}
        {renderCreateProjectDialogForm({
          createPending: createProject.isPending,
          description,
          name,
          onCancel: handleCancel,
          onDescriptionChange: handleDescriptionChange,
          onIntegrationsChange: handleIntegrationsChange,
          onNameChange: handleNameChange,
          onSubmit: handleSubmit,
          openIntegrations,
        })}
      </DialogContent>
    </Dialog>
  );
}
