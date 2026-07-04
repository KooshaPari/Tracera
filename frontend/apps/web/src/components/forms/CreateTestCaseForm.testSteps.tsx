import type { JSX } from 'react';
import type { Control, UseFormRegister } from 'react-hook-form';

import { Plus, Trash2 } from 'lucide-react';
import { useCallback, useMemo } from 'react';
import { useFieldArray } from 'react-hook-form';

import type { TestCaseFormInput } from './CreateTestCaseForm.constants';

import { getFieldHandlers, getFieldProps } from './CreateTestCaseForm.fieldHelpers';

interface TestStepsSectionProps {
  register: UseFormRegister<TestCaseFormInput>;
  control: Control<TestCaseFormInput>;
}

interface TestStepRowProps {
  register: UseFormRegister<TestCaseFormInput>;
  index: number;
  fieldId: string;
  onRemove: () => void;
}

function TestStepRow({ register, index, fieldId, onRemove }: TestStepRowProps): JSX.Element {
  const actionField = getFieldProps(register(`testSteps.${index}.action` as const));
  const expectedResultField = getFieldProps(register(`testSteps.${index}.expectedResult` as const));
  const testDataField = getFieldProps(register(`testSteps.${index}.testData` as const));
  const actionHandlers = getFieldHandlers(actionField);
  const expectedHandlers = getFieldHandlers(expectedResultField);
  const testDataHandlers = getFieldHandlers(testDataField);
  const stepId = `test-case-step-${index}`;
  const handleRemoveClick = onRemove;

  return (
    <div className='rounded-lg border p-3'>
      <div className='mb-2 flex items-center justify-between'>
        <span className='text-muted-foreground text-sm font-medium'>Step {index + 1}</span>
        <button
          type='button'
          onClick={handleRemoveClick}
          className='text-red-500 hover:text-red-700'
          aria-label={`Remove step ${index + 1}`}
        >
          <Trash2 className='h-4 w-4' />
        </button>
      </div>
      <div className='space-y-2'>
        <label className='sr-only' htmlFor={`${stepId}-action`}>
          Action
        </label>
        <input
          id={`${stepId}-action`}
          name={actionField.name}
          onBlur={actionHandlers.handleBlur}
          onChange={actionHandlers.handleChange}
          ref={actionField.ref}
          placeholder='Action to perform...'
          className='bg-background w-full rounded-lg border px-3 py-2 text-sm'
        />
        <label className='sr-only' htmlFor={`${stepId}-expected`}>
          Expected result
        </label>
        <input
          id={`${stepId}-expected`}
          name={expectedResultField.name}
          onBlur={expectedHandlers.handleBlur}
          onChange={expectedHandlers.handleChange}
          ref={expectedResultField.ref}
          placeholder='Expected result...'
          className='bg-background w-full rounded-lg border px-3 py-2 text-sm'
        />
        <label className='sr-only' htmlFor={`${stepId}-data`}>
          Test data
        </label>
        <input
          id={`${stepId}-data`}
          name={testDataField.name}
          onBlur={testDataHandlers.handleBlur}
          onChange={testDataHandlers.handleChange}
          ref={testDataField.ref}
          placeholder='Test data (optional)...'
          className='bg-background w-full rounded-lg border px-3 py-2 text-sm'
        />
      </div>
      <input id={fieldId} type='hidden' value={fieldId} />
    </div>
  );
}

function TestStepsSection({ register, control }: TestStepsSectionProps): JSX.Element {
  const { fields, append, remove } = useFieldArray({ control, name: 'testSteps' });
  const handleAddStep = useCallback(() => {
    append({ action: '', expectedResult: '', testData: '' });
  }, [append]);
  const handleRemoveStepHandlers = useMemo(
    (): (() => void)[] =>
      fields.map((_, index): (() => void) => () => {
        remove(index);
      }),
    [fields, remove],
  );

  return (
    <div>
      <div className='flex items-center justify-between'>
        <span className='block text-sm font-medium'>Test Steps</span>
        <button
          type='button'
          onClick={handleAddStep}
          className='text-primary hover:text-primary/80 flex items-center gap-1 text-sm'
        >
          <Plus className='h-4 w-4' /> Add Step
        </button>
      </div>
      <div className='mt-2 space-y-3'>
        {fields.map((field, index) => (
          <TestStepRow
            key={field.id}
            register={register}
            index={index}
            fieldId={field.id}
            onRemove={handleRemoveStepHandlers[index]!}
          />
        ))}
        {fields.length === 0 && (
          <p className='text-muted-foreground text-sm italic'>
            No test steps defined. Click &quot;Add Step&quot; to add one.
          </p>
        )}
      </div>
    </div>
  );
}

export { TestStepsSection };
