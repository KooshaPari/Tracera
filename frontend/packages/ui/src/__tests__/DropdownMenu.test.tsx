import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../components/DropdownMenu';

describe('DropdownMenu component', () => {
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

  it('renders the trigger button', () => {
    renderDropdown();
    expect(screen.getByText('Open Menu')).toBeInTheDocument();
  });

  it('trigger has aria-haspopup=menu', () => {
    renderDropdown();
    expect(screen.getByText('Open Menu')).toHaveAttribute('aria-haspopup', 'menu');
  });

  it('trigger starts closed', () => {
    renderDropdown();
    expect(screen.getByText('Open Menu')).toHaveAttribute('data-state', 'closed');
  });

  it('opens menu when trigger is activated', () => {
    renderDropdown();
    openDropdown();
    expect(screen.getByText('Edit')).toBeInTheDocument();
    expect(screen.getByText('Delete')).toBeInTheDocument();
  });

  it('renders menu label when open', () => {
    renderDropdown();
    openDropdown();
    expect(screen.getByText('Actions')).toBeInTheDocument();
  });

  it('renders menu separator when open', () => {
    renderDropdown();
    openDropdown();
    const separators = document.querySelectorAll("[role='separator']");
    expect(separators.length).toBeGreaterThan(0);
  });
});

describe('DropdownMenuItem component', () => {
  it('renders with inset padding when inset is true', () => {
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
    expect(screen.getByText('Inset Item').className).toContain('pl-8');
  });
});

describe('DropdownMenuCheckboxItem component', () => {
  it('renders checkbox item with default checked=false', () => {
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
    expect(screen.getByText('Check me')).toBeInTheDocument();
  });

  it('renders checkbox item with checked=true', () => {
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
    expect(screen.getByText('Checked')).toBeInTheDocument();
  });
});

describe('DropdownMenuLabel component', () => {
  it('renders with inset padding when inset is true', () => {
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
    expect(screen.getByText('Inset Label').className).toContain('pl-8');
  });
});
