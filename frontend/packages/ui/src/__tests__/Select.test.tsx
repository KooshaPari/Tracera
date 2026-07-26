import { render, screen } from '@testing-library/react';
import * as Vitest from 'vitest';

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/Select';

Vitest.describe('Select component', () => {
  Vitest.it('renders the trigger with combobox role', () => {
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
    Vitest.expect(screen.getByRole('combobox')).toBeInTheDocument();
  });

  Vitest.it('renders with placeholder when no value selected', () => {
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
    Vitest.expect(screen.getByText('Choose...')).toBeInTheDocument();
  });

  Vitest.it('trigger has aria-expanded attribute', () => {
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
    Vitest.expect(screen.getByRole('combobox')).toHaveAttribute('aria-expanded', 'false');
  });
});

Vitest.describe('SelectTrigger component', () => {
  Vitest.it('applies custom className', () => {
    render(
      <Select>
        <SelectTrigger className='custom-trigger'>
          <SelectValue />
        </SelectTrigger>
      </Select>,
    );
    Vitest.expect(screen.getByRole('combobox').className).toContain('custom-trigger');
  });

  Vitest.it('can be disabled', () => {
    render(
      <Select disabled>
        <SelectTrigger>
          <SelectValue />
        </SelectTrigger>
      </Select>,
    );
    Vitest.expect(screen.getByRole('combobox')).toBeDisabled();
  });

  Vitest.it('has data-state=closed by default', () => {
    render(
      <Select>
        <SelectTrigger>
          <SelectValue placeholder='Pick' />
        </SelectTrigger>
      </Select>,
    );
    Vitest.expect(screen.getByRole('combobox')).toHaveAttribute('data-state', 'closed');
  });

  Vitest.it('passes through additional props', () => {
    render(
      <Select>
        <SelectTrigger data-testid='select-trigger'>
          <SelectValue />
        </SelectTrigger>
      </Select>,
    );
    Vitest.expect(screen.getByTestId('select-trigger')).toBeInTheDocument();
  });
});
