/**
 * CreateItemDialog Component
 *
 * Phase 4 of the Type-Aware Node System
 * Unified multi-step item creation dialog with two-step flow:
 * 1. Select item type using ItemTypeSelector
 * 2. Fill type-specific form (CreateTestItemForm, CreateRequirementItemForm, etc.)
 *
 * Props:
 * - open: boolean - Dialog open state
 * - onOpenChange: (open: boolean) => void - Handler for dialog state changes
 * - projectId: string - Current project ID
 * - defaultView: ViewType - Current view (determines available item types)
 *
 * Note: Type-specific forms render their own dialog structure, so this component
 * conditionally renders either the type selector dialog or delegates to the form.
 */

import { useCallback, useState } from 'react';

import type { CreateItemInput } from '@/lib/validation/schemas';
import type { ViewType } from '@/types';

import { createItem } from '@/api/items';
import { toast } from '@/components/ui/toaster';
import {
  buildErrorMetadata,
  extractValidationErrors,
  formatValidationErrorMessage,
} from '@/lib/api-error-handler';
import { isAuthError } from '@/lib/api-error-handler';
import { logger } from '@/lib/logger';
import { queueMutation, removeMutationFromQueue, updateMutationError } from '@/lib/mutation-queue';
import { withRetry } from '@/lib/retry';

import { CreateDefectItemForm } from './CreateDefectItemForm';
import { CreateEpicItemForm } from './CreateEpicItemForm';
import { CreateRequirementItemForm } from './CreateRequirementItemForm';
import { CreateTaskItemForm } from './CreateTaskItemForm';
import { CreateTestItemForm } from './CreateTestItemForm';
import { CreateUserStoryItemForm } from './CreateUserStoryItemForm';
import { ItemTypeSelector } from './ItemTypeSelector';

interface CreateItemDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  projectId: string;
  defaultView: ViewType;
  /** Dialog title (e.g. "Create New Feature"). Default: "Create New Item" */
  title?: string | undefined;
}

