import type { ChangeEvent, FocusEvent } from 'react';

interface RegisterFieldProps {
  name: string;
  onBlur: (event: FocusEvent) => void;
  onChange: (event: ChangeEvent) => void;
  ref: (instance: Element | null) => void;
}

interface FieldHandlers {
  handleBlur: RegisterFieldProps['onBlur'];
  handleChange: RegisterFieldProps['onChange'];
}

function getFieldProps(field: RegisterFieldProps): RegisterFieldProps {
  return {
    name: field.name,
    onBlur: field.onBlur,
    onChange: field.onChange,
    ref: field.ref,
  };
}

function getFieldHandlers(field: RegisterFieldProps): FieldHandlers {
  return {
    handleBlur: field.onBlur,
    handleChange: field.onChange,
  };
}

export { getFieldHandlers, getFieldProps };
export type { FieldHandlers, RegisterFieldProps };
