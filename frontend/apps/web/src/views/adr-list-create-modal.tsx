import type { UseMutationResult } from '@tanstack/react-query';

import { useState } from 'react';
import { toast } from 'sonner';

import type { ADRStatus } from '@tracertm/types';

import {
  Button,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui';

interface CreateADRData {
  projectId: string;
  title: string;
  context: string;
  decision: string;
  consequences: string;
}

interface ADRCreateModalProps {
  projectId: string;
  createADR: UseMutationResult<unknown, Error, CreateADRData>;
  onClose: () => void;
}

export function ADRCreateModal({
  projectId,
  createADR,
  onClose,
}: ADRCreateModalProps): React.JSX.Element {
  const [newTitle, setNewTitle] = useState('');
  const [newStatus, setNewStatus] = useState<ADRStatus>('proposed');
  const [newContext, setNewContext] = useState('');
  const [newDecision, setNewDecision] = useState('');

  const handleCreate = async (): Promise<void> => {
    if (!newTitle.trim()) {
      toast.error('Title is required');
      return;
    }
    try {
      await createADR.mutateAsync({
        projectId,
        title: newTitle,
        context: newContext,
        decision: newDecision,
        consequences: '',
      });
      toast.success('ADR created successfully');
      onClose();
    } catch {
      toast.error('Failed to create ADR');
    }
  };

  return (
    <div className='fixed inset-0 z-50 flex items-center justify-center'>
      <div
        className='fixed inset-0 bg-black/50 backdrop-blur-sm'
        onClick={onClose}
        onKeyDown={(event) => {
          if (event.key === 'Escape') onClose();
        }}
        role='button'
        tabIndex={0}
        aria-label='Close dialog'
      />
      <div
        className='bg-background relative w-full max-w-2xl rounded-xl border p-6 shadow-2xl'
        role='dialog'
        aria-modal='true'
        aria-labelledby='create-adr-title'
      >
        <div className='mb-6 flex items-center justify-between'>
          <h2 id='create-adr-title' className='text-lg font-semibold'>
            Create New ADR
          </h2>
          <button
            type='button'
            onClick={onClose}
            aria-label='Close dialog'
            className='hover:bg-accent rounded-lg p-1'
          >
            &#x2715;
          </button>
        </div>

        <div className='space-y-4'>
          <div>
            <label htmlFor='adr-title' className='mb-1 block text-sm font-medium'>
              Title
            </label>
            <Input
              id='adr-title'
              value={newTitle}
              onChange={(event) => {
                setNewTitle(event.target.value);
              }}
              placeholder='e.g., Use PostgreSQL for persistence'
              className='h-10'
            />
          </div>

          <div className='grid gap-4 sm:grid-cols-2'>
            <div>
              <label htmlFor='adr-status' className='mb-1 block text-sm font-medium'>
                Status
              </label>
              <Select
                value={newStatus}
                onValueChange={(value) => {
                  setNewStatus(value as ADRStatus);
                }}
              >
                <SelectTrigger id='adr-status' className='h-10'>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value='proposed'>Proposed</SelectItem>
                  <SelectItem value='accepted'>Accepted</SelectItem>
                  <SelectItem value='deprecated'>Deprecated</SelectItem>
                  <SelectItem value='superseded'>Superseded</SelectItem>
                  <SelectItem value='rejected'>Rejected</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div>
            <label htmlFor='adr-context' className='mb-1 block text-sm font-medium'>
              Context
            </label>
            <textarea
              id='adr-context'
              value={newContext}
              onChange={(event) => {
                setNewContext(event.target.value);
              }}
              placeholder='Describe the issue or context that led to this decision...'
              className='border-input bg-background h-24 w-full rounded-lg border px-3 py-2'
            />
          </div>

          <div>
            <label htmlFor='adr-decision' className='mb-1 block text-sm font-medium'>
              Decision
            </label>
            <textarea
              id='adr-decision'
              value={newDecision}
              onChange={(event) => {
                setNewDecision(event.target.value);
              }}
              placeholder='Describe the decision that was made...'
              className='border-input bg-background h-24 w-full rounded-lg border px-3 py-2'
            />
          </div>

          <div className='flex justify-end gap-2 pt-4'>
            <Button type='button' variant='ghost' onClick={onClose}>
              Cancel
            </Button>
            <Button
              type='button'
              onClick={() => {
                void handleCreate();
              }}
              disabled={createADR.isPending || !newTitle.trim()}
            >
              {createADR.isPending ? 'Creating...' : 'Create ADR'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
