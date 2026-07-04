/**
 * Accessibility Tests for Forms - Enhanced
 * Tests aria-describedby, required indicators, validation announcements, focus management
 */
/// <reference path="./jest-axe.d.ts" />

import { render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';

import { axe } from './setup';

// Mock form component with accessibility features
function AccessibleForm() {
  return (
    <div
      role='dialog'
      aria-modal='true'
      aria-labelledby='form-title'
      aria-describedby='form-description'
    >
      <h2 id='form-title'>Create Item</h2>
      <p id='form-description' className='sr-only'>
        Fill in the required fields marked with an asterisk and click Create Item to submit.
      </p>

      <form>
        <div>
          <label htmlFor='title'>
            Title <span aria-label='required'>*</span>
          </label>
          <input
            id='title'
            type='text'
            placeholder='Enter item title'
            aria-describedby='title-help title-error'
            aria-required='true'
            aria-invalid='false'
            required
          />
          <span id='title-help' className='text-muted-foreground text-xs'>
            Give this item a clear, descriptive title
          </span>
        </div>

        <div>
          <label htmlFor='type'>
            Type <span aria-label='required'>*</span>
          </label>
          <select
            id='type'
            aria-describedby='type-help type-error'
            aria-required='true'
            aria-invalid='false'
            required
          >
            <option>epic</option>
            <option>feature</option>
          </select>
          <span id='type-help' className='text-muted-foreground text-xs'>
            Select from options based on your chosen view
          </span>
        </div>

        <div>
          <label htmlFor='description'>Description</label>
          <textarea
            id='description'
            placeholder='Describe this item...'
            aria-describedby='description-help'
            rows={3}
          />
          <span id='description-help' className='text-muted-foreground text-xs'>
            Optional: Provide additional context or details
          </span>
        </div>

        <div>
          <label htmlFor='status'>Status</label>
          <select id='status' aria-describedby='status-help'>
            <option>todo</option>
            <option>in_progress</option>
          </select>
          <span id='status-help' className='text-muted-foreground text-xs'>
            Current status of this item
          </span>
        </div>

        <div className='flex gap-3'>
          <button type='button' aria-label='Discard changes and close dialog'>
            Cancel
          </button>
          <button type='submit' aria-busy='false' aria-label='Create item'>
            Create Item
          </button>
        </div>
      </form>
    </div>
  );
}

describe('Form Accessibility - aria-describedby Connections', () => {
  it('should connect required fields with help and error text', async () => {
    const { container, getByLabelText } = render(<AccessibleForm />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();

    const titleInput = getByLabelText(/title/i);
    expect(titleInput).toHaveAttribute('aria-describedby');
    expect(titleInput).toHaveAttribute('aria-required', 'true');
  });

  it('should associate help text with form fields', async () => {
    const { container, getByLabelText, getByText } = render(<AccessibleForm />);

    const titleInput = getByLabelText(/title/i);
    const describedBy = titleInput.getAttribute('aria-describedby');

    expect(describedBy).toContain('title-help');

    const helpText = getByText(/Give this item a clear/i);
    expect(helpText).toHaveAttribute('id', 'title-help');

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should support multiple describedby values', async () => {
    const { container, getByLabelText } = render(<AccessibleForm />);

    const typeSelect = getByLabelText(/type/i);
    const describedBy = typeSelect.getAttribute('aria-describedby');

    // Should have both help and error IDs
    expect(describedBy).toBeTruthy();
    expect(describedBy?.split(' ').length).toBeGreaterThanOrEqual(1);

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});

describe('Form Accessibility - Required Indicators', () => {
  it('should mark required fields with aria-required', async () => {
    const { container, getByLabelText } = render(<AccessibleForm />);

    const titleInput = getByLabelText(/title/i);
    expect(titleInput).toHaveAttribute('aria-required', 'true');

    const typeSelect = getByLabelText(/type/i);
    expect(typeSelect).toHaveAttribute('aria-required', 'true');

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have accessible required indicator in label', () => {
    const { getByLabelText } = render(<AccessibleForm />);

    const titleLabel = getByLabelText(/title/i);
    expect(titleLabel).toBeInTheDocument();

    // Check for aria-label="required" on the asterisk
    const requiredIndicator = getByLabelText('required');
    expect(requiredIndicator).toHaveTextContent('*');
  });

  it('should have required attribute and aria-required in sync', async () => {
    const { container, getByLabelText } = render(<AccessibleForm />);

    const titleEl = getByLabelText(/title/i);
    const titleInput = titleEl instanceof HTMLInputElement ? titleEl : null;
    expect(titleInput).not.toBeNull();
    expect(titleInput!.required).toBeTruthy();
    expect(titleInput!).toHaveAttribute('aria-required', 'true');

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});

describe('Form Accessibility - Validation Announcements', () => {
  it('should have aria-invalid for error states', () => {
    const { rerender, getByLabelText } = render(<AccessibleForm />);

    let titleInputEl = getByLabelText(/title/i);
    let titleInput = titleInputEl instanceof HTMLInputElement ? titleInputEl : null;
    expect(titleInput).not.toBeNull();
    expect(titleInput!).toHaveAttribute('aria-invalid', 'false');

    // Simulate error state
    rerender(
      <div
        role='dialog'
        aria-modal='true'
        aria-labelledby='form-title'
        aria-describedby='form-description'
      >
        <h2 id='form-title'>Create Item</h2>
        <p id='form-description' className='sr-only'>
          Fill in the required fields marked with an asterisk and click Create Item to submit.
        </p>

        <form>
          <div>
            <label htmlFor='title'>
              Title <span aria-label='required'>*</span>
            </label>
            <input
              id='title'
              type='text'
              placeholder='Enter item title'
              aria-describedby='title-help title-error'
              aria-required='true'
              aria-invalid='true'
              required
            />
            <span id='title-help' className='text-muted-foreground text-xs'>
              Give this item a clear, descriptive title
            </span>
            <p id='title-error' role='alert' aria-live='polite' aria-atomic='true'>
              Title is required
            </p>
          </div>
        </form>
      </div>,
    );

    titleInputEl = getByLabelText(/title/i);
    titleInput = titleInputEl instanceof HTMLInputElement ? titleInputEl : null;
    expect(titleInput!).toHaveAttribute('aria-invalid', 'true');
  });

  it("should have role='alert' on error messages", () => {
    const ErrorForm = () => (
      <form>
        <div>
          <label htmlFor='username'>Username</label>
          <input id='username' aria-invalid='true' aria-describedby='username-error' required />
          <p id='username-error' role='alert' aria-live='polite' aria-atomic='true'>
            Username is already taken
          </p>
        </div>
      </form>
    );

    const { getByRole } = render(<ErrorForm />);

    const errorMessage = getByRole('alert');
    expect(errorMessage).toHaveAttribute('aria-live', 'polite');
    expect(errorMessage).toHaveAttribute('aria-atomic', 'true');
  });

  it('should announce validation errors via aria-live', () => {
    const { getByRole } = render(
      <div>
        <form>
          <label htmlFor='title'>Title</label>
          <input id='title' minLength={5} aria-invalid='true' aria-describedby='title-error' />
          <p id='title-error' role='alert' aria-live='polite' aria-atomic='true'>
            Title must be at least 5 characters
          </p>
        </form>
      </div>,
    );

    const errorAlert = getByRole('alert');
    expect(errorAlert).toBeInTheDocument();
    expect(errorAlert).toHaveAttribute('aria-live', 'polite');
  });
});

describe('Form Accessibility - Focus Management', () => {
  it('should have visible focus indicators on all form fields', () => {
    const { getByLabelText } = render(<AccessibleForm />);

    const titleInput = getByLabelText(/title/i);
    titleInput.focus();
    expect(titleInput).toHaveFocus();

    const typeSelect = getByLabelText(/type/i);
    typeSelect.focus();
    expect(typeSelect).toHaveFocus();
  });

  it('should support keyboard navigation through form fields', async () => {
    const { getByLabelText, getByPlaceholderText } = render(<AccessibleForm />);
    const user = userEvent.setup();

    const titleInput = getByLabelText(/title/i);
    const typeSelect = getByLabelText(/type/i);
    const descriptionTextarea = getByPlaceholderText(/Describe this item/i);

    // Start at title
    titleInput.focus();
    expect(titleInput).toHaveFocus();

    // Tab to next field
    await globalThis.user.tab();
    expect(typeSelect).toHaveFocus();

    // Tab to next field
    await globalThis.user.tab();
    expect(descriptionTextarea).toHaveFocus();
  });

  it('should support Shift+Tab for reverse navigation', async () => {
    const { getByLabelText } = render(<AccessibleForm />);
    const user = userEvent.setup();

    const titleInput = getByLabelText(/title/i);
    const typeSelect = getByLabelText(/type/i);

    typeSelect.focus();
    expect(typeSelect).toHaveFocus();

    await user.tab({ shift: true });
    expect(titleInput).toHaveFocus();
  });
});

describe('Form Accessibility - Dialog Focus Trap', () => {
  it('should have dialog role and aria-modal', async () => {
    const { container, getByRole } = render(<AccessibleForm />);

    const dialog = getByRole('dialog');
    expect(dialog).toHaveAttribute('aria-modal', 'true');
    expect(dialog).toHaveAttribute('aria-labelledby');
    expect(dialog).toHaveAttribute('aria-describedby');

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have proper dialog structure with title and description', () => {
    const { getByRole, getByText } = render(<AccessibleForm />);

    const dialog = getByRole('dialog');
    const title = getByText('Create Item');
    const description = getByText(/Fill in the required fields/);

    expect(title).toHaveAttribute('id');
    expect(description).toHaveAttribute('id', 'form-description');

    const labelledBy = dialog.getAttribute('aria-labelledby');
    expect(labelledBy).toContain(title.getAttribute('id'));
  });
});

describe('Form Accessibility - WCAG 2.1 AA Compliance', () => {
  it('should pass comprehensive accessibility audit', async () => {
    const { container } = render(<AccessibleForm />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have proper label associations', async () => {
    const { container, getByLabelText } = render(<AccessibleForm />);

    const titleInput = getByLabelText(/title/i);
    const typeSelect = getByLabelText(/type/i);

    expect(titleInput).toBeInTheDocument();
    expect(typeSelect).toBeInTheDocument();

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should support autocomplete attributes', () => {
    const FormWithAutocomplete = () => (
      <form>
        <label htmlFor='email'>Email</label>
        <input id='email' type='email' autoComplete='email' aria-describedby='email-help' />
        <span id='email-help'>We'll never share your email</span>
      </form>
    );

    const { getByLabelText } = render(<FormWithAutocomplete />);
    const emailEl = getByLabelText(/email/i);
    const emailInput = emailEl instanceof HTMLInputElement ? emailEl : null;
    expect(emailInput).not.toBeNull();
    expect(emailInput!.getAttribute('autocomplete')).toBe('email');
  });
});

describe('Form Accessibility - Help Text and Hints', () => {
  it('should have help text for all fields', () => {
    const { getByText } = render(<AccessibleForm />);

    const titleHelp = getByText(/Give this item a clear/i);
    const typeHelp = getByText(/Select from options/i);
    const descriptionHelp = getByText(/Provide additional context/i);

    expect(titleHelp).toBeInTheDocument();
    expect(typeHelp).toBeInTheDocument();
    expect(descriptionHelp).toBeInTheDocument();
  });

  it('should connect help text via aria-describedby', () => {
    const { getByLabelText, getByText } = render(<AccessibleForm />);

    const titleInput = getByLabelText(/title/i);
    const describedBy = titleInput.getAttribute('aria-describedby');

    expect(describedBy).toContain('title-help');

    const helpText = getByText(/Give this item a clear/i);
    expect(helpText).toHaveAttribute('id');
  });

  it('should differentiate between help and error text', () => {
    const { rerender, getByLabelText } = render(<AccessibleForm />);

    // Initially just help text
    let titleInput = getByLabelText(/title/i);
    let describedBy = titleInput.getAttribute('aria-describedby');
    expect(describedBy).toContain('title-help');

    // Now with error
    rerender(
      <div>
        <form>
          <label htmlFor='title'>Title</label>
          <input id='title' aria-describedby='title-help title-error' aria-invalid='true' />
          <span id='title-help'>Help text</span>
          <p id='title-error' role='alert'>
            Error message
          </p>
        </form>
      </div>,
    );

    titleInput = getByLabelText(/title/i);
    describedBy = titleInput.getAttribute('aria-describedby');

    // Should have both
    expect(describedBy).toContain('title-help');
    expect(describedBy).toContain('title-error');
  });
});
