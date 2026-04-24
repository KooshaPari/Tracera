import { render, screen } from '@testing-library/react';
import { createRef } from 'react';
import * as Vitest from 'vitest';

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '../components/Card';

Vitest.describe('Card component', () => {
  Vitest.it('renders with children', () => {
    render(<Card>Card content</Card>);
    Vitest.expect(screen.getByText('Card content')).toBeInTheDocument();
  });

  Vitest.it('forwards ref', () => {
    const ref = createRef<HTMLDivElement>();
    render(<Card ref={ref}>Test</Card>);
    Vitest.expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  Vitest.it('applies custom className', () => {
    render(<Card className='custom-card'>Test</Card>);
    Vitest.expect(screen.getByText('Test').className).toContain('custom-card');
  });
});

Vitest.describe('CardHeader component', () => {
  Vitest.it('renders with children', () => {
    render(<CardHeader>Header</CardHeader>);
    Vitest.expect(screen.getByText('Header')).toBeInTheDocument();
  });

  Vitest.it('forwards ref', () => {
    const ref = createRef<HTMLDivElement>();
    render(<CardHeader ref={ref}>Header</CardHeader>);
    Vitest.expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  Vitest.it('applies custom className', () => {
    render(<CardHeader className='custom-header'>Header</CardHeader>);
    Vitest.expect(screen.getByText('Header').className).toContain('custom-header');
  });
});

Vitest.describe('CardTitle component', () => {
  Vitest.it('renders as h3 element', () => {
    render(<CardTitle>Title</CardTitle>);
    const title = screen.getByText('Title');
    Vitest.expect(title.tagName).toBe('H3');
  });

  Vitest.it('forwards ref', () => {
    const ref = createRef<HTMLParagraphElement>();
    render(<CardTitle ref={ref}>Title</CardTitle>);
    Vitest.expect(ref.current).toBeInstanceOf(HTMLHeadingElement);
  });
});

Vitest.describe('CardDescription component', () => {
  Vitest.it('renders as p element', () => {
    render(<CardDescription>Description</CardDescription>);
    const desc = screen.getByText('Description');
    Vitest.expect(desc.tagName).toBe('P');
  });

  Vitest.it('applies custom className', () => {
    render(<CardDescription className='custom-desc'>Desc</CardDescription>);
    Vitest.expect(screen.getByText('Desc').className).toContain('custom-desc');
  });
});

Vitest.describe('CardContent component', () => {
  Vitest.it('renders children', () => {
    render(<CardContent>Content here</CardContent>);
    Vitest.expect(screen.getByText('Content here')).toBeInTheDocument();
  });

  Vitest.it('forwards ref', () => {
    const ref = createRef<HTMLDivElement>();
    render(<CardContent ref={ref}>Content</CardContent>);
    Vitest.expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });
});

Vitest.describe('CardFooter component', () => {
  Vitest.it('renders children', () => {
    render(<CardFooter>Footer</CardFooter>);
    Vitest.expect(screen.getByText('Footer')).toBeInTheDocument();
  });

  Vitest.it('forwards ref', () => {
    const ref = createRef<HTMLDivElement>();
    render(<CardFooter ref={ref}>Footer</CardFooter>);
    Vitest.expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });
});

Vitest.describe('Card composition', () => {
  Vitest.it('renders a complete card with all sub-components', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>My Card</CardTitle>
          <CardDescription>A description</CardDescription>
        </CardHeader>
        <CardContent>Main content</CardContent>
        <CardFooter>Footer content</CardFooter>
      </Card>,
    );

    Vitest.expect(screen.getByText('My Card')).toBeInTheDocument();
    Vitest.expect(screen.getByText('A description')).toBeInTheDocument();
    Vitest.expect(screen.getByText('Main content')).toBeInTheDocument();
    Vitest.expect(screen.getByText('Footer content')).toBeInTheDocument();
  });
});
