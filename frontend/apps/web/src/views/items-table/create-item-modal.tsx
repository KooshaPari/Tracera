import { X } from 'lucide-react';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { toast } from 'sonner';

import type { ItemStatus, Priority } from '@tracertm/types';

import {
  Button,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui';

import itemsTableConstants from './constants';

interface ItemsTableLabels {
  title: string;
  description: string;
  emptyTitle: string;
  emptyDescription: string;
  createModalTitle?: string | undefined;
  createButtonLabel?: string | undefined;
  newButtonLabel?: string | undefined;
}

interface CreateItemPayload {
  title: string;
  description: string | undefined;
  type: string;
  status: ItemStatus;
  priority: Priority;
}

interface CreateItemModalProps {
  labels: ItemsTableLabels;
  defaultType: string;
  pending: boolean;
  onClose: () => void;
  onCreate: (payload: CreateItemPayload) => void;
}

function readNonEmptyString(value: string): string | undefined {
  const trimmed = value.trim();
  if (trimmed === itemsTableConstants.EMPTY_STRING) {
    return;
  }
  return trimmed;
}

function isItemStatus(value: string): value is ItemStatus {
  return itemsTableConstants.STATUS_VALUES.some((status) => status === value);
}

function isPriority(value: string): value is Priority {
  return itemsTableConstants.PRIORITY_VALUES.some((priority) => priority === value);
}

const FOCUSABLE_SELECTOR = [
  'button',
  'input',
  'textarea',
  'select',
  "[tabindex]:not([tabindex='-1'])",
].join(',');

function getFocusableElements(modal: HTMLElement): HTMLElement[] {
  return [...modal.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR)].filter(
    (element) => !element.hasAttribute('disabled') && element.tabIndex !== -1,
  );
}

function handleInitialTab({
  event,
  titleInput,
  hasTabbedInModalRef,
}: {
  event: KeyboardEvent;
  titleInput: HTMLInputElement | null;
  hasTabbedInModalRef: { current: boolean };
}): boolean {
  if (document.activeElement !== titleInput || hasTabbedInModalRef.current) {
    return false;
  }

  event.preventDefault();
  hasTabbedInModalRef.current = true;
  return true;
}

function getFocusableEdges(
  modal: HTMLElement,
): { first: HTMLElement; last: HTMLElement } | undefined {
  const focusable = getFocusableElements(modal);
  const first = focusable.at(0);
  const last = focusable.at(-1);
  if (first === undefined || last === undefined) {
    return undefined;
  }
  return { first, last };
}

function getActiveElementInModal(modal: HTMLElement): HTMLElement | undefined {
  const active = document.activeElement;
  if (active instanceof HTMLElement && modal.contains(active)) {
    return active;
  }
  return undefined;
}

function focusFirstElement(
  first: HTMLElement,
  titleInput: HTMLInputElement | null,
  hasTabbedInModalRef: { current: boolean },
): void {
  first.focus();
  if (first === titleInput) {
    hasTabbedInModalRef.current = true;
  }
}

function handleTabKeyDown({
  event,
  modal,
  titleInput,
  hasTabbedInModalRef,
}: {
  event: KeyboardEvent;
  modal: HTMLElement;
  titleInput: HTMLInputElement | null;
  hasTabbedInModalRef: { current: boolean };
}): void {
  if (handleInitialTab({ event, hasTabbedInModalRef, titleInput })) {
    return;
  }

  const edges = getFocusableEdges(modal);
  if (edges === undefined) {
    return;
  }

  const active = getActiveElementInModal(modal);
  if (active === undefined) {
    event.preventDefault();
    focusFirstElement(edges.first, titleInput, hasTabbedInModalRef);
    return;
  }

  if (event.shiftKey) {
    if (active === edges.first) {
      event.preventDefault();
      edges.last.focus();
    }
    return;
  }

  if (active === edges.last) {
    event.preventDefault();
    edges.first.focus();
  }
}

