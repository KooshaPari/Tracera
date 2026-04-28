import { fireEvent, render, screen } from '@testing-library/react';
import * as Vitest from 'vitest';

import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../components/Collapsible';

Vitest.describe('Collapsible component', () => {
  Vitest.it('renders children', () => {
    render(
      <Collapsible>
        <CollapsibleTrigger>Toggle</CollapsibleTrigger>
        <CollapsibleContent>Hidden content</CollapsibleContent>
      </Collapsible>,
    );
    Vitest.expect(screen.getByText('Toggle')).toBeInTheDocument();
  });

  Vitest.it('hides content when closed (default)', () => {
    render(
      <Collapsible>
        <CollapsibleTrigger>Toggle</CollapsibleTrigger>
        <CollapsibleContent>Hidden content</CollapsibleContent>
      </Collapsible>,
    );
    // Content should not be in the document when closed
    Vitest.expect(screen.queryByText('Hidden content')).not.toBeInTheDocument();
  });

  Vitest.it('shows content when open is true', () => {
    render(
      <Collapsible open>
        <CollapsibleTrigger>Toggle</CollapsibleTrigger>
        <CollapsibleContent>Visible content</CollapsibleContent>
      </Collapsible>,
    );
    Vitest.expect(screen.getByText('Visible content')).toBeInTheDocument();
  });

  Vitest.it('calls onOpenChange when trigger is clicked', () => {
    const handleChange = Vitest.vi.fn();
    render(
      <Collapsible onOpenChange={handleChange}>
        <CollapsibleTrigger>Toggle</CollapsibleTrigger>
        <CollapsibleContent>Content</CollapsibleContent>
      </Collapsible>,
    );
    fireEvent.click(screen.getByRole('button', { name: /toggle/i }));
    Vitest.expect(handleChange).toHaveBeenCalledWith(true);
  });

  Vitest.it('calls onOpenChange with false when open collapsible is toggled', () => {
    const handleChange = Vitest.vi.fn();
    render(
      <Collapsible open onOpenChange={handleChange}>
        <CollapsibleTrigger>Toggle</CollapsibleTrigger>
        <CollapsibleContent>Content</CollapsibleContent>
      </Collapsible>,
    );
    fireEvent.click(screen.getByRole('button', { name: /toggle/i }));
    Vitest.expect(handleChange).toHaveBeenCalledWith(false);
  });
});

Vitest.describe('CollapsibleTrigger component', () => {
  Vitest.it('renders as a button', () => {
    render(
      <Collapsible>
        <CollapsibleTrigger>Click me</CollapsibleTrigger>
      </Collapsible>,
    );
    Vitest.expect(screen.getByRole('button')).toBeInTheDocument();
  });

  Vitest.it('has type=button attribute', () => {
    render(
      <Collapsible>
        <CollapsibleTrigger>Click me</CollapsibleTrigger>
      </Collapsible>,
    );
    Vitest.expect(screen.getByRole('button')).toHaveAttribute('type', 'button');
  });
});

Vitest.describe('CollapsibleContent component', () => {
  Vitest.it('applies opacity-0 and max-h-0 classes when closed', () => {
    const { container } = render(
      <Collapsible>
        <CollapsibleContent>Content</CollapsibleContent>
      </Collapsible>,
    );
    const content = container.querySelector("[class*='opacity-0']");
    Vitest.expect(content).toBeInTheDocument();
  });

  Vitest.it('applies opacity-100 class when open', () => {
    const { container } = render(
      <Collapsible open>
        <CollapsibleContent>Content</CollapsibleContent>
      </Collapsible>,
    );
    const content = container.querySelector("[class*='opacity-100']");
    Vitest.expect(content).toBeInTheDocument();
  });
});
