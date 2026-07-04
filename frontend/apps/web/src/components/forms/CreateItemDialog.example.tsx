/**
 * CreateItemDialog Usage Example
 *
 * This file demonstrates how to use the CreateItemDialog component
 * in your views/pages.
 */

import { useCallback, useState } from 'react';

import type { ViewType } from '@tracertm/types';

import { CreateItemDialog } from './CreateItemDialog';

const CreateItemDialogInstructions = () => (
  <div className='mt-8 space-y-4'>
    <h2 className='text-xl font-semibold'>How it works:</h2>
    <ol className='list-inside list-decimal space-y-2'>
      <li>Click &quot;Create New Item&quot; to open the dialog</li>
      <li>Select an item type from the available options (based on current view)</li>
      <li>Fill in the type-specific form</li>
      <li>Submit to create the item (currently mocked with console.log)</li>
      <li>Or click &quot;Back&quot; to return to type selection</li>
    </ol>
    <h2 className='mt-6 text-xl font-semibold'>Props:</h2>
    <ul className='list-inside list-disc space-y-2'>
      <li>
        <code className='bg-muted rounded px-1 py-0.5'>open</code>: boolean - Controls dialog
        visibility
      </li>
      <li>
        <code className='bg-muted rounded px-1 py-0.5'>onOpenChange</code>: (open: boolean) =&gt;
        void
      </li>
      <li>
        <code className='bg-muted rounded px-1 py-0.5'>projectId</code>: string
      </li>
      <li>
        <code className='bg-muted rounded px-1 py-0.5'>defaultView</code>: ViewType
      </li>
    </ul>
    <h2 className='mt-6 text-xl font-semibold'>Available Item Types:</h2>
    <ul className='list-inside list-disc space-y-2'>
      <li>Test, Requirement, Epic, User Story, Task, Defect/Bug</li>
    </ul>
  </div>
);

export const CreateItemDialogExample = () => {
  const [isOpen, setIsOpen] = useState(false);
  const projectId = 'example-project-123';
  const currentView: ViewType = 'TEST';
  const onOpenClick = useCallback(() => {
    setIsOpen(true);
  }, []);

  return (
    <div className='p-4'>
      <h1 className='mb-4 text-2xl font-bold'>CreateItemDialog Example</h1>
      <button
        type='button'
        onClick={onOpenClick}
        className='bg-primary text-primary-foreground hover:bg-primary/90 rounded-lg px-4 py-2'
      >
        Create New Item
      </button>
      <CreateItemDialog
        open={isOpen}
        onOpenChange={setIsOpen}
        projectId={projectId}
        defaultView={currentView}
      />
      <CreateItemDialogInstructions />
    </div>
  );
};
