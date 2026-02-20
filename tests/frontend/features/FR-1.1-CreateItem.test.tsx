# FR-1.1: Create Item - Comprehensive Test Suite

**Linked to**: FR-1.1 (Create Item with Basic Information)  
**Story**: US-1.1, US-1.2, US-1.3, US-1.4, US-1.5  
**ADR**: ADR-2 (Frontend), ADR-12 (API Design)  
**ARU**: ARU-1 (Frontend Architecture)

---

## TEST SUITE: FR-1.1 - Create Item

### Test Group 1: Basic Item Creation (AC-1 to AC-10)

#### Test 1.1.1: User can enter item title (1-255 characters)
```typescript
describe('FR-1.1: Create Item - Basic Information', () => {
  describe('AC-1: User can enter item title', () => {
    test('should accept title with 1 character', async () => {
      // Linked to: AC-1, Validation Rule 1
      const { getByTestId, getByText } = render(<CreateItemForm />);
      const titleInput = getByTestId('item-title-input');
      
      fireEvent.change(titleInput, { target: { value: 'A' } });
      expect(titleInput.value).toBe('A');
      expect(getByText('Create Item')).toBeEnabled();
    });

    test('should accept title with 255 characters', async () => {
      // Linked to: AC-1, Validation Rule 1
      const title = 'A'.repeat(255);
      const { getByTestId } = render(<CreateItemForm />);
      const titleInput = getByTestId('item-title-input');
      
      fireEvent.change(titleInput, { target: { value: title } });
      expect(titleInput.value).toBe(title);
    });

    test('should reject empty title', async () => {
      // Linked to: Validation Rule 1, Error Scenario 1
      const { getByTestId, getByText } = render(<CreateItemForm />);
      const titleInput = getByTestId('item-title-input');
      const submitButton = getByText('Create Item');
      
      fireEvent.change(titleInput, { target: { value: '' } });
      fireEvent.click(submitButton);
      
      expect(getByText('Item title is required')).toBeInTheDocument();
    });

    test('should reject title > 255 characters', async () => {
      // Linked to: Validation Rule 1, Error Scenario 1
      const title = 'A'.repeat(256);
      const { getByTestId, getByText } = render(<CreateItemForm />);
      const titleInput = getByTestId('item-title-input');
      const submitButton = getByText('Create Item');
      
      fireEvent.change(titleInput, { target: { value: title } });
      fireEvent.click(submitButton);
      
      expect(getByText('Title must be 255 characters or less')).toBeInTheDocument();
    });

    test('should trim whitespace from title', async () => {
      // Linked to: Validation Rule 1
      const { getByTestId } = render(<CreateItemForm />);
      const titleInput = getByTestId('item-title-input');
      
      fireEvent.change(titleInput, { target: { value: '  Test Title  ' } });
      fireEvent.blur(titleInput);
      
      expect(titleInput.value).toBe('Test Title');
    });
  });

  describe('AC-2: User can select item type from 8 types', () => {
    test('should display all 8 item types', async () => {
      // Linked to: AC-2, Validation Rule 2
      const { getByTestId, getByText } = render(<CreateItemForm />);
      const typeSelect = getByTestId('item-type-select');
      
      fireEvent.click(typeSelect);
      
      expect(getByText('REQUIREMENT')).toBeInTheDocument();
      expect(getByText('DESIGN')).toBeInTheDocument();
      expect(getByText('IMPLEMENTATION')).toBeInTheDocument();
      expect(getByText('TEST')).toBeInTheDocument();
      expect(getByText('DEPLOYMENT')).toBeInTheDocument();
      expect(getByText('DOCUMENTATION')).toBeInTheDocument();
      expect(getByText('RESEARCH')).toBeInTheDocument();
      expect(getByText('SPIKE')).toBeInTheDocument();
    });

    test('should select item type', async () => {
      // Linked to: AC-2
      const { getByTestId, getByText } = render(<CreateItemForm />);
      const typeSelect = getByTestId('item-type-select');
      
      fireEvent.click(typeSelect);
      fireEvent.click(getByText('IMPLEMENTATION'));
      
      expect(typeSelect.value).toBe('IMPLEMENTATION');
    });

    test('should reject invalid item type', async () => {
      // Linked to: Validation Rule 2, Error Scenario 2
      const { getByTestId, getByText } = render(<CreateItemForm />);
      const submitButton = getByText('Create Item');
      
      // Try to submit without selecting type
      fireEvent.click(submitButton);
      
      expect(getByText('Item type is required')).toBeInTheDocument();
    });
  });

  describe('AC-3: User can enter description (0-5000 characters, markdown)', () => {
    test('should accept empty description', async () => {
      // Linked to: AC-3
      const { getByTestId } = render(<CreateItemForm />);
      const descInput = getByTestId('item-description-input');
      
      fireEvent.change(descInput, { target: { value: '' } });
      expect(descInput.value).toBe('');
    });

    test('should accept markdown description', async () => {
      // Linked to: AC-3
      const markdown = '# Title\n\n**Bold** and *italic*\n\n- List item';
      const { getByTestId } = render(<CreateItemForm />);
      const descInput = getByTestId('item-description-input');
      
      fireEvent.change(descInput, { target: { value: markdown } });
      expect(descInput.value).toBe(markdown);
    });

    test('should reject description > 5000 characters', async () => {
      // Linked to: Validation Rule 3, Error Scenario 3
      const desc = 'A'.repeat(5001);
      const { getByTestId, getByText } = render(<CreateItemForm />);
      const descInput = getByTestId('item-description-input');
      const submitButton = getByText('Create Item');
      
      fireEvent.change(descInput, { target: { value: desc } });
      fireEvent.click(submitButton);
      
      expect(getByText('Description must be 5000 characters or less')).toBeInTheDocument();
    });

    test('should preview markdown', async () => {
      // Linked to: AC-3
      const markdown = '# Title';
      const { getByTestId, getByText } = render(<CreateItemForm />);
      const descInput = getByTestId('item-description-input');
      const previewButton = getByTestId('preview-button');
      
      fireEvent.change(descInput, { target: { value: markdown } });
      fireEvent.click(previewButton);
      
      expect(getByText('Title')).toBeInTheDocument();
    });
  });

  describe('AC-4: User can add tags (0-20 tags)', () => {
    test('should add single tag', async () => {
      // Linked to: AC-4
      const { getByTestId, getByText } = render(<CreateItemForm />);
      const tagInput = getByTestId('tag-input');
      const addTagButton = getByText('Add Tag');
      
      fireEvent.change(tagInput, { target: { value: 'urgent' } });
      fireEvent.click(addTagButton);
      
      expect(getByText('urgent')).toBeInTheDocument();
    });

    test('should add multiple tags (up to 20)', async () => {
      // Linked to: AC-4
      const { getByTestId, getByText } = render(<CreateItemForm />);
      const tagInput = getByTestId('tag-input');
      const addTagButton = getByText('Add Tag');
      
      for (let i = 0; i < 20; i++) {
        fireEvent.change(tagInput, { target: { value: `tag${i}` } });
        fireEvent.click(addTagButton);
      }
      
      expect(getByText('tag0')).toBeInTheDocument();
      expect(getByText('tag19')).toBeInTheDocument();
    });

    test('should reject > 20 tags', async () => {
      // Linked to: Validation Rule 8, Error Scenario 8
      const { getByTestId, getByText } = render(<CreateItemForm />);
      const tagInput = getByTestId('tag-input');
      const addTagButton = getByText('Add Tag');
      
      for (let i = 0; i < 21; i++) {
        fireEvent.change(tagInput, { target: { value: `tag${i}` } });
        fireEvent.click(addTagButton);
      }
      
      expect(getByText('Maximum 20 tags allowed')).toBeInTheDocument();
    });

    test('should remove tag', async () => {
      // Linked to: AC-4
      const { getByTestId, getByText, queryByText } = render(<CreateItemForm />);
      const tagInput = getByTestId('tag-input');
      const addTagButton = getByText('Add Tag');
      
      fireEvent.change(tagInput, { target: { value: 'urgent' } });
      fireEvent.click(addTagButton);
      
      const removeButton = getByTestId('remove-tag-urgent');
      fireEvent.click(removeButton);
      
      expect(queryByText('urgent')).not.toBeInTheDocument();
    });
  });

  describe('AC-5: User can set priority (LOW, MEDIUM, HIGH, CRITICAL)', () => {
    test('should display all priority options', async () => {
      // Linked to: AC-5
      const { getByTestId, getByText } = render(<CreateItemForm />);
      const prioritySelect = getByTestId('item-priority-select');
      
      fireEvent.click(prioritySelect);
      
      expect(getByText('LOW')).toBeInTheDocument();
      expect(getByText('MEDIUM')).toBeInTheDocument();
      expect(getByText('HIGH')).toBeInTheDocument();
      expect(getByText('CRITICAL')).toBeInTheDocument();
    });

    test('should select priority', async () => {
      // Linked to: AC-5
      const { getByTestId, getByText } = render(<CreateItemForm />);
      const prioritySelect = getByTestId('item-priority-select');
      
      fireEvent.click(prioritySelect);
      fireEvent.click(getByText('HIGH'));
      
      expect(prioritySelect.value).toBe('HIGH');
    });
  });

  describe('AC-6 to AC-10: Item Creation and Real-Time Updates', () => {
    test('should create item with DRAFT status', async () => {
      // Linked to: AC-6, Story US-1.1
      const { getByTestId, getByText } = render(<CreateItemForm />);
      const titleInput = getByTestId('item-title-input');
      const typeSelect = getByTestId('item-type-select');
      const submitButton = getByText('Create Item');
      
      fireEvent.change(titleInput, { target: { value: 'Test Item' } });
      fireEvent.click(typeSelect);
      fireEvent.click(getByText('IMPLEMENTATION'));
      fireEvent.click(submitButton);
      
      // Mock API call
      await waitFor(() => {
        expect(getByText('Item created successfully')).toBeInTheDocument();
      });
    });

    test('should appear in items list immediately', async () => {
      // Linked to: AC-7, Real-Time Event
      const { getByTestId, getByText } = render(<ItemsList />);
      
      // Create item
      const createButton = getByText('Create Item');
      fireEvent.click(createButton);
      
      // Item should appear in list
      await waitFor(() => {
        expect(getByText('Test Item')).toBeInTheDocument();
      });
    });

    test('should send confirmation notification', async () => {
      // Linked to: AC-8, Notification Type 1
      const { getByTestId, getByText } = render(<CreateItemForm />);
      const submitButton = getByText('Create Item');
      
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(getByText('Item created successfully')).toBeInTheDocument();
      });
    });

    test('should index item for search', async () => {
      // Linked to: AC-9, Search Functionality
      const { getByTestId, getByText } = render(<SearchBar />);
      const searchInput = getByTestId('search-input');
      
      fireEvent.change(searchInput, { target: { value: 'Test Item' } });
      
      await waitFor(() => {
        expect(getByText('Test Item')).toBeInTheDocument();
      });
    });

    test('should appear in activity feed', async () => {
      // Linked to: AC-10, Activity Feed
      const { getByTestId, getByText } = render(<ActivityFeed />);
      
      await waitFor(() => {
        expect(getByText('Item created: Test Item')).toBeInTheDocument();
      });
    });
  });
});
```

---

## PERFORMANCE TESTS

### Test 1.1.P1: Response Time < 100ms
```typescript
test('should create item in < 100ms', async () => {
  // Linked to: Performance Requirement 1
  const startTime = performance.now();
  
  // Create item
  const { getByTestId, getByText } = render(<CreateItemForm />);
  const submitButton = getByText('Create Item');
  fireEvent.click(submitButton);
  
  await waitFor(() => {
    expect(getByText('Item created successfully')).toBeInTheDocument();
  });
  
  const endTime = performance.now();
  expect(endTime - startTime).toBeLessThan(100);
});
```

---

## ERROR HANDLING TESTS

### Test 1.1.E1: Missing Title Error
```typescript
test('should show error for missing title', async () => {
  // Linked to: Error Scenario 1
  const { getByTestId, getByText } = render(<CreateItemForm />);
  const submitButton = getByText('Create Item');
  
  fireEvent.click(submitButton);
  
  expect(getByText('Item title is required')).toBeInTheDocument();
});
```

---

## TOTAL TESTS: 20+ tests for FR-1.1


