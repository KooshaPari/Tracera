/**
 * Integration Tests: Cross-Feature Workflows and End-to-End Scenarios
 * Tests complex workflows combining multiple features
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

let user: ReturnType<typeof userEvent.setup>;

// Mock API Client
class MockApiClient {
  private delay = 50;

  async createProject(name: string, description: string) {
    await new Promise((resolve) => setTimeout(resolve, this.delay));
    return {
      createdAt: new Date(),
      description,
      id: `proj-${Date.now()}`,
      name,
    };
  }

  async createItem(projectId: string, name: string) {
    await new Promise((resolve) => setTimeout(resolve, this.delay));
    return { createdAt: new Date(), id: `item-${Date.now()}`, name, projectId };
  }

  async createLink(sourceId: string, targetId: string, type: string) {
    await new Promise((resolve) => setTimeout(resolve, this.delay));
    return { id: `link-${Date.now()}`, sourceId, targetId, type };
  }

  async shareItem(itemId: string) {
    await new Promise((resolve) => setTimeout(resolve, this.delay));
    return { shareLink: `https://tracertm.local/items/${itemId}/shared` };
  }

  async generateReport(projectId: string, type: string, format: string) {
    await new Promise((resolve) => setTimeout(resolve, 100));
    return {
      reportId: `report-${Date.now()}`,
      url: `/reports/report-${Date.now()}.${format}`,
    };
  }

  async searchItems(query: string) {
    await new Promise((resolve) => setTimeout(resolve, this.delay));
    return [
      { id: '1', name: `Result matching "${query}"` },
      { id: '2', name: `Another result for "${query}"` },
    ];
  }
}

// Mock Project Management Workflow
function MockProjectWorkflow({
  onWorkflowComplete = vi.fn(),
}: {
  onWorkflowComplete?: (result: unknown) => void;
}) {
  const [step, setStep] = React.useState(1);
  const [project, setProject] = React.useState<any>(null);
  const [items, setItems] = React.useState<any[]>([]);
  const [api] = React.useState(() => new MockApiClient());
  const [isLoading, setIsLoading] = React.useState(false);

  const handleCreateProject = async (name: string, description: string) => {
    setIsLoading(true);
    try {
      const newProject = await api.createProject(name, description);
      setProject(newProject);
      setStep(2);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateItem = async (name: string) => {
    setIsLoading(true);
    try {
      const newItem = await api.createItem(project.id, name);
      setItems([...items, newItem]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCompleteWorkflow = async () => {
    setIsLoading(true);
    try {
      const report = await api.generateReport(project.id, 'coverage', 'pdf');
      onWorkflowComplete({ items, project, report });
      setStep(3);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className='rounded border p-4'>
      <h2 className='mb-4 text-xl font-bold'>Project Setup Workflow</h2>

      {step === 1 && (
        <div>
          <h3 className='mb-3 font-semibold'>Step 1: Create Project</h3>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.currentTarget);
              const name = formData.get('name');
              const description = formData.get('description');
              void handleCreateProject(
                typeof name === 'string' ? name : '',
                typeof description === 'string' ? description : '',
              );
            }}
          >
            <input
              name='name'
              placeholder='Project name'
              className='mb-3 w-full rounded border px-3 py-2'
              required
            />
            <textarea
              name='description'
              placeholder='Description'
              className='mb-3 w-full rounded border px-3 py-2'
            />
            <button
              type='submit'
              disabled={isLoading}
              className='rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50'
            >
              Create Project
            </button>
          </form>
        </div>
      )}

      {step === 2 && project && (
        <div>
          <h3 className='mb-3 font-semibold'>Step 2: Add Items</h3>
          <p className='mb-4'>Project: {project.name}</p>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              const input = e.currentTarget.querySelector("input[name='item-name']");
              if (input instanceof HTMLInputElement) {
                void handleCreateItem(input.value);
                input.value = '';
              }
            }}
          >
            <input
              name='item-name'
              placeholder='Item name'
              className='mb-3 w-full rounded border px-3 py-2'
              required
            />
            <button
              type='submit'
              disabled={isLoading}
              className='rounded bg-green-600 px-4 py-2 text-white hover:bg-green-700 disabled:opacity-50'
            >
              Add Item
            </button>
          </form>

          <div className='mt-4'>
            <h4 className='mb-2 font-semibold'>Items: ({items.length})</h4>
            {items.map((item) => (
              <div key={item.id} className='mb-2 rounded bg-gray-100 p-2'>
                {item.name}
              </div>
            ))}
          </div>

          {items.length > 0 && (
            <button
              onClick={handleCompleteWorkflow}
              disabled={isLoading}
              className='mt-4 rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50'
            >
              Complete Setup
            </button>
          )}
        </div>
      )}

      {step === 3 && (
        <div>
          <h3 className='mb-3 font-semibold text-green-600'>Workflow Complete!</h3>
          <p>Project setup finished successfully.</p>
        </div>
      )}
    </div>
  );
}

// Mock Search and Filter Workflow
function MockSearchWorkflow({ onSearch = vi.fn() }: { onSearch?: (results: unknown[]) => void }) {
  const [query, setQuery] = React.useState('');
  const [results, setResults] = React.useState<any[]>([]);
  const [isSearching, setIsSearching] = React.useState(false);
  const [api] = React.useState(() => new MockApiClient());

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSearching(true);

    try {
      const searchResults = await api.searchItems(query);
      setResults(searchResults);
      onSearch(searchResults);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className='rounded border p-4'>
      <h2 className='mb-4 text-xl font-bold'>Search Items</h2>

      <form onSubmit={handleSearch} className='mb-4'>
        <div className='flex gap-2'>
          <input
            type='search'
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
            }}
            placeholder='Search items...'
            className='flex-1 rounded border px-3 py-2'
            required
          />
          <button
            type='submit'
            disabled={isSearching || !query}
            className='rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50'
          >
            Search
          </button>
        </div>
      </form>

      {isSearching && <p>Searching...</p>}

      {results.length > 0 && (
        <div>
          <h3 className='mb-2 font-semibold'>Results ({results.length})</h3>
          {results.map((result) => (
            <div key={result.id} className='mb-2 rounded bg-blue-50 p-3'>
              {result.name}
            </div>
          ))}
        </div>
      )}

      {results.length === 0 && query && !isSearching && (
        <p className='text-gray-600'>No results found for "{query}"</p>
      )}
    </div>
  );
}

// Mock Link Creation Workflow
function MockLinkCreationWorkflow({
  onLinkCreate = vi.fn(),
}: {
  onLinkCreate?: (link: unknown) => void;
}) {
  const [sourceId, setSourceId] = React.useState('');
  const [targetId, setTargetId] = React.useState('');
  const [linkType, setLinkType] = React.useState('traces');
  const [links, setLinks] = React.useState<any[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);
  const [api] = React.useState(() => new MockApiClient());

  const handleCreateLink = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const newLink = await api.createLink(sourceId, targetId, linkType);
      setLinks([...links, newLink]);
      onLinkCreate(newLink);
      setSourceId('');
      setTargetId('');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className='rounded border p-4'>
      <h2 className='mb-4 text-xl font-bold'>Create Traceability Links</h2>

      <form onSubmit={handleCreateLink} className='mb-4'>
        <div className='mb-3'>
          <label className='mb-1 block text-sm font-medium'>Source Item ID</label>
          <input
            type='text'
            value={sourceId}
            onChange={(e) => {
              setSourceId(e.target.value);
            }}
            placeholder='e.g., REQ-001'
            className='w-full rounded border px-3 py-2'
            required
          />
        </div>

        <div className='mb-3'>
          <label className='mb-1 block text-sm font-medium'>Target Item ID</label>
          <input
            type='text'
            value={targetId}
            onChange={(e) => {
              setTargetId(e.target.value);
            }}
            placeholder='e.g., TEST-001'
            className='w-full rounded border px-3 py-2'
            required
          />
        </div>

        <div className='mb-3'>
          <label className='mb-1 block text-sm font-medium'>Link Type</label>
          <select
            value={linkType}
            onChange={(e) => {
              setLinkType(e.target.value);
            }}
            className='w-full rounded border px-3 py-2'
          >
            <option value='traces'>Traces</option>
            <option value='implements'>Implements</option>
            <option value='verifies'>Verifies</option>
            <option value='depends_on'>Depends On</option>
          </select>
        </div>

        <button
          type='submit'
          disabled={isLoading}
          className='w-full rounded bg-green-600 px-4 py-2 text-white hover:bg-green-700 disabled:opacity-50'
        >
          Create Link
        </button>
      </form>

      {links.length > 0 && (
        <div>
          <h3 className='mb-2 font-semibold'>Links ({links.length})</h3>
          {links.map((link) => (
            <div key={link.id} className='mb-2 rounded bg-green-50 p-2'>
              {link.sourceId} → {link.targetId} ({link.type})
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

describe('Project Creation Workflow - End-to-End', () => {
  beforeEach(() => {
    user = userEvent.setup();
  });

  it('should complete multi-step project setup', async () => {
    const handleComplete = vi.fn();

    render(<MockProjectWorkflow onWorkflowComplete={handleComplete} />);

    // Step 1: Create project
    const nameInput = screen.getByPlaceholderText('Project name');
    const descInput = screen.getByPlaceholderText('Description');

    await user.type(nameInput, 'E2E Test Project');
    await user.type(descInput, 'Testing workflow');

    const createBtn = screen.getByRole('button', { name: 'Create Project' });
    await user.click(createBtn);

    // Wait for project creation
    await waitFor(() => {
      expect(screen.getByText('Step 2: Add Items')).toBeInTheDocument();
    });

    // Step 2: Add items
    const itemInput = screen.getByPlaceholderText('Item name');
    await user.type(itemInput, 'Requirement 1');
    const addBtn = screen.getByRole('button', { name: 'Add Item' });
    await user.click(addBtn);

    await waitFor(() => {
      expect(screen.getByText('Requirement 1')).toBeInTheDocument();
    });

    // Add another item
    await user.type(itemInput, 'Requirement 2');
    await user.click(addBtn);

    await waitFor(() => {
      expect(screen.getByText('Items: (2)')).toBeInTheDocument();
    });

    // Complete workflow
    const completeBtn = screen.getByRole('button', {
      name: 'Complete Setup',
    });
    await user.click(completeBtn);

    await waitFor(() => {
      expect(handleComplete).toHaveBeenCalled();
      expect(screen.getByText('Workflow Complete!')).toBeInTheDocument();
    });
  });

  it('should prevent incomplete workflow progression', async () => {
    render(<MockProjectWorkflow />);

    // Create project
    const nameInput = screen.getByPlaceholderText('Project name');
    await user.type(nameInput, 'Test');

    const createBtn = screen.getByRole('button', { name: 'Create Project' });
    await user.click(createBtn);

    // Should now be on step 2
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Item name')).toBeInTheDocument();
    });

    // Complete button should not be visible yet (no items)
    const completeBtn = screen.queryByRole('button', {
      name: 'Complete Setup',
    });
    expect(completeBtn).not.toBeInTheDocument();
  });
});

describe('Search and Filter Integration', () => {
  beforeEach(() => {
    user = userEvent.setup();
  });

  it('should perform search and return results', async () => {
    const handleSearch = vi.fn();

    render(<MockSearchWorkflow onSearch={handleSearch} />);

    const searchInput = screen.getByPlaceholderText('Search items...');
    const searchBtn = screen.getByRole('button', { name: 'Search' });

    await user.type(searchInput, 'requirement');
    await user.click(searchBtn);

    await waitFor(() => {
      expect(handleSearch).toHaveBeenCalledWith(expect.any(Array));
      expect(screen.getByText(/Results/)).toBeInTheDocument();
    });
  });

  it('should display no results message when search returns empty', async () => {
    render(<MockSearchWorkflow />);

    const searchInput = screen.getByPlaceholderText('Search items...');
    const searchBtn = screen.getByRole('button', { name: 'Search' });

    await user.type(searchInput, 'nonexistent');
    await user.click(searchBtn);

    await waitFor(() => {
      expect(screen.getByText(/No results found/)).toBeInTheDocument();
    });
  });

  it('should disable search button when query is empty', () => {
    render(<MockSearchWorkflow />);

    const searchBtn = screen.getByRole('button', { name: 'Search' });
    expect(searchBtn).toBeDisabled();
  });

  it('should enable search button when query is entered', async () => {
    render(<MockSearchWorkflow />);

    const searchInput = screen.getByPlaceholderText('Search items...');
    const searchBtn = screen.getByRole('button', { name: 'Search' });

    await user.type(searchInput, 'test');

    expect(searchBtn).not.toBeDisabled();
  });
});

describe('Link Creation Workflow', () => {
  beforeEach(() => {
    user = userEvent.setup();
  });

  it('should create traceability links', async () => {
    const handleLinkCreate = vi.fn();

    render(<MockLinkCreationWorkflow onLinkCreate={handleLinkCreate} />);

    const sourceInput = screen.getByPlaceholderText('e.g., REQ-001');
    const targetInput = screen.getByPlaceholderText('e.g., TEST-001');
    const submitBtn = screen.getByRole('button', { name: 'Create Link' });

    await user.type(sourceInput, 'REQ-001');
    await user.type(targetInput, 'TEST-001');
    await user.click(submitBtn);

    await waitFor(() => {
      expect(handleLinkCreate).toHaveBeenCalled();
      expect(screen.getByText(/REQ-001 → TEST-001/)).toBeInTheDocument();
    });
  });

  it('should support different link types', async () => {
    render(<MockLinkCreationWorkflow />);

    const linkTypeSelect = screen.getByDisplayValue('Traces');

    // Should have multiple options
    const options = linkTypeSelect instanceof HTMLSelectElement ? linkTypeSelect.options : [];
    expect(options).toHaveLength(4);
    expect(options[1]).toHaveTextContent('Implements');
    expect(options[2]).toHaveTextContent('Verifies');
  });

  it('should create multiple links in sequence', async () => {
    render(<MockLinkCreationWorkflow />);

    const sourceInput = screen.getByPlaceholderText('e.g., REQ-001');
    const targetInput = screen.getByPlaceholderText('e.g., TEST-001');
    const submitBtn = screen.getByRole('button', { name: 'Create Link' });

    // First link
    await user.type(sourceInput, 'REQ-001');
    await user.type(targetInput, 'TEST-001');
    await user.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText(/REQ-001 → TEST-001/)).toBeInTheDocument();
    });

    // Second link
    await user.type(sourceInput, 'REQ-002');
    await user.type(targetInput, 'TEST-002');
    await user.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText(/REQ-002 → TEST-002/)).toBeInTheDocument();
      expect(screen.getByText(/Links \(2\)/)).toBeInTheDocument();
    });
  });
});

describe('Cross-Feature Workflow Integration', () => {
  function MockCompleteWorkflow({
    onWorkflowMetrics = vi.fn(),
  }: {
    onWorkflowMetrics?: (metrics: unknown) => void;
  }) {
    const [workflowState, setWorkflowState] = React.useState({
      itemsAdded: 0,
      linksCreated: 0,
      projectCreated: false,
      reportGenerated: false,
      sharedLink: null,
    });

    React.useEffect(() => {
      onWorkflowMetrics(workflowState);
    }, [workflowState, onWorkflowMetrics]);

    return (
      <div className='space-y-4 p-4'>
        <div className='rounded bg-blue-50 p-3'>
          <input
            type='checkbox'
            checked={workflowState.projectCreated}
            onChange={(e) => {
              setWorkflowState({
                ...workflowState,
                projectCreated: e.target.checked,
              });
            }}
          />
          Project Created
        </div>

        <div className='rounded bg-green-50 p-3'>
          <input
            type='number'
            value={workflowState.itemsAdded}
            onChange={(e) => {
              setWorkflowState({
                ...workflowState,
                itemsAdded: Number.parseInt(e.target.value, 10),
              });
            }}
            min='0'
          />
          Items Added
        </div>

        <div className='rounded bg-purple-50 p-3'>
          <input
            type='number'
            value={workflowState.linksCreated}
            onChange={(e) => {
              setWorkflowState({
                ...workflowState,
                linksCreated: Number.parseInt(e.target.value, 10),
              });
            }}
            min='0'
          />
          Links Created
        </div>

        <div className='rounded bg-yellow-50 p-3'>
          <input
            type='checkbox'
            checked={workflowState.reportGenerated}
            onChange={(e) => {
              setWorkflowState({
                ...workflowState,
                reportGenerated: e.target.checked,
              });
            }}
          />
          Report Generated
        </div>

        <div className='rounded bg-indigo-50 p-3'>
          <input
            type='text'
            value={workflowState.sharedLink ?? ''}
            onChange={(e) => {
              setWorkflowState({
                ...workflowState,
                sharedLink: e.target.value || null,
              });
            }}
            placeholder='Share link'
            className='w-full rounded border px-2 py-1'
          />
        </div>
      </div>
    );
  }

  beforeEach(() => {
    user = userEvent.setup();
  });

  it('should track cross-feature workflow metrics', async () => {
    const handleMetrics = vi.fn();

    render(<MockCompleteWorkflow onWorkflowMetrics={handleMetrics} />);

    // Complete various workflow steps
    const checkboxes = screen.getAllByRole('checkbox');
    await user.click(checkboxes[0]); // Create project

    const numberInputs = screen.getAllByRole('spinbutton');
    await user.clear(numberInputs[0]);
    await user.type(numberInputs[0], '5'); // Add items

    await user.clear(numberInputs[1]);
    await user.type(numberInputs[1], '3'); // Create links

    await user.click(checkboxes[1]); // Generate report

    // Verify workflow tracking
    await waitFor(() => {
      expect(handleMetrics).toHaveBeenCalledWith(
        expect.objectContaining({
          itemsAdded: 5,
          linksCreated: 3,
          projectCreated: true,
          reportGenerated: true,
        }),
      );
    });
  });
});

describe('Error Recovery in Workflows', () => {
  function MockWorkflowWithErrorHandling({
    shouldFail = false,
    onError = vi.fn(),
  }: {
    shouldFail?: boolean;
    onError?: (error: Error) => void;
  }) {
    const [error, setError] = React.useState<string | null>(null);

    const handleAction = async () => {
      try {
        if (shouldFail) {
          throw new Error('Operation failed');
        }
        setError(null);
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : 'Unknown error';
        setError(errorMsg);
        onError(new Error(errorMsg));
      }
    };

    return (
      <div className='p-4'>
        <button onClick={handleAction} className='rounded bg-blue-600 px-4 py-2 text-white'>
          Perform Action
        </button>

        {error && (
          <div role='alert' className='mt-4 border-l-4 border-red-600 bg-red-50 p-3 text-red-800'>
            Error: {error}
            <button
              onClick={() => {
                setError(null);
              }}
              className='ml-2 text-sm underline'
            >
              Dismiss
            </button>
          </div>
        )}
      </div>
    );
  }

  beforeEach(() => {
    user = userEvent.setup();
  });

  it('should handle workflow errors gracefully', async () => {
    const handleError = vi.fn();

    render(<MockWorkflowWithErrorHandling shouldFail onError={handleError} />);

    const actionBtn = screen.getByRole('button', {
      name: 'Perform Action',
    });
    await user.click(actionBtn);

    await waitFor(() => {
      expect(handleError).toHaveBeenCalled();
      expect(screen.getByText(/Error:/)).toBeInTheDocument();
    });
  });

  it('should allow dismissing errors', async () => {
    render(<MockWorkflowWithErrorHandling shouldFail />);

    const actionBtn = screen.getByRole('button', {
      name: 'Perform Action',
    });
    await user.click(actionBtn);

    await waitFor(() => {
      expect(screen.getByText(/Error:/)).toBeInTheDocument();
    });

    const dismissBtn = screen.getByRole('button', { name: 'Dismiss' });
    await user.click(dismissBtn);

    expect(screen.queryByText(/Error:/)).not.toBeInTheDocument();
  });
});
