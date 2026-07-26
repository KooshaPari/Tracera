import { fireEvent, render, screen } from '@testing-library/react';
import * as Vitest from 'vitest';

import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../components/DropdownMenu';

Vitest.describe('DropdownMenu component', () => {
  const openDropdown = () => {
    // Radix dropdown needs pointerDown then click to open
    const trigger = screen.getByText('Open Menu');
    fireEvent.pointerDown(trigger, { pointerType: 'mouse' });
    fireEvent.click(trigger);
  };

  const renderDropdown = () =>
    render(
      <DropdownMenu>
        <DropdownMenuTrigger>Open Menu</DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuLabel>Actions</DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem>Edit</DropdownMenuItem>
          <DropdownMenuItem>Delete</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>,
    );

  Vitest.it('renders the trigger button', () => {
    renderDropdown();
    Vitest.expect(screen.getByText('Open Menu')).toBeInTheDocument();
  });

  Vitest.it('trigger has aria-haspopup=menu', () => {
    renderDropdown();
    Vitest.expect(screen.getByText('Open Menu')).toHaveAttribute('aria-haspopup', 'menu');
  });

  Vitest.it('trigger starts closed', () => {
    renderDropdown();
    Vitest.expect(screen.getByText('Open Menu')).toHaveAttribute('data-state', 'closed');
  });

  Vitest.it('opens menu when trigger is activated', () => {
    renderDropdown();
    openDropdown();
    Vitest.expect(screen.getByText('Edit')).toBeInTheDocument();
    Vitest.expect(screen.getByText('Delete')).toBeInTheDocument();
  });

  Vitest.it('renders menu label when open', () => {
    renderDropdown();
    openDropdown();
    Vitest.expect(screen.getByText('Actions')).toBeInTheDocument();
  });

  Vitest.it('renders menu separator when open', () => {
    renderDropdown();
    openDropdown();
    const separators = document.querySelectorAll("[role='separator']");
    Vitest.expect(separators.length).toBeGreaterThan(0);
  });
});

Vitest.describe('DropdownMenuItem component', () => {
  Vitest.it('renders with inset padding when inset is true', () => {
    render(
      <DropdownMenu>
        <DropdownMenuTrigger>Menu</DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuItem inset>Inset Item</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>,
    );
    const trigger = screen.getByText('Menu');
    fireEvent.pointerDown(trigger, { pointerType: 'mouse' });
    fireEvent.click(trigger);
    Vitest.expect(screen.getByText('Inset Item').className).toContain('pl-8');
  });
});

Vitest.describe('DropdownMenuCheckboxItem component', () => {
  Vitest.it('renders checkbox item with default checked=false', () => {
    render(
      <DropdownMenu>
        <DropdownMenuTrigger>Menu</DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuCheckboxItem>Check me</DropdownMenuCheckboxItem>
        </DropdownMenuContent>
      </DropdownMenu>,
    );
    const trigger = screen.getByText('Menu');
    fireEvent.pointerDown(trigger, { pointerType: 'mouse' });
    fireEvent.click(trigger);
    Vitest.expect(screen.getByText('Check me')).toBeInTheDocument();
  });

  Vitest.it('renders checkbox item with checked=true', () => {
    render(
      <DropdownMenu>
        <DropdownMenuTrigger>Menu</DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuCheckboxItem checked>Checked</DropdownMenuCheckboxItem>
        </DropdownMenuContent>
      </DropdownMenu>,
    );
    const trigger = screen.getByText('Menu');
    fireEvent.pointerDown(trigger, { pointerType: 'mouse' });
    fireEvent.click(trigger);
    Vitest.expect(screen.getByText('Checked')).toBeInTheDocument();
  });
});

Vitest.describe('DropdownMenuLabel component', () => {
  Vitest.it('renders with inset padding when inset is true', () => {
    render(
      <DropdownMenu>
        <DropdownMenuTrigger>Menu</DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuLabel inset>Inset Label</DropdownMenuLabel>
        </DropdownMenuContent>
      </DropdownMenu>,
    );
    const trigger = screen.getByText('Menu');
    fireEvent.pointerDown(trigger, { pointerType: 'mouse' });
    fireEvent.click(trigger);
    Vitest.expect(screen.getByText('Inset Label').className).toContain('pl-8');
  });
});
