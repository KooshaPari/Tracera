import type { JSX } from 'react';
import type { Control, FieldErrors, UseFormRegister } from 'react-hook-form';

import type { TestCaseFormInput } from './CreateTestCaseForm.constants';

import {
  automationLabels,
  automationStatuses,
  categoryOptions,
  priorities,
  testTypes,
  typeLabels,
} from './CreateTestCaseForm.constants';
import { getFieldHandlers, getFieldProps } from './CreateTestCaseForm.fieldHelpers';
import { TestStepsSection } from './CreateTestCaseForm.testSteps';

interface BaseSectionProps {
  register: UseFormRegister<TestCaseFormInput>;
  errors: FieldErrors<TestCaseFormInput>;
}

interface FieldArraySectionProps extends BaseSectionProps {
  control: Control<TestCaseFormInput>;
}

function TitleSection({ register, errors }: BaseSectionProps): JSX.Element {
  const titleField = getFieldProps(register('title'));
  const titleHandlers = getFieldHandlers(titleField);

  return (
    <div>
      <label className='block text-sm font-medium' htmlFor='test-case-title'>
        Title <span className='text-red-500'>*</span>
      </label>
      <input
        id='test-case-title'
        name={titleField.name}
        onBlur={titleHandlers.handleBlur}
        onChange={titleHandlers.handleChange}
        ref={titleField.ref}
        placeholder='Brief description of the test case'
        className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
      />
      {errors.title && <p className='mt-1 text-sm text-red-500'>{errors.title.message}</p>}
    </div>
  );
}

function DescriptionObjectiveSection({ register }: BaseSectionProps): JSX.Element {
  const descriptionField = getFieldProps(register('description'));
  const objectiveField = getFieldProps(register('objective'));
  const descriptionHandlers = getFieldHandlers(descriptionField);
  const objectiveHandlers = getFieldHandlers(objectiveField);

  return (
    <div className='grid gap-4 sm:grid-cols-2'>
      <div>
        <label className='block text-sm font-medium' htmlFor='test-case-description'>
          Description
        </label>
        <textarea
          id='test-case-description'
          name={descriptionField.name}
          onBlur={descriptionHandlers.handleBlur}
          onChange={descriptionHandlers.handleChange}
          ref={descriptionField.ref}
          rows={3}
          placeholder='Detailed description of what this test case covers...'
          className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
        />
      </div>
      <div>
        <label className='block text-sm font-medium' htmlFor='test-case-objective'>
          Objective
        </label>
        <textarea
          id='test-case-objective'
          name={objectiveField.name}
          onBlur={objectiveHandlers.handleBlur}
          onChange={objectiveHandlers.handleChange}
          ref={objectiveField.ref}
          rows={3}
          placeholder='What is the goal of this test?'
          className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
        />
      </div>
    </div>
  );
}

