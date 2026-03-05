import { render, screen } from '@testing-library/react';
import { createRef } from 'react';
import { describe, expect, it } from 'vitest';

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/Select';

describe('Select component', () => {
  it('renders the trigger with combobox role', () => {
    render(
      <Select>
        <SelectTrigger>
          <SelectValue placeholder='Choose...' />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value='a'>A</SelectItem>
        </SelectContent>
      </Select>,
    );
    expect(screen.getByRole('combobox')).toBeInTheDocument();
  });

  it('renders with placeholder when no value selected', () => {
    render(
      <Select>
        <SelectTrigger>
          <SelectValue placeholder='Choose...' />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value='a'>A</SelectItem>
        </SelectContent>
      </Select>,
    );
    expect(screen.getByText('Choose...')).toBeInTheDocument();
  });

  it('trigger has aria-expanded attribute', () => {
    render(
      <Select>
        <SelectTrigger>
          <SelectValue placeholder='Pick' />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value='a'>A</SelectItem>
        </SelectContent>
      </Select>,
    );
    expect(screen.getByRole('combobox')).toHaveAttribute('aria-expanded', 'false');
  });
});

describe('SelectTrigger component', () => {
  it('applies custom className', () => {
    render(
      <Select>
        <SelectTrigger className='custom-trigger'>
          <SelectValue />
        </SelectTrigger>
      </Select>,
    );
    expect(screen.getByRole('combobox').className).toContain('custom-trigger');
  });

  it('can be disabled', () => {
    render(
      <Select disabled>
        <SelectTrigger>
          <SelectValue />
        </SelectTrigger>
      </Select>,
    );
    expect(screen.getByRole('combobox')).toBeDisabled();
  });

  it('has data-state=closed by default', () => {
    render(
      <Select>
        <SelectTrigger>
          <SelectValue placeholder='Pick' />
        </SelectTrigger>
      </Select>,
    );
    expect(screen.getByRole('combobox')).toHaveAttribute('data-state', 'closed');
  });

  it('passes through additional props', () => {
    render(
      <Select>
        <SelectTrigger data-testid='select-trigger'>
          <SelectValue />
        </SelectTrigger>
      </Select>,
    );
    expect(screen.getByTestId('select-trigger')).toBeInTheDocument();
  });
});
