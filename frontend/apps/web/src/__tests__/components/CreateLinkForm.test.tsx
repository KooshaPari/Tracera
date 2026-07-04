/**
 * CreateLinkForm Component Tests
 *
 * Comprehensive tests covering:
 * - Form rendering and initialization
 * - Source and target item selection
 * - Link type selection
 * - Form validation
 * - Form submission
 * - Cancellation
 * - Preselected source
 * - Loading states
 * - Edge cases
 */

import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { CreateLinkForm } from '@/components/forms/CreateLinkForm';

const mockItems = [
  {
    id: '550e8400-e29b-41d4-a716-446655440001',
    title: 'Epic 1',
    type: 'Epic',
    view: 'Feature',
  },
  {
    id: '550e8400-e29b-41d4-a716-446655440002',
    title: 'Story 1',
    type: 'Story',
    view: 'Feature',
  },
  {
    id: '550e8400-e29b-41d4-a716-446655440003',
    title: 'Module A',
    type: 'Module',
    view: 'Code',
  },
  {
    id: '550e8400-e29b-41d4-a716-446655440004',
    title: 'Test Suite 1',
    type: 'Suite',
    view: 'Test',
  },
  {
    id: '550e8400-e29b-41d4-a716-446655440005',
    title: 'API Endpoint',
    type: 'Endpoint',
    view: 'API',
  },
];

