/**
 * Accessibility Tests: Form Validation and Error Handling
 * Tests WCAG 2.1 AA compliance for form validation and error messaging
 */

import { render, screen, waitFor } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { useState } from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { axe } from '../a11y/setup';
import '../a11y/jest-axe';

let user = userEvent.setup();

beforeEach(() => {
  user = userEvent.setup();
});

enum FormField {
  Email = 'email',
  Message = 'message',
  Name = 'name',
}

interface FormDataMap {
  email?: string;
  message?: string;
  name?: string;
}

interface FormErrors {
  email?: string;
  message?: string;
  name?: string;
}

interface FormTouched {
  email?: boolean;
  message?: boolean;
  name?: boolean;
}

interface MockAccessibleFormProps {
  onSubmit?: (data: FormDataMap) => void;
}

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const MIN_NAME_LENGTH = 2;
const MIN_MESSAGE_LENGTH = 10;
const DEFAULT_ON_SUBMIT = vi.fn();

function normalizeInput(value: FormDataEntryValue | null): string {
  if (typeof value === 'string') {
    return value;
  }
  return '';
}

function buildFormValues(form: HTMLFormElement): FormDataMap {
  const formData = new FormData(form);
  return {
    email: normalizeInput(formData.get(FormField.Email)),
    message: normalizeInput(formData.get(FormField.Message)),
    name: normalizeInput(formData.get(FormField.Name)),
  };
}

function validateFormData(formData: FormDataMap): FormErrors {
  const newErrors: FormErrors = {};
  const email = formData.email ?? '';
  const name = formData.name ?? '';
  const message = formData.message ?? '';

  if (email.trim().length === 0) {
    newErrors.email = 'Email is required';
  } else if (!EMAIL_REGEX.test(email)) {
    newErrors.email = 'Please enter a valid email address';
  }

  if (name.trim().length < MIN_NAME_LENGTH) {
    newErrors.name = 'Name must be at least 2 characters';
  }

  if (message.trim().length < MIN_MESSAGE_LENGTH) {
    newErrors.message = 'Message must be at least 10 characters';
  }

  return newErrors;
}

function buildInputClass(hasError: boolean): string {
  let className =
    'w-full rounded border px-3 py-2 focus:border-transparent focus:ring-2 focus:ring-blue-600';
  if (hasError) {
    className = `${className} border-red-600 bg-red-50`;
  } else {
    className = `${className} border-gray-300`;
  }
  return className;
}

function shouldShowError(errors: FormErrors, touched: FormTouched, field: FormField): boolean {
  const fieldError = errors[field];
  const fieldTouched = touched[field] === true;
  return fieldError !== undefined && fieldTouched;
}

function buildErrorSummary(errors: FormErrors, touched: FormTouched): JSX.Element | undefined {
  const hasErrors = Object.keys(errors).length > 0;
  const isTouched = Object.keys(touched).length > 0;
  if (!hasErrors || !isTouched) {
    return undefined;
  }

  return (
    <div role='alert' aria-live='polite' className='mt-4 border-l-4 border-red-600 bg-red-50 p-4'>
      <h3 className='mb-2 font-semibold text-red-800'>Please fix the following errors:</h3>
      <ul className='list-inside list-disc text-sm text-red-700'>
        {Object.entries(errors).map(([field, error]) => (
          <li key={field}>{error}</li>
        ))}
      </ul>
    </div>
  );
}

