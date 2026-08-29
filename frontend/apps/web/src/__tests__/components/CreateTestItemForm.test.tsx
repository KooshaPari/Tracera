import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { CreateTestItemForm } from '../../components/forms/CreateTestItemForm';

let user: ReturnType<typeof userEvent.setup>;

describe(CreateTestItemForm, () => {
  beforeEach(() => {
    user = userEvent.setup();
  });
  it('renders the form with all required fields', () => {
    const onSubmit = vi.fn();
    const onCancel = vi.fn();

    render(<CreateTestItemForm onSubmit={onSubmit} onCancel={onCancel} />);

    // Check for title
    expect(screen.getByRole('heading', { name: 'Create Test Item' })).toBeInTheDocument();

    // Check for required sections
    expect(screen.getByText('Test Details')).toBeInTheDocument();
    expect(screen.getByText('Test Specification')).toBeInTheDocument();

    // Check for base fields
    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/status/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/priority/i)).toBeInTheDocument();

    // Check for test spec fields
    expect(screen.getByLabelText(/test type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/test framework/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/language/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/oracle type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/coverage type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/safety level/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/critical path/i)).toBeInTheDocument();

    // Check for buttons
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create test item/i })).toBeInTheDocument();
  });

  it('calls onCancel when cancel button is clicked', async () => {
    const onSubmit = vi.fn();
    const onCancel = vi.fn();

    render(<CreateTestItemForm onSubmit={onSubmit} onCancel={onCancel} />);

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    await user.click(cancelButton);

    expect(onCancel).toHaveBeenCalledOnce();
  });

  it('validates required fields on submit', async () => {
    const onSubmit = vi.fn();
    const onCancel = vi.fn();

    render(<CreateTestItemForm onSubmit={onSubmit} onCancel={onCancel} />);

    const submitButton = screen.getByRole('button', {
      name: /create test item/i,
    });
    await user.click(submitButton);

    // Form should show validation errors
    await waitFor(() => {
      expect(screen.getByText(/title is required/i)).toBeInTheDocument();
    });

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('submits form with valid data', async () => {
    const onSubmit = vi.fn();
    const onCancel = vi.fn();

    render(<CreateTestItemForm onSubmit={onSubmit} onCancel={onCancel} />);

    // Fill in title
    const titleInput = screen.getByLabelText(/title/i);
    await user.type(titleInput, 'Test Login Validation');

    // Fill in description
    const descriptionInput = screen.getByLabelText(/description/i);
    await user.type(descriptionInput, 'Verify login form validation');

    // Owner
    const ownerInput = screen.getByLabelText(/owner/i);
    await user.type(ownerInput, 'test-engineer');

    // Submit
    const submitButton = screen.getByRole('button', {
      name: /create test item/i,
    });
    await user.click(submitButton);

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledOnce();
    });

    // Verify submitted data structure
    const submittedData = onSubmit.mock.calls[0][0];
    expect(submittedData).toMatchObject({
      description: 'Verify login form validation',
      owner: 'test-engineer',
      priority: 'medium',
      status: 'todo',
      test_type: 'unit',
      title: 'Test Login Validation',
    });
  });

  it('allows selecting different test types', async () => {
    const onSubmit = vi.fn();
    const onCancel = vi.fn();

    render(<CreateTestItemForm onSubmit={onSubmit} onCancel={onCancel} />);

    const testTypeSelect = screen.getByLabelText(/test type/i);

    // Check default value
    expect(testTypeSelect).toHaveValue('unit');

    // Change to integration
    await user.selectOptions(testTypeSelect, 'integration');
    expect(testTypeSelect).toHaveValue('integration');

    // Change to e2e
    await user.selectOptions(testTypeSelect, 'e2e');
    expect(testTypeSelect).toHaveValue('e2e');
  });

  it('allows toggling critical path checkbox', async () => {
    const onSubmit = vi.fn();
    const onCancel = vi.fn();

    render(<CreateTestItemForm onSubmit={onSubmit} onCancel={onCancel} />);

    const criticalPathCheckbox = screen.getByLabelText(/critical path/i);

    // Initially unchecked
    expect(criticalPathCheckbox).not.toBeChecked();

    // Click to check
    await user.click(criticalPathCheckbox);
    expect(criticalPathCheckbox).toBeChecked();

    // Click to uncheck
    await user.click(criticalPathCheckbox);
    expect(criticalPathCheckbox).not.toBeChecked();
  });

  it('displays loading state when isLoading is true', () => {
    const onSubmit = vi.fn();
    const onCancel = vi.fn();

    render(<CreateTestItemForm onSubmit={onSubmit} onCancel={onCancel} isLoading />);

    const submitButton = screen.getByRole('button', { name: /creating/i });
    expect(submitButton).toBeDisabled();
  });
});
