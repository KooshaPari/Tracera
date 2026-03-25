import { fireEvent, render, screen } from '@testing-library/react';
import * as Vitest from 'vitest';

import {
  ContextMenu,
  ContextMenuCheckboxItem,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuLabel,
  ContextMenuRadioGroup,
  ContextMenuRadioItem,
  ContextMenuSeparator,
  ContextMenuShortcut,
  ContextMenuSub,
  ContextMenuSubContent,
  ContextMenuSubTrigger,
  ContextMenuTrigger,
} from '../components/ContextMenu';

const openContextMenu = () => {
  const trigger = screen.getByTestId('ctx-trigger');
  // Radix ContextMenu opens on contextmenu event (right-click)
  fireEvent.contextMenu(trigger);
};

Vitest.describe('ContextMenu component', () => {
  Vitest.it('renders the trigger', () => {
    render(
      <ContextMenu>
        <ContextMenuTrigger data-testid='ctx-trigger'>Right click me</ContextMenuTrigger>
        <ContextMenuContent>
          <ContextMenuItem>Action</ContextMenuItem>
        </ContextMenuContent>
      </ContextMenu>,
    );
    Vitest.expect(screen.getByText('Right click me')).toBeInTheDocument();
  });

  Vitest.it('opens context menu on right click and shows items', () => {
    render(
      <ContextMenu>
        <ContextMenuTrigger data-testid='ctx-trigger'>Right click</ContextMenuTrigger>
        <ContextMenuContent>
          <ContextMenuItem>Edit</ContextMenuItem>
          <ContextMenuItem>Delete</ContextMenuItem>
        </ContextMenuContent>
      </ContextMenu>,
    );
    openContextMenu();
    Vitest.expect(screen.getByText('Edit')).toBeInTheDocument();
    Vitest.expect(screen.getByText('Delete')).toBeInTheDocument();
  });

  Vitest.it('renders menu item without inset', () => {
    render(
      <ContextMenu>
        <ContextMenuTrigger data-testid='ctx-trigger'>Right click</ContextMenuTrigger>
        <ContextMenuContent>
          <ContextMenuItem>No Inset</ContextMenuItem>
        </ContextMenuContent>
      </ContextMenu>,
    );
    openContextMenu();
    Vitest.expect(screen.getByText('No Inset').className).not.toContain('pl-8');
  });

  Vitest.it('renders menu item with inset', () => {
    render(
      <ContextMenu>
        <ContextMenuTrigger data-testid='ctx-trigger'>Right click</ContextMenuTrigger>
        <ContextMenuContent>
          <ContextMenuItem inset>Inset Item</ContextMenuItem>
        </ContextMenuContent>
      </ContextMenu>,
    );
    openContextMenu();
    Vitest.expect(screen.getByText('Inset Item').className).toContain('pl-8');
  });

  Vitest.it('renders label without inset', () => {
    render(
      <ContextMenu>
        <ContextMenuTrigger data-testid='ctx-trigger'>Right click</ContextMenuTrigger>
        <ContextMenuContent>
          <ContextMenuLabel>Label</ContextMenuLabel>
        </ContextMenuContent>
      </ContextMenu>,
    );
    openContextMenu();
    Vitest.expect(screen.getByText('Label').className).not.toContain('pl-8');
  });

  Vitest.it('renders label with inset', () => {
    render(
      <ContextMenu>
        <ContextMenuTrigger data-testid='ctx-trigger'>Right click</ContextMenuTrigger>
        <ContextMenuContent>
          <ContextMenuLabel inset>Inset Label</ContextMenuLabel>
        </ContextMenuContent>
      </ContextMenu>,
    );
    openContextMenu();
    Vitest.expect(screen.getByText('Inset Label').className).toContain('pl-8');
  });

  Vitest.it('renders separator', () => {
    render(
      <ContextMenu>
        <ContextMenuTrigger data-testid='ctx-trigger'>Right click</ContextMenuTrigger>
        <ContextMenuContent>
          <ContextMenuItem>A</ContextMenuItem>
          <ContextMenuSeparator />
          <ContextMenuItem>B</ContextMenuItem>
        </ContextMenuContent>
      </ContextMenu>,
    );
    openContextMenu();
    const seps = document.querySelectorAll("[role='separator']");
    Vitest.expect(seps.length).toBeGreaterThan(0);
  });

  Vitest.it('renders checkbox item with checked=undefined', () => {
    render(
      <ContextMenu>
        <ContextMenuTrigger data-testid='ctx-trigger'>Right click</ContextMenuTrigger>
        <ContextMenuContent>
          <ContextMenuCheckboxItem>Unchecked</ContextMenuCheckboxItem>
        </ContextMenuContent>
      </ContextMenu>,
    );
    openContextMenu();
    Vitest.expect(screen.getByText('Unchecked')).toBeInTheDocument();
  });

  Vitest.it('renders checkbox item with checked=true', () => {
    render(
      <ContextMenu>
        <ContextMenuTrigger data-testid='ctx-trigger'>Right click</ContextMenuTrigger>
        <ContextMenuContent>
          <ContextMenuCheckboxItem checked>Checked</ContextMenuCheckboxItem>
        </ContextMenuContent>
      </ContextMenu>,
    );
    openContextMenu();
    Vitest.expect(screen.getByText('Checked')).toBeInTheDocument();
  });

  Vitest.it('renders radio item inside radio group', () => {
    render(
      <ContextMenu>
        <ContextMenuTrigger data-testid='ctx-trigger'>Right click</ContextMenuTrigger>
        <ContextMenuContent>
          <ContextMenuRadioGroup value='a'>
            <ContextMenuRadioItem value='a'>Option A</ContextMenuRadioItem>
            <ContextMenuRadioItem value='b'>Option B</ContextMenuRadioItem>
          </ContextMenuRadioGroup>
        </ContextMenuContent>
      </ContextMenu>,
    );
    openContextMenu();
    Vitest.expect(screen.getByText('Option A')).toBeInTheDocument();
    Vitest.expect(screen.getByText('Option B')).toBeInTheDocument();
  });

  Vitest.it('renders sub trigger without inset', () => {
    render(
      <ContextMenu>
        <ContextMenuTrigger data-testid='ctx-trigger'>Right click</ContextMenuTrigger>
        <ContextMenuContent>
          <ContextMenuSub>
            <ContextMenuSubTrigger>Sub Menu</ContextMenuSubTrigger>
            <ContextMenuSubContent>
              <ContextMenuItem>Sub Item</ContextMenuItem>
            </ContextMenuSubContent>
          </ContextMenuSub>
        </ContextMenuContent>
      </ContextMenu>,
    );
    openContextMenu();
    Vitest.expect(screen.getByText('Sub Menu').className).not.toContain('pl-8');
  });

  Vitest.it('renders sub trigger with inset', () => {
    render(
      <ContextMenu>
        <ContextMenuTrigger data-testid='ctx-trigger'>Right click</ContextMenuTrigger>
        <ContextMenuContent>
          <ContextMenuSub>
            <ContextMenuSubTrigger inset>Inset Sub</ContextMenuSubTrigger>
            <ContextMenuSubContent>
              <ContextMenuItem>Sub Item</ContextMenuItem>
            </ContextMenuSubContent>
          </ContextMenuSub>
        </ContextMenuContent>
      </ContextMenu>,
    );
    openContextMenu();
    Vitest.expect(screen.getByText('Inset Sub').className).toContain('pl-8');
  });

  Vitest.it('renders content with custom className', () => {
    render(
      <ContextMenu>
        <ContextMenuTrigger data-testid='ctx-trigger'>Right click</ContextMenuTrigger>
        <ContextMenuContent className='custom-ctx-content'>
          <ContextMenuItem>Item</ContextMenuItem>
        </ContextMenuContent>
      </ContextMenu>,
    );
    openContextMenu();
    Vitest.expect(screen.getByText('Item').closest("[role='menu']")?.className).toContain(
      'custom-ctx-content',
    );
  });
});

Vitest.describe('ContextMenuShortcut component', () => {
  Vitest.it('renders shortcut text', () => {
    render(<ContextMenuShortcut>Ctrl+C</ContextMenuShortcut>);
    Vitest.expect(screen.getByText('Ctrl+C')).toBeInTheDocument();
  });

  Vitest.it('applies custom className', () => {
    render(<ContextMenuShortcut className='custom-shortcut'>Ctrl+V</ContextMenuShortcut>);
    Vitest.expect(screen.getByText('Ctrl+V').className).toContain('custom-shortcut');
  });

  Vitest.it('has default styling classes', () => {
    render(<ContextMenuShortcut>Ctrl+X</ContextMenuShortcut>);
    const shortcut = screen.getByText('Ctrl+X');
    Vitest.expect(shortcut.className).toContain('ml-auto');
    Vitest.expect(shortcut.className).toContain('text-xs');
  });
});
