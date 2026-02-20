import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../components/Collapsible';

describe('Collapsible', () => {
  it('renders children', () => {
    render(
      <Collapsible>
        <CollapsibleTrigger>Toggle</CollapsibleTrigger>
        <CollapsibleContent>Hidden content</CollapsibleContent>
      </Collapsible>,
    );
    expect(screen.getByText('Toggle')).toBeInTheDocument();
  });

  it('hides content when closed (default)', () => {
    render(
      <Collapsible>
        <CollapsibleTrigger>Toggle</CollapsibleTrigger>
        <CollapsibleContent>Hidden content</CollapsibleContent>
      </Collapsible>,
    );
    // Content should not be in the document when closed
    expect(screen.queryByText('Hidden content')).not.toBeInTheDocument();
  });

  it('shows content when open is true', () => {
    render(
      <Collapsible open>
        <CollapsibleTrigger>Toggle</CollapsibleTrigger>
        <CollapsibleContent>Visible content</CollapsibleContent>
      </Collapsible>,
    );
    expect(screen.getByText('Visible content')).toBeInTheDocument();
  });

  it('calls onOpenChange when trigger is clicked', () => {
    const handleChange = vi.fn();
    render(
      <Collapsible onOpenChange={handleChange}>
        <CollapsibleTrigger>Toggle</CollapsibleTrigger>
        <CollapsibleContent>Content</CollapsibleContent>
      </Collapsible>,
    );
    fireEvent.click(screen.getByRole('button', { name: /toggle/i }));
    expect(handleChange).toHaveBeenCalledWith(true);
  });

  it('calls onOpenChange with false when open collapsible is toggled', () => {
    const handleChange = vi.fn();
    render(
      <Collapsible open onOpenChange={handleChange}>
        <CollapsibleTrigger>Toggle</CollapsibleTrigger>
        <CollapsibleContent>Content</CollapsibleContent>
      </Collapsible>,
    );
    fireEvent.click(screen.getByRole('button', { name: /toggle/i }));
    expect(handleChange).toHaveBeenCalledWith(false);
  });
});

describe('CollapsibleTrigger', () => {
  it('renders as a button', () => {
    render(
      <Collapsible>
        <CollapsibleTrigger>Click me</CollapsibleTrigger>
      </Collapsible>,
    );
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('has type=button attribute', () => {
    render(
      <Collapsible>
        <CollapsibleTrigger>Click me</CollapsibleTrigger>
      </Collapsible>,
    );
    expect(screen.getByRole('button')).toHaveAttribute('type', 'button');
  });
});

describe('CollapsibleContent', () => {
  it('applies opacity-0 and max-h-0 classes when closed', () => {
    const { container } = render(
      <Collapsible>
        <CollapsibleContent>Content</CollapsibleContent>
      </Collapsible>,
    );
    const content = container.querySelector("[class*='opacity-0']");
    expect(content).toBeInTheDocument();
  });

  it('applies opacity-100 class when open', () => {
    const { container } = render(
      <Collapsible open>
        <CollapsibleContent>Content</CollapsibleContent>
      </Collapsible>,
    );
    const content = container.querySelector("[class*='opacity-100']");
    expect(content).toBeInTheDocument();
  });
});