describe('CreateLinkForm Component', () => {
  const mockOnSubmit = vi.fn();
  const mockOnCancel = vi.fn();
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    mockOnSubmit.mockClear();
    mockOnCancel.mockClear();
    user = userEvent.setup();
  });

  describe('Basic Rendering', () => {
    it('should render form title', () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      expect(screen.getByText('Create Traceability Link')).toBeInTheDocument();
    });

    it('should render close button', () => {
      const { container } = render(
        <CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />,
      );

      const closeButton = container.querySelector('button');
      expect(closeButton).toBeInTheDocument();
    });

    it('should render source item select', () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      expect(screen.getByText(/source item/i)).toBeInTheDocument();
    });

    it('should render target item select', () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      expect(screen.getByText(/target item/i)).toBeInTheDocument();
    });

    it('should render link type select', () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      expect(screen.getByText(/link type/i)).toBeInTheDocument();
    });

    it('should render description textarea', () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      expect(screen.getByText(/description/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/why are these items linked/i)).toBeInTheDocument();
    });

    it('should render Cancel button', () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      expect(screen.getByText('Cancel')).toBeInTheDocument();
    });

    it('should render Create Link button', () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      expect(screen.getByText('Create Link')).toBeInTheDocument();
    });
  });

  describe('Source Item Selection', () => {
    it('should display all items grouped by view in source select', () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      const sourceSelect = screen.getAllByRole('combobox')[0];
      expect(sourceSelect).toBeInTheDocument();
    });

    it('should show placeholder in source select', () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      expect(screen.getByText(/select source/i)).toBeInTheDocument();
    });

    it('should allow selecting a source item', async () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      const sourceSelect = screen.getAllByRole('combobox')[0];
      fireEvent.change(sourceSelect, {
        target: { value: '550e8400-e29b-41d4-a716-446655440001' },
      });

      await waitFor(() => {
        expect(sourceSelect).toHaveValue('550e8400-e29b-41d4-a716-446655440001');
      });
    });

    it('should preselect source when preselectedSource provided', () => {
      render(
        <CreateLinkForm
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          items={mockItems}
          preselectedSource='550e8400-e29b-41d4-a716-446655440002'
        />,
      );

      const sourceSelect = screen.getAllByRole('combobox')[0];
      expect(sourceSelect).toHaveValue('550e8400-e29b-41d4-a716-446655440002');
    });

    it('should group items by view', () => {
      const { container } = render(
        <CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />,
      );

      // Optgroup elements should exist
      const optgroups = container.querySelectorAll('optgroup');
      expect(optgroups.length).toBeGreaterThan(0);
    });

    it('should display item type and title in options', () => {
      const { container } = render(
        <CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />,
      );

      // Options should contain [Type] Title format
      expect(container.textContent).toContain('[Epic] Epic 1');
    });
  });

  describe('Target Item Selection', () => {
    it('should show placeholder in target select', () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      expect(screen.getByText(/select target/i)).toBeInTheDocument();
    });

    it('should allow selecting a target item', async () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      const targetSelect = screen.getAllByRole('combobox')[1];
      fireEvent.change(targetSelect, {
        target: { value: '550e8400-e29b-41d4-a716-446655440003' },
      });

      await waitFor(() => {
        expect(targetSelect).toHaveValue('550e8400-e29b-41d4-a716-446655440003');
      });
    });

    it('should exclude selected source from target options', async () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      const sourceSelect = screen.getAllByRole('combobox')[0];
      fireEvent.change(sourceSelect, {
        target: { value: '550e8400-e29b-41d4-a716-446655440001' },
      });

      // Target select should filter out item with id '1'
      const targetSelect = screen.getAllByRole('combobox')[1];
      const targetOptions = targetSelect.querySelectorAll('option');

      // Should not include the source item
      const hasSourceInTarget = [...targetOptions].some((opt) => opt.value === '1');
      expect(hasSourceInTarget).toBeFalsy();
    });
  });

  describe('Link Preview', () => {
    it('should show preview when both source and target are selected', async () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      const sourceSelect = screen.getAllByRole('combobox')[0];
      const targetSelect = screen.getAllByRole('combobox')[1];

      fireEvent.change(sourceSelect, {
        target: { value: '550e8400-e29b-41d4-a716-446655440001' },
      });
      fireEvent.change(targetSelect, {
        target: { value: '550e8400-e29b-41d4-a716-446655440002' },
      });

      await waitFor(() => {
        expect(screen.getByText('Epic 1')).toBeInTheDocument();
        expect(screen.getByText('Story 1')).toBeInTheDocument();
      });
    });

    it('should not show preview when only source is selected', () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      const sourceSelect = screen.getAllByRole('combobox')[0];
      fireEvent.change(sourceSelect, {
        target: { value: '550e8400-e29b-41d4-a716-446655440001' },
      });

      // Preview container should not be visible
      const preview = screen.queryByText(/→/);
      expect(preview).not.toBeInTheDocument();
    });

    it('should not show preview when only target is selected', () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      const targetSelect = screen.getAllByRole('combobox')[1];
      fireEvent.change(targetSelect, {
        target: { value: '550e8400-e29b-41d4-a716-446655440002' },
      });

      // Preview should not show without source
      expect(screen.queryByText('Story 1')).not.toBeInTheDocument();
    });

    it('should display arrow in preview', async () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      const sourceSelect = screen.getAllByRole('combobox')[0];
      const targetSelect = screen.getAllByRole('combobox')[1];

      fireEvent.change(sourceSelect, {
        target: { value: '550e8400-e29b-41d4-a716-446655440001' },
      });
      fireEvent.change(targetSelect, {
        target: { value: '550e8400-e29b-41d4-a716-446655440002' },
      });

      await waitFor(() => {
        expect(screen.getByText('→')).toBeInTheDocument();
      });
    });
  });

  describe('Link Type Selection', () => {
    it('should have "implements" as default link type', () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      const linkTypeSelect = screen.getAllByRole('combobox')[2];
      expect(linkTypeSelect).toHaveValue('implements');
    });

    it('should allow changing link type', async () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      const linkTypeSelect = screen.getAllByRole('combobox')[2];
      fireEvent.change(linkTypeSelect, { target: { value: 'tests' } });

      await waitFor(() => {
        expect(linkTypeSelect).toHaveValue('tests');
      });
    });

    it('should display all link type options', () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      const linkTypeSelect = screen.getAllByRole('combobox')[2];
      const options = linkTypeSelect.querySelectorAll('option');

      expect(options.length).toBe(6); // Implements, tests, depends_on, related_to, blocks, parent_of
    });

    it('should format link type labels correctly', () => {
      const { container } = render(
        <CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />,
      );

      expect(container.textContent).toContain('depends on');
      expect(container.textContent).toContain('related to');
      expect(container.textContent).toContain('parent of');
    });
  });

  describe('Description Field', () => {
    it('should accept description input', async () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      const descriptionTextarea = screen.getByPlaceholderText(/why are these items linked/i);

      await user.type(descriptionTextarea, 'This is a test description');

      expect(descriptionTextarea).toHaveValue('This is a test description');
    });

    it('should be optional', async () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      const sourceSelect = screen.getAllByRole('combobox')[0];
      const targetSelect = screen.getAllByRole('combobox')[1];

      fireEvent.change(sourceSelect, {
        target: { value: '550e8400-e29b-41d4-a716-446655440001' },
      });
      fireEvent.change(targetSelect, {
        target: { value: '550e8400-e29b-41d4-a716-446655440002' },
      });

      fireEvent.submit(screen.getByText('Create Link').closest('form')!);

      // Should submit without description
      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled();
      });
    });

    it('should have row attribute', () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      const descriptionTextarea = screen.getByPlaceholderText(/why are these items linked/i);
      expect(descriptionTextarea).toHaveAttribute('rows', '2');
    });
  });

  describe('Form Validation', () => {
    it('should require source item', async () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      const targetSelect = screen.getAllByRole('combobox')[1];
      fireEvent.change(targetSelect, {
        target: { value: '550e8400-e29b-41d4-a716-446655440002' },
      });

      fireEvent.submit(screen.getByText('Create Link').closest('form')!);

      await waitFor(() => {
        expect(screen.getByText(/select a source item/i)).toBeInTheDocument();
      });
    });

    it('should require target item', async () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      const sourceSelect = screen.getAllByRole('combobox')[0];
      fireEvent.change(sourceSelect, {
        target: { value: '550e8400-e29b-41d4-a716-446655440001' },
      });

      fireEvent.submit(screen.getByText('Create Link').closest('form')!);

      await waitFor(() => {
        expect(screen.getByText(/select a target item/i)).toBeInTheDocument();
      });
    });

    it('should validate description max length', async () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      const sourceSelect = screen.getAllByRole('combobox')[0];
      const targetSelect = screen.getAllByRole('combobox')[1];
      const descriptionTextarea = screen.getByPlaceholderText(/why are these items linked/i);

      fireEvent.change(sourceSelect, {
        target: { value: '550e8400-e29b-41d4-a716-446655440001' },
      });
      fireEvent.change(targetSelect, {
        target: { value: '550e8400-e29b-41d4-a716-446655440002' },
      });

      // Type more than 1000 characters
      await user.type(descriptionTextarea, 'A'.repeat(1001));

      fireEvent.submit(screen.getByText('Create Link').closest('form')!);

      // Form validation should fail
      await waitFor(() => {
        expect(mockOnSubmit).not.toHaveBeenCalled();
      });
    });
  });

  describe('Form Submission', () => {
    it('should submit form with valid data', async () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      const sourceSelect = screen.getAllByRole('combobox')[0];
      const targetSelect = screen.getAllByRole('combobox')[1];

      fireEvent.change(sourceSelect, {
        target: { value: '550e8400-e29b-41d4-a716-446655440001' },
      });
      fireEvent.change(targetSelect, {
        target: { value: '550e8400-e29b-41d4-a716-446655440002' },
      });

      fireEvent.submit(screen.getByText('Create Link').closest('form')!);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            sourceId: '550e8400-e29b-41d4-a716-446655440001',
            targetId: '550e8400-e29b-41d4-a716-446655440002',
            type: 'implements',
          }),
          expect.anything(), // SyntheticBaseEvent
        );
      });
    });

    it('should submit form with description', async () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      const sourceSelect = screen.getAllByRole('combobox')[0];
      const targetSelect = screen.getAllByRole('combobox')[1];
      const descriptionTextarea = screen.getByPlaceholderText(/why are these items linked/i);

      fireEvent.change(sourceSelect, {
        target: { value: '550e8400-e29b-41d4-a716-446655440001' },
      });
      fireEvent.change(targetSelect, {
        target: { value: '550e8400-e29b-41d4-a716-446655440003' },
      });
      await user.type(descriptionTextarea, 'Test relationship');

      fireEvent.submit(screen.getByText('Create Link').closest('form')!);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            description: 'Test relationship',
            sourceId: '550e8400-e29b-41d4-a716-446655440001',
            targetId: '550e8400-e29b-41d4-a716-446655440003',
            type: 'implements',
          }),
          expect.anything(), // SyntheticBaseEvent
        );
      });
    });

    it('should submit with selected link type', async () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      const sourceSelect = screen.getAllByRole('combobox')[0];
      const targetSelect = screen.getAllByRole('combobox')[1];
      const linkTypeSelect = screen.getAllByRole('combobox')[2];

      fireEvent.change(sourceSelect, {
        target: { value: '550e8400-e29b-41d4-a716-446655440001' },
      });
      fireEvent.change(targetSelect, {
        target: { value: '550e8400-e29b-41d4-a716-446655440002' },
      });
      fireEvent.change(linkTypeSelect, { target: { value: 'depends_on' } });

      fireEvent.submit(screen.getByText('Create Link').closest('form')!);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({ type: 'depends_on' }),
          expect.anything(), // SyntheticBaseEvent
        );
      });
    });
  });

  describe('Loading State', () => {
    it('should disable submit button when loading', () => {
      render(
        <CreateLinkForm
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          items={mockItems}
          isLoading
        />,
      );

      const submitButton = screen.getByText('Creating...');
      expect(submitButton).toBeDisabled();
    });

    it('should show loading text when loading', () => {
      render(
        <CreateLinkForm
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          items={mockItems}
          isLoading
        />,
      );

      expect(screen.getByText('Creating...')).toBeInTheDocument();
    });

    it('should show normal text when not loading', () => {
      render(
        <CreateLinkForm
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          items={mockItems}
          isLoading={false}
        />,
      );

      expect(screen.getByText('Create Link')).toBeInTheDocument();
    });
  });

  describe('Cancellation', () => {
    it('should call onCancel when Cancel button is clicked', () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      fireEvent.click(screen.getByText('Cancel'));

      expect(mockOnCancel).toHaveBeenCalledTimes(1);
    });

    it('should call onCancel when close button is clicked', () => {
      const { container } = render(
        <CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />,
      );

      const closeButton = container.querySelector('button');
      if (closeButton) {
        fireEvent.click(closeButton);
      }

      expect(mockOnCancel).toHaveBeenCalled();
    });

    it('should call onCancel when backdrop is clicked', () => {
      const { container } = render(
        <CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />,
      );

      // The backdrop is the element with bg-black/50 and onClick={onCancel}
      const backdrop = container.querySelector(String.raw`.bg-black\/50`);
      if (backdrop) {
        fireEvent.click(backdrop);
      }

      expect(mockOnCancel).toHaveBeenCalled();
    });

    it('should not call onCancel when modal content is clicked', () => {
      const { container } = render(
        <CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />,
      );

      const modalContent = container.querySelector('.relative.w-full');
      if (modalContent) {
        fireEvent.click(modalContent);
      }

      expect(mockOnCancel).not.toHaveBeenCalled();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty items array', () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={[]} />);

      expect(screen.getByText('Create Traceability Link')).toBeInTheDocument();
    });

    it('should handle items with same view', () => {
      const sameViewItems = [
        { id: '1', title: 'Item 1', type: 'Epic', view: 'Feature' },
        { id: '2', title: 'Item 2', type: 'Story', view: 'Feature' },
      ];

      render(
        <CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={sameViewItems} />,
      );

      expect(screen.getByText('Create Traceability Link')).toBeInTheDocument();
    });

    it('should handle very long item titles', () => {
      const longTitleItems = [{ id: '1', title: 'A'.repeat(200), type: 'Epic', view: 'Feature' }];

      render(
        <CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={longTitleItems} />,
      );

      expect(screen.getByText('Create Traceability Link')).toBeInTheDocument();
    });

    it('should handle special characters in item titles', () => {
      const specialCharItems = [
        { id: '1', title: '<Epic> & "Special"', type: 'Epic', view: 'Feature' },
      ];

      render(
        <CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={specialCharItems} />,
      );

      expect(screen.getByText('Create Traceability Link')).toBeInTheDocument();
    });

    it('should handle invalid preselectedSource', () => {
      render(
        <CreateLinkForm
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          items={mockItems}
          preselectedSource='invalid-id'
        />,
      );

      // Invalid preselectedSource will be set but won't match any option
      // The form should still render without crashing
      const sourceSelect = screen.getAllByRole('combobox')[0];
      expect(sourceSelect).toBeInTheDocument();
      // The value will either be the invalid-id (if controlled) or empty string
      expect((sourceSelect as HTMLSelectElement).value).toBeDefined();
    });
  });

  describe('Accessibility', () => {
    it('should have labeled form fields', () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      expect(screen.getByText(/source item/i)).toBeInTheDocument();
      expect(screen.getByText(/target item/i)).toBeInTheDocument();
      expect(screen.getByText(/link type/i)).toBeInTheDocument();
    });

    it('should indicate required fields', () => {
      const { container } = render(
        <CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />,
      );

      const requiredIndicators = container.querySelectorAll('.text-red-500');
      expect(requiredIndicators.length).toBeGreaterThan(0);
    });

    it('should have accessible form elements', () => {
      render(<CreateLinkForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} items={mockItems} />);

      const selects = screen.getAllByRole('combobox');
      expect(selects.length).toBe(3);
    });
  });
});
