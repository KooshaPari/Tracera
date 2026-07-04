import type { FC } from 'react';

import { useCallback } from 'react';
import { toast } from 'sonner';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface CreateContractModalProps {
  readonly isOpen: boolean;
  readonly onClose: () => void;
}

export const CreateContractModal: FC<CreateContractModalProps> = ({ isOpen, onClose }) => {
  const handleCreate = useCallback(async () => {
    toast.error('Not implemented - API integration required');
  }, []);

  if (!isOpen) {
    return null;
  }

  return (
    <div className='fixed inset-0 z-50 flex items-center justify-center'>
      <button
        type='button'
        className='fixed inset-0 bg-black/50 backdrop-blur-sm'
        aria-label='Close dialog'
        onClick={onClose}
      />
      <div
        className='bg-background relative w-full max-w-2xl rounded-xl border p-6 shadow-2xl'
        role='dialog'
        aria-modal='true'
        aria-labelledby='create-contract-title'
      >
        <div className='mb-6 flex items-center justify-between'>
          <h2 id='create-contract-title' className='text-lg font-semibold'>
            Create New Contract
          </h2>
          <button
            type='button'
            onClick={onClose}
            aria-label='Close dialog'
            className='hover:bg-accent rounded-lg p-1'
          >
            ✕
          </button>
        </div>

        <div className='space-y-4'>
          <div>
            <label htmlFor='contract-title' className='mb-1 block text-sm font-medium'>
              Title
            </label>
            <Input id='contract-title' placeholder='e.g., User API Contract' className='h-10' />
          </div>

          <div className='grid gap-4 sm:grid-cols-2'>
            <div>
              <label htmlFor='contract-type' className='mb-1 block text-sm font-medium'>
                Type
              </label>
              <select
                id='contract-type'
                className='border-input bg-background h-10 w-full rounded-lg border px-3 text-sm'
              >
                <option value='api'>API</option>
                <option value='function'>Function</option>
                <option value='invariant'>Invariant</option>
                <option value='data'>Data</option>
                <option value='integration'>Integration</option>
              </select>
            </div>

            <div>
              <label htmlFor='contract-status' className='mb-1 block text-sm font-medium'>
                Status
              </label>
              <select
                id='contract-status'
                className='border-input bg-background h-10 w-full rounded-lg border px-3 text-sm'
              >
                <option value='draft'>Draft</option>
                <option value='active'>Active</option>
                <option value='verified'>Verified</option>
                <option value='violated'>Violated</option>
                <option value='deprecated'>Deprecated</option>
              </select>
            </div>
          </div>

          <div>
            <label htmlFor='contract-description' className='mb-1 block text-sm font-medium'>
              Description
            </label>
            <textarea
              id='contract-description'
              placeholder='Describe the contract...'
              className='border-input bg-background h-24 w-full rounded-lg border px-3 py-2'
            />
          </div>

          <div className='flex justify-end gap-2 pt-4'>
            <Button variant='ghost' onClick={onClose}>
              Cancel
            </Button>
            <Button onClick={handleCreate}>Create Contract</Button>
          </div>
        </div>
      </div>
    </div>
  );
};