function CreateItemModal({
  labels,
  defaultType,
  pending,
  onClose,
  onCreate,
}: CreateItemModalProps): JSX.Element {
  const [newTitle, setNewTitle] = useState<string>(itemsTableConstants.EMPTY_STRING);
  const [newDescription, setNewDescription] = useState<string>(itemsTableConstants.EMPTY_STRING);
  const [newType, setNewType] = useState<string>(defaultType);
  const [newStatus, setNewStatus] = useState<ItemStatus>(itemsTableConstants.DEFAULT_STATUS);
  const [newPriority, setNewPriority] = useState<Priority>(itemsTableConstants.DEFAULT_PRIORITY);
  const [formError, setFormError] = useState<string>();

  const titleInputRef = useRef<HTMLInputElement>(null);
  const modalRef = useRef<HTMLDivElement>(null);
  const hasTabbedInModalRef = useRef(false);

  useEffect((): (() => void) => {
    hasTabbedInModalRef.current = false;
    const timer = globalThis.setTimeout(() => {
      const input = titleInputRef.current;
      if (input !== null) {
        input.focus();
      }
    }, 0);

    const handleKeyDown = (event: KeyboardEvent): void => {
      if (event.key === 'Escape') {
        event.preventDefault();
        onClose();
        return;
      }

      if (event.key !== 'Tab') {
        return;
      }

      const modal = modalRef.current;
      if (modal === null) {
        return;
      }

      handleTabKeyDown({
        event,
        hasTabbedInModalRef,
        modal,
        titleInput: titleInputRef.current,
      });
    };

    globalThis.addEventListener('keydown', handleKeyDown);
    return (): void => {
      globalThis.clearTimeout(timer);
      globalThis.removeEventListener('keydown', handleKeyDown);
    };
  }, [onClose]);

  const titleValue = useMemo(() => newTitle.trim(), [newTitle]);
  const canSubmit = titleValue !== itemsTableConstants.EMPTY_STRING && !pending;

  const handleCreateSubmit = useCallback((): void => {
    const trimmedTitle = readNonEmptyString(newTitle);
    if (trimmedTitle === undefined) {
      toast.error('Title is required.');
      setFormError('Title is required.');
      return;
    }

    const description = readNonEmptyString(newDescription);
    onCreate({
      description,
      priority: newPriority,
      status: newStatus,
      title: trimmedTitle,
      type: newType,
    });
  }, [newDescription, newPriority, newStatus, newTitle, newType, onCreate]);

  const handleTitleChange = useCallback((event: React.ChangeEvent<HTMLInputElement>): void => {
    setNewTitle(event.target.value);
  }, []);

  const handleDescriptionChange = useCallback(
    (event: React.ChangeEvent<HTMLTextAreaElement>): void => {
      setNewDescription(event.target.value);
    },
    [],
  );

  const handleStatusChange = useCallback((event: React.ChangeEvent<HTMLSelectElement>): void => {
    const { value } = event.target;
    if (isItemStatus(value)) {
      setNewStatus(value);
    }
  }, []);

  const handlePriorityChange = useCallback((event: React.ChangeEvent<HTMLSelectElement>): void => {
    const { value } = event.target;
    if (isPriority(value)) {
      setNewPriority(value);
    }
  }, []);

  return (
    <div className='fixed inset-0 z-50 flex items-center justify-center'>
      <button
        type='button'
        className='fixed inset-0 bg-black/50 backdrop-blur-sm'
        onClick={onClose}
        aria-label='Close modal'
      />
      <div
        ref={modalRef}
        className='bg-background relative w-full max-w-lg rounded-xl border p-6 shadow-2xl'
        role='dialog'
        aria-modal='true'
        aria-labelledby='create-item-title'
      >
        <div className='flex items-center justify-between'>
          <h2 id='create-item-title' className='text-lg font-semibold'>
            {labels.createModalTitle ?? itemsTableConstants.DEFAULT_CREATE_LABEL}
          </h2>
          <button
            type='button'
            onClick={onClose}
            id='close-create-item'
            aria-label='Close dialog'
            tabIndex={-1}
            className='hover:bg-accent focus:ring-primary rounded-lg p-1 focus:ring-2 focus:outline-none'
          >
            <X className='h-5 w-5' />
          </button>
        </div>
        <div className='mt-4 space-y-4'>
          {formError !== undefined && (
            <div
              role='alert'
              aria-live='assertive'
              className='border-destructive/30 bg-destructive/10 text-destructive rounded-lg border px-3 py-2 text-sm'
            >
              {formError}
            </div>
          )}
          <div>
            <label htmlFor='item-title' className='block text-sm font-medium'>
              Title
            </label>
            <Input
              id='item-title'
              name='title'
              ref={titleInputRef}
              value={newTitle}
              onChange={handleTitleChange}
              placeholder='Enter item title'
              className='mt-1'
              aria-label='Title'
            />
          </div>
          <div>
            <label htmlFor='item-description' className='block text-sm font-medium'>
              Description
            </label>
            <textarea
              id='item-description'
              name='description'
              value={newDescription}
              onChange={handleDescriptionChange}
              placeholder='Describe the item'
              className='border-input bg-background focus:ring-primary mt-1 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:ring-2 focus:outline-none'
              aria-label='Description'
            />
          </div>
          <div className='grid gap-4 sm:grid-cols-2'>
            <div>
              <label htmlFor='item-type' className='block text-sm font-medium'>
                Type
              </label>
              <Select value={newType} onValueChange={setNewType}>
                <SelectTrigger
                  id='item-type'
                  aria-label='Type'
                  className='border-input bg-background focus:ring-primary mt-1 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:ring-2 focus:outline-none'
                >
                  <SelectValue placeholder='Select type' />
                </SelectTrigger>
                <SelectContent>
                  {itemsTableConstants.VIEW_TYPE_OPTIONS.map((option) => (
                    <SelectItem key={option} value={option}>
                      {option}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label htmlFor='item-status' className='block text-sm font-medium'>
                Status
              </label>
              <select
                id='item-status'
                name='status'
                value={newStatus}
                onChange={handleStatusChange}
                tabIndex={-1}
                className='border-input bg-background focus:ring-primary mt-1 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:ring-2 focus:outline-none'
                aria-label='Status'
              >
                {itemsTableConstants.STATUS_VALUES.map((status) => (
                  <option key={status} value={status}>
                    {status.replace('_', ' ')}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <label htmlFor='item-priority' className='block text-sm font-medium'>
              Priority
            </label>
            <select
              id='item-priority'
              name='priority'
              value={newPriority}
              onChange={handlePriorityChange}
              tabIndex={-1}
              className='border-input bg-background focus:ring-primary mt-1 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:ring-2 focus:outline-none'
              aria-label='Priority'
            >
              {itemsTableConstants.PRIORITY_VALUES.map((priority) => (
                <option key={priority} value={priority}>
                  {priority}
                </option>
              ))}
            </select>
          </div>
          <div className='flex justify-end gap-2 pt-2'>
            <Button id='create-item-save' onClick={handleCreateSubmit} disabled={!canSubmit}>
              {pending
                ? 'Creating...'
                : (labels.createButtonLabel ?? itemsTableConstants.DEFAULT_CREATE_LABEL)}
            </Button>
            <Button id='create-item-cancel' variant='ghost' onClick={onClose}>
              Cancel
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

export { CreateItemModal };
export type { CreateItemModalProps, CreateItemPayload, ItemsTableLabels };
