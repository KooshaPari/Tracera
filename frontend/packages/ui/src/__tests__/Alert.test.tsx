import { render, screen } from '@testing-library/react';
import { createRef } from 'react';
import { describe, expect, it } from 'vitest';

import { Alert, AlertDescription, AlertTitle } from '../components/Alert';

describe('Alert component', () => {
  it('renders with role=alert', () => {
    render(<Alert>Alert content</Alert>);
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  it('renders children', () => {
    render(<Alert>Warning message</Alert>);
    expect(screen.getByText('Warning message')).toBeInTheDocument();
  });

  it('applies default variant', () => {
    render(<Alert>Default</Alert>);
    const alert = screen.getByRole('alert');
    expect(alert.className).toContain('bg-background');
  });

  it('applies destructive variant', () => {
    render(<Alert variant='destructive'>Error</Alert>);
    const alert = screen.getByRole('alert');
    expect(alert.className).toContain('border-destructive');
  });

  it('applies success variant', () => {
    render(<Alert variant='success'>Success</Alert>);
    const alert = screen.getByRole('alert');
    expect(alert.className).toContain('border-green-500');
  });

  it('applies warning variant', () => {
    render(<Alert variant='warning'>Warning</Alert>);
    const alert = screen.getByRole('alert');
    expect(alert.className).toContain('border-yellow-500');
  });

  it('forwards ref', () => {
    const ref = createRef<HTMLDivElement>();
    render(<Alert ref={ref}>Ref test</Alert>);
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  it('merges custom className', () => {
    render(<Alert className='my-alert'>Custom</Alert>);
    const alert = screen.getByRole('alert');
    expect(alert.className).toContain('my-alert');
  });
});

describe('AlertTitle component', () => {
  it('renders as h5 element', () => {
    render(<AlertTitle>Title</AlertTitle>);
    const title = screen.getByText('Title');
    expect(title.tagName).toBe('H5');
  });

  it('forwards ref', () => {
    const ref = createRef<HTMLParagraphElement>();
    render(<AlertTitle ref={ref}>Ref title</AlertTitle>);
    expect(ref.current).toBeInstanceOf(HTMLHeadingElement);
  });

  it('applies custom className', () => {
    render(<AlertTitle className='custom-title'>Title</AlertTitle>);
    expect(screen.getByText('Title').className).toContain('custom-title');
  });
});

describe('AlertDescription component', () => {
  it('renders children', () => {
    render(<AlertDescription>Description text</AlertDescription>);
    expect(screen.getByText('Description text')).toBeInTheDocument();
  });

  it('renders as div element', () => {
    render(<AlertDescription>Desc</AlertDescription>);
    expect(screen.getByText('Desc').tagName).toBe('DIV');
  });

  it('forwards ref', () => {
    const ref = createRef<HTMLParagraphElement>();
    render(<AlertDescription ref={ref}>Ref desc</AlertDescription>);
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });
});

describe('Alert composition', () => {
  it('renders title and description together', () => {
    render(
      <Alert>
        <AlertTitle>Error occurred</AlertTitle>
        <AlertDescription>Please try again later.</AlertDescription>
      </Alert>,
    );
    expect(screen.getByText('Error occurred')).toBeInTheDocument();
    expect(screen.getByText('Please try again later.')).toBeInTheDocument();
  });
});
