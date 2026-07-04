import { fireEvent, render, screen } from '@testing-library/react';
import * as Vitest from 'vitest';

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../components/Dialog';

Vitest.describe('Dialog component', () => {
  Vitest.it('renders the trigger button', () => {
    render(
      <Dialog>
        <DialogTrigger>Open Dialog</DialogTrigger>
        <DialogContent>
          <DialogTitle>Test</DialogTitle>
          <DialogDescription>Test description</DialogDescription>
        </DialogContent>
      </Dialog>,
    );
    Vitest.expect(screen.getByText('Open Dialog')).toBeInTheDocument();
  });

  Vitest.it('opens dialog when trigger is clicked', () => {
    render(
      <Dialog>
        <DialogTrigger>Open</DialogTrigger>
        <DialogContent>
          <DialogTitle>Dialog Title</DialogTitle>
          <DialogDescription>Dialog body content</DialogDescription>
        </DialogContent>
      </Dialog>,
    );
    fireEvent.click(screen.getByText('Open'));
    Vitest.expect(screen.getByText('Dialog Title')).toBeInTheDocument();
    Vitest.expect(screen.getByText('Dialog body content')).toBeInTheDocument();
  });

  Vitest.it('renders dialog content when open is true', () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogTitle>Always Open</DialogTitle>
          <DialogDescription>Visible content</DialogDescription>
        </DialogContent>
      </Dialog>,
    );
    Vitest.expect(screen.getByText('Always Open')).toBeInTheDocument();
  });

  Vitest.it('renders the close button inside DialogContent', () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogTitle>With Close</DialogTitle>
          <DialogDescription>Content</DialogDescription>
        </DialogContent>
      </Dialog>,
    );
    const closeButton = screen.getByRole('button');
    Vitest.expect(closeButton).toBeInTheDocument();
  });

  Vitest.it('renders dialog with role=dialog', () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogTitle>Title</DialogTitle>
          <DialogDescription>Desc</DialogDescription>
        </DialogContent>
      </Dialog>,
    );
    Vitest.expect(screen.getByRole('dialog')).toBeInTheDocument();
  });
});

Vitest.describe('DialogHeader component', () => {
  Vitest.it('renders children', () => {
    render(<DialogHeader>Header content</DialogHeader>);
    Vitest.expect(screen.getByText('Header content')).toBeInTheDocument();
  });

  Vitest.it('applies custom className', () => {
    render(<DialogHeader className='custom-header'>Header</DialogHeader>);
    Vitest.expect(screen.getByText('Header').className).toContain('custom-header');
  });
});

Vitest.describe('DialogFooter component', () => {
  Vitest.it('renders children', () => {
    render(<DialogFooter>Footer content</DialogFooter>);
    Vitest.expect(screen.getByText('Footer content')).toBeInTheDocument();
  });

  Vitest.it('applies custom className', () => {
    render(<DialogFooter className='custom-footer'>Footer</DialogFooter>);
    Vitest.expect(screen.getByText('Footer').className).toContain('custom-footer');
  });
});

Vitest.describe('DialogTitle component', () => {
  Vitest.it('renders within an open dialog', () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogTitle>My Title</DialogTitle>
          <DialogDescription>Description</DialogDescription>
        </DialogContent>
      </Dialog>,
    );
    Vitest.expect(screen.getByText('My Title')).toBeInTheDocument();
  });
});

Vitest.describe('DialogDescription component', () => {
  Vitest.it('renders within an open dialog', () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogTitle>Title</DialogTitle>
          <DialogDescription>My Description</DialogDescription>
        </DialogContent>
      </Dialog>,
    );
    Vitest.expect(screen.getByText('My Description')).toBeInTheDocument();
  });
});
