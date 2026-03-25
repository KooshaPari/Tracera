import { fireEvent, render, screen } from '@testing-library/react';
import * as Vitest from 'vitest';

import { Popover, PopoverContent, PopoverTrigger } from '../components/Popover';

Vitest.describe('Popover component', () => {
  Vitest.it('renders the trigger', () => {
    render(
      <Popover>
        <PopoverTrigger>Open Popover</PopoverTrigger>
        <PopoverContent>Popover body</PopoverContent>
      </Popover>,
    );
    Vitest.expect(screen.getByText('Open Popover')).toBeInTheDocument();
  });

  Vitest.it('opens popover when trigger is clicked', () => {
    render(
      <Popover>
        <PopoverTrigger>Open</PopoverTrigger>
        <PopoverContent>Popover content here</PopoverContent>
      </Popover>,
    );
    fireEvent.click(screen.getByText('Open'));
    Vitest.expect(screen.getByText('Popover content here')).toBeInTheDocument();
  });

  Vitest.it('renders popover content when open', () => {
    render(
      <Popover open>
        <PopoverTrigger>Trigger</PopoverTrigger>
        <PopoverContent>Always visible</PopoverContent>
      </Popover>,
    );
    Vitest.expect(screen.getByText('Always visible')).toBeInTheDocument();
  });

  Vitest.it('applies custom className to PopoverContent', () => {
    render(
      <Popover open>
        <PopoverTrigger>Trigger</PopoverTrigger>
        <PopoverContent className='custom-popover'>Content</PopoverContent>
      </Popover>,
    );
    Vitest.expect(screen.getByText('Content').className).toContain('custom-popover');
  });
});
