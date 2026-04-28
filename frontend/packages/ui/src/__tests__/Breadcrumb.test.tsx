import { render, screen } from '@testing-library/react';
import { createRef } from 'react';
import * as Vitest from 'vitest';

import {
  Breadcrumb,
  BreadcrumbEllipsis,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '../components/Breadcrumb';

Vitest.describe('Breadcrumb component', () => {
  Vitest.it('renders as nav element with aria-label', () => {
    render(
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href='/'>Home</BreadcrumbLink>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>,
    );
    const nav = screen.getByLabelText('breadcrumb');
    Vitest.expect(nav.tagName).toBe('NAV');
  });

  Vitest.it('forwards ref', () => {
    const ref = createRef<HTMLElement>();
    render(
      <Breadcrumb ref={ref}>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href='/'>Home</BreadcrumbLink>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>,
    );
    Vitest.expect(ref.current).toBeInstanceOf(HTMLElement);
  });
});

Vitest.describe('BreadcrumbList component', () => {
  Vitest.it('renders as ol element', () => {
    render(
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href='/'>Home</BreadcrumbLink>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>,
    );
    Vitest.expect(screen.getByRole('list')).toBeInTheDocument();
  });

  Vitest.it('applies custom className', () => {
    render(
      <Breadcrumb>
        <BreadcrumbList className='custom-list'>
          <BreadcrumbItem>
            <BreadcrumbLink href='/'>Home</BreadcrumbLink>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>,
    );
    Vitest.expect(screen.getByRole('list').className).toContain('custom-list');
  });
});

Vitest.describe('BreadcrumbItem component', () => {
  Vitest.it('renders as li element', () => {
    render(
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href='/'>Home</BreadcrumbLink>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>,
    );
    Vitest.expect(screen.getByRole('listitem')).toBeInTheDocument();
  });
});

Vitest.describe('BreadcrumbLink component', () => {
  Vitest.it('renders as anchor by default', () => {
    render(
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href='/home'>Home</BreadcrumbLink>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>,
    );
    const link = screen.getByRole('link', { name: 'Home' });
    Vitest.expect(link).toHaveAttribute('href', '/home');
  });

  Vitest.it('renders as child component when asChild is true', () => {
    render(
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink asChild>
              <span data-testid='custom-link'>Custom</span>
            </BreadcrumbLink>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>,
    );
    Vitest.expect(screen.getByTestId('custom-link')).toBeInTheDocument();
  });
});

Vitest.describe('BreadcrumbPage component', () => {
  Vitest.it('renders with aria-current=page', () => {
    render(
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbPage>Current Page</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>,
    );
    const page = screen.getByText('Current Page');
    Vitest.expect(page).toHaveAttribute('aria-current', 'page');
    Vitest.expect(page).toHaveAttribute('aria-disabled', 'true');
  });
});

Vitest.describe('BreadcrumbSeparator component', () => {
  Vitest.it('renders with aria-hidden', () => {
    const { container } = render(
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href='/'>Home</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>Page</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>,
    );
    const separator = container.querySelector("[aria-hidden='true']");
    Vitest.expect(separator).toBeInTheDocument();
  });

  Vitest.it('renders custom separator content', () => {
    render(
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbSeparator>/</BreadcrumbSeparator>
        </BreadcrumbList>
      </Breadcrumb>,
    );
    Vitest.expect(screen.getByText('/')).toBeInTheDocument();
  });
});

Vitest.describe('BreadcrumbEllipsis component', () => {
  Vitest.it('renders with aria-hidden', () => {
    const { container } = render(
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbEllipsis />
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>,
    );
    const ellipsis = container.querySelector("[aria-hidden='true']");
    Vitest.expect(ellipsis).toBeInTheDocument();
  });

  Vitest.it('has sr-only text for accessibility', () => {
    render(
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbEllipsis />
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>,
    );
    Vitest.expect(screen.getByText('More')).toBeInTheDocument();
  });
});
