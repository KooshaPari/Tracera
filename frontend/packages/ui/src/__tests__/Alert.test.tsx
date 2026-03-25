import { render, screen } from '@testing-library/react';
import { createRef } from 'react';
import * as Vitest from 'vitest';

import { Alert, AlertDescription, AlertTitle } from '../components/Alert';

Vitest.describe('Alert component', () => {
  Vitest.it('renders with role=alert', () => {
    render(<Alert>Alert content</Alert>);
    Vitest.expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  Vitest.it('renders children', () => {
    render(<Alert>Warning message</Alert>);
    Vitest.expect(screen.getByText('Warning message')).toBeInTheDocument();
  });

  Vitest.it('applies default variant', () => {
    render(<Alert>Default</Alert>);
    const alert = screen.getByRole('alert');
    Vitest.expect(alert.className).toContain('bg-background');
  });

  Vitest.it('applies destructive variant', () => {
    render(<Alert variant='destructive'>Error</Alert>);
    const alert = screen.getByRole('alert');
    Vitest.expect(alert.className).toContain('border-destructive');
  });

  Vitest.it('applies success variant', () => {
    render(<Alert variant='success'>Success</Alert>);
    const alert = screen.getByRole('alert');
    Vitest.expect(alert.className).toContain('border-green-500');
  });

  Vitest.it('applies warning variant', () => {
    render(<Alert variant='warning'>Warning</Alert>);
    const alert = screen.getByRole('alert');
    Vitest.expect(alert.className).toContain('border-yellow-500');
  });

  Vitest.it('forwards ref', () => {
    const ref = createRef<HTMLDivElement>();
    render(<Alert ref={ref}>Ref test</Alert>);
    Vitest.expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  Vitest.it('merges custom className', () => {
    render(<Alert className='my-alert'>Custom</Alert>);
    const alert = screen.getByRole('alert');
    Vitest.expect(alert.className).toContain('my-alert');
  });
});

Vitest.describe('AlertTitle component', () => {
  Vitest.it('renders as h5 element', () => {
    render(<AlertTitle>Title</AlertTitle>);
    const title = screen.getByText('Title');
    Vitest.expect(title.tagName).toBe('H5');
  });

  Vitest.it('forwards ref', () => {
    const ref = createRef<HTMLParagraphElement>();
    render(<AlertTitle ref={ref}>Ref title</AlertTitle>);
    Vitest.expect(ref.current).toBeInstanceOf(HTMLHeadingElement);
  });

  Vitest.it('applies custom className', () => {
    render(<AlertTitle className='custom-title'>Title</AlertTitle>);
    Vitest.expect(screen.getByText('Title').className).toContain('custom-title');
  });
});

Vitest.describe('AlertDescription component', () => {
  Vitest.it('renders children', () => {
    render(<AlertDescription>Description text</AlertDescription>);
    Vitest.expect(screen.getByText('Description text')).toBeInTheDocument();
  });

  Vitest.it('renders as div element', () => {
    render(<AlertDescription>Desc</AlertDescription>);
    Vitest.expect(screen.getByText('Desc').tagName).toBe('DIV');
  });

  Vitest.it('forwards ref', () => {
    const ref = createRef<HTMLParagraphElement>();
    render(<AlertDescription ref={ref}>Ref desc</AlertDescription>);
    Vitest.expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });
});

Vitest.describe('Alert composition', () => {
  Vitest.it('renders title and description together', () => {
    render(
      <Alert>
        <AlertTitle>Error occurred</AlertTitle>
        <AlertDescription>Please try again later.</AlertDescription>
      </Alert>,
    );
    Vitest.expect(screen.getByText('Error occurred')).toBeInTheDocument();
    Vitest.expect(screen.getByText('Please try again later.')).toBeInTheDocument();
  });
});
