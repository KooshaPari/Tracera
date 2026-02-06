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

import { useState } from 'react';

import type { ViewType } from '@tracertm/types';

import { logger } from '@/lib/logger';

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
  title?: string;
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
  const handleFormSubmit = async (data: unknown) => {
    setIsSubmitting(true);
    try {
      // TODO: Replace with actual API call
      logger.info('Creating item:', {
        data,
        projectId,
        type: selectedType,
        view: defaultView,
      });

      // Mock API delay
      await new Promise((resolve) => setTimeout(resolve, 500));

      // Success - close dialog and reset
      handleOpenChange(false);
    } catch (error) {
      logger.error('Failed to create item:', error);
      // TODO: Show error notification
    } finally {
      setIsSubmitting(false);
    }
  };

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
