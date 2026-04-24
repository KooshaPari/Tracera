/**
 * Accessibility Tests for Forms
 * Tests form components and interactions for WCAG 2.1 Level AA compliance
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import { Button, Input } from '@tracertm/ui';

import { axe } from './setup';

describe('Form Field Labels', () => {
  it('should associate labels with inputs', async () => {
    const { container } = render(
      <form>
        <label htmlFor='username'>Username</label>
        <Input id='username' type='text' />
      </form>,
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();

    const input = screen.getByLabelText('Username');
    expect(input).toBeInTheDocument();
  });

  it('should support aria-label when visual label not present', async () => {
    const { container } = render(
      <form>
        <Input aria-label='Search query' type='search' />
      </form>,
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should support aria-labelledby for complex labels', async () => {
    const { container } = render(
      <form>
        <span id='name-label'>Full Name</span>
        <span id='name-desc'>(First and Last)</span>
        <Input aria-labelledby='name-label name-desc' type='text' />
      </form>,
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});

describe('Form Validation', () => {
  it('should mark required fields appropriately', async () => {
    const { container } = render(
      <form>
        <label htmlFor='email'>
          Email <span aria-label='required'>*</span>
        </label>
        <Input id='email' type='email' required aria-required='true' />
      </form>,
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();

    const input = screen.getByLabelText(/email/i);
    expect(input).toHaveAttribute('required');
    expect(input).toHaveAttribute('aria-required', 'true');
  });

  it('should associate error messages with fields', async () => {
    const { container } = render(
      <form>
        <label htmlFor='password'>Password</label>
        <Input
          id='password'
          type='password'
          aria-invalid='true'
          aria-describedby='password-error'
        />
        <span id='password-error' role='alert'>
          Password must be at least 8 characters
        </span>
      </form>,
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();

    const input = screen.getByLabelText('Password');
    expect(input).toHaveAttribute('aria-invalid', 'true');
    expect(input).toHaveAttribute('aria-describedby', 'password-error');
  });

  it('should provide helpful error messages', async () => {
    const { container } = render(
      <form>
        <label htmlFor='age'>Age</label>
        <Input
          id='age'
          type='number'
          aria-invalid='true'
          aria-describedby='age-error'
          min='0'
          max='120'
        />
        <span id='age-error' role='alert'>
          Age must be between 0 and 120
        </span>
      </form>,
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should clear errors when valid', async () => {
    const { container, rerender } = render(
      <form>
        <label htmlFor='name'>Name</label>
        <Input id='name' aria-invalid='true' aria-describedby='name-error' />
        <span id='name-error' role='alert'>
          Name is required
        </span>
      </form>,
    );

    // Initially invalid
    let input = screen.getByLabelText('Name');
    expect(input).toHaveAttribute('aria-invalid', 'true');

    // After fixing
    rerender(
      <form>
        <label htmlFor='name'>Name</label>
        <Input id='name' aria-invalid='false' />
      </form>,
    );

    input = screen.getByLabelText('Name');
    expect(input).toHaveAttribute('aria-invalid', 'false');

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});

describe('Form Groups and Fieldsets', () => {
  it('should group related fields with fieldset and legend', async () => {
    const { container } = render(
      <form>
        <fieldset>
          <legend>Contact Information</legend>
          <label htmlFor='phone'>Phone</label>
          <Input id='phone' type='tel' />
          <label htmlFor='email'>Email</label>
          <Input id='email' type='email' />
        </fieldset>
      </form>,
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();

    expect(screen.getByRole('group', { name: 'Contact Information' })).toBeInTheDocument();
  });

  it('should properly group radio buttons', async () => {
    const { container } = render(
      <form>
        <fieldset>
          <legend>Notification Preference</legend>
          <label>
            <input type='radio' name='notify' value='email' />
            Email
          </label>
          <label>
            <input type='radio' name='notify' value='sms' />
            SMS
          </label>
          <label>
            <input type='radio' name='notify' value='both' />
            Both
          </label>
        </fieldset>
      </form>,
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();

    const radios = screen.getAllByRole('radio');
    expect(radios).toHaveLength(3);
  });

  it('should properly group checkboxes', async () => {
    const { container } = render(
      <form>
        <fieldset>
          <legend>Interests</legend>
          <label>
            <input type='checkbox' name='interests' value='coding' />
            Coding
          </label>
          <label>
            <input type='checkbox' name='interests' value='design' />
            Design
          </label>
          <label>
            <input type='checkbox' name='interests' value='testing' />
            Testing
          </label>
        </fieldset>
      </form>,
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();

    const checkboxes = screen.getAllByRole('checkbox');
    expect(checkboxes).toHaveLength(3);
  });
});

describe('Form Submission', () => {
  it('should have accessible submit button', async () => {
    const handleSubmit = vi.fn((e) => e.preventDefault());
    const { container } = render(
      <form onSubmit={handleSubmit}>
        <label htmlFor='comment'>Comment</label>
        <Input id='comment' />
        <Button type='submit'>Submit</Button>
      </form>,
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();

    const submitButton = screen.getByRole('button', { name: 'Submit' });
    expect(submitButton).toHaveAttribute('type', 'submit');
  });

  it('should have accessible cancel/reset buttons', async () => {
    const { container } = render(
      <form>
        <Button type='submit'>Save</Button>
        <Button type='reset'>Reset</Button>
        <Button type='button'>Cancel</Button>
      </form>,
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should prevent submission while loading', async () => {
    const { container } = render(
      <form>
        <Button type='submit' disabled aria-busy='true'>
          Submitting...
        </Button>
      </form>,
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });
});

describe('Form Autocomplete', () => {
  it('should support autocomplete attributes', async () => {
    const { container } = render(
      <form>
        <label htmlFor='name'>Full Name</label>
        <Input id='name' autoComplete='name' />

        <label htmlFor='email'>Email</label>
        <Input id='email' type='email' autoComplete='email' />

        <label htmlFor='phone'>Phone</label>
        <Input id='phone' type='tel' autoComplete='tel' />

        <label htmlFor='address'>Address</label>
        <Input id='address' autoComplete='street-address' />
      </form>,
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});

describe('Form Keyboard Navigation', () => {
  it('should allow tabbing through form fields', async () => {
    const user = userEvent.setup();
    render(
      <form>
        <label htmlFor='field1'>Field 1</label>
        <Input id='field1' />
        <label htmlFor='field2'>Field 2</label>
        <Input id='field2' />
        <label htmlFor='field3'>Field 3</label>
        <Input id='field3' />
        <Button type='submit'>Submit</Button>
      </form>,
    );

    const field1 = screen.getByLabelText('Field 1');
    const field2 = screen.getByLabelText('Field 2');
    const field3 = screen.getByLabelText('Field 3');
    const submitButton = screen.getByRole('button', { name: 'Submit' });

    field1.focus();
    expect(field1).toHaveFocus();

    await user.tab();
    expect(field2).toHaveFocus();

    await user.tab();
    expect(field3).toHaveFocus();

    await user.tab();
    expect(submitButton).toHaveFocus();
  });

  it('should allow shift+tab to go backwards', async () => {
    const user = userEvent.setup();
    render(
      <form>
        <label htmlFor='first'>First</label>
        <Input id='first' />
        <label htmlFor='second'>Second</label>
        <Input id='second' />
      </form>,
    );

    const first = screen.getByLabelText('First');
    const second = screen.getByLabelText('Second');

    second.focus();
    expect(second).toHaveFocus();

    await user.tab({ shift: true });
    expect(first).toHaveFocus();
  });

  it('should submit form with Enter key', async () => {
    const user = userEvent.setup();
    const handleSubmit = vi.fn((e) => e.preventDefault());

    render(
      <form onSubmit={handleSubmit}>
        <label htmlFor='input'>Input</label>
        <Input id='input' />
        <Button type='submit'>Submit</Button>
      </form>,
    );

    const input = screen.getByLabelText('Input');
    input.focus();

    await user.keyboard('{Enter}');
    await waitFor(() => {
      expect(handleSubmit).toHaveBeenCalled();
    });
  });
});

describe('Form Help Text', () => {
  it('should associate help text with fields', async () => {
    const { container } = render(
      <form>
        <label htmlFor='password'>Password</label>
        <Input id='password' type='password' aria-describedby='password-help' />
        <span id='password-help'>
          Must be at least 8 characters with uppercase, lowercase, and numbers
        </span>
      </form>,
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();

    const input = screen.getByLabelText('Password');
    expect(input).toHaveAttribute('aria-describedby', 'password-help');
  });

  it('should support both help text and error messages', async () => {
    const { container } = render(
      <form>
        <label htmlFor='username'>Username</label>
        <Input id='username' aria-invalid='true' aria-describedby='username-help username-error' />
        <span id='username-help'>Choose a unique username</span>
        <span id='username-error' role='alert'>
          Username is already taken
        </span>
      </form>,
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
