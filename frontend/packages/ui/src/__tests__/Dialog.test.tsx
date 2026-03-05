import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../components/Dialog';

describe('Dialog component', () => {
  it('renders the trigger button', () => {
    render(
      <Dialog>
        <DialogTrigger>Open Dialog</DialogTrigger>
        <DialogContent>
          <DialogTitle>Test</DialogTitle>
          <DialogDescription>Test description</DialogDescription>
        </DialogContent>
      </Dialog>,
    );
    expect(screen.getByText('Open Dialog')).toBeInTheDocument();
  });

  it('opens dialog when trigger is clicked', () => {
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
    expect(screen.getByText('Dialog Title')).toBeInTheDocument();
    expect(screen.getByText('Dialog body content')).toBeInTheDocument();
  });

  it('renders dialog content when open is true', () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogTitle>Always Open</DialogTitle>
          <DialogDescription>Visible content</DialogDescription>
        </DialogContent>
      </Dialog>,
    );
    expect(screen.getByText('Always Open')).toBeInTheDocument();
  });

  it('renders the close button inside DialogContent', () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogTitle>With Close</DialogTitle>
          <DialogDescription>Content</DialogDescription>
        </DialogContent>
      </Dialog>,
    );
    const closeButton = screen.getByRole('button');
    expect(closeButton).toBeInTheDocument();
  });

  it('renders dialog with role=dialog', () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogTitle>Title</DialogTitle>
          <DialogDescription>Desc</DialogDescription>
        </DialogContent>
      </Dialog>,
    );
    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });
});

describe('DialogHeader component', () => {
  it('renders children', () => {
    render(<DialogHeader>Header content</DialogHeader>);
    expect(screen.getByText('Header content')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    render(<DialogHeader className='custom-header'>Header</DialogHeader>);
    expect(screen.getByText('Header').className).toContain('custom-header');
  });
});

describe('DialogFooter component', () => {
  it('renders children', () => {
    render(<DialogFooter>Footer content</DialogFooter>);
    expect(screen.getByText('Footer content')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    render(<DialogFooter className='custom-footer'>Footer</DialogFooter>);
    expect(screen.getByText('Footer').className).toContain('custom-footer');
  });
});

describe('DialogTitle component', () => {
  it('renders within an open dialog', () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogTitle>My Title</DialogTitle>
          <DialogDescription>Description</DialogDescription>
        </DialogContent>
      </Dialog>,
    );
    expect(screen.getByText('My Title')).toBeInTheDocument();
  });
});

describe('DialogDescription component', () => {
  it('renders within an open dialog', () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogTitle>Title</DialogTitle>
          <DialogDescription>My Description</DialogDescription>
        </DialogContent>
      </Dialog>,
    );
    expect(screen.getByText('My Description')).toBeInTheDocument();
  });
});