function MockAccessibleForm({
  onSubmit = DEFAULT_ON_SUBMIT,
}: MockAccessibleFormProps): JSX.Element {
  const [errors, setErrors] = useState<FormErrors>({});
  const [touched, setTouched] = useState<FormTouched>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const setAllTouched = (): void => {
    setTouched({
      email: true,
      message: true,
      name: true,
    });
  };

  const submitForm = async (form: HTMLFormElement): Promise<void> => {
    setIsSubmitting(true);
    const data = buildFormValues(form);
    const validationErrors = validateFormData(data);
    setErrors(validationErrors);
    setAllTouched();

    if (Object.keys(validationErrors).length === 0) {
      await Promise.resolve();
      onSubmit(data);
      setErrors({});
      setTouched({});
      form.reset();
    }

    setIsSubmitting(false);
  };

  const handleSubmit = (event: {
    preventDefault: () => void;
    currentTarget: HTMLFormElement;
  }): void => {
    event.preventDefault();
    void submitForm(event.currentTarget);
  };

  const handleBlur = (fieldName: FormField): void => {
    setTouched((prev) => ({ ...prev, [fieldName]: true }));

    const formElement = document.querySelector('form');
    if (!formElement) {
      return;
    }

    const data = buildFormValues(formElement);
    const fieldErrors = validateFormData(data);
    const fieldError = fieldErrors[fieldName];

    if (fieldError) {
      setErrors((prev) => ({ ...prev, [fieldName]: fieldError }));
      return;
    }

    const { [fieldName]: _removed, ...remaining } = errors;
    setErrors(remaining);
  };

  const nameHasError = shouldShowError(errors, touched, FormField.Name);
  const emailHasError = shouldShowError(errors, touched, FormField.Email);
  const messageHasError = shouldShowError(errors, touched, FormField.Message);

  let nameDescribedBy: string | undefined;
  if (errors.name) {
    nameDescribedBy = 'name-error';
  }

  let emailDescribedBy: string | undefined;
  if (errors.email) {
    emailDescribedBy = 'email-error';
  } else {
    emailDescribedBy = 'email-hint';
  }

  let messageDescribedBy: string | undefined;
  if (errors.message) {
    messageDescribedBy = 'message-error';
  } else {
    messageDescribedBy = 'message-help';
  }

  let nameErrorNode: JSX.Element | undefined;
  if (nameHasError && errors.name) {
    nameErrorNode = (
      <div id='name-error' role='alert' className='mt-2 text-sm text-red-600'>
        {errors.name}
      </div>
    );
  }

  let emailErrorNode: JSX.Element | undefined;
  if (emailHasError && errors.email) {
    emailErrorNode = (
      <div id='email-error' role='alert' className='mt-2 text-sm text-red-600'>
        {errors.email}
      </div>
    );
  }

  let messageErrorNode: JSX.Element | undefined;
  if (messageHasError && errors.message) {
    messageErrorNode = (
      <div id='message-error' role='alert' className='mt-2 text-sm text-red-600'>
        {errors.message}
      </div>
    );
  }

  const errorSummaryNode = buildErrorSummary(errors, touched);

  return (
    <form onSubmit={handleSubmit} noValidate aria-label='Contact form'>
      <div className='mb-6'>
        <label htmlFor='name' className='mb-2 block text-sm font-medium'>
          Name
          <span className='ml-1 text-red-600' aria-label='required'>
            *
          </span>
        </label>
        <input
          id='name'
          name='name'
          type='text'
          placeholder='Your name'
          onBlur={() => {
            handleBlur(FormField.Name);
          }}
          aria-invalid={nameHasError}
          aria-describedby={nameDescribedBy}
          className={buildInputClass(nameHasError)}
          required
        />
        {nameErrorNode}
      </div>

      <div className='mb-6'>
        <label htmlFor='email' className='mb-2 block text-sm font-medium'>
          Email
          <span className='ml-1 text-red-600' aria-label='required'>
            *
          </span>
        </label>
        <input
          id='email'
          name='email'
          type='email'
          placeholder='your@email.com'
          onBlur={() => {
            handleBlur(FormField.Email);
          }}
          aria-invalid={emailHasError}
          aria-describedby={emailDescribedBy}
          className={buildInputClass(emailHasError)}
          required
        />
        <span id='email-hint' className='sr-only'>
          Email format: user@example.com
        </span>
        {emailErrorNode}
      </div>

      <div className='mb-6'>
        <label htmlFor='message' className='mb-2 block text-sm font-medium'>
          Message
          <span className='ml-1 text-red-600' aria-label='required'>
            *
          </span>
        </label>
        <textarea
          id='message'
          name='message'
          placeholder='Your message here...'
          rows={4}
          onBlur={() => {
            handleBlur(FormField.Message);
          }}
          aria-invalid={messageHasError}
          aria-describedby={messageDescribedBy}
          className={`resize-vertical ${buildInputClass(messageHasError)}`}
          required
        />
        <span id='message-help' className='sr-only'>
          Message must be at least 10 characters long
        </span>
        {messageErrorNode}
      </div>

      <div className='flex gap-3'>
        <button
          type='submit'
          disabled={isSubmitting}
          className='rounded bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 active:bg-blue-800 disabled:opacity-50'
          aria-busy={isSubmitting}
        >
          {isSubmitting ? 'Sending...' : 'Send Message'}
        </button>
        <button
          type='reset'
          className='rounded bg-gray-300 px-4 py-2 font-medium text-gray-800 hover:bg-gray-400'
        >
          Clear
        </button>
      </div>

      {errorSummaryNode}
    </form>
  );
}

describe('Form Validation - Field-Level Errors', () => {
  it('should show error on invalid email', async () => {
    const { container } = render(<MockAccessibleForm />);

    const emailInput = screen.getByPlaceholderText('your@email.com');
    await user.type(emailInput, 'invalid');
    const focusAway = container.querySelector('button');
    if (focusAway) {
      await user.click(focusAway);
    }

    await waitFor(() => {
      const error = screen.getByText('Please enter a valid email address');
      expect(error).toBeInTheDocument();
    });
  });

  it('should show error on missing required field', async () => {
    render(<MockAccessibleForm />);

    const submitBtn = screen.getByRole('button', { name: 'Send Message' });
    await user.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText('Email is required')).toBeInTheDocument();
      expect(screen.getByText('Name must be at least 2 characters')).toBeInTheDocument();
    });
  });

  it('should clear error when field becomes valid', async () => {
    render(<MockAccessibleForm />);

    const emailInput = screen.getByPlaceholderText('your@email.com');
    const submitBtn = screen.getByRole('button', { name: 'Send Message' });

    await user.click(submitBtn);
    await user.clear(emailInput);
    await user.type(emailInput, 'valid@email.com');
    await user.click(submitBtn);

    await waitFor(() => {
      expect(screen.queryByText('Please enter a valid email address')).not.toBeInTheDocument();
    });
  });
});

describe('Form Validation - Error Announcements', () => {
  it('should announce errors to screen readers', async () => {
    const { container } = render(<MockAccessibleForm />);

    const submitBtn = screen.getByRole('button', { name: 'Send Message' });
    await user.click(submitBtn);

    await waitFor(() => {
      const errorSummary = screen.getByRole('alert');
      expect(errorSummary).toBeInTheDocument();
      expect(errorSummary).toHaveTextContent('Please fix the following errors');
    });

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});

describe('Form Validation - Focus Management', () => {
  it('should allow error navigation with keyboard', async () => {
    render(<MockAccessibleForm />);

    const emailInput = screen.getByPlaceholderText('your@email.com');
    const submitBtn = screen.getByRole('button', { name: 'Send Message' });

    await user.click(submitBtn);
    await user.tab();

    expect(emailInput).toHaveFocus();
  });
});