export function CreateItemDialog({
  open,
  onOpenChange,
  projectId,
  defaultView,
  title: titleProp = 'Create New Item',
}: CreateItemDialogProps) {
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Reset state when dialog closes
  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      // Reset to step 1 when dialog closes
      setSelectedType(null);
      setIsSubmitting(false);
    }
    onOpenChange(newOpen);
  };

  // Handle type selection (step 1 -> step 2)
  const handleTypeSelect = (type: string) => {
    setSelectedType(type);
  };

  // Handle form submission (step 2)
  const handleFormSubmit = useCallback(
    async (data: unknown) => {
      setIsSubmitting(true);
      const toastId = `create_item_${Date.now()}`;

      try {
        // Validate form data
        if (!data || typeof data !== 'object') {
          toast.error('Invalid form data', { id: toastId });
          setIsSubmitting(false);
          return;
        }

        const formData = data as Record<string, unknown>;

        // Build CreateItemInput with required fields
        const itemInput = {
          description: (formData['description'] as string | undefined) ?? '',
          priority: (formData['priority'] as string) ?? 'medium',
          projectId,
          status: (formData['status'] as string) ?? 'draft',
          title: (formData['name'] ?? formData['title']) as string,
          type: (selectedType ?? 'item') as CreateItemInput['type'],
          view: (formData['view'] as string) ?? defaultView,
          ...formData,
        } as CreateItemInput;

        // Show retrying toast
        const retryingToastId = `create_item_retrying_${Date.now()}`;

        // Attempt to create item with retry logic
        const result = await withRetry(async () => createItem(itemInput), {
          maxAttempts: 3,
          baseDelayMs: 1000,
          onRetry: (attempt, error) => {
            toast.loading(`Retrying... (Attempt ${attempt}/3)`, {
              id: retryingToastId,
            });
            logger.warn(`Retry attempt ${attempt} after error:`, error.message);
          },
        });

        if (!result.success) {
          // Handle failed creation after all retries
          const errorMetadata = buildErrorMetadata(result.error);
          logger.error('Failed to create item after retries:', {
            ...errorMetadata,
            attempts: result.attempts,
          });

          // Special handling for auth errors
          if (isAuthError(result.error)) {
            toast.error('Your session has expired. Please log in again.', {
              id: toastId,
            });
            // Redirect to login would happen via auth store
            setIsSubmitting(false);
            return;
          }

          // Check for validation errors
          const validationErrors = extractValidationErrors(result.error);
          if (validationErrors) {
            const errorMessage = formatValidationErrorMessage(validationErrors);
            toast.error(errorMessage, {
              description: 'Please fix the errors and try again.',
              id: toastId,
            });
            setIsSubmitting(false);
            return;
          }

          // For transient errors, offer queue option
          if (errorMetadata.retryable) {
            const mutationId = queueMutation({
              createdAt: new Date().toISOString(),
              data: itemInput,
              failedAttempts: result.attempts,
              lastError: result.error?.message,
              type: 'create_item',
            });

            toast.error(errorMetadata.userMessage, {
              action: {
                label: 'Undo',
                onClick: () => {
                  removeMutationFromQueue(mutationId);
                  toast.success('Operation cancelled', { id: toastId });
                },
              },
              description: 'Your operation has been queued and will retry when you reconnect.',
              id: toastId,
            });

            // Still close the dialog since mutation is queued
            handleOpenChange(false);
            setIsSubmitting(false);
            return;
          }

          // Unknown error
          toast.error(errorMetadata.userMessage, {
            description: 'Please try again or contact support if the problem persists.',
            id: toastId,
          });
          setIsSubmitting(false);
          return;
        }

        // Success!
        logger.info('Item created successfully:', {
          itemId: (result.data as { id?: string }).id,
          type: selectedType,
        });

        toast.success('Item created successfully', { id: toastId });

        // Close dialog and reset
        handleOpenChange(false);
      } catch (error) {
        // Catch any unexpected errors not caught by retry logic
        const errorMetadata = buildErrorMetadata(error);
        logger.error('Unexpected error creating item:', errorMetadata);

        toast.error(errorMetadata.userMessage, {
          description: 'An unexpected error occurred. Please try again.',
          id: toastId,
        });
      } finally {
        setIsSubmitting(false);
      }
    },
    [selectedType, handleOpenChange],
  );

  // Handle cancel (go back to step 1 or close dialog)
  const handleCancel = () => {
    if (selectedType) {
      // If on step 2, go back to step 1
      setSelectedType(null);
    } else {
      // If on step 1, close dialog
      handleOpenChange(false);
    }
  };

  // Render the appropriate form based on selected type
  const renderForm = () => {
    if (!selectedType) {
      return null;
    }

    const formProps = {
      isLoading: isSubmitting,
      onCancel: handleCancel,
      onSubmit: handleFormSubmit,
    };

    switch (selectedType) {
      case 'test': {
        return <CreateTestItemForm {...formProps} />;
      }
      case 'requirement': {
        return <CreateRequirementItemForm {...formProps} />;
      }
      case 'epic': {
        return <CreateEpicItemForm {...formProps} />;
      }
      case 'user_story':
      case 'story': {
        return <CreateUserStoryItemForm {...formProps} />;
      }
      case 'task': {
        return <CreateTaskItemForm {...formProps} />;
      }
      case 'bug':
      case 'defect': {
        return <CreateDefectItemForm {...formProps} />;
      }
      default: {
        // Fallback for unknown types
        return (
          <div className='p-4 text-center'>
            <p className='text-muted-foreground'>
              Form for type "{selectedType}" not yet implemented.
            </p>
            <button
              type='button'
              onClick={handleCancel}
              className='hover:bg-accent mt-4 rounded-lg border px-4 py-2'
            >
              Back to Type Selection
            </button>
          </div>
        );
      }
    }
  };

  // If a type is selected, render the type-specific form directly
  // (forms have their own dialog structure)
  if (selectedType) {
    return <>{renderForm()}</>;
  }

  // Otherwise render the type selection dialog
  if (!open) {
    return null;
  }

  return (
    <div className='fixed inset-0 z-50 flex items-center justify-center'>
      {/* Backdrop */}
      <div
        className='fixed inset-0 bg-black/50 backdrop-blur-sm'
        onClick={handleCancel}
        aria-hidden='true'
      />

      {/* Dialog */}
      <div
        role='dialog'
        aria-modal='true'
        aria-labelledby='dialog-title'
        className='bg-background relative max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-xl border p-6 shadow-2xl'
      >
        <div className='mb-6'>
          <h2 id='dialog-title' className='text-lg font-semibold'>
            {titleProp}
          </h2>
          <p className='text-muted-foreground mt-1 text-sm'>
            Select the type of item you want to create
          </p>
        </div>

        <div className='mt-6'>
          <ItemTypeSelector
            view={defaultView}
            selectedType={selectedType ?? undefined}
            onSelect={handleTypeSelect}
          />
        </div>

        {/* Cancel button */}
        <div className='mt-6 flex justify-end border-t pt-4'>
          <button
            type='button'
            onClick={handleCancel}
            className='hover:bg-accent focus-visible:ring-primary rounded-lg border px-4 py-2 focus:outline-none focus-visible:ring-2'
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
