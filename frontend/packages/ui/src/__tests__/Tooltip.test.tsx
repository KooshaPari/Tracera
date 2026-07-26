import { render, screen } from '@testing-library/react';
import * as Vitest from 'vitest';

import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../components/Tooltip';

Vitest.describe('Tooltip component', () => {
  Vitest.it('renders the trigger element', () => {
    render(
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger>Hover me</TooltipTrigger>
          <TooltipContent>Tooltip text</TooltipContent>
        </Tooltip>
      </TooltipProvider>,
    );
    Vitest.expect(screen.getByText('Hover me')).toBeInTheDocument();
  });

  Vitest.it('renders tooltip content when open', () => {
    render(
      <TooltipProvider>
        <Tooltip open>
          <TooltipTrigger>Trigger</TooltipTrigger>
          <TooltipContent>Tooltip content</TooltipContent>
        </Tooltip>
      </TooltipProvider>,
    );
    // Radix renders tooltip text in both the visible content and an sr-only span
    const matches = screen.getAllByText('Tooltip content');
    Vitest.expect(matches.length).toBeGreaterThanOrEqual(1);
  });

  Vitest.it('renders with custom className on TooltipContent', () => {
    render(
      <TooltipProvider>
        <Tooltip open>
          <TooltipTrigger>Trigger</TooltipTrigger>
          <TooltipContent className='custom-tooltip'>Custom Content</TooltipContent>
        </Tooltip>
      </TooltipProvider>,
    );
    // Radix duplicates text (visible + sr-only), find the one with our className
    const matches = screen.getAllByText('Custom Content');
    const withClass = matches.find((el) => el.className.includes('custom-tooltip'));
    Vitest.expect(withClass).toBeDefined();
  });

  Vitest.it('does not render tooltip content when closed', () => {
    render(
      <TooltipProvider>
        <Tooltip open={false}>
          <TooltipTrigger>Trigger</TooltipTrigger>
          <TooltipContent>Hidden</TooltipContent>
        </Tooltip>
      </TooltipProvider>,
    );
    Vitest.expect(screen.queryByText('Hidden')).not.toBeInTheDocument();
  });
});
