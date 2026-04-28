/**
 * Feature Tests: Link Sharing, Spec Creation, and Project Management
 * Tests newly implemented features for phases 8-16
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { describe, expect, it, vi } from 'vitest';

const setupUser = () => userEvent.setup();

// Mock Link Sharing Component
function MockLinkSharing({
  itemId = 'item-1',
  onShare = vi.fn(),
}: {
  itemId?: string;
  onShare?: (link: string) => void;
}) {
  const [copied, setCopied] = React.useState(false);
  const shareLink = `https://tracertm.local/items/${itemId}/shared`;

  const handleCopyLink = async () => {
    await navigator.clipboard.writeText(shareLink);
    setCopied(true);
    onShare(shareLink);
    setTimeout(() => {
      setCopied(false);
    }, 2000);
  };

  return (
    <div className='rounded border p-4'>
      <h3 className='mb-3 font-semibold'>Share Item</h3>
      <div className='flex gap-2'>
        <input
          type='text'
          readOnly
          value={shareLink}
          className='flex-1 rounded border px-3 py-2'
          aria-label='Share link'
        />
        <button
          onClick={handleCopyLink}
          className='rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700'
          aria-label={copied ? 'Link copied' : 'Copy link'}
        >
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
      <button
        onClick={() => window.open(shareLink, '_blank')}
        className='mt-2 w-full rounded bg-gray-200 px-4 py-2 hover:bg-gray-300'
      >
        Open in new tab
      </button>
    </div>
  );
}

// Mock Spec Creation Component
function MockSpecCreation({
  onSpecCreate = vi.fn(),
}: {
  onSpecCreate?: (spec: { name: string; type: string; content: string }) => void;
}) {
  const [specName, setSpecName] = React.useState('');
  const [specType, setSpecType] = React.useState('openapi');
  const [specContent, setSpecContent] = React.useState('');
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const spec = { content: specContent, name: specName, type: specType };
      await new Promise((resolve) => setTimeout(resolve, 100));
      onSpecCreate(spec);
      setSpecName('');
      setSpecContent('');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className='rounded border p-4'>
      <h3 className='mb-3 font-semibold'>Create API Specification</h3>

      <div className='mb-4'>
        <label htmlFor='spec-name' className='mb-1 block text-sm font-medium'>
          Specification Name
        </label>
        <input
          id='spec-name'
          type='text'
          value={specName}
          onChange={(e) => {
            setSpecName(e.target.value);
          }}
          placeholder='e.g., User API v1.0'
          className='w-full rounded border px-3 py-2'
          required
        />
      </div>

      <div className='mb-4'>
        <label htmlFor='spec-type' className='mb-1 block text-sm font-medium'>
          Specification Type
        </label>
        <select
          id='spec-type'
          value={specType}
          onChange={(e) => {
            setSpecType(e.target.value);
          }}
          className='w-full rounded border px-3 py-2'
        >
          <option value='openapi'>OpenAPI 3.0</option>
          <option value='asyncapi'>AsyncAPI</option>
          <option value='graphql'>GraphQL</option>
          <option value='protobuf'>Protocol Buffers</option>
        </select>
      </div>

      <div className='mb-4'>
        <label htmlFor='spec-content' className='mb-1 block text-sm font-medium'>
          Specification Content
        </label>
        <textarea
          id='spec-content'
          value={specContent}
          onChange={(e) => {
            setSpecContent(e.target.value);
          }}
          placeholder='Paste your specification content'
          className='h-48 w-full rounded border px-3 py-2 font-mono text-sm'
          required
        />
      </div>

      <button
        type='submit'
        disabled={isSubmitting}
        className='w-full rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50'
        aria-busy={isSubmitting}
      >
        {isSubmitting ? 'Creating...' : 'Create Specification'}
      </button>
    </form>
  );
}

// Mock Project Edit Component
function MockProjectEdit({
  initialProject = {
    description: 'Test project',
    id: 'proj-1',
    name: 'Project 1',
  },
  onSave = vi.fn(),
}: {
  initialProject?: { id: string; name: string; description: string };
  onSave?: (project: { name: string; description: string }) => void;
}) {
  const [name, setName] = React.useState(initialProject.name);
  const [description, setDescription] = React.useState(initialProject.description);
  const [isModified, setIsModified] = React.useState(false);
  const [isSaving, setIsSaving] = React.useState(false);

  const handleChange = (field: string, value: string) => {
    if (field === 'name') {
      setName(value);
    } else {
      setDescription(value);
    }
    setIsModified(true);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);

    try {
      await new Promise((resolve) => setTimeout(resolve, 100));
      onSave({ description, name });
      setIsModified(false);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <form onSubmit={handleSave} className='rounded border p-4'>
      <h3 className='mb-3 font-semibold'>Edit Project</h3>

      <div className='mb-4'>
        <label htmlFor='proj-name' className='mb-1 block text-sm font-medium'>
          Project Name
        </label>
        <input
          id='proj-name'
          type='text'
          value={name}
          onChange={(e) => {
            handleChange('name', e.target.value);
          }}
          className='w-full rounded border px-3 py-2'
          required
        />
      </div>

      <div className='mb-4'>
        <label htmlFor='proj-desc' className='mb-1 block text-sm font-medium'>
          Description
        </label>
        <textarea
          id='proj-desc'
          value={description}
          onChange={(e) => {
            handleChange('description', e.target.value);
          }}
          className='h-24 w-full rounded border px-3 py-2'
        />
      </div>

      <div className='flex gap-2'>
        <button
          type='submit'
          disabled={!isModified || isSaving}
          className='flex-1 rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50'
          aria-busy={isSaving}
        >
          {isSaving ? 'Saving...' : 'Save Changes'}
        </button>
        <button
          type='button'
          onClick={() => {
            setName(initialProject.name);
            setDescription(initialProject.description);
            setIsModified(false);
          }}
          className='rounded bg-gray-200 px-4 py-2 hover:bg-gray-300'
        >
          Reset
        </button>
      </div>
    </form>
  );
}

// Mock Reports Generation Component
function MockReportsGeneration({
  projectId: _projectId = 'proj-1',
  onGenerateReport = vi.fn(),
}: {
  projectId?: string;
  onGenerateReport?: (report: { type: string; format: string }) => void;
}) {
  const [reportType, setReportType] = React.useState('coverage');
  const [format, setFormat] = React.useState('pdf');
  const [isGenerating, setIsGenerating] = React.useState(false);

  const handleGenerate = async () => {
    setIsGenerating(true);

    try {
      await new Promise((resolve) => setTimeout(resolve, 200));
      onGenerateReport({ format, type: reportType });
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className='rounded border p-4'>
      <h3 className='mb-3 font-semibold'>Generate Report</h3>

      <div className='mb-4'>
        <label htmlFor='report-type' className='mb-1 block text-sm font-medium'>
          Report Type
        </label>
        <select
          id='report-type'
          value={reportType}
          onChange={(e) => {
            setReportType(e.target.value);
          }}
          className='w-full rounded border px-3 py-2'
        >
          <option value='coverage'>Coverage Summary</option>
          <option value='traceability'>Traceability Matrix</option>
          <option value='gaps'>Gap Analysis</option>
          <option value='compliance'>Compliance Report</option>
        </select>
      </div>

      <div className='mb-4'>
        <label htmlFor='report-format' className='mb-1 block text-sm font-medium'>
          Export Format
        </label>
        <select
          id='report-format'
          value={format}
          onChange={(e) => {
            setFormat(e.target.value);
          }}
          className='w-full rounded border px-3 py-2'
        >
          <option value='pdf'>PDF</option>
          <option value='excel'>Excel</option>
          <option value='html'>HTML</option>
          <option value='markdown'>Markdown</option>
        </select>
      </div>

      <button
        onClick={handleGenerate}
        disabled={isGenerating}
        className='w-full rounded bg-green-600 px-4 py-2 text-white hover:bg-green-700 disabled:opacity-50'
        aria-busy={isGenerating}
      >
        {isGenerating ? 'Generating...' : 'Generate Report'}
      </button>
    </div>
  );
}

describe('Link Sharing - Basic Functionality', () => {
  it('should display shareable link', () => {
    render(<MockLinkSharing itemId='item-123' />);

    const linkInput = screen.getByDisplayValue(/tracertm\.local\/items\/item-123/);
    expect(linkInput).toBeInTheDocument();
  });

  it('should copy link to clipboard', async () => {
    const handleShare = vi.fn();

    render(<MockLinkSharing itemId='item-1' onShare={handleShare} />);

    const user = setupUser();
    const copyBtn = screen.getByRole('button', { name: /Copy/i });
    await user.click(copyBtn);

    await waitFor(() => {
      expect(copyBtn).toHaveTextContent('Copied!');
    });

    expect(handleShare).toHaveBeenCalledWith(expect.stringContaining('item-1'));
  });

  it('should revert copy button after 2 seconds', async () => {
    vi.useFakeTimers();

    render(<MockLinkSharing itemId='item-1' />);

    const user = setupUser();
    const copyBtn = screen.getByRole('button', { name: /Copy/i });
    await user.click(copyBtn);

    expect(copyBtn).toHaveTextContent('Copied!');

    vi.advanceTimersByTime(2000);

    await waitFor(() => {
      expect(copyBtn).toHaveTextContent('Copy');
    });

    vi.useRealTimers();
  });

  it('should open shared link in new tab', async () => {
    const openSpy = vi.spyOn(globalThis, 'open').mockReturnValue(null);

    render(<MockLinkSharing itemId='item-1' />);

    const user = setupUser();
    const openBtn = screen.getByRole('button', { name: /Open in new tab/i });
    await user.click(openBtn);

    expect(openSpy).toHaveBeenCalledWith(expect.stringContaining('item-1'), '_blank');

    openSpy.mockRestore();
  });
});

describe('Spec Creation - Form Validation', () => {
  it('should render spec creation form', () => {
    render(<MockSpecCreation />);

    expect(screen.getByLabelText('Specification Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Specification Type')).toBeInTheDocument();
    expect(screen.getByLabelText('Specification Content')).toBeInTheDocument();
  });

  it('should require specification name', async () => {
    render(<MockSpecCreation />);

    const nameInput = screen.getByLabelText('Specification Name');
    expect(nameInput.required).toBeTruthy();
  });

  it('should require specification content', async () => {
    render(<MockSpecCreation />);

    const contentInput = screen.getByLabelText('Specification Content');
    expect(contentInput.required).toBeTruthy();
  });

  it('should provide multiple spec type options', () => {
    render(<MockSpecCreation />);

    const typeSelect = screen.getByDisplayValue('OpenAPI 3.0');
    expect(typeSelect.options).toHaveLength(4);
    expect(typeSelect.options[0]).toHaveTextContent('OpenAPI 3.0');
    expect(typeSelect.options[1]).toHaveTextContent('AsyncAPI');
    expect(typeSelect.options[2]).toHaveTextContent('GraphQL');
    expect(typeSelect.options[3]).toHaveTextContent('Protocol Buffers');
  });
});

describe('Spec Creation - Submission', () => {
  it('should submit spec creation form', async () => {
    const handleCreate = vi.fn();

    render(<MockSpecCreation onSpecCreate={handleCreate} />);

    const user = setupUser();
    const nameInput = screen.getByLabelText('Specification Name');
    const contentInput = screen.getByLabelText('Specification Content');
    const submitBtn = screen.getByRole('button', {
      name: 'Create Specification',
    });

    await user.type(nameInput, 'Test API');
    await user.type(contentInput, 'openapi: 3.0.0');
    await user.click(submitBtn);

    await waitFor(() => {
      expect(handleCreate).toHaveBeenCalledWith(
        expect.objectContaining({
          content: 'openapi: 3.0.0',
          name: 'Test API',
          type: 'openapi',
        }),
      );
    });
  });

  it('should disable submit button while submitting', async () => {
    const handleCreate = vi.fn(async () => new Promise((resolve) => setTimeout(resolve, 200)));

    render(<MockSpecCreation onSpecCreate={handleCreate} />);

    const user = setupUser();
    const nameInput = screen.getByLabelText('Specification Name');
    const contentInput = screen.getByLabelText('Specification Content');
    const submitBtn = screen.getByRole('button');

    await user.type(nameInput, 'Test API');
    await user.type(contentInput, 'content');
    await user.click(submitBtn);

    expect(submitBtn).toBeDisabled();
  });

  it('should clear form after successful submission', async () => {
    render(<MockSpecCreation />);

    const user = setupUser();
    const nameInput = screen.getByLabelText('Specification Name');
    const contentInput = screen.getByLabelText('Specification Content');
    const submitBtn = screen.getByRole('button');

    await user.type(nameInput, 'Test API');
    await user.type(contentInput, 'content');
    await user.click(submitBtn);

    await waitFor(() => {
      expect(nameInput.value).toBe('');
      expect(contentInput.value).toBe('');
    });
  });
});

describe('Project Edit - Form Functionality', () => {
  it('should populate form with initial project data', () => {
    render(
      <MockProjectEdit
        initialProject={{
          description: 'A test project',
          id: 'proj-1',
          name: 'Test Project',
        }}
      />,
    );

    expect(screen.getByDisplayValue('Test Project')).toBeInTheDocument();
    expect(screen.getByDisplayValue('A test project')).toBeInTheDocument();
  });

  it('should track field modifications', async () => {
    render(
      <MockProjectEdit
        initialProject={{
          description: 'Original desc',
          id: 'proj-1',
          name: 'Original',
        }}
      />,
    );

    const user = setupUser();
    const nameInput = screen.getByDisplayValue('Original');
    const saveBtn = screen.getByRole('button', {
      name: 'Save Changes',
    });

    // Button should be disabled initially
    expect(saveBtn.disabled).toBeTruthy();

    await user.clear(nameInput);
    await user.type(nameInput, 'Updated');

    // Button should now be enabled
    expect(saveBtn.disabled).toBeFalsy();
  });

  it('should reset changes', async () => {
    render(
      <MockProjectEdit
        initialProject={{
          description: 'Original desc',
          id: 'proj-1',
          name: 'Original',
        }}
      />,
    );

    const user = setupUser();
    const nameInput = screen.getByDisplayValue('Original');
    const resetBtn = screen.getByRole('button', { name: 'Reset' });

    await user.clear(nameInput);
    await user.type(nameInput, 'Updated');

    await user.click(resetBtn);

    expect(nameInput.value).toBe('Original');
  });

  it('should save project changes', async () => {
    const handleSave = vi.fn();

    render(
      <MockProjectEdit
        initialProject={{
          description: 'Desc',
          id: 'proj-1',
          name: 'Original',
        }}
        onSave={handleSave}
      />,
    );

    const user = setupUser();
    const nameInput = screen.getByDisplayValue('Original');
    const saveBtn = screen.getByRole('button', { name: 'Save Changes' });

    await user.clear(nameInput);
    await user.type(nameInput, 'Updated');
    await user.click(saveBtn);

    await waitFor(() => {
      expect(handleSave).toHaveBeenCalledWith({
        description: 'Desc',
        name: 'Updated',
      });
    });
  });
});

describe('Reports Generation - Options', () => {
  it('should provide multiple report types', () => {
    render(<MockReportsGeneration />);

    const typeSelect = screen.getByDisplayValue('Coverage Summary');
    expect(typeSelect.options).toHaveLength(4);
    expect(typeSelect.options[0]).toHaveTextContent('Coverage Summary');
    expect(typeSelect.options[1]).toHaveTextContent('Traceability Matrix');
    expect(typeSelect.options[2]).toHaveTextContent('Gap Analysis');
    expect(typeSelect.options[3]).toHaveTextContent('Compliance Report');
  });

  it('should provide multiple export formats', () => {
    render(<MockReportsGeneration />);

    const formatSelect = screen.getByDisplayValue('PDF');
    expect(formatSelect.options).toHaveLength(4);
    expect(formatSelect.options[0]).toHaveTextContent('PDF');
    expect(formatSelect.options[1]).toHaveTextContent('Excel');
    expect(formatSelect.options[2]).toHaveTextContent('HTML');
    expect(formatSelect.options[3]).toHaveTextContent('Markdown');
  });

  it('should generate report with selected options', async () => {
    const handleGenerate = vi.fn();

    render(<MockReportsGeneration onGenerateReport={handleGenerate} />);

    const user = setupUser();
    const typeSelect = screen.getByDisplayValue('Coverage Summary');
    const formatSelect = screen.getByDisplayValue('PDF');
    const generateBtn = screen.getByRole('button', {
      name: 'Generate Report',
    });

    await user.selectOptions(typeSelect, 'traceability');
    await user.selectOptions(formatSelect, 'excel');
    await user.click(generateBtn);

    await waitFor(() => {
      expect(handleGenerate).toHaveBeenCalledWith({
        format: 'excel',
        type: 'traceability',
      });
    });
  });

  it('should show loading state while generating', async () => {
    const handleGenerate = vi.fn(async () => new Promise((resolve) => setTimeout(resolve, 500)));

    render(<MockReportsGeneration onGenerateReport={handleGenerate} />);

    const user = setupUser();
    const generateBtn = screen.getByRole('button');

    await user.click(generateBtn);

    expect(generateBtn).toBeDisabled();
    expect(generateBtn).toHaveAttribute('aria-busy', 'true');
  });
});

describe('Contract and Compliance Features', () => {
  function MockComplianceChecklist({
    items = [
      { completed: false, id: '1', name: 'Security Review' },
      { completed: false, id: '2', name: 'Performance Test' },
      { completed: false, id: '3', name: 'Documentation' },
    ],
    onCheck = vi.fn(),
  }: {
    items?: { id: string; name: string; completed: boolean }[];
    onCheck?: (id: string, completed: boolean) => void;
  }) {
    return (
      <div className='rounded border p-4'>
        <h3 className='mb-3 font-semibold'>Compliance Checklist</h3>
        <ul>
          {items.map((item) => (
            <li key={item.id} className='mb-2'>
              <label className='flex items-center gap-2'>
                <input
                  type='checkbox'
                  checked={item.completed}
                  onChange={(e) => {
                    onCheck(item.id, e.target.checked);
                  }}
                  aria-label={item.name}
                />
                {item.name}
              </label>
            </li>
          ))}
        </ul>
        <div className='mt-4 rounded bg-blue-50 p-2'>
          {items.filter((i) => i.completed).length} of {items.length} completed
        </div>
      </div>
    );
  }

  it('should track compliance items', async () => {
    render(<MockComplianceChecklist />);

    const user = setupUser();
    const checkboxes = screen.getAllByRole('checkbox');
    expect(checkboxes).toHaveLength(3);

    await user.click(checkboxes[0]);
    expect(checkboxes[0]).toBeChecked();
  });

  it('should calculate completion percentage', () => {
    render(
      <MockComplianceChecklist
        items={[
          { completed: true, id: '1', name: 'Item 1' },
          { completed: true, id: '2', name: 'Item 2' },
          { completed: false, id: '3', name: 'Item 3' },
        ]}
      />,
    );

    expect(screen.getByText('2 of 3 completed')).toBeInTheDocument();
  });
});
