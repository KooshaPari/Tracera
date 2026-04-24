interface FormValidationErrorProps {
  message: string;
  testId?: string;
}

export function FormValidationError({ message, testId = 'form-error' }: FormValidationErrorProps) {
  if (!message) {
    return null;
  }

  return (
    <div
      className='bg-destructive/10 text-destructive border-destructive/20 rounded-md border p-3 text-sm'
      data-testid={testId}
      role='alert'
    >
      {message}
    </div>
  );
}
