import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { useForm } from 'react-hook-form';
import { describe, expect, it } from 'vitest';

import { FormArrayField } from './FormArrayField';

interface StringListForm {
  labels: string[];
}

function StringListHarness() {
  const { control, register } = useForm<StringListForm>({
    defaultValues: { labels: [] },
  });

  return (
    <FormArrayField<StringListForm>
      addButtonLabel='Add label'
      control={control}
      defaultValue=''
      label='Labels'
      name='labels'
      renderField={(index) => <input aria-label={`Label ${index + 1}`} {...register(`labels.${index}`)} />}
    />
  );
}

describe(FormArrayField, () => {
  it('appends the configured empty string item for a string-array field', () => {
    render(<StringListHarness />);

    fireEvent.click(screen.getByRole('button', { name: 'Add label' }));

    expect(screen.getByRole('textbox', { name: 'Label 1' })).toHaveValue('');
  });
});
