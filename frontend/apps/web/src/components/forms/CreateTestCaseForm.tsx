import type { JSX, SyntheticEvent } from 'react';
import type { Resolver, SubmitHandler } from 'react-hook-form';

import { zodResolver } from '@hookform/resolvers/zod';
import { X } from 'lucide-react';
import { useCallback } from 'react';
import { useForm } from 'react-hook-form';

import { logger } from '@/lib/logger';

import type { TestCaseFormData, TestCaseFormInput } from './CreateTestCaseForm.constants';

import { useCreateTestCase } from '../../hooks/useTestCases';
import { testCaseSchema } from './CreateTestCaseForm.constants';
import { buildCreateTestCasePayload } from './CreateTestCaseForm.payload';
import { TestCaseFormSections } from './CreateTestCaseForm.sections';

interface CreateTestCaseFormProps {
  projectId: string;
  onCancel: () => void;
  onSuccess: () => void;
}

interface CancelButtonProps {
  onCancel: () => void;
}

function ModalOverlay({ onCancel }: CancelButtonProps): JSX.Element {
  return (
    <button
      type='button'
      className='fixed inset-0 bg-black/50 backdrop-blur-sm'
      aria-label='Close dialog'
      onClick={onCancel}
    />
  );
}

function ModalHeader({ onCancel }: CancelButtonProps): JSX.Element {
  return (
    <div className='flex items-center justify-between'>
      <h2 id='create-test-case-title' className='text-lg font-semibold'>
        Create Test Case
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
  );
}

function CreateTestCaseForm({
  projectId,
  onCancel,
  onSuccess,
}: CreateTestCaseFormProps): JSX.Element {
  const createTestCase = useCreateTestCase();
  const resolver: Resolver<TestCaseFormInput, unknown, TestCaseFormData> =
    zodResolver(testCaseSchema);

  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<TestCaseFormInput, unknown, TestCaseFormData>({
    defaultValues: {
      automationStatus: 'not_automated',
      priority: 'medium',
      testSteps: [],
      testType: 'functional',
    },
    resolver,
  });

  const onSubmit: SubmitHandler<TestCaseFormData> = async (data) => {
    try {
      const payload = buildCreateTestCasePayload(data, projectId);
      await createTestCase.mutateAsync(payload);
      onSuccess();
    } catch (error) {
      logger.error('Failed to create test case:', error);
    }
  };

  const submitHandler = handleSubmit(onSubmit);
  const handleFormSubmit = useCallback(
    (event: SyntheticEvent<HTMLFormElement>): void => {
      const _submitResult = submitHandler(event);
    },
    [submitHandler],
  );

  const errorMessage = getErrorMessage(createTestCase);

  return (
    <div className='fixed inset-0 z-50 flex items-center justify-center'>
      <ModalOverlay onCancel={onCancel} />
      <div
        className='bg-background relative max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-xl border p-6 shadow-2xl'
        role='dialog'
        aria-modal='true'
        aria-labelledby='create-test-case-title'
      >
        <ModalHeader onCancel={onCancel} />
        <form onSubmit={handleFormSubmit} className='mt-6 space-y-4'>
          <TestCaseFormSections
            register={register}
            errors={errors}
            control={control}
            isPending={createTestCase.isPending}
            errorMessage={errorMessage}
            onCancel={onCancel}
          />
        </form>
      </div>
    </div>
  );
}

function getErrorMessage(createTestCase: ReturnType<typeof useCreateTestCase>): string | undefined {
  if (!createTestCase.isError) {
    return undefined;
  }

  const { error } = createTestCase;
  if (error instanceof Error) {
    return error.message;
  }
  return 'Failed to create test case';
}

export { CreateTestCaseForm };