function TypePriorityCategorySection({ register }: BaseSectionProps): JSX.Element {
  const testTypeField = getFieldProps(register('testType'));
  const priorityField = getFieldProps(register('priority'));
  const categoryField = getFieldProps(register('category'));
  const testTypeHandlers = getFieldHandlers(testTypeField);
  const priorityHandlers = getFieldHandlers(priorityField);
  const categoryHandlers = getFieldHandlers(categoryField);

  return (
    <div className='grid gap-4 sm:grid-cols-3'>
      <div>
        <label className='block text-sm font-medium' htmlFor='test-case-type'>
          Test Type <span className='text-red-500'>*</span>
        </label>
        <select
          id='test-case-type'
          name={testTypeField.name}
          onBlur={testTypeHandlers.handleBlur}
          onChange={testTypeHandlers.handleChange}
          ref={testTypeField.ref}
          className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
        >
          {testTypes.map((type) => (
            <option key={type} value={type}>
              {typeLabels[type]}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label className='block text-sm font-medium' htmlFor='test-case-priority'>
          Priority <span className='text-red-500'>*</span>
        </label>
        <select
          id='test-case-priority'
          name={priorityField.name}
          onBlur={priorityHandlers.handleBlur}
          onChange={priorityHandlers.handleChange}
          ref={priorityField.ref}
          className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
        >
          {priorities.map((priority) => (
            <option key={priority} value={priority}>
              {priority.charAt(0).toUpperCase() + priority.slice(1)}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label className='block text-sm font-medium' htmlFor='test-case-category'>
          Category
        </label>
        <select
          id='test-case-category'
          name={categoryField.name}
          onBlur={categoryHandlers.handleBlur}
          onChange={categoryHandlers.handleChange}
          ref={categoryField.ref}
          className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
        >
          <option value=''>Select category...</option>
          {categoryOptions.map((category) => (
            <option key={category} value={category}>
              {category}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}

function TagsSection({ register }: BaseSectionProps): JSX.Element {
  const tagsField = getFieldProps(register('tags'));
  const tagsHandlers = getFieldHandlers(tagsField);

  return (
    <div>
      <label className='block text-sm font-medium' htmlFor='test-case-tags'>
        Tags
      </label>
      <input
        id='test-case-tags'
        name={tagsField.name}
        onBlur={tagsHandlers.handleBlur}
        onChange={tagsHandlers.handleChange}
        ref={tagsField.ref}
        placeholder='Comma-separated tags (e.g., smoke, login, api)'
        className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
      />
    </div>
  );
}

function PreconditionsSection({ register }: BaseSectionProps): JSX.Element {
  const preconditionsField = getFieldProps(register('preconditions'));
  const preconditionsHandlers = getFieldHandlers(preconditionsField);

  return (
    <div>
      <label className='block text-sm font-medium' htmlFor='test-case-preconditions'>
        Preconditions
      </label>
      <textarea
        id='test-case-preconditions'
        name={preconditionsField.name}
        onBlur={preconditionsHandlers.handleBlur}
        onChange={preconditionsHandlers.handleChange}
        ref={preconditionsField.ref}
        rows={2}
        placeholder='What conditions must be met before running this test?'
        className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
      />
    </div>
  );
}

function ExpectedPostconditionsSection({ register }: BaseSectionProps): JSX.Element {
  const expectedResultField = getFieldProps(register('expectedResult'));
  const postconditionsField = getFieldProps(register('postconditions'));
  const expectedHandlers = getFieldHandlers(expectedResultField);
  const postconditionsHandlers = getFieldHandlers(postconditionsField);

  return (
    <div className='grid gap-4 sm:grid-cols-2'>
      <div>
        <label className='block text-sm font-medium' htmlFor='test-case-expected-result'>
          Overall Expected Result
        </label>
        <textarea
          id='test-case-expected-result'
          name={expectedResultField.name}
          onBlur={expectedHandlers.handleBlur}
          onChange={expectedHandlers.handleChange}
          ref={expectedResultField.ref}
          rows={2}
          placeholder='Expected overall outcome of the test...'
          className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
        />
      </div>
      <div>
        <label className='block text-sm font-medium' htmlFor='test-case-postconditions'>
          Postconditions
        </label>
        <textarea
          id='test-case-postconditions'
          name={postconditionsField.name}
          onBlur={postconditionsHandlers.handleBlur}
          onChange={postconditionsHandlers.handleChange}
          ref={postconditionsField.ref}
          rows={2}
          placeholder='State after test completion...'
          className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
        />
      </div>
    </div>
  );
}

function AutomationSection({ register }: BaseSectionProps): JSX.Element {
  const automationStatusField = getFieldProps(register('automationStatus'));
  const automationFrameworkField = getFieldProps(register('automationFramework'));
  const automationScriptField = getFieldProps(register('automationScriptPath'));
  const automationNotesField = getFieldProps(register('automationNotes'));
  const automationStatusHandlers = getFieldHandlers(automationStatusField);
  const automationFrameworkHandlers = getFieldHandlers(automationFrameworkField);
  const automationScriptHandlers = getFieldHandlers(automationScriptField);
  const automationNotesHandlers = getFieldHandlers(automationNotesField);

  return (
    <div className='bg-muted/30 rounded-lg border p-4'>
      <h3 className='mb-3 text-sm font-medium'>Automation Settings</h3>
      <div className='grid gap-4 sm:grid-cols-2'>
        <div>
          <label className='block text-sm font-medium' htmlFor='test-case-automation-status'>
            Automation Status
          </label>
          <select
            id='test-case-automation-status'
            name={automationStatusField.name}
            onBlur={automationStatusHandlers.handleBlur}
            onChange={automationStatusHandlers.handleChange}
            ref={automationStatusField.ref}
            className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
          >
            {automationStatuses.map((status) => (
              <option key={status} value={status}>
                {automationLabels[status]}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className='block text-sm font-medium' htmlFor='test-case-automation-framework'>
            Framework
          </label>
          <input
            id='test-case-automation-framework'
            name={automationFrameworkField.name}
            onBlur={automationFrameworkHandlers.handleBlur}
            onChange={automationFrameworkHandlers.handleChange}
            ref={automationFrameworkField.ref}
            placeholder='e.g., Playwright, Cypress, Jest...'
            className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
          />
        </div>
        <div className='sm:col-span-2'>
          <label className='block text-sm font-medium' htmlFor='test-case-automation-script'>
            Script Path
          </label>
          <input
            id='test-case-automation-script'
            name={automationScriptField.name}
            onBlur={automationScriptHandlers.handleBlur}
            onChange={automationScriptHandlers.handleChange}
            ref={automationScriptField.ref}
            placeholder='Path to automation script...'
            className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
          />
        </div>
        <div className='sm:col-span-2'>
          <label className='block text-sm font-medium' htmlFor='test-case-automation-notes'>
            Automation Notes
          </label>
          <textarea
            id='test-case-automation-notes'
            name={automationNotesField.name}
            onBlur={automationNotesHandlers.handleBlur}
            onChange={automationNotesHandlers.handleChange}
            ref={automationNotesField.ref}
            rows={2}
            placeholder='Any notes about automation...'
            className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
          />
        </div>
      </div>
    </div>
  );
}

function EstimatesAssignmentSection({ register }: BaseSectionProps): JSX.Element {
  const durationField = getFieldProps(register('estimatedDurationMinutes'));
  const assignedToField = getFieldProps(register('assignedTo'));
  const durationHandlers = getFieldHandlers(durationField);
  const assignedToHandlers = getFieldHandlers(assignedToField);

  return (
    <div className='grid gap-4 sm:grid-cols-2'>
      <div>
        <label className='block text-sm font-medium' htmlFor='test-case-duration'>
          Estimated Duration (minutes)
        </label>
        <input
          id='test-case-duration'
          name={durationField.name}
          onBlur={durationHandlers.handleBlur}
          onChange={durationHandlers.handleChange}
          ref={durationField.ref}
          type='number'
          min={1}
          placeholder='e.g., 15'
          className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
        />
      </div>
      <div>
        <label className='block text-sm font-medium' htmlFor='test-case-assignee'>
          Assigned To
        </label>
        <input
          id='test-case-assignee'
          name={assignedToField.name}
          onBlur={assignedToHandlers.handleBlur}
          onChange={assignedToHandlers.handleChange}
          ref={assignedToField.ref}
          placeholder='Person responsible...'
          className='bg-background mt-1 w-full rounded-lg border px-3 py-2'
        />
      </div>
    </div>
  );
}

interface ActionsSectionProps {
  isPending: boolean;
  errorMessage?: string | undefined;
  onCancel: () => void;
}

function ActionsSection({ isPending, errorMessage, onCancel }: ActionsSectionProps): JSX.Element {
  let submitLabel = 'Create Test Case';
  if (isPending) {
    submitLabel = 'Creating...';
  }

  const hasErrorMessage = errorMessage !== undefined && errorMessage !== '';
  let errorNode: JSX.Element | undefined = undefined;
  if (hasErrorMessage) {
    errorNode = <p className='text-sm text-red-500'>Error: {errorMessage}</p>;
  }

  return (
    <>
      <div className='flex gap-3 pt-4'>
        <button
          type='button'
          onClick={onCancel}
          className='hover:bg-accent flex-1 rounded-lg border px-4 py-2'
        >
          Cancel
        </button>
        <button
          type='submit'
          disabled={isPending}
          className='bg-primary text-primary-foreground flex-1 rounded-lg px-4 py-2 disabled:opacity-50'
        >
          {submitLabel}
        </button>
      </div>
      {errorNode}
    </>
  );
}

interface TestCaseFormSectionsProps extends FieldArraySectionProps, ActionsSectionProps {}

function TestCaseFormSections({
  register,
  errors,
  control,
  isPending,
  errorMessage,
  onCancel,
}: TestCaseFormSectionsProps): JSX.Element {
  return (
    <>
      <TitleSection register={register} errors={errors} />
      <DescriptionObjectiveSection register={register} errors={errors} />
      <TypePriorityCategorySection register={register} errors={errors} />
      <TagsSection register={register} errors={errors} />
      <PreconditionsSection register={register} errors={errors} />
      <TestStepsSection register={register} control={control} />
      <ExpectedPostconditionsSection register={register} errors={errors} />
      <AutomationSection register={register} errors={errors} />
      <EstimatesAssignmentSection register={register} errors={errors} />
      <ActionsSection isPending={isPending} errorMessage={errorMessage} onCancel={onCancel} />
    </>
  );
}

export {
  ActionsSection,
  AutomationSection,
  DescriptionObjectiveSection,
  EstimatesAssignmentSection,
  ExpectedPostconditionsSection,
  PreconditionsSection,
  TagsSection,
  TestCaseFormSections,
  TestStepsSection,
  TitleSection,
  TypePriorityCategorySection,
};
