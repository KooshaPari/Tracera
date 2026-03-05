import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { Popover, PopoverContent, PopoverTrigger } from '../components/Popover';

describe('Popover component', () => {
  it('renders the trigger', () => {
    render(
      <Popover>
        <PopoverTrigger>Open Popover</PopoverTrigger>
        <PopoverContent>Popover body</PopoverContent>
      </Popover>,
    );
    expect(screen.getByText('Open Popover')).toBeInTheDocument();
  });

  it('opens popover when trigger is clicked', () => {
    render(
      <Popover>
        <PopoverTrigger>Open</PopoverTrigger>
        <PopoverContent>Popover content here</PopoverContent>
      </Popover>,
    );
    fireEvent.click(screen.getByText('Open'));
    expect(screen.getByText('Popover content here')).toBeInTheDocument();
  });

  it('renders popover content when open', () => {
    render(
      <Popover open>
        <PopoverTrigger>Trigger</PopoverTrigger>
        <PopoverContent>Always visible</PopoverContent>
      </Popover>,
    );
    expect(screen.getByText('Always visible')).toBeInTheDocument();
  });

  it('applies custom className to PopoverContent', () => {
    render(
      <Popover open>
        <PopoverTrigger>Trigger</PopoverTrigger>
        <PopoverContent className='custom-popover'>Content</PopoverContent>
      </Popover>,
    );
    expect(screen.getByText('Content').className).toContain('custom-popover');
  });
});
